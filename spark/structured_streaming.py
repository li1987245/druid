# coding=utf-8
from __future__ import print_function
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, window
from pyspark.sql.functions import split

spark = SparkSession.builder.appName("StructuredNetworkWordCount").getOrCreate()
# Create DataFrame representing the stream of input lines from connection to localhost:9999
lines = spark \
    .readStream \
    .format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .option('includeTimestamp', 'true') \
    .load()
lines.isStreaming()    # Returns True for DataFrames that have streaming sources

lines.printSchema()

# Split the lines into words,explode arr to row
words = lines.select(
    explode(
        split(lines.value, " ")
    ).alias("word"),
    lines.timestamp
)
# 窗口函数 Group the data by window and word and compute the count of each group,aggregation with 10 min windows,
# sliding every 5 mins
windowedCounts = words.groupBy(
    window(words.timestamp, "5 minutes", "1 minutes"),
    words.word
).count()

# Group the data by window and word and compute the count of each group
# windowedCounts = words \
#     .withWatermark("timestamp", "10 minutes") \
#     .groupBy(
#         window(words.timestamp, "10 minutes", "5 minutes"),
#         words.word) \
#     .count()

# streamingDf.join(staticDf, "type")  # inner equi-join with a static DF
# streamingDf.join(staticDf, "type", "right_join")  # right outer join with a static DF

#Without watermark using guid column
# lines.dropDuplicates("guid")

#With watermark using guid and eventTime columns
# lines \
#   .withWatermark("eventTime", "10 seconds") \
#   .dropDuplicates("guid", "eventTime")

# Generate running word count
# wordCounts = words.groupBy("word").count()
# Start running the query that prints the running counts to the console,output model complete/append/update(2.1.1+)
'''
The “Output” is defined as what gets written out to the external storage. The output can be defined in a different mode:

Complete Mode - The entire updated Result Table will be written to the external storage. It is up to the storage connector to decide how to handle writing of the entire table.

Append Mode - Only the new rows appended in the Result Table since the last trigger will be written to the external storage. This is applicable only on the queries where existing rows in the Result Table are not expected to change.

Update Mode - Only the rows that were updated in the Result Table since the last trigger will be written to the external storage (available since Spark 2.1.1). Note that this is different from the Complete Mode in that this mode only outputs the rows that have changed since the last trigger. If the query doesn’t contain aggregations, it will be equivalent to Append mode.
'''
query = windowedCounts\
        .writeStream\
        .outputMode('complete')\
        .format('console')\
        .option('truncate', 'false')\
        .start()

# writeStream
#     .format("parquet")        // can be "orc", "json", "csv", etc.
#     .option("path", "path/to/destination/dir")
#     .start()
# writeStream
#     .foreach(...)
#     .start()

query.awaitTermination()
