import os
from dotenv import load_dotenv

from app.config.elastic_config.elastic_connection import elastic_client

load_dotenv(verbose=True)

TASK_INDEX = os.environ.get("TASK_INDEX")


def setup_task_index():
    """Create the 'tasks' index with a proper mapping if it doesn't exist."""
    if not elastic_client.indices.exists(index=TASK_INDEX):
        body = {
            "mappings": {
                "properties": {
                    "id": {"type": "integer"},
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "is_completed": {"type": "boolean"},
                    "due_date": {"type": "date"}
                }
            }
        }
        elastic_client.indices.create(index=TASK_INDEX, body=body)
        print(f"Index '{TASK_INDEX}' created successfully.")
    else:
        print(f"Index '{TASK_INDEX}' already exists.")
