from flask import Flask

from app.routes.elasticsearch_routes import elastic_bp
from app.routes.graph_routes import graph_bp
from app.routes.terror_events_routes import event_bp
from app.services.consume_kafka_service import consume_real_time_for_mongo_and_elastic
from app.utils.process_utils import run_parallel


def run_flask():
    app = Flask(__name__)
    app.register_blueprint(event_bp, url_prefix="/terror_events")
    app.register_blueprint(graph_bp, url_prefix="/graph_events")
    app.register_blueprint(elastic_bp, url_prefix="/search")
    app.run()


STARTUP_TASKS = [
    run_flask,
    consume_real_time_for_mongo_and_elastic()
]


if __name__ == '__main__':
    run_parallel(STARTUP_TASKS)
