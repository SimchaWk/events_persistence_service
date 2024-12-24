from typing import List, Dict

from app.config.elastic_config.elastic_connection import elastic_client
from app.config.mongo_config.mongo_client import terror_events_collection


def save_terror_events_to_mongo(events: List[Dict]) -> bool:
    try:
        if events:
            result = terror_events_collection.insert_many(events)
            print(f"Inserted {len(result.inserted_ids)} events into MongoDB.")
            return True
        else:
            print("No events to insert.")
            return False

    except Exception as e:
        print(f"Error saving batch to MongoDB: {str(e)}")
        return False


def save_terror_event_to_mongo(event: Dict) -> bool:
    try:

        result = terror_events_collection.insert_one(event)
        print(result)

        return result

    except Exception as e:
        print(f"Error saving to MongoDB: {str(e)}")
        return False


def save_to_elastic(event_id: str, description: str) -> bool:
    try:
        doc = {
            'event_id': event_id,
            'description': description
        }

        result = elastic_client.index(
            index='terror-events-descriptions',
            document=doc,
            id=event_id
        )
        return result['result'] in ['created', 'updated']

    except Exception as e:
        print(f"Error saving to Elasticsearch: {str(e)}")
        return False


if __name__ == '__main__':
    pass
