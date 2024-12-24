import folium
from typing import List, Dict, Any, Tuple, Optional
import branca.colormap as cm
from folium import plugins


def get_region_coordinates(region: str) -> Optional[Tuple[float, float]]:
    coordinates = {
        'South Asia': (34.516895, 69.147011),
        'Middle East & North Africa': (41.106178, 28.689863),
        'Sub-Saharan Africa': (9.145, 40.489673),
        'Eastern Europe': (52.50153, 13.401851),
        'Southeast Asia': (14.67428, 121.057495),
        'Western Europe': (48.8566, 2.3522),
        'North America': (39.8283, -98.5795),
        'Central America & Caribbean': (23.6345, -102.5528),
        'South America': (-15.7801, -47.9292),
        'Australasia & Oceania': (-35.2809, 149.1300),
        'Central Asia': (41.2995, 69.2401)
    }

    return coordinates.get(region)


# 2
def create_base_map(
        center: Tuple[float, float] = (31.5, 34.8),
        zoom: int = 4,
        tile_layer: str = 'OpenStreetMap'
) -> folium.Map:
    """
    Creates a base map with default settings

    Args:
        center: Tuple of (latitude, longitude) for map center
        zoom: Initial zoom level
        tile_layer: Name of the tile layer to use

    Returns:
        folium.Map: Base map instance
    """
    return folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=tile_layer,
        attr='© OpenStreetMap contributors'
    )


def create_color_scale(
        data: List[Dict[str, Any]],
        value_key: str,
        colors: List[str] = ['yellow', 'orange', 'red'],
        caption: str = ''
) -> cm.LinearColormap:
    """
    Creates a color scale based on data values

    Args:
        data: List of data points
        value_key: Dictionary key to use for values
        colors: List of colors for the scale
        caption: Legend caption

    Returns:
        branca.colormap.LinearColormap: Color scale
    """
    valid_values = [item[value_key] for item in data
                    if item.get('latitude') != 0 or item.get('longitude') != 0]

    if not valid_values:
        raise ValueError("No valid values found for color scale")

    return cm.LinearColormap(
        colors=colors,
        vmin=min(valid_values),
        vmax=max(valid_values),
        caption=caption
    )


def create_circle_marker(
        location: Dict[str, Any],
        colormap: cm.LinearColormap,
        value_key: str,
        min_value: float,
        max_value: float,
        popup_content: str,
        min_radius: int = 8,
        max_radius: int = 20
) -> folium.CircleMarker:
    """
    Creates a circle marker with dynamic size and color

    Args:
        location: Dictionary containing location data
        colormap: Color scale to use
        value_key: Key for the value determining color/size
        min_value: Minimum value for normalization
        max_value: Maximum value for normalization
        popup_content: HTML content for popup
        min_radius: Minimum circle radius
        max_radius: Maximum circle radius

    Returns:
        folium.CircleMarker: Configured circle marker
    """
    value = location[value_key]
    value_ratio = (value - min_value) / (max_value - min_value)
    radius = min_radius + (value_ratio * (max_radius - min_radius))

    return folium.CircleMarker(
        location=[location['latitude'], location['longitude']],
        radius=radius,
        popup=popup_content,
        color=colormap(value),
        fill=True,
        fill_color=colormap(value),
        fill_opacity=0.7
    )


def create_popup_content(data: Dict[str, Any], title_key: str, fields: List[Tuple[str, str, Optional[str]]]) -> str:
    """
    Creates formatted popup HTML content

    Args:
        data: Dictionary containing the data
        title_key: Key for the popup title
        fields: List of tuples (label, key, format_string)

    Returns:
        str: Formatted HTML content
    """
    rows = ""
    for label, key, format_str in fields:
        value = data[key]
        if format_str:
            value = format_str.format(value)
        rows += f"""
            <tr>
                <td><b>{label}:</b></td>
                <td style='text-align: right;'>{value}</td>
            </tr>
        """

    return f"""
        <div style='font-family: Arial; min-width: 180px;'>
            <h4 style='margin: 0 0 10px 0;'>{data[title_key]}</h4>
            <table style='width: 100%; border-spacing: 5px;'>
                {rows}
            </table>
        </div>
    """


