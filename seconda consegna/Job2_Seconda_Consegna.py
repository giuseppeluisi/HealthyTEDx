import sys
import json
import pyspark
from pyspark.sql.functions import col, collect_list, array_join

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job


##### DA FILES
tedx_dataset_path = "s3://tedx-prova-2024/tags.csv"

# Leggi i parametri
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Avvia i contesti Spark e Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Inizializza il job Glue
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Carica il dataset dei tag
tags_dataset = spark.read.option("header", "true").csv(tedx_dataset_path)

# Definisci i tag di interesse
new_tags = ['nutrition','food', 'diet', 'healthy', 'vegetarian', 'veganism', 'protein', 'carbohydrates', 'vitamins', 'minerals', 'calories', 'cuisine', 'recipes', 'meals', 'eat', 'sports', 'exercise', 'fitness', 'physical activity', 'motivation']

# Filtra i tag relativi alla nutrizione e allo sport
filtered_tags_dataset = tags_dataset.filter(
    col("tag").isin(new_tags))

# output con i nuovi tag
output_path = "s3://tedx-prova-2024/filtered_tags.csv" 

# Scrivi il dataset filtrato in output
filtered_tags_dataset.write.mode("overwrite").csv(output_path, header=True)

# Commit del job
job.commit()

# Scrivi i dati su MongoDB
write_mongo_options = {
    "connectionName": "TEDX2024_1",
    "database": "unibg_tedx_2024",
    "collection": "tedx_data_2",
    "ssl": "true",
    "ssl.domain_match": "false"}

from awsglue.dynamicframe import DynamicFrame
tedx_dataset_dynamic_frame = DynamicFrame.fromDF(filtered_tags_dataset, glueContext, "nested")

glueContext.write_dynamic_frame.from_options(tedx_dataset_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)

