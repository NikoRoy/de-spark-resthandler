import unittest
from unittest.mock import patch
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

from distributed_rest.handlers.sparkrestapihandler import SparkRestApiHandler
from distributed_rest.models.model import BearerToken


class TestSparkRestApiHandler(unittest.TestCase):
    
    def setUp(self):
        self.sparkrestapihandler = SparkRestApiHandler(token=BearerToken('r32791rh3n', 3600))

    def test_combine(self):
        tocomb = [["Latest","LatestOfficial","DP1", "DP2", "DP3", "DP4", "DP5", "DP6", "DP7", "DP8", "DP9", "DP10"],
                    ["Reported","Planned","WorkingTime","Available","ReportedLocked"]]
        ct = 0
        for _ in self.sparkrestapihandler._combine(*tocomb):
            ct += 1
        self.assertEqual(ct, len(tocomb[0])*len(tocomb[1]))

    def test_format_row(self):
        #columns = ["verb", "url", "body", "page"]
        column_headers = {"verb": "POST", "url": "http://example.com/v1/endpoint?limit={limit}&offset={offset}", "body": {'baselineFilter': None, 'timeTypes': None}, "page": None}
        row: Row = self.sparkrestapihandler.format_row(column_headers.keys())  
        self.assertIsInstance(row, Row)
        self.assertIn('verb', row)
        self.assertIn('url', row)
        self.assertIn('body', row)
        self.assertIn('page', row)
        self.assertNotIn('result', row)

    def test_format_combinatorics_dataframe(self):
        spark = SparkSession.builder.getOrCreate()
        to_combine = [
                ["Latest","LatestOfficial","DP1", "DP2", "DP3", "DP4", "DP5", "DP6", "DP7", "DP8", "DP9", "DP10"], 
                ["Reported","Planned","WorkingTime","Available","ReportedLocked"]
            ]
        comb_body_map = {'baselineFilter': "{{'kind': 'BasedOnSelection', 'selections': ['{0}']}}", 'timeTypes': '[{0}]'}
        column_headers = {"verb": "POST", "url": "http://example.com/v1/endpoint", "body": "{'baselineFilter': {baselineFilter}, 'timeTypes': {timeTypes}}", "page": None}
        df: DataFrame = self.sparkrestapihandler.format_combinatorics_dataframe(spark, to_combine, comb_body_map, column_headers)
        self.assertIsInstance(df, DataFrame)
        self.assertEqual(df.count(), len(to_combine[0])*len(to_combine[1]))

    def test_format_offset_dataframe(self):
        spark = SparkSession.builder.getOrCreate()
        offset = 0
        limit = 100
        total = 1052
        expected = (total // limit) 
        expected += 1 if total % limit > 0 else 0
        column_headers = {"verb": "POST", "url": "http://example.com/v1/endpoint?limit={limit}&offset={offset}", "body": "{'baselineFilter': None, 'timeTypes': None}", "page": None}

        df: DataFrame = self.sparkrestapihandler.format_offset_dataframe(spark, offset=offset, limit=limit, total=total, column_headers=column_headers)
        self.assertIsInstance(df, DataFrame)
        self.assertEqual(df.count(), expected)

    def test_format_paginated_dataframe(self):
        spark = SparkSession.builder.getOrCreate()
        pages = 4
        column_headers = {"verb": "GET", "url": "http://example.com/v1/endpoint?page={page}", "body": '{}', "page": 0}
        df: DataFrame = self.sparkrestapihandler.format_paginated_dataframe(spark, pages, column_headers)
        self.assertIsInstance(df, DataFrame)
        self.assertEqual(df.count(), pages)

    def test_execute_formatted_rest_api(self):
        column_headers = {"verb": "GET", "url": "http://example.com/v1/endpoint?page={page}", "body": '{}', "page": 0}
        with patch('distributed_rest.handlers.sparkrestapihandler.requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'status': 'success'}
            response = self.sparkrestapihandler.execute_formatted_rest_api(column_headers["verb"], column_headers["url"], column_headers["body"])
            self.assertEqual(response, {'status': 'success'})
            mock_get.assert_called_once()

    def test_empty_formatted_df(self):
        spark = SparkSession.builder.getOrCreate()
        formatted_rowtype = self.sparkrestapihandler.format_row(["verb", "url", "body", "page"])
        formatted_df = spark.createDataFrame([formatted_rowtype('Get', 'http://', 'head, hands, legs', 1)])
        self.assertIsInstance(formatted_rowtype, Row)
        self.assertIsInstance(formatted_df, DataFrame)