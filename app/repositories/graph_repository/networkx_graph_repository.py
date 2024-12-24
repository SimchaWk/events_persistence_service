import networkx as nx
from typing import Dict, List
import os
import pickle

from app.config.local_files_config.local_files import EVENTS_GRAPH_NETWORKX


def load_or_create_graph() -> nx.Graph:
    if os.path.exists(EVENTS_GRAPH_NETWORKX):
        with open(EVENTS_GRAPH_NETWORKX, 'rb') as f:
            return pickle.load(f)
    return nx.Graph()


def save_graph(G: nx.Graph):
    with open(EVENTS_GRAPH_NETWORKX, 'wb') as f:
        pickle.dump(G, f)


def handle_nodes_networkx(G: nx.Graph, node_type: str, nodes: List[Dict]) -> None:
    try:
        for node in nodes:
            G.add_node(node['id'], **node, type=node_type)
        print(f"Added {len(nodes)} nodes of type {node_type}")
    except Exception as e:
        print(f"Error handling nodes: {e}")


def handle_relationships_networkx(G: nx.Graph, relationships: List[Dict]) -> None:
    try:
        for rel in relationships:
            G.add_edge(
                rel['source_id'],
                rel['target_id'],
                **rel['properties'],
                type=rel['relation_type']
            )
        print(f"Added {len(relationships)} relationships")
    except Exception as e:
        print(f"Error handling relationships: {e}")


def print_graph_stats_networkx(G: nx.Graph):
    print("\nGraph Statistics:")
    print(f"Number of nodes: {G.number_of_nodes()}")
    print(f"Number of edges: {G.number_of_edges()}")

    node_types = {}
    for node, attrs in G.nodes(data=True):
        node_type = attrs.get('type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1

    print("\nNodes by type:")
    for node_type, count in node_types.items():
        print(f"- {node_type}: {count}")

    edge_types = {}
    for _, _, attrs in G.edges(data=True):
        edge_type = attrs.get('type', 'unknown')
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

    print("\nEdges by type:")
    for edge_type, count in edge_types.items():
        print(f"- {edge_type}: {count}")


if __name__ == '__main__':
    G = load_or_create_graph()
    print_graph_stats_networkx(G)
