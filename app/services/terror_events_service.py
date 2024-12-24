from typing import List, Dict, Any, Optional, Union

from app.repositories.mongo_repositories.terror_events_repository import (
    get_deadly_attack_types, get_casualties_by_region, get_top_terrorist_groups,
    get_attack_frequency, get_attack_type_target_correlation, get_attack_change_by_region,
    get_terror_heatmap_data
)
from app.services.map_service import create_basic_casualties_map, create_terror_heatmap


# 1
def process_deadly_attack_types(top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    raw_data = get_deadly_attack_types(top_n=top_n)
    return [
        {
            'attack_type': item['_id'],
            'total_damage': item.get('total_damage', 0),
            'total_events': item.get('total_events', 0)
        } for item in raw_data
    ]


# 2
def process_casualties_by_region(
        top_n: Optional[int] = None,
        include_map: bool = False
) -> Union[List[Dict[str, Any]], str]:
    raw_data = get_casualties_by_region(top_n=top_n)

    processed_data = [
        {
            'region': item['_id'],
            'avg_killed': item.get('avg_killed', 0),
            'avg_wounded': item.get('avg_wounded', 0),
            'total_events': item.get('total_events', 0),
            'latitude': item.get('representative_location', {}).get('latitude', 0),
            'longitude': item.get('representative_location', {}).get('longitude', 0),
        } for item in raw_data
    ]

    return create_basic_casualties_map(processed_data) if include_map else processed_data


def process_casualties_by_region1(top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    raw_data = get_casualties_by_region(top_n=top_n)
    return [
        {
            'region': item['_id'],
            # 'avg_killed': f"{item.get('avg_killed', 0):.2%}",
            # 'avg_wounded': f"{item.get('avg_wounded', 0):.2%}",
            'avg_killed': item.get('avg_killed', 0),
            'avg_wounded': item.get('avg_wounded', 0),
            'total_events': item.get('total_events', 0),
            'latitude': item.get('avg_latitude', 0),
            'longitude': item.get('avg_longitude', 0),
        } for item in raw_data
    ]


# 3
def process_top_terrorist_groups(top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    raw_data = get_top_terrorist_groups(top_n=top_n)
    return [
        {
            'terror_group': item['_id'],
            'total_killed': item.get('total_killed', 0),
            'total_wounded': item.get('total_wounded', 0),
            'total_events': item.get('total_events', 0),
            'avg_latitude': item.get('avg_latitude', 0),
            'avg_longitude': item.get('avg_longitude', 0),
        } for item in raw_data
    ]


# 4
def process_attack_type_target_correlation() -> List[Dict[str, Any]]:
    raw_data = get_attack_type_target_correlation()
    return [
        {
            'attack_type': item['_id']['attack_type'],
            'target_type': item['_id']['target_type'],
            'total_events': item.get('total_events', 0)
        } for item in raw_data
    ]


# 5
def process_attack_frequency() -> List[Dict[str, Any]]:
    raw_data = get_attack_frequency()
    return [
        {
            'year': item['_id']['year'],
            'month': item['_id']['month'],
            'total_events': item.get('total_events', 0),
            'total_killed': item.get('total_killed', 0),
            'total_wounded': item.get('total_wounded', 0)
        } for item in raw_data
    ]


# 6
def process_attack_change_by_region(top_n=None):
    raw_data = get_attack_change_by_region(top_n=top_n)
    return [
        {
            'region': item['region'],
            'yearly_changes': [
                {
                    'year': change['year'],
                    'previous_year': change['previous_year'],
                    'percent_change': round(change['percent_change'], 2)
                }
                for change in item.get('yearly_changes', [])
            ]
        } for item in raw_data
    ]


# 7
def process_terror_heatmap_data(
        time_period: str = 'year',
        start_year: int = 1970,
        include_map: bool = False
) -> Union[List[Dict[str, Any]], str]:
    raw_data = get_terror_heatmap_data(
        time_period=time_period,
        start_year=start_year
    )

    processed_data = [
        {
            'latitude': item['latitude'],
            'longitude': item['longitude'],
            'year': item['year'],
            'month': item['month'],
            'events_count': item['events_count'],
            'total_casualties': item['total_casualties']
        }
        for item in raw_data
    ]

    return create_terror_heatmap(processed_data) if include_map else processed_data


if __name__ == '__main__':
    process_deadly_attack_types()
