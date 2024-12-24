from typing import List

import networkx as nx
import pickle

from app.config.local_files_config.local_files import EVENTS_GRAPH_NETWORKX
from app.config.neo4j_config.neo4j_connection import driver
from app.repositories.graph_repository.graph_queries_repository import get_regions_high_group_activity_query, \
    get_shared_attack_types_query, get_groups_shared_targets_query


def load_local_graph():
    with open(EVENTS_GRAPH_NETWORKX, 'rb') as f:
        return pickle.load(f)


def load_graph_to_memgraph(nx_graph: nx.Graph):
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

        for node_id, data in nx_graph.nodes(data=True):
            node_type = data.get('type')
            properties = {k: v for k, v in data.items() if k != 'type'}
            properties['id'] = str(node_id)

            props_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
            query = f"CREATE (:{node_type} {{{props_str}}})"
            session.run(query, parameters=properties)

        for source, target, data in nx_graph.edges(data=True):
            rel_type = data.get('type', 'RELATED_TO')
            properties = {k: v for k, v in data.items() if k != 'type'}

            query = f"""
            MATCH (source), (target)
            WHERE source.id = $source_id AND target.id = $target_id
            CREATE (source)-[r:{rel_type}]->(target)
            SET r += $properties
            """

            session.run(query, {
                'source_id': str(source),
                'target_id': str(target),
                'properties': properties
            })


def init_database():
    try:
        nx_graph = load_local_graph()

        load_graph_to_memgraph(nx_graph)

        with driver.session() as session:
            nodes = session.run("MATCH (n) RETURN count(n) as count").single()['count']
            rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()['count']

        print(f"Loaded {nodes} nodes and {rels} relationships")
        return True

    except Exception as e:
        print(f"Error initializing database: {e}")
        return False


# 16
def get_regions_high_group_activity(filter_by: str = None, filter_value: str = None) -> list:
    with driver.session() as session:
        try:
            query = get_regions_high_group_activity_query(filter_by, filter_value)
            result = session.run(query)
            return [record.data() for record in result]
        except Exception as e:
            print(f"Error in get_regions_high_group_activity: {e}")
            return []


# 14
def get_shared_attack_types(filter_by: str = None, filter_value: str = None) -> list:
    with driver.session() as session:
        try:
            query = get_shared_attack_types_query(filter_by, filter_value)
            result = session.run(query)
            return [record.data() for record in result]
        except Exception as e:
            print(f"Error in get_shared_attack_types: {e}")
            return []


# 11
def get_groups_shared_targets(filter_by: str = None, filter_value: str = None) -> list:
    with driver.session() as session:
        try:
            query = get_groups_shared_targets_query(filter_by, filter_value)
            result = session.run(query)
            return [record.data() for record in result]
        except Exception as e:
            print(f"Error in get_groups_shared_targets: {e}")
            return []


#########

def connection():
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN n")
        return result.single()


def find_group_activity_by_region(filter_by: str = None, filter_value: str = None):
    with driver.session() as session:
        try:
            where_clause = ""
            if filter_by and filter_value:
                where_clause = f"WHERE l.{filter_by} = '{filter_value}'"

            query = f"""
            MATCH (l:Location)<-[:OCCURRED_IN]-(a:Attack)<-[:ATTACKED]-(g:TerrorGroup)
            {where_clause}
            WITH l, collect(DISTINCT g) as groups
            RETURN l.country as country,
                   l.region as region,
                   l.latitude as latitude,
                   l.longitude as longitude,
                   groups,
                   size(groups) as unique_groups_count
            ORDER BY unique_groups_count DESC
            """

            result = session.run(query)
            return [record.data() for record in result]

        except Exception as e:
            print(f"Error finding group activity by region: {e}")
            return None


if __name__ == "__main__":
    # init_database()
    print(
        get_regions_high_group_activity()
    )
