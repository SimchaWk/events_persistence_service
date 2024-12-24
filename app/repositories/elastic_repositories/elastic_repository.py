import os
from typing import Dict, Any, List, Optional
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from elasticsearch.helpers import streaming_bulk

from app.config.elastic_config.elastic_connection import elastic_client

load_dotenv(verbose=True)

terror_events_index = os.environ.get("TERROR_EVENTS_INDEX")


def transform_event_for_elastic(event: Dict[str, Any]) -> Dict[str, Any]:
    elastic_doc = {
        "event_id": event.get("event_id"),
        "event_date": event.get("event_date"),
        "location": {
            "country": event.get("country"),
            "city": event.get("city"),
            "region": event.get("region"),
            "province_or_state": event.get("province_or_state")
        },
        "terror_groups": event.get("terror_groups", []),
        "attack_types": event.get("attack_types", []),
        "target_details": event.get("target_details", []),
        "data_source": event.get("data_source")
    }

    if "latitude" in event and "longitude" in event:
        elastic_doc["location"]["coordinates"] = {
            "lat": event["latitude"],
            "lon": event["longitude"]
        }

    if "description" in event:
        elastic_doc["description"] = event["description"]
    if "summary" in event:
        elastic_doc["summary"] = event["summary"]

    return elastic_doc


def save_terror_events_to_elastic(
        events: List[Dict[str, Any]],
        elastic_client: Elasticsearch = elastic_client) -> None:
    try:
        actions = [
            {
                "_index": terror_events_index,
                "_id": event["event_id"],
                "_source": transform_event_for_elastic(event)
            }
            for event in events
        ]

        success, failed = 0, 0
        for ok, item in streaming_bulk(elastic_client, actions, chunk_size=500, max_retries=3):
            if ok:
                success += 1
            else:
                failed += 1
                print(f"Failed to index document: {item}")

        print(f"Indexed {success} documents to Elasticsearch. Failed: {failed}")

    except Exception as e:
        print(f"Error saving to Elasticsearch: {e}")


def create_base_query(keywords: str, limit: Optional[int] = None) -> Dict[str, Any]:
    query = {
        "bool": {
            "should": [
                {"match": {"description": keywords}},
                {"match": {"summary": keywords}}
            ],
            "minimum_should_match": 1
        }
    }

    body = {
        "query": query,
        "sort": [{"_score": "desc"}]
    }

    if limit:
        body["size"] = limit

    return body


def search_by_query(
        index_name: str,
        query: Dict[str, Any],
        client: Elasticsearch = elastic_client
) -> Dict[str, Any]:
    try:
        return client.search(
            index=index_name,
            body=query
        )
    except Exception as e:
        raise Exception(f"Search failed: {str(e)}")
