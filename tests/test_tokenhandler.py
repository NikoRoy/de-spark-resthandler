import unittest
# import requests
# from requests.auth import HTTPBasicAuth
from unittest.mock import patch, MagicMock
from distributed_rest.handlers.tokenhandler import TokenHandler
from distributed_rest.models.model import BearerToken


class TestTokenHandler(unittest.TestCase):
    def setUp(self):
        self.tokenhandler = TokenHandler('http://example.com/token', 'user01', 'pwd12345')

    def tearDown(self):
        self.tokenhandler = None

    @patch('distributed_rest.handlers.tokenhandler.HTTPBasicAuth', autospec=True)
    @patch.object(TokenHandler, '_start', autospec=True)
    def test_get_access_token(self, mock_start, MockHttpAuth):
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'access_token': '1234abc',
                'token_type': 'bearer',
                'expires_in': 3600,
                'scope': 'api',
                'grant_type': 'client_credentials'
            }
            mock_post.return_value = mock_response
            mock_start.return_value = None

            self.tokenhandler.get_access_token()

            self.assertIsInstance(self.tokenhandler.bearer_token, BearerToken)
            self.assertEqual(self.tokenhandler.bearer_token.access_token, '1234abc')
            self.assertEqual(self.tokenhandler.bearer_token.token_type, 'bearer')
            self.assertEqual(self.tokenhandler.bearer_token.expires_in, 3600)
            self.assertEqual(self.tokenhandler.bearer_token.scope, 'api')
            self.assertEqual(self.tokenhandler.bearer_token.grant_type, 'client_credentials')
            MockHttpAuth.assert_called_once_with('user01', 'pwd12345')
            mock_post.assert_called_once_with('http://example.com/token', auth=MockHttpAuth.return_value, data={'grant_type': 'client_credentials', 'scope': 'api'}, headers={'Content-Type': 'application/x-www-form-urlencoded'})
            mock_start.assert_called_once()

    def test_timer_elapsed_eventhandler(self):
        with patch.object(self.tokenhandler, 'get_access_token') as mock_get_access_token:
            #mock up fake token for get_access_token called by event handler
            mock_get_access_token.return_value = BearerToken('262703t4', 60).access_token

            handler = MagicMock(return_value=None)
            self.tokenhandler.on_token_refreshed.subscribe(handler)  
            self.tokenhandler.timer_elapsed_eventhandler()

            mock_get_access_token.assert_called_once()
            handler.assert_called_once()
            handler.assert_called_with('262703t4')

    # mock EventTimer class with respect to import in TokenHandler not the original module
    # this allows us to test the EventTimer instantiation in the start method
    @patch('distributed_rest.handlers.tokenhandler.EventTimer', autospec=True) 
    def test_start(self, MockEventTimer):
        self.tokenhandler.bearer_token = BearerToken('262703t4', 60)
        mock_timer_instance = MockEventTimer.return_value
        mock_timer_instance.start.return_value = None
        mock_timer_instance.on_timer_elapsed = MagicMock()
        mock_timer_instance.on_timer_elapsed.subscribe = MagicMock()
        
        self.tokenhandler._start()

        # assert construction with calculated interval
        MockEventTimer.assert_called_once_with(45)  
        # assert mock object is same as tokenhandler timer
        self.assertEqual(self.tokenhandler.token_timer, mock_timer_instance)
        # assert mock instance registers real tokenhandler eventhandler
        mock_timer_instance.on_timer_elapsed.subscribe.assert_called_once()
        self.assertIn(self.tokenhandler.timer_elapsed_eventhandler, mock_timer_instance.on_timer_elapsed.subscribe.call_args[0])
        # assert we started the timer
        mock_timer_instance.start.assert_called()

    def test_stop(self):
        with patch.object(self.tokenhandler, 'token_timer', new_callable=MagicMock) as mock_timer:
            mock_timer.active = True
            def side_effect():
                mock_timer.active = False
            mock_timer.stop.side_effect = side_effect
            mock_timer.stop.return_value = None
            
            self.tokenhandler._stop()

            mock_timer.stop.assert_called()
            self.assertFalse(mock_timer.active)
