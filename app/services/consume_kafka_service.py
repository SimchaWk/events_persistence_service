import json
import os
from datetime import datetime, UTC
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


def process_kafka_messages(
        topic: str,
        batch_size: int = 100,
        save_fns: List[callable] = None
) -> None:
    consumer = create_kafka_consumer(topic)
    batch = []

    try:
        for message in consumer:
            try:
                event = (
                    json.loads(message.value)
                    if isinstance(message.value, str)
                    else message.value
                )

                event['received_at'] = datetime.now(UTC).isoformat()
                batch.append(event)

                if len(batch) >= batch_size:
                    [save_fn(batch) for save_fn in save_fns]
                    consumer.commit()
                    batch = []

            except json.JSONDecodeError as e:
                print(f"Error decoding message: {e}")
                continue

    except Exception as e:
        print(f"Error processing messages: {e}")
    finally:
        if batch:
            [save_fn(batch) for save_fn in save_fns]
        consumer.close()


def consume_for_mongo_and_elastic():
    KAFKA_TOPIC = os.environ['TERROR_EVENTS']
    BATCH_SIZE = 100

    setup_terror_events_index(elastic_client)

    save_functions = [
        save_terror_events_to_mongo,
        save_terror_events_to_elastic
    ]

    process_kafka_messages(
        topic=KAFKA_TOPIC,
        batch_size=BATCH_SIZE,
        save_fns=save_functions
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
    consume_for_mongo_and_elastic()
    # consume_for_neo4j()
    pass
