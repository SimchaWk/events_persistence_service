from flask import Blueprint, jsonify, request

from app.repositories.graph_repository.memgraph_repository import get_regions_high_group_activity
from app.services.graph_service import get_regions_high_group_activity_data, get_attack_strategies_data, \
    create_attack_strategies_map, get_shared_targets_data, create_shared_targets_map
from app.services.map_service import create_high_group_activity_map

graph_bp = Blueprint('groups', __name__)

# 16
@graph_bp.route('/high-group-activity', methods=['GET'])
def high_group_activity_route():
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    try:
        data = get_regions_high_group_activity(filter_by, filter_value)
        return create_high_group_activity_map(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 14
@graph_bp.route('/attack-strategies', methods=['GET'])
def attack_strategies_route():
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    try:
        data = get_attack_strategies_data(filter_by, filter_value)
        map_html = create_attack_strategies_map(data)
        return map_html
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 11
@graph_bp.route('/shared-targets', methods=['GET'])
def shared_targets_route():
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    try:
        data = get_shared_targets_data(filter_by, filter_value)
        map_html = create_shared_targets_map(data)
        return map_html
    except Exception as e:
        return jsonify({'error': str(e)}), 500