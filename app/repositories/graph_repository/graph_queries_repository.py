def get_regions_high_group_activity_query(filter_by: str = None, filter_value: str = None) -> str:
    query = """
    MATCH (l:locations)<-[:OCCURRED_IN]-(a:attacks)<-[:ATTACKED]-(g:terror_groups)
    WITH l, g, COUNT(a) as attacks_count
    WITH l, COLLECT({
        id: g.id,
        name: g.name,
        subname: g.subname,
        attacks: attacks_count
    }) as groups, SUM(attacks_count) as total_attacks
    """

    if filter_by and filter_value:
        query += f"WHERE l.{filter_by} = '{filter_value}' "

    query += """
    RETURN l.country as country,
           l.region as region,
           l.latitude as latitude,
           l.longitude as longitude,
           groups as groups,
           size(groups) as unique_groups_count,
           total_attacks
    ORDER BY total_attacks DESC
    """
    return query


# 14
def get_shared_attack_types_query(filter_by: str = None, filter_value: str = None) -> str:
    query = """
    MATCH (l:locations)<-[:OCCURRED_IN]-(a:attacks)<-[:ATTACKED]-(g:terror_groups)
    WITH l, g, a.attack_types as attack_type
    UNWIND attack_type as single_type
    WITH l, single_type, COLLECT(DISTINCT g.name) as groups
    WITH l, 
         COLLECT({
            attack_type: single_type,
            groups: groups,
            groups_count: SIZE(groups)
         }) as attack_strategies
    """

    if filter_by and filter_value:
        query += f"WHERE l.{filter_by} = '{filter_value}' "

    query += """
    RETURN l.country as country,
           l.region as region,
           l.latitude as latitude,
           l.longitude as longitude,
           attack_strategies,
           SIZE(attack_strategies) as unique_attack_types_count
    ORDER BY unique_attack_types_count DESC
    """
    return query


# 11
def get_groups_shared_targets_query(filter_by: str = None, filter_value: str = None) -> str:
    query = """
    MATCH (l:locations)<-[:OCCURRED_IN]-(a:attacks)<-[:ATTACKED]-(g:terror_groups)
    WITH l, g, COLLECT(DISTINCT a.attack_types) as target_types
    WITH l, target_types, COLLECT(DISTINCT g.name) as group_names
    WITH l, COLLECT({
        target_types: target_types,
        groups: group_names,
        groups_count: SIZE(group_names)
    }) as shared_targets
    WITH l, shared_targets,
         REDUCE(max = 0, x IN shared_targets | CASE WHEN x.groups_count > max THEN x.groups_count ELSE max END) as max_shared_groups
    """

    if filter_by and filter_value:
        query += f"WHERE l.{filter_by} = '{filter_value}' "

    query += """
    RETURN l.country as country,
           l.region as region,
           l.latitude as latitude,
           l.longitude as longitude,
           shared_targets,
           max_shared_groups
    ORDER BY max_shared_groups DESC
    """
    return query
