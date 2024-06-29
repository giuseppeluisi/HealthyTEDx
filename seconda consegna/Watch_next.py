###### TEDx-Load-Aggregate-Model
######

import sys
import json
import pyspark
from pyspark.sql.functions import col, collect_list, array_join

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job




##### FROM FILES
tedx_dataset_path = "s3://tedx-progetto-2024/final_list.csv"

###### READ PARAMETERS
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

##### START JOB CONTEXT AND JOB
sc = SparkContext()


glueContext = GlueContext(sc)
spark = glueContext.spark_session


    
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


#### READ INPUT FILES TO CREATE AN INPUT DATASET
tedx_dataset = spark.read \
    .option("header","true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(tedx_dataset_path)
    
tedx_dataset.printSchema()


#### FILTER ITEMS WITH NULL POSTING KEY
count_items = tedx_dataset.count()
count_items_null = tedx_dataset.filter("id is not null").count()

print(f"Number of items from RAW DATA {count_items}")
print(f"Number of items from RAW DATA with NOT NULL KEY {count_items_null}")

## READ THE DETAILS
details_dataset_path = "s3://tedx-progetto-2024/details.csv"
details_dataset = spark.read \
    .option("header","true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(details_dataset_path)

details_dataset = details_dataset.select(col("id").alias("id_ref"),
                                         col("description"),
                                         col("duration"),
                                         col("publishedAt"))

# AND JOIN WITH THE MAIN TABLE
tedx_dataset_main = tedx_dataset.join(details_dataset, tedx_dataset.id == details_dataset.id_ref, "left") \
    .drop("id_ref")

tedx_dataset_main.printSchema()

## READ THE IMAGES (VERSIONE NUOVA)
images_dataset_path = "s3://tedx-progetto-2024/images.csv"
images_dataset = spark.read \
    .option("header","true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(images_dataset_path)
 
images_dataset = images_dataset.select(col("id").alias("id_ref"),
                                         col("url").alias("image_url"))
 
# AND JOIN WITH THE MAIN TABLE
tedx_dataset_main = tedx_dataset.join(details_dataset, tedx_dataset.id == details_dataset.id_ref, "left") \
    .drop("id_ref")
#VERSIONE NUOVA DEL JOIN
tedx_dataset_main = tedx_dataset_main.join(images_dataset, tedx_dataset_main.id == images_dataset.id_ref, "left") \
    .drop("id_ref")
    
## ADD RELATED VIDEO
related_video_path = "s3://tedx-progetto-2024/related_videos.csv"
related_video = spark.read \
    .option("header","true") \
    .option("quote", "\"") \
    .option("escape", "\"") \
    .csv(related_video_path)
    
## DELETE DUPLICATES
related_video = related_video.dropDuplicates()

related_video_agg = related_video.groupBy(col("id").alias("id_rel")) \
        .agg(collect_list("related_id").alias("id_related_video"), collect_list("title").alias("title_related_video"))
## JOIN WITH DATASET
tedx_dataset_agg_with_related_video = tedx_dataset_main.join(related_video_agg, tedx_dataset_main.id == related_video_agg.id_rel, "left")\
    .drop("id_rel") \
    .select(col("id").alias("id_related"), col("*")) 

tedx_dataset_agg_with_related_video.printSchema()

## READ TAGS DATASET
tags_dataset_path = "s3://tedx-progetto-2024/tags.csv"
tags_dataset = spark.read.option("header","true").csv(tags_dataset_path)


# CREATE THE AGGREGATE MODEL, ADD TAGS TO TEDX_DATASET
tags_dataset_agg = tags_dataset.groupBy(col("id").alias("id_ref")).agg(collect_list("tag").alias("tags"))
tags_dataset_agg.printSchema()
tedx_dataset_agg = tedx_dataset_agg_with_related_video.join(tags_dataset_agg, tedx_dataset.id == tags_dataset_agg.id_ref, "left") \
    .drop("id_ref") \
    .select(col("id").alias("_id"), col("*")) \
    .drop("id") \
    
tedx_dataset_agg.printSchema()


write_mongo_options = {
    "connectionName": "TEDX2024_1",
    "database": "unibg_tedx_2024",
    "collection": "tedx_data_1",
    "ssl": "true",
    "ssl.domain_match": "false"}
from awsglue.dynamicframe import DynamicFrame
tedx_dataset_dynamic_frame = DynamicFrame.fromDF(tedx_dataset_agg, glueContext, "nested")

glueContext.write_dynamic_frame.from_options(tedx_dataset_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)
