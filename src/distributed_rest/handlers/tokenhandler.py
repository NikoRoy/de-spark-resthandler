import requests
from typing import Optional
from requests.auth import HTTPBasicAuth

from distributed_rest.events.baseevent import BaseEvent
from distributed_rest.events.eventtimer import EventTimer
from distributed_rest.models.model import BearerToken


class TokenHandler:
    def __init__(
            self,
            token_url: str,
            client_id: str,
            client_secret: str,
            grantType: Optional[str] = 'client_credentials',
            scope: Optional[str] = 'api',
            contentType: Optional[str] = 'application/x-www-form-urlencoded',
            refresh_factor: Optional[float] = 0.75
            ):
        self.token_url = token_url
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.grant_type = grantType
        self.scope = scope
        self.content_type = contentType
        self.refresh_factor = refresh_factor
        self.bearer_token: BearerToken = None
        self.token_timer: EventTimer = None
        self.on_token_refreshed = BaseEvent()

    def _start(self) -> None:
        if not self.token_timer:
            self.token_timer = EventTimer(self.bearer_token.expires_in * self.refresh_factor)
            self.token_timer.on_timer_elapsed.subscribe(self.timer_elapsed_eventhandler)
        self.token_timer.start()

    def _stop(self) -> None:
        self.token_timer.stop()
        return None

    def get_access_token(self) -> None:
        auth = HTTPBasicAuth(self.__client_id, self.__client_secret)
        payload = {
            'grant_type': self.grant_type,
            'scope': self.scope
        }
        headers = {
            'Content-Type': self.content_type
        }
        response = requests.post(self.token_url, auth=auth, data=payload, headers=headers)
        self.bearer_token = BearerToken(**response.json())

        self._start()
        return self.bearer_token.access_token

    # event handler to run every time the token timer elapses
    # this method is the subscriber of the EventTimer event
    def timer_elapsed_eventhandler(self) -> None:
        # refresh and update BearerToken
        token = self.get_access_token()
        # event to notify subscribers of the TokenHandler class that the token has been refreshed
        self.on_token_refreshed._fire(token)
        return None
