from typing import List, Dict, Any, Optional
from pymongo.collection import Collection

from app.config.mongo_config.mongo_client import terror_events_collection
from app.repositories.mongo_repositories.mongo_queries_repository import (
    query_deadly_attack_types, query_casualties_by_region, query_top_terrorist_groups,
    query_attack_frequency, query_attack_type_target_correlation, query_attack_change_by_region,
    query_terror_heatmap_data,
)


def get_collection_schema():
    sample_doc = terror_events_collection.find_one()
    if sample_doc:
        print("Sample document structure:")
        for key, value in sample_doc.items():
            print(f"{key}: {type(value)}")


# 1
def get_deadly_attack_types(
        collection: Collection = terror_events_collection,
        top_n: Optional[int] = None
) -> List[Dict[str, Any]]:
    pipeline = query_deadly_attack_types(top_n)
    return list(collection.aggregate(pipeline))


# 2
def get_casualties_by_region(
        collection=terror_events_collection,
        top_n: Optional[int] = None
) -> List[Dict[str, Any]]:
    pipeline = query_casualties_by_region(top_n)
    return list(collection.aggregate(pipeline))


# 3
def get_top_terrorist_groups(
        collection=terror_events_collection,
        top_n: Optional[int] = None
) -> List[Dict[str, Any]]:
    pipeline = query_top_terrorist_groups(top_n)
    return list(collection.aggregate(pipeline))


# 4
def get_attack_type_target_correlation(collection=terror_events_collection):
    pipeline = query_attack_type_target_correlation()
    return list(collection.aggregate(pipeline))


# 5
def get_attack_frequency(collection=terror_events_collection):
    pipeline = query_attack_frequency()
    return list(collection.aggregate(pipeline))


# 6
def get_attack_change_by_region(collection=terror_events_collection, top_n=None):
    pipeline = query_attack_change_by_region(top_n)
    return list(collection.aggregate(pipeline))


# 7
def get_terror_heatmap_data(
        collection=terror_events_collection,
        time_period: str = 'year',
        start_year: int = 1970
) -> List[Dict[str, Any]]:
    pipeline = query_terror_heatmap_data(time_period, start_year)
    return list(collection.aggregate(pipeline))


if __name__ == '__main__':
    print(
        get_casualties_by_region()
    )