def create_basic_casualties_map(data: List[Dict[str, Any]]) -> str:

    # Create base map
    m = create_base_map()

    # Create color scale
    colormap = create_color_scale(
        data=data,
        value_key='total_events',
        caption='Number of Events'
    )
    colormap.add_to(m)

    # Calculate min/max for normalization
    valid_events = [loc['total_events'] for loc in data
                    if loc['latitude'] != 0 or loc['longitude'] != 0]
    if not valid_events:
        return m._repr_html_()

    min_events = min(valid_events)
    max_events = max(valid_events)

    # Add markers
    for location in data:
        if location['latitude'] == 0 and location['longitude'] == 0:
            continue

        popup_content = create_popup_content(
            data=location,
            title_key='region',
            fields=[
                ('Total Events', 'total_events', '{:,}'),
                ('Avg. Killed', 'avg_killed', '{:.2f}'),
                ('Avg. Wounded', 'avg_wounded', '{:.2f}')
            ]
        )

        marker = create_circle_marker(
            location=location,
            colormap=colormap,
            value_key='total_events',
            min_value=min_events,
            max_value=max_events,
            popup_content=popup_content
        )
        marker.add_to(m)

    return m._repr_html_()


# 6
def create_popup_content_for_changes(location: Dict[str, Any]) -> str:
    """
    Creates formatted popup HTML content specifically for attack changes visualization

    Args:
        location: Dictionary containing the region data and changes

    Returns:
        str: Formatted HTML content
    """
    return f"""
        <div style='font-family: Arial; min-width: 180px;'>
            <h4 style='margin: 0 0 10px 0;'>{location['region']}</h4>
            <table style='width: 100%; border-spacing: 5px;'>
                <tr>
                    <td><b>Latest Change ({location['latest_years']}):</b></td>
                    <td style='text-align: right;'>{location['latest_change']:+.2f}%</td>
                </tr>
                <tr>
                    <td><b>Average Change:</b></td>
                    <td style='text-align: right;'>{location['avg_change']:+.2f}%</td>
                </tr>
                <tr>
                    <td><b>Years Count:</b></td>
                    <td style='text-align: right;'>{len(location['yearly_changes'])}</td>
                </tr>
            </table>
        </div>
    """


