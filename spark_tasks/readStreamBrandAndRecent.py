import sys
import findspark
import redis
import json
import dateutil.parser

findspark.init()

kafkaHost = "localhost"
kafkaPort = "9094"
kafkaTopic = "timestamp"


def processRecentItem(db, inputRow):
    inputRowKey = inputRow.key
    if inputRowKey:
        inputRowValue = json.loads(inputRow.value)
        keyMap = "event:Recent:" + inputRowKey
        if db.exists(keyMap):
            parsedPreviousHashValue = json.loads(db.get(keyMap))
            if 'dateAdded' in parsedPreviousHashValue:
                previousDateAdded = dateutil.parser.parse(parsedPreviousHashValue['dateAdded'])
                if 'dateAdded' in inputRowValue:
                    inputRowDateAdded = dateutil.parser.parse(inputRowValue['dateAdded'])
                    if (inputRowDateAdded > previousDateAdded):
                        with db.lock('my_lock-2'):
                            db.set(keyMap, inputRow.value)
        else:
            with db.lock('my_lock-2'):
                db.set(keyMap, inputRow.value)


def processBrandCount(db, inputRow):
    inputRowKey = inputRow.key
    inputRowValue = json.loads(inputRow.value)
    if inputRowKey:
        keyMap = "event:Brand:" + inputRowKey
        if db.exists(keyMap):
            previousHashValue = json.loads(db.get(keyMap))
            if inputRowValue['brand']:
                inputRowBrand = inputRowValue['brand']
                if inputRowBrand in previousHashValue:
                    previousHashValue[inputRowBrand] = int(previousHashValue[inputRowBrand]) + 1
                    with db.lock('my_lock'):
                        db.set(keyMap, json.dumps(previousHashValue))
        else:
            brands = {inputRowValue['brand']: 1}
            with db.lock('my_lock'):
                db.set(keyMap, json.dumps(brands))


def processRow(inputRow):
    db = redis.StrictRedis('localhost')
    processRecentItem(db, inputRow)
    processBrandCount(db, inputRow)


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
        df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", kafkaHost + ":" + kafkaPort).option(
            "startingOffsets", "latest").option("subscribe", kafkaTopic).load()
        streamedDf = df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")
        queryProcess = streamedDf.writeStream.foreach(processRow).start()
        queryProcess.awaitTermination(200)
    except ImportError as e:
        print("Can not import Spark Modules", e)
        sys.exit(1)


startStreaming()