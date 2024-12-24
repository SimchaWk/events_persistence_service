import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from app.repositories.elastic_repositories.elastic_repository import create_base_query, search_by_query

load_dotenv(verbose=True)

terror_events = os.environ['TERROR_EVENTS_INDEX']


def format_results(results: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "total": results["hits"]["total"]["value"],
        "results": [hit["_source"] for hit in results["hits"]["hits"]]
    }


def search_all(keywords: str, limit: Optional[int] = None, index_name: str = terror_events) -> Dict[str, Any]:
    query = create_base_query(keywords, limit)
    results = search_by_query(index_name, query)
    return format_results(results)


def search_news(keywords: str, limit: Optional[int] = None, index_name: str = terror_events) -> Dict[str, Any]:
    query = create_base_query(keywords, limit)
    query["query"]["bool"]["must"] = [{"term": {"data_source": "news"}}]
    results = search_by_query(index_name, query)
    return format_results(results)


def search_historic(keywords: str, limit: Optional[int] = None, index_name: str = terror_events) -> Dict[
    str, Any]:
    query = create_base_query(keywords, limit)
    query["query"]["bool"]["must_not"] = [{"term": {"data_source": "news"}}]
    results = search_by_query(index_name, query)
    return format_results(results)


def search_combined(
        keywords: str,
        start_date: Optional[str] = None, end_date: Optional[str] = None,
        limit: Optional[int] = None,
        index_name: str = terror_events
) -> Dict[str, Any]:
    query = create_base_query(keywords, limit)

    if start_date or end_date:
        date_range = {}
        if start_date:
            date_range["gte"] = start_date
        if end_date:
            date_range["lte"] = end_date

        query["query"]["bool"]["filter"] = [
            {"range": {"event_date": date_range}}
        ]

    results = search_by_query(index_name, query)
    return format_results(results)
