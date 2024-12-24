import json
import os
from dotenv import load_dotenv
from kafka import KafkaConsumer

load_dotenv(verbose=True)


def create_kafka_consumer(topic: str) -> KafkaConsumer:
    return KafkaConsumer(
        topic,
        bootstrap_servers=os.environ['BOOTSTRAP_SERVERS'],
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        group_id='terror_events_group',
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )
