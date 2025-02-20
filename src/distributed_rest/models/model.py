import requests
from dataclasses import dataclass
from typing import Dict, List, Optional, Literal, Iterable
from enum import Enum

class RequestVerb(Enum):
    GET = 0
    POST = 1
    PUT = 2
    DELETE = 3
    PATCH = 4

    @property
    def action(self):
        return [
            requests.get,
            requests.post,
            requests.put,
            requests.delete,
            requests.patch
        ][self.value]

@dataclass
class BearerToken:
    access_token: str
    expires_in: int
    token_type: Optional[str] = None
    scope: Optional[str] = None
    grant_type: Optional[str] = None  

@dataclass
class RequestParameter:
    name: Optional[str] = None
    page: Optional[int] = None
    type: Optional[str] = None
    state: Optional[Literal['On', 'Off']] = None 
    date: Optional[str] = None

@dataclass
class ResponseSchema:
    name: str
    type: str
    nullable: bool
    metadata: Dict[str, str]

@dataclass
class ResponseInfo:
    count: int
    page: int
    next: Optional[str]
    prev: Optional[str]

@dataclass
class Response:
    info: ResponseInfo
    results: List[ResponseSchema]

    def __post_init__(self):
        self.info = ResponseInfo(**self.info)
        self.results = [ResponseSchema(**result) for result in self.results]