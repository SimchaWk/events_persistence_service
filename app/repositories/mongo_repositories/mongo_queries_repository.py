from typing import List, Dict, Any, Optional


# 1 - Deadly attack types
def query_deadly_attack_types(top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    pipeline = [
        {
            '$unwind': '$attack_types'
        },
        {
            '$match': {
                'attack_types': {'$ne': 'Unknown'}
            }
        },
        {
            '$group': {
                '_id': '$attack_types',
                'total_damage': {
                    '$sum': {
                        '$add': [
                            {'$multiply': [{'$ifNull': ['$num_terrorist_killed', 0]}, 2]},
                            {'$ifNull': ['$num_terrorist_wounded', 0]}
                        ]
                    }
                },
                'total_events': {'$sum': 1}
            }
        },
        {'$sort': {'total_damage': -1}}
    ]

    if top_n:
        pipeline.append({'$limit': top_n})

    return pipeline


# 2 - Casualties by region
def query_casualties_by_region(top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    pipeline = [
        {
            '$group': {
                '_id': '$region',
                'total_events': {'$sum': 1},
                'avg_killed': {'$avg': {'$ifNull': ['$num_killed', 0]}},
                'avg_wounded': {'$avg': {'$ifNull': ['$num_wounded', 0]}},
                'total_casualties': {
                    '$sum': {
                        '$add': [
                            {'$ifNull': ['$num_killed', 0]},
                            {'$ifNull': ['$num_wounded', 0]}
                        ]
                    }
                },
                'representative_location': {
                    '$first': {
                        'latitude': '$latitude',
                        'longitude': '$longitude'
                    }
                }
            }
        },
        {'$sort': {'total_casualties': -1}}
    ]

    pipeline.append({'$limit': top_n}) if top_n else None

    return pipeline


# 3 - Top terrorist groups
def query_top_terrorist_groups(top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    pipeline = [
        {
            '$unwind': '$terror_groups'  # Unwind the terror groups array
        },
        {
            '$match': {
                'terror_groups': {'$ne': 'Unknown'}
            }
        },
        {
            '$group': {
                '_id': '$terror_groups',
                'total_killed': {'$sum': {'$ifNull': ['$num_terrorist_killed', 0]}},
                'total_wounded': {'$sum': {'$ifNull': ['$num_terrorist_wounded', 0]}},
                'total_events': {'$sum': 1},
                'avg_latitude': {'$avg': '$latitude'},
                'avg_longitude': {'$avg': '$longitude'}
            }
        },
        {'$sort': {'total_killed': -1}}
    ]

    if top_n:
        pipeline.append({'$limit': top_n})

    return pipeline


# 4 - Attack type and target correlation
def query_attack_type_target_correlation() -> List[Dict[str, Any]]:
    pipeline = [
        {
            '$unwind': '$attack_types'  # Unwind the attack types array
        },
        {
            '$unwind': '$target_details'  # Unwind the target details array
        },
        {
            '$group': {
                '_id': {
                    'attack_type': '$attack_types',
                    'target_type': '$target_details'
                },
                'total_events': {'$sum': 1}
            }
        },
        {'$sort': {'total_events': -1}}
    ]

    return pipeline


# 5 - Attack frequency
def query_attack_frequency() -> List[Dict[str, Any]]:
    pipeline = [
        {
            '$group': {
                '_id': {
                    'year': {'$year': {'$toDate': '$event_date'}},
                    'month': {'$month': {'$toDate': '$event_date'}}
                },
                'total_events': {'$sum': 1},
                'total_killed': {'$sum': {'$ifNull': ['$num_terrorist_killed', 0]}},
                'total_wounded': {'$sum': {'$ifNull': ['$num_terrorist_wounded', 0]}}
            }
        },
        {'$sort': {'_id.year': 1, '_id.month': 1}}
    ]

    return pipeline


# 6 - Attack change by region
def query_attack_change_by_region(top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    pipeline = [
        {
            "$match": {
                "region": {"$ne": None},
                "event_date": {"$ne": None}
            }
        },
        {
            "$addFields": {
                "year": {"$year": {"$toDate": "$event_date"}}
            }
        },
        {
            "$group": {
                "_id": {
                    "region": "$region",
                    "year": "$year"
                },
                "event_count": {"$sum": 1}
            }
        },
        {
            "$sort": {
                "_id.region": 1,
                "_id.year": 1
            }
        },
        {
            "$group": {
                "_id": "$_id.region",
                "years": {
                    "$push": {
                        "year": "$_id.year",
                        "event_count": "$event_count"
                    }
                }
            }
        },
        {
            "$project": {
                "region": "$_id",
                "_id": 0,
                "yearly_changes": {
                    "$map": {
                        "input": {"$range": [1, {"$size": "$years"}]},
                        "as": "index",
                        "in": {
                            "year": {
                                "$arrayElemAt": ["$years.year", "$$index"]
                            },
                            "previous_year": {
                                "$arrayElemAt": ["$years.year", {"$subtract": ["$$index", 1]}]
                            },
                            "percent_change": {
                                "$multiply": [
                                    100,
                                    {
                                        "$divide": [
                                            {
                                                "$subtract": [
                                                    {"$arrayElemAt": ["$years.event_count", "$$index"]},
                                                    {"$arrayElemAt": ["$years.event_count",
                                                                      {"$subtract": ["$$index", 1]}]}
                                                ]
                                            },
                                            {"$arrayElemAt": ["$years.event_count", {"$subtract": ["$$index", 1]}]}
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }
            }
        }
    ]

    pipeline.append({'$limit': top_n}) if top_n else None

    return pipeline


# 7 -
def query_terror_heatmap_data(time_period: str = 'year', start_year: int = 1970) -> List[Dict[str, Any]]:

    # חישוב טווח השנים בהתאם לפרמטרים
    year_ranges = {
        'year': 1,
        '3_years': 3,
        '5_years': 5
    }

    years_to_fetch = year_ranges.get(time_period, 1)
    end_year = start_year + years_to_fetch

    pipeline = [
        {
            "$match": {
                "latitude": {"$exists": True, "$ne": None},
                "longitude": {"$exists": True, "$ne": None},
                "event_date": {"$exists": True, "$ne": None}
            }
        },
        {
            "$addFields": {
                "year": {"$year": {"$toDate": "$event_date"}},
                "month": {"$month": {"$toDate": "$event_date"}}
            }
        },
        {
            "$match": {
                "year": {
                    "$gte": start_year,
                    "$lt": end_year
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "latitude": "$latitude",
                    "longitude": "$longitude",
                    "year": "$year",
                    "month": "$month"
                },
                "location": {
                    "$first": {
                        "latitude": "$latitude",
                        "longitude": "$longitude"
                    }
                },
                "events_count": {"$sum": 1},
                "total_casualties": {
                    "$sum": {
                        "$add": [
                            {"$ifNull": ["$num_killed", 0]},
                            {"$ifNull": ["$num_wounded", 0]}
                        ]
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "latitude": "$location.latitude",
                "longitude": "$location.longitude",
                "year": "$_id.year",
                "month": "$_id.month",
                "events_count": 1,
                "total_casualties": 1
            }
        },
        {
            "$sort": {"year": 1, "month": 1}
        }
    ]

    return pipeline