def create_attack_change_map(data: List[Dict[str, Any]]) -> str:

    # Create base map
    m = folium.Map(location=[31.5, 34.8], zoom_start=4,
                   tiles='OpenStreetMap', attr='© OpenStreetMap contributors')

    # Process data for visualization
    for region_data in data:
        region = region_data['region']
        changes = region_data['yearly_changes']

        if not changes:  # Skip if no changes data
            continue

        # Get latest change value
        latest_change = changes[-1]['percent_change']
        year_range = f"{changes[-1]['previous_year']}-{changes[-1]['year']}"

        # Calculate average change
        avg_change = sum(change['percent_change'] for change in changes) / len(changes)

        # Get coordinates for the region
        coordinates = get_region_coordinates(region)
        if not coordinates:
            continue

        # Determine color based on latest change
        color = 'red' if latest_change < 0 else 'blue'

        # Create popup content
        popup_html = f"""
            <div style='font-family: Arial; min-width: 180px;'>
                <h4 style='margin: 0 0 10px 0;'>{region}</h4>
                <table style='width: 100%; border-spacing: 5px;'>
                    <tr>
                        <td><b>Latest Change ({year_range}):</b></td>
                        <td style='text-align: right;'>{latest_change:+.2f}%</td>
                    </tr>
                    <tr>
                        <td><b>Average Change:</b></td>
                        <td style='text-align: right;'>{avg_change:+.2f}%</td>
                    </tr>
                    <tr>
                        <td><b>Years Analyzed:</b></td>
                        <td style='text-align: right;'>{len(changes)}</td>
                    </tr>
                </table>
            </div>
        """

        # Add circle marker
        folium.CircleMarker(
            location=coordinates,
            radius=10,
            popup=popup_html,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=2
        ).add_to(m)

    # Add a simple legend
    legend_html = """
        <div style='position: fixed; 
                    bottom: 50px; right: 50px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color: white;
                    padding: 10px;'>
            <p style='margin: 0 0 5px 0;'><b>Change in Attacks:</b></p>
            <p style='margin: 0;'>
                <span style='color: blue;'>■</span> Increase<br>
                <span style='color: red;'>■</span> Decrease
            </p>
        </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m._repr_html_()


def create_attack_change_map_detailed(data: List[Dict[str, Any]]) -> str:

    # Create base map
    m = folium.Map(location=[31.5, 34.8], zoom_start=4,
                   tiles='OpenStreetMap', attr='© OpenStreetMap contributors')

    # Process data for visualization
    for region_data in data:
        region = region_data['region']
        changes = region_data['yearly_changes']

        if not changes:  # Skip if no changes data
            continue

        # Get latest change value for marker color
        latest_change = changes[-1]['percent_change']

        # Calculate average change
        avg_change = sum(change['percent_change'] for change in changes) / len(changes)

        # Get coordinates for the region
        coordinates = get_region_coordinates(region)
        if not coordinates:
            continue

        # Determine color based on latest change
        color = 'red' if latest_change < 0 else 'blue'

        # Create popup content with all historical changes
        changes_rows = ""
        # Sort changes by year in descending order
        for change in sorted(changes, key=lambda x: x['year'], reverse=True):
            changes_rows += f"""
                <tr>
                    <td>{change['previous_year']} → {change['year']}:</td>
                    <td style='text-align: right;'>{change['percent_change']:+.2f}%</td>
                </tr>
            """

        popup_html = f"""
            <div style='font-family: Arial; min-width: 200px; max-height: 300px; overflow-y: auto;'>
                <h4 style='margin: 0 0 10px 0;'>{region}</h4>
                <table style='width: 100%; border-spacing: 5px;'>
                    <tr>
                        <td><b>Average Change:</b></td>
                        <td style='text-align: right;'>{avg_change:+.2f}%</td>
                    </tr>
                    <tr>
                        <td><b>Years Analyzed:</b></td>
                        <td style='text-align: right;'>{len(changes)}</td>
                    </tr>
                </table>
                <hr style='margin: 10px 0;'>
                <p style='margin: 5px 0;'><b>Historical Changes:</b></p>
                <table style='width: 100%; border-spacing: 5px;'>
                    {changes_rows}
                </table>
            </div>
        """

        # Add circle marker
        folium.CircleMarker(
            location=coordinates,
            radius=10,
            popup=popup_html,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=2
        ).add_to(m)

    # Add a simple legend
    legend_html = """
        <div style='position: fixed; 
                    bottom: 50px; right: 50px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color: white;
                    padding: 10px;'>
            <p style='margin: 0 0 5px 0;'><b>Change in Attacks:</b></p>
            <p style='margin: 0;'>
                <span style='color: blue;'>■</span> Increase<br>
                <span style='color: red;'>■</span> Decrease
            </p>
        </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    return m._repr_html_()


