def get_create_nodes_query(node_type: str) -> str:
    return f"""
    UNWIND $nodes AS node
    MERGE (n:{node_type} {{id: node.id}})
    SET n += node
    """


def get_create_relationships_query() -> str:
    return """
    UNWIND $relationships AS rel
    MATCH (source) WHERE source.id = rel.source_id
    MATCH (target) WHERE target.id = rel.target_id
    MERGE (source)-[r:`${rel.relation_type}`]->(target)
    SET r += rel.properties
    """


def get_create_constraints_queries() -> list[str]:
    return [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (g:TerrorGroup) REQUIRE g.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Attack) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Target) REQUIRE t.id IS UNIQUE"
    ]
