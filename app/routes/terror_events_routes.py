from flask import Blueprint, jsonify, request

from app.services.map_service import create_attack_change_map, create_attack_change_map_detailed
from app.services.terror_events_service import (
    process_deadly_attack_types, process_casualties_by_region, process_top_terrorist_groups, process_attack_frequency,
    process_attack_type_target_correlation, process_attack_change_by_region, process_terror_heatmap_data
)
from app.utils.valid_date_util import is_valid_date

event_bp = Blueprint('events', __name__)


# 1
@event_bp.route('/deadly_attacks')
def deadly_attacks():
    try:
        top_n = request.args.get('top', type=int)
        results = process_deadly_attack_types(top_n=top_n)
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 2
@event_bp.route('/casualties_by_region', methods=['GET'])
def get_casualties_by_region():
    try:
        top_n = request.args.get('top', type=int)
        include_map = request.args.get('include_map', type=bool, default=False)

        if top_n is not None and top_n <= 0:
            return jsonify({
                'error': 'Invalid top parameter. Must be a positive integer.'
            }), 400

        results = process_casualties_by_region(
            top_n=top_n,
            include_map=include_map
        )

        if isinstance(results, str):
            return results, 200, {'Content-Type': 'text/html'}

        return jsonify(results)

    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


# 3
@event_bp.route('/top_terrorist_groups', methods=['GET'])
def get_top_terrorist_groups():
    try:
        top_n = request.args.get('top', type=int)

        if top_n is not None and top_n <= 0:
            return jsonify({
                'error': 'Invalid top parameter. Must be a positive integer.'
            }), 400

        results = process_top_terrorist_groups(top_n=top_n if top_n else 5)
        return jsonify(results)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


# 4
@event_bp.route('/attack_type_target_correlation', methods=['GET'])
def get_attack_type_target_correlation():
    try:
        results = process_attack_type_target_correlation()
        return jsonify(results)

    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


# 5 לוודא תקינות
@event_bp.route('/attack_frequency', methods=['GET'])
def get_attack_frequency():
    try:
        freq_type = request.args.get('type', 'all')

        results = process_attack_frequency()

        if freq_type == 'yearly':
            results = [
                item for item in results
                if item['month'] == 1
            ]

        return jsonify(results)

    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


# 6
@event_bp.route('/attack_change_by_region', methods=['GET'])
def get_attack_change_by_region():
    try:
        top_n = request.args.get('top', type=int)
        include_map = request.args.get('include_map', type=bool, default=False)

        if top_n is not None and top_n <= 0:
            return jsonify({
                'error': 'Invalid top parameter. Must be a positive integer.'
            }), 400

        results = process_attack_change_by_region(top_n=top_n)

        if include_map:
            map_html = create_attack_change_map(results)
            return map_html, 200, {'Content-Type': 'text/html'}

        return jsonify(results)

    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


# 6 b
@event_bp.route('/attack_change_by_region_2', methods=['GET'])
def get_attack_change_by_region_2():
    try:
        top_n = request.args.get('top', type=int)
        include_map = request.args.get('include_map', type=bool, default=False)
        detailed = request.args.get('detailed', type=bool, default=False)  # New parameter

        if top_n is not None and top_n <= 0:
            return jsonify({
                'error': 'Invalid top parameter. Must be a positive integer.'
            }), 400

        results = process_attack_change_by_region(top_n=top_n)

        if include_map:
            map_html = create_attack_change_map_detailed(results) if detailed else create_attack_change_map(results)
            return map_html, 200, {'Content-Type': 'text/html'}

        return jsonify(results)

    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


# 7
@event_bp.route('/terror_hotspots', methods=['GET'])
def get_terror_hotspots():
    try:
        time_period = request.args.get('time_period', default='year')
        start_year = request.args.get('start_year', default=1970, type=int)
        include_map = request.args.get('include_map', type=bool, default=False)

        valid_periods = ['year', '3_years', '5_years']
        if time_period not in valid_periods:
            return jsonify({
                'error': f'Invalid time_period. Must be one of: {", ".join(valid_periods)}'
            }), 400

        if start_year < 1970:
            return jsonify({
                'error': 'start_year must be >= 1970'
            }), 400

        results = process_terror_heatmap_data(
            time_period=time_period,
            start_year=start_year,
            include_map=include_map
        )

        if isinstance(results, str):
            return results, 200, {'Content-Type': 'text/html'}

        return jsonify(results)

    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500


@event_bp.route('/geographic_terror_hotspots_2', methods=['GET'])
def get_geographic_hotspots_2():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        include_map = request.args.get('include_map', type=bool, default=False)

        # Validate dates if provided
        if start_date and not is_valid_date(start_date):
            return jsonify({'error': 'Invalid start_date format'}), 400
        if end_date and not is_valid_date(end_date):
            return jsonify({'error': 'Invalid end_date format'}), 400

        results = process_terror_heatmap_data(
            start_date=start_date,
            end_date=end_date,
            include_map=include_map
        )

        if isinstance(results, str):
            return results, 200, {'Content-Type': 'text/html'}

        return jsonify(results)

    except Exception as e:
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500