# 7
def create_terror_heatmap_90(data: List[Dict[str, Any]]) -> str:

    # יצירת מפת בסיס
    m = folium.Map(location=[31.5, 34.8], zoom_start=4,
                   tiles='OpenStreetMap', attr='© OpenStreetMap contributors')

    # הכנת נתונים למפת חום - חשוב להמיר למספרים
    heat_data = []
    for event in data:
        try:
            lat = float(event['latitude'])
            lon = float(event['longitude'])
            weight = float(event['events_count'])
            if lat and lon:
                heat_data.append([lat, lon, weight])
        except (TypeError, ValueError) as e:
            print(f"Error processing data point: {e}")
            continue

    if heat_data:  # בדיקה שיש נתונים להצגה
        # הוספת שכבת מפת החום
        plugins.HeatMap(
            heat_data,
            min_opacity=0.3,
            max_opacity=0.8,
            radius=15,
            blur=10,
            gradient={
                0.4: '#fee0d2',
                0.6: '#fc9272',
                0.8: '#de2d26',
                1.0: '#a50f15'
            }
        ).add_to(m)

    return m._repr_html_()


def create_terror_heatmap(data: List[Dict[str, Any]]) -> str:

    # Create base map centered on a middle point
    m = folium.Map(location=[31.5, 34.8], zoom_start=3)

    # Prepare data points for heatmap
    heat_data = []

    # Add each point to the heatmap data
    for point in data:
        lat = point['latitude']
        lon = point['longitude']
        # Use events_count as weight
        weight = point['events_count']

        # Only add valid coordinates
        if lat != 0 and lon != 0:
            heat_data.append([lat, lon, weight])

    # Create and add the heatmap layer
    plugins.HeatMap(
        heat_data,
        min_opacity=0.3,
        max_opacity=0.8,
        radius=25,
        blur=15,
        gradient={
            0.2: '#fee0d2',
            0.4: '#fc9272',
            0.6: '#de2d26',
            1.0: '#a50f15'
        }
    ).add_to(m)

    # Add a simple legend
    legend_html = '''
        <div style="position: fixed; bottom: 50px; right: 50px; 
                    z-index: 1000; background-color: white;
                    padding: 10px; border: 2px solid grey;">
            <p><strong>Terror Events Heat Map</strong></p>
            <p>Darker red indicates higher concentration of events</p>
        </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    return m._repr_html_()


#####

# 16
def create_high_group_activity_map(data: List[Dict[str, Any]]) -> str:
    m = folium.Map(location=[31.5, 34.8], zoom_start=4)

    values = [item['total_attacks'] for item in data
              if item.get('latitude') and item.get('longitude')]

    if not values:
        return m._repr_html_()

    colormap = cm.LinearColormap(
        colors=['yellow', 'orange', 'red'],
        vmin=min(values),
        vmax=max(values),
        caption='Number of Attacks'
    )
    colormap.add_to(m)

    for location in data:
        if not location['latitude'] or not location['longitude']:
            continue

        # יצירת HTML מותאם לפופאפ
        popup_html = f"""
            <div style='font-family: Arial; min-width: 180px;'>
                <h4 style='margin: 0 0 10px 0;'>{location['country']}</h4>
                <table style='width: 100%; border-spacing: 5px;'>
                    <tr>
                        <td><b>Region:</b></td>
                        <td style='text-align: right;'>{location['region']}</td>
                    </tr>
                    <tr>
                        <td><b>Total Attacks:</b></td>
                        <td style='text-align: right;'>{location['total_attacks']}</td>
                    </tr>
                    <tr>
                        <td><b>Number of Groups:</b></td>
                        <td style='text-align: right;'>{location['unique_groups_count']}</td>
                    </tr>
                </table>
                <hr style='margin: 10px 0;'>
                <p style='margin: 5px 0;'><b>Groups Details:</b></p>
                <table style='width: 100%; border-spacing: 5px;'>
        """

        for group in location['groups']:
            popup_html += f"""
                <tr>
                    <td>{group['name']}</td>
                    <td style='text-align: right;'>{group['attacks']} attacks</td>
                </tr>
            """

        popup_html += """
                </table>
            </div>
        """

        marker = create_circle_marker(
            location=location,
            colormap=colormap,
            value_key='total_attacks',
            min_value=min(values),
            max_value=max(values),
            popup_content=popup_html
        )
        marker.add_to(m)

    return m._repr_html_()
