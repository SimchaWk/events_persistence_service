from typing import Dict, List, Optional
import os
from kafka import KafkaConsumer
import json

from app.config.neo4j_config.neo4j_connection import driver
from app.repositories.memgraph_repository.neo4j_queries_repository import (
    get_create_constraints_queries, get_create_nodes_query, get_create_relationships_query
)

def create_constraints() -> bool:
    with driver.session() as session:
        try:
            for query in get_create_constraints_queries():
                session.run(query)
            return True
        except Exception as e:
            print(f"Error creating constraints: {e}")
            return False


def handle_nodes(node_type: str, nodes: List[Dict]) -> Optional[List[Dict]]:
    with driver.session() as session:
        try:
            print(f"Attempting to create {len(nodes)} nodes of type {node_type}")
            query = get_create_nodes_query(node_type)
            result = session.run(query, nodes=nodes)
            print(f"Finished creating nodes of type {node_type}")
            return result.data()
        except Exception as e:
            print(f"Error handling nodes: {e}")
            return None

def handle_relationships(relationships: List[Dict]) -> Optional[List[Dict]]:
    with driver.session() as session:
        try:
            print(f"Attempting to create {len(relationships)} relationships")
            query = get_create_relationships_query()
            result = session.run(query, relationships=relationships)
            print(f"Finished creating relationships")
            return result.data()
        except Exception as e:
            print(f"Error handling relationships: {e}")
            return None


def verify_data():
    with driver.session() as session:
        try:
            # בדיקת כמות צמתים מכל סוג
            nodes_query = """
            MATCH (n)
            RETURN labels(n) as type, count(*) as count
            """
            nodes_result = session.run(nodes_query).data()
            print("Nodes count:", nodes_result)

            # בדיקת כמות קשרים מכל סוג
            rels_query = """
            MATCH ()-[r]->()
            RETURN type(r) as type, count(*) as count
            """
            rels_result = session.run(rels_query).data()
            print("Relationships count:", rels_result)

        except Exception as e:
            print(f"Error verifying data: {e}")




