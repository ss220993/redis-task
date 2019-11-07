import os
import sys
import findspark
findspark.init()

kafkaHost = "localhost"
kafkaPort = "9093"
kafkaTopic = "colors"
inputPath = 'redis-task/womens-shoes-prices-1'

def startStreaming():
  try:
      from pyspark import SparkContext
      from pyspark import SparkConf
      from pyspark.python.pyspark.shell import sc
      from pyspark.sql import SQLContext
      from pyspark.sql.functions import date_format
      from pyspark.sql.functions import to_json, struct
      from pyspark.sql.session import SparkSession
      import json
      from pyspark.sql.types import TimestampType, StringType, StructType, StructField
      spark = SparkSession(sc)
      columns = ['dateAdded', 'id','brand', 'colors']
      schema = StructType([ StructField("id", StringType(), True),
                        StructField("dateAdded", StringType(), True),
                        StructField("dateUpdated", StringType(), True),
                        StructField("asins", StringType(), True),
                        StructField("brand", StringType(), True),
                        StructField("categories", StringType(), True),
                        StructField("primaryCategories", StringType(), True),
                        StructField("colors", StringType(), True)])
      df = spark.readStream.schema(schema).option("sep", ",").option("header", "true").option("enforceSchema", "true").csv(inputPath)
      read = df.select((df.dateAdded).alias('key'),to_json(struct([df[x] for x in columns])).alias("value")).writeStream.format("kafka").option("kafka.bootstrap.servers", kafkaHost+":"+kafkaPort).option("topic",kafkaTopic).option("checkpointLocation", "checkpoint").start()
      read.awaitTermination(2000)
  except ImportError as e:
      print ("Can not import Spark Modules", e)
      sys.exit(1)

startStreaming()