import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv(verbose=True)

terror_events_index = os.environ.get("TERROR_EVENTS_INDEX")


def setup_terror_events_index(elastic_client: Elasticsearch) -> None:
    if not elastic_client.indices.exists(index=terror_events_index):
        mapping = {
            "settings": {
                "number_of_shards": 3,
                "number_of_replicas": 1,
                "analysis": {
                    "analyzer": {
                        "standard": {
                            "type": "standard"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "event_id": {"type": "keyword"},
                    "event_date": {"type": "date"},
                    "location": {
                        "properties": {
                            "country": {"type": "keyword"},
                            "city": {"type": "keyword"},
                            "region": {"type": "keyword"},
                            "province_or_state": {"type": "keyword"},
                            "coordinates": {"type": "geo_point"}
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "summary": {
                        "type": "text",
                        "analyzer": "standard",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "terror_groups": {
                        "type": "keyword"
                    },
                    "attack_types": {
                        "type": "keyword"
                    },
                    "target_details": {
                        "type": "keyword"
                    },
                    "data_source": {"type": "keyword"}
                }
            }
        }

        elastic_client.indices.create(index=terror_events_index, body=mapping)
        print(f"Index '{terror_events_index}' created successfully with 3 shards and 1 replica.")
    else:
        print(f"Index '{terror_events_index}' already exists.")
