import unittest
from unittest.mock import patch

from distributed_rest.events.eventtimer import EventTimer

class TestEventTimer(unittest.TestCase):
    
    def setUp(self):
        self.timer = EventTimer(1)

    def tearDown(self):
        self.timer._timer = None
        self.timer = None
    
    @patch('distributed_rest.events.eventtimer.Timer', autospec=True)
    def test_timer_start(self, MockTimer):
        mock_timer_instance = MockTimer.return_value  
        mock_timer_instance.start.return_value = None
        
        self.timer.start()

        self.assertIs(self.timer._timer, mock_timer_instance)
        self.assertTrue(self.timer.active)
        mock_timer_instance.start.assert_called_once()
    
    @patch('distributed_rest.events.eventtimer.Timer', autospec=True)
    def test_timer_stop(self, MockTimer):
        mock_timer_instance = MockTimer.return_value
        mock_timer_instance.cancel.return_value = None
        self.timer._timer = mock_timer_instance

        self.timer.stop()

        self.assertIs(self.timer._timer, mock_timer_instance)
        self.assertFalse(self.timer.active)
        mock_timer_instance.cancel.assert_called_once()
    
    @patch('distributed_rest.events.eventtimer.Timer', autospec=True)
    def test_timer_run(self, MockTimer):
        mock_timer_instance = MockTimer.return_value
        mock_timer_instance.start.return_value = None
        ct = 0
        def elapsed_handler():
            nonlocal ct
            ct +=1
        self.timer.on_timer_elapsed.subscribe(elapsed_handler)

        self.timer._run()
        
        self.assertEqual(ct, 1)
        self.assertIs(self.timer._timer, mock_timer_instance)
        mock_timer_instance.start.assert_called_once()


if __name__ == '__main__':
    unittest.main()
