import json
import os
import time
from datetime import datetime, UTC
from functools import partial
from typing import List

from app.config.elastic_config.elastic_connection import elastic_client
from app.config.kafka_config.consumer import create_kafka_consumer
from app.repositories.elastic_repositories.elastic_repository import save_terror_events_to_elastic
from app.repositories.elastic_repositories.setup_es_indices import setup_terror_events_index
from app.repositories.graph_repository.neo4j_entities_repository import (
    create_constraints, handle_nodes, handle_relationships
)
from app.repositories.graph_repository.networkx_graph_repository import (
    load_or_create_graph, handle_nodes_networkx, handle_relationships_networkx,
    save_graph, print_graph_stats_networkx
)

from app.services.storage_service import save_terror_events_to_mongo


def process_kafka_messages(topic: str, batch_size: int = 100, save_fns: List[callable] = None, timeout_seconds: int = 60) -> None:
    consumer = create_kafka_consumer(topic)
    batch = []
    last_save = time.time()

    try:
        for message in consumer:
            try:
                event = json.loads(message.value) if isinstance(message.value, str) else message.value
                event['received_at'] = datetime.now(UTC).isoformat()
                batch.append(event)

                current_time = time.time()
                if len(batch) >= batch_size or (current_time - last_save) >= timeout_seconds:
                    [save_fn(batch) for save_fn in save_fns]
                    consumer.commit()
                    batch = []
                    last_save = current_time

            except json.JSONDecodeError as e:
                print(f"Error decoding message: {e}")
                continue

    except Exception as e:
        print(f"Error processing messages: {e}")
    finally:
        if batch:
            [save_fn(batch) for save_fn in save_fns]
        consumer.close()


def consume_for_mongo_and_elastic(topic_name: str, batch_size: int = 100) -> None:

    setup_terror_events_index(elastic_client)

    save_functions = [
        save_terror_events_to_mongo,
        save_terror_events_to_elastic
    ]

    process_kafka_messages(
        topic=topic_name,
        batch_size=batch_size,
        save_fns=save_functions
    )


consume_real_time_for_mongo_and_elastic = partial(
    consume_for_mongo_and_elastic,
    topic_name=os.environ['TERROR_EVENTS'],
    batch_size=50
)


consume_history_for_mongo_and_elastic = partial(
    consume_for_mongo_and_elastic,
    topic_name=os.environ['API_TERROR_EVENTS'],
    batch_size=100
)


def consume_for_neo4j():
    consumer = create_kafka_consumer(os.environ['NEO4J_ENTITIES'])

    try:
        create_constraints()

        for message in consumer:
            try:
                data = message.value
                if data['type'] == 'nodes':
                    handle_nodes(data['node_type'], data['data'])
                elif data['type'] == 'relationships':
                    handle_relationships(data['data'])
                consumer.commit()
            except Exception as e:
                print(f"Error processing message: {e}")
    finally:
        consumer.close()


def consume_for_networkx():
    consumer = create_kafka_consumer(os.environ['NEO4J_ENTITIES'])
    G = load_or_create_graph()

    try:
        for message in consumer:
            try:
                data = message.value
                if data['type'] == 'nodes':
                    handle_nodes_networkx(G, data['node_type'], data['data'])
                elif data['type'] == 'relationships':
                    handle_relationships_networkx(G, data['data'])

                if message.offset % 1000 == 0:
                    save_graph(G)

                consumer.commit()
            except Exception as e:
                print(f"Error processing message: {e}")
    finally:
        save_graph(G)
        print_graph_stats_networkx(G)


if __name__ == "__main__":
    consume_history_for_mongo_and_elastic()
    # consume_for_neo4j()
    pass
