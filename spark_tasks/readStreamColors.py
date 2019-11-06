import os
import sys
import findspark
import redis
import json
import dateutil.parser
findspark.init()

kafkaHost = "localhost"
kafkaPort = "9093"
kafkaTopic = "colors"

def processColors(db, inputRow):
  inp = json.loads(inputRow.value)
  if 'colors' in inp:
    colors = inp['colors'].split(',')
    for color in colors:
      keyMap = "event:Color:" + color
      if inputRow.key != 'dateAdded':
        epoch_time = int(dateutil.parser.parse(inputRow.key).timestamp())
        db.zadd(keyMap, {inputRow.value: epoch_time})

def processRow(inputRow):
  db = redis.StrictRedis('localhost')
  processColors(db, inputRow)

def startStreaming():
  try:
      from pyspark import SparkContext
      from pyspark import SparkConf
      from pyspark.python.pyspark.shell import sc
      from pyspark.sql import SQLContext
      from pyspark.sql.session import SparkSession
      from pyspark.sql.functions import to_json, struct, from_json
      from pyspark.sql.types import StringType, StructType, StructField
      spark = SparkSession(sc)
      df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", kafkaHost+":"+kafkaPort).option("startingOffsets", "latest").option("subscribe", kafkaTopic).load()
      streamedDf = df.selectExpr("CAST(key AS STRING)","CAST(value AS STRING)")
      queryProcess = streamedDf.writeStream.foreach(processRow).start()
      queryProcess.awaitTermination(200)
  except ImportError as e:
      print ("Can not import Spark Modules", e)
      sys.exit(1)

startStreaming()