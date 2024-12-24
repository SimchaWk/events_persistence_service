from typing import List, Dict, Any
import folium
import branca.colormap as cm

from app.repositories.graph_repository.memgraph_repository import get_regions_high_group_activity, \
    get_shared_attack_types, get_groups_shared_targets
from app.services.map_service import create_circle_marker


# 16
def get_regions_high_group_activity_data(filter_by: str = None, filter_value: str = None) -> List:
    return get_regions_high_group_activity(filter_by, filter_value)


def create_high_group_activity_map_old(data: List) -> str:
    m = folium.Map(location=[0, 0], zoom_start=2)

    for record in data:
        if record['latitude'] and record['longitude']:
            popup_content = f"""
                <b>Country:</b> {record['country']}<br>
                <b>Region:</b> {record['region']}<br>
                <b>Number of Groups:</b> {record['unique_groups_count']}<br>
                <b>Groups:</b><br>
                {'<br>'.join([g['name'] for g in record['groups']])}
            """

            radius = min(record['unique_groups_count'] * 5, 30)

            folium.CircleMarker(
                location=[record['latitude'], record['longitude']],
                radius=radius,
                popup=folium.Popup(popup_content, max_width=300),
                color='red',
                fill=True,
                fill_opacity=0.7
            ).add_to(m)

    map_file = "high_group_activity_map.html"
    m.save(map_file)
    return map_file


# 14
def get_attack_strategies_data(filter_by: str = None, filter_value: str = None) -> list:
    return get_shared_attack_types(filter_by, filter_value)


def create_attack_strategies_map(data: List[Dict[str, Any]]) -> str:
    m = folium.Map(location=[31.5, 34.8], zoom_start=4)

    values = [item['unique_attack_types_count'] for item in data
              if item.get('latitude') and item.get('longitude')]

    if not values:
        return m._repr_html_()

    colormap = cm.LinearColormap(
        colors=['yellow', 'orange', 'red'],
        vmin=min(values),
        vmax=max(values),
        caption='Number of Attack Types'
    )
    colormap.add_to(m)

    for location in data:
        if not location['latitude'] or not location['longitude']:
            continue

        popup_html = f"""
            <div style='font-family: Arial; min-width: 200px;'>
                <h4 style='margin: 0 0 10px 0;'>{location['country']}</h4>
                <table style='width: 100%; border-spacing: 5px;'>
                    <tr>
                        <td><b>Region:</b></td>
                        <td style='text-align: right;'>{location['region']}</td>
                    </tr>
                    <tr>
                        <td><b>Attack Types:</b></td>
                        <td style='text-align: right;'>{location['unique_attack_types_count']}</td>
                    </tr>
                </table>
                <hr style='margin: 10px 0;'>
                <p style='margin: 5px 0;'><b>Attack Strategies:</b></p>
                <table style='width: 100%; border-spacing: 5px;'>
        """

        for strategy in location['attack_strategies']:
            popup_html += f"""
                <tr>
                    <td colspan='2'><b>{strategy['attack_type']}</b></td>
                </tr>
                <tr>
                    <td>Groups ({strategy['groups_count']}):</td>
                    <td style='text-align: right;'>{', '.join(strategy['groups'])}</td>
                </tr>
            """

        popup_html += """
                </table>
            </div>
        """

        marker = create_circle_marker(
            location=location,
            colormap=colormap,
            value_key='unique_attack_types_count',
            min_value=min(values),
            max_value=max(values),
            popup_content=popup_html
        )
        marker.add_to(m)

    return m._repr_html_()


# 11
def get_shared_targets_data(filter_by: str = None, filter_value: str = None) -> list:
    return get_groups_shared_targets(filter_by, filter_value)


def create_shared_targets_map(data: List[Dict[str, Any]]) -> str:
    m = folium.Map(location=[31.5, 34.8], zoom_start=4)

    values = [item['max_shared_groups'] for item in data
              if item.get('latitude') and item.get('longitude')]

    if not values:
        return m._repr_html_()

    colormap = cm.LinearColormap(
        colors=['yellow', 'orange', 'red'],
        vmin=min(values),
        vmax=max(values),
        caption='Number of Groups Sharing Targets'
    )
    colormap.add_to(m)

    for location in data:
        if not location['latitude'] or not location['longitude']:
            continue

        popup_html = f"""
            <div style='font-family: Arial; min-width: 200px;'>
                <h4 style='margin: 0 0 10px 0;'>{location['country']}</h4>
                <table style='width: 100%; border-spacing: 5px;'>
                    <tr>
                        <td><b>Region:</b></td>
                        <td style='text-align: right;'>{location['region']}</td>
                    </tr>
                    <tr>
                        <td><b>Max Groups Sharing Targets:</b></td>
                        <td style='text-align: right;'>{location['max_shared_groups']}</td>
                    </tr>
                </table>
                <hr style='margin: 10px 0;'>
                <p style='margin: 5px 0;'><b>Target Groups:</b></p>
                <table style='width: 100%; border-spacing: 5px;'>
        """

        for target in location['shared_targets']:
            attack_types = [item for sublist in target['target_types'] for item in sublist]
            attack_types = list(set(attack_types))

            popup_html += f"""
                <tr>
                    <td colspan='2'><b>Attack Types:</b></td>
                </tr>
                <tr>
                    <td colspan='2'>{', '.join(attack_types)}</td>
                </tr>
                <tr>
                    <td>Groups ({target['groups_count']}):</td>
                    <td style='text-align: right;'>{', '.join(target['groups'])}</td>
                </tr>
                <tr><td colspan='2'><hr></td></tr>
            """

        popup_html += """
                </table>
            </div>
        """

        folium.CircleMarker(
            location=[location['latitude'], location['longitude']],
            radius=10,
            popup=folium.Popup(popup_html, max_width=300),
            color=colormap(location['max_shared_groups']),
            fill=True,
            fill_color=colormap(location['max_shared_groups']),
            fill_opacity=0.7
        ).add_to(m)

    return m._repr_html_()
