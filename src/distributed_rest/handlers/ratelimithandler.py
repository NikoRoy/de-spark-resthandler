from __future__ import annotations
from typing import Dict, List, Optional, Iterable
from pyspark.sql import DataFrame, SparkSession, Row

class SparkRateLimiter:
    def __init__(self, spark: SparkSession, limit: int, unit_time: str, margin: float = 0.1):
        self.spark = spark
        self.limit = limit
        self.unit_time = unit_time

        assert 0 <= margin <= 1
        self.margin = margin
        self._usage_factor = 1-self.margin



    def limit(self, df: DataFrame) -> DataFrame:
        pass

#usage example

# srl = SparkRateLimiter(spark, 100, 'second') 100/s
# for df in srl.limit(df):
#   df.union(df)