from app.repositories.mongo_repositories.terror_events_repository import get_deadly_attack_types


def test_get_deadly_attack_types():
    print(
        get_deadly_attack_types()
    )