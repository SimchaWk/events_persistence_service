import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv(verbose=True)

elastic_client = Elasticsearch(
    [os.environ['ELASTICSEARCH_URL']],
    verify_certs=False
)
