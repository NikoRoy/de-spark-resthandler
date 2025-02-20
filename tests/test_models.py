import unittest
import requests
from unittest.mock import patch

from distributed_rest.models.model import RequestVerb


class TestRequestVerb(unittest.TestCase):

    def test_request_verb_enum(self):
        v_get = "GET"
        v_post = "POST"
        v_put = "PUT"
        v_delete = "DELETE"
        v_patch = "PATCH"

        self.assertEqual(RequestVerb[v_get].value, 0)
        self.assertEqual(RequestVerb[v_get].action, requests.get)

        self.assertEqual(RequestVerb[v_post].value, 1)
        self.assertEqual(RequestVerb[v_post].action, requests.post)

        self.assertEqual(RequestVerb[v_put].value, 2)
        self.assertEqual(RequestVerb[v_put].action, requests.put)

        self.assertEqual(RequestVerb[v_delete].value, 3)
        self.assertEqual(RequestVerb[v_delete].action, requests.delete)

        self.assertEqual(RequestVerb[v_patch].value, 4)
        self.assertEqual(RequestVerb[v_patch].action, requests.patch)

    def test_enum_action(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value = "GOT"
            v_get = "GET"
            callable_action = RequestVerb[v_get].action
            response = callable_action("http://example.com")
            self.assertEqual(response, "GOT")
