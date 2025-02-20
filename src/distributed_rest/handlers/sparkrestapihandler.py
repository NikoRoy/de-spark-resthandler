from __future__ import annotations
import requests
import json
from itertools import product
from typing import Dict, List, Optional, Iterable
from pyspark.sql import Row
try:
    from databricks.connect import DatabricksSession as SparkSession
    spark = SparkSession.builder.getOrCreate()
    if spark.version < '3.5':
        from pyspark.sql import DataFrame
    else:
        from pyspark.sql.connect.dataframe import DataFrame
except ImportError:
    from pyspark.sql import SparkSession, DataFrame

from distributed_rest.models.model import BearerToken
from distributed_rest.models.model import RequestVerb


class SparkRestApiHandler:
    _TOKEN: BearerToken

    def __init__(self, token: BearerToken):
        SparkRestApiHandler._TOKEN = token

    #: function to generate cartesian product of the iterables when POST request bodies are unweildy
    # -> return intended to be used to interpolate post body
    def _combine(self, *args: Iterable[Iterable]) -> Iterable[tuple]:
        for it in args:
            if not isinstance(it, Iterable):
                raise ValueError(f'Expected an Iterable but got {type(it)}')
        for combination in product(*args):
            yield combination

    #: function to format the response from the API
    def format_row(self, columns: List[str]) -> Row:
        return Row(*columns)

    #: function to format the combinatorics dataframe
    def format_combinatorics_dataframe(self,
            spark: SparkSession, 
            to_combine: List[List[str]], 
            comb_body_map: Dict[str, str],
            column_headers: Dict[str,str] = {"verb": None, "url": None, "body": {}, "page": 0}
            ) -> DataFrame:
        assert to_combine is not None, 'to_combine cannot be None'
        assert comb_body_map is not None, 'comb_body_map cannot be None'
        assert all([column_headers["body"].__contains__(k) for k in comb_body_map.keys()]), 'All keys in comb_body_map must be present in body'
        def generate_rows():
            base_api_row_type: Row = self.format_row(column_headers.keys())
            page = 0
            keyList = list(comb_body_map.keys()) #['baselineFilter', 'timeTypes']
            for combination in self._combine(*to_combine):    # [1,2,3] * [4,5,6] = [(1,4),(1,5),(1,6), (2,4),(2,5),(2,6), (3,4),(3,5),(3,6)]
                body = column_headers["body"]
                for i in range(len(combination)):    # [(Latest, Reported), (Latest, Planned), ...]
                    key = keyList[i]
                    body=body.replace(f"{{{key}}}", comb_body_map[key].format(combination[i]))
                page += 1
                yield base_api_row_type(column_headers['verb'], column_headers['url'], body, page)
        rows = list(generate_rows())
        return spark.createDataFrame(rows)

    #: function to format offset and limits for pagination
    def format_offset_dataframe(self,
            spark: SparkSession,
            offset: int,
            limit: int,
            total: int,
            column_headers: Dict[str, str] = {"verb": None, "url": None, "body": {}, "page": 0}
            ) -> DataFrame:
        assert isinstance(offset, int), 'Integers must be provided for offset, limit, and total'
        assert isinstance(limit, int), 'Integers must be provided for offset, limit, and total'
        assert isinstance(total, int), 'Integers must be provided for offset, limit, and total'
        assert offset >= 0, 'Integers must be greater than 0'
        assert limit > 0, 'Integers must be greater than 0'
        assert total > 0, 'Integers must be greater than 0'
        assert column_headers["url"].__contains__("{offset}"), 'URL must contain {offset}'
        assert column_headers["url"].__contains__("{limit}"), 'URL must contain {limit}'

        def generate_rows():
            base_api_row_type: Row = self.format_row(column_headers.keys())
            page_ct =  (total // limit) + (1 if total % limit > 0 else 0)
            for page in range(page_ct):
                yield base_api_row_type(
                    column_headers["verb"],
                    column_headers["url"].format(offset=offset, limit=limit),
                    column_headers["body"],
                    page
                )
        res = list(generate_rows())
        return spark.createDataFrame(res)

    #: function to format the paginated dataframe
    def format_paginated_dataframe(
            self,
            spark: SparkSession,
            pages: int,
            column_headers: Dict[str, str] = {"verb": None, "url": None, "body": {}, "page": 0}
            ) -> DataFrame:
        assert isinstance(pages, int), 'Integers must be provided for offset, limit, and total'
        assert pages > 0, 'Integers must be greater than 0'
        assert column_headers["url"].__contains__("{page}"), 'URL must contain {page}'

        def generate_rows():
            base_api_row_type: Row = self.format_row(column_headers.keys())
            for page in range(pages):
                yield base_api_row_type(
                    column_headers["verb"],
                    column_headers["url"].format(page=page),
                    column_headers["body"],
                    page
                )
        res = list(generate_rows())
        return spark.createDataFrame(res)
    
    #: function to execute udf
    def execute_formatted_rest_api(self, verb: str, url: str, body: str, headers = None) -> Optional[Dict]:
        if headers is None:
            headers = {
                'Authorization': f"Bearer {SparkRestApiHandler._TOKEN.access_token}",
                'Content-Type': "application/json"
            }
        # Make API request, get response object back, create dataframe from above schema.
        req_callable = RequestVerb[verb.upper()].action
        res = req_callable(url=url, data=body, headers=headers)
        res.raise_for_status()
        if res is not None:
            return res.json()
        return None

    #: event handler for token refresh
    def token_refresh_eventhandler(self, new_token: BearerToken) -> None:
        """
            usage: tokenhandler = TokenHandler()
            tokenhandler.on_token_refreshed.subscribe(token_refresh_eventhandler)
        """
        SparkRestApiHandler._TOKEN = new_token
        return None


