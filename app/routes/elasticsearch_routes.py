from flask import Blueprint, request, jsonify
from app.services.elastic_service import elastic_service as search_service

elastic_bp = Blueprint('search', __name__)


@elastic_bp.route('/keywords', methods=['GET'])
def search_all():
    keywords = request.args.get('q')
    limit = request.args.get('limit', type=int)

    if not keywords:
        return jsonify({"error": "Missing search keywords"}), 400

    try:
        results = search_service.search_all(keywords=keywords, limit=limit)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@elastic_bp.route('/news', methods=['GET'])
def search_news():
    keywords = request.args.get('q')
    limit = request.args.get('limit', type=int)

    if not keywords:
        return jsonify({"error": "Missing search keywords"}), 400

    try:
        results = search_service.search_news(keywords=keywords, limit=limit)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@elastic_bp.route('/historic', methods=['GET'])
def search_historic():
    keywords = request.args.get('q')
    limit = request.args.get('limit', type=int)

    if not keywords:
        return jsonify({"error": "Missing search keywords"}), 400

    try:
        results = search_service.search_historic(keywords=keywords, limit=limit)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@elastic_bp.route('/combined', methods=['GET'])
def search_combined():
    keywords = request.args.get('q')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', type=int)

    if not keywords:
        return jsonify({"error": "Missing search keywords"}), 400

    try:
        results = search_service.search_combined(
            keywords=keywords, start_date=start_date, end_date=end_date, limit=limit
        )
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
