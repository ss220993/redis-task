# redis-task
Architecture Design

![design](design.png)

**The process is as follows**

1. Get the input directory which contains csv files to be processed.

2. Spark process to get the dataframe and stream it to kafka
   Two things are involved:
   1. Select dataframe having dateAdded (format-> yyy-mm-dd)
   as key and columns(id, dateAdded, brand, colors) as value and 
   stream it to kafka in **topic timestamp**
   2. Select dataframe having dateAdded(as such) as key and columns
   (id,dateAdded, brand, colors) as value and stream it to kafka
   in **topic colors**

3. Kafka reads the stream and process it via spark to select
   key and value from dataframe.
   Every row is processed and stored in Redis Db using the following
   logic.
   
   1.To get the recent item "event:Recent:" + dateAdded(yyy-mm-dd)
   key is used. This key will compare dateAdded(timestamp) with every
   input and store the recent value(id,brand,dateAdded,colors)
   
   2.To get the brands count "event:Brand:" + dateAdded(yyy-mm-dd) key is used.
   This key will have hash of brands and its count. Update the value whenever
   brand is seen for the given dateAdded. Api will fetch the above key for given date
   and sort the value in descending.
   
   3.To get top 10 colors "event:Color" + color key is used and zadd datastructure is used.
   zadd will have dateAdded(epoch) as score and hash of values of that
   record(id, dateAdded, colors, brand). While fetching via api zrevrangebyscore
   is used to get top 10. "event:Color" + color (key is formed by iterating over
   each colors of input record while reading from the stream produced by kafka).
   
   All the 3 processes are done after consumed by Kafka.
   
Apis are done using flask
1.getRecentItem 2. getBrandsCount 3.getRecentItemsbyColor three
are done. 

Docker will have redis, flask, zookeeper and kafka

**Prerequisites:**
1. Kafka to be installed (used version : 2.12-2.3.1) and all kafka related
commands need to be under kafka_2.12-2.3.1 folder.
2. Spark version used 2.4.3
3. Spark submit uses this package org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.1 for kafka
streaming.
4. Input folder womens-shoes-prices-1 and womens-shoes-prices-2 included

**How to execute:**
1. `docker-compose up` inside the redis-task folder.
2. Create two topics timestamp and colors  
  `bin/kafka-topics.sh --create --topic timestamp --zookeeper 0.0.0.0:2181 --partitions 1 --replication-factor 1`  
  `bin/kafka-topics.sh --create --topic colors --zookeeper 0.0.0.0:2181 --partitions 1 --replication-factor 1`
3. start producers consumers in 4 different tabs
   (two producers and two consumers)
   1. Consumer and Producer in topic timestamp listening to port 9094  
   `bin/kafka-console-producer.sh --broker-list 127.0.0.1:9094 --topic timestamp`  
   `bin/kafka-console-consumer.sh --bootstrap-server 127.0.0.1:9094 --topic timestamp`
   2. Consumer and Producer in topic colors listening to port 9093  
   `bin/kafka-console-producer.sh --broker-list 127.0.0.1:9093 --topic colors` 
   `bin/kafka-console-consumer.sh --bootstrap-server 127.0.0.1:9093 --topic colors`
4. Do spark submit for 4 processes in 4 different tabs
   1. Write stream to Kafka for processing timestamp topic (reading from csv each record stream to kafka)   
   `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.1 redis-task/spark_tasks/writeStreamRecentandBrand.py`
   2. Read stream from Kafka for processing timestamp topic      
   `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.1 redis-task/spark_tasks/readStreamBrandAndRecent.py`
   3. Write stream to Kafka for processing colors topic (reading from csv each record stream to kafka)   
   `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.1 redis-task/spark_tasks/writeStreamColors.py`
   2. Read stream from Kafka for processing colors topic      
   `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.1 redis-task/spark_tasks/readStreamColors.py`
5. Hit the Api  
   1. To get top 10 colors.   
   `curl -i -X GET 'http://127.0.0.1:5000/getItemsbyColor/?color=Blue'`
   2. To get recent item.  
   `curl -i -X GET 'http://127.0.0.1:5000/getRecentItem/?date=27-10-11'`
   3. To get brands count   
   `curl -i -X GET 'http://127.0.0.1:5000/getBrandsCount/?date=27-10-11'`
   
*Used docker config using this https://github.com/simplesteph/kafka-stack-docker-compose/blob/master/zk-single-kafka-multiple.yml*
