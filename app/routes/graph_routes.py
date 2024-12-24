from flask import Blueprint, jsonify, request

from app.services.graph_service import get_regions_high_group_activity_data, create_high_group_activity_map

graph_bp = Blueprint('groups', __name__)


@graph_bp.route('/high-group-activity', methods=['GET'])
def high_group_activity_route():
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    try:
        data = get_regions_high_group_activity_data(filter_by, filter_value)
        map_file = create_high_group_activity_map(data)
        return jsonify({
            'data': data,
            'map_file': map_file
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500