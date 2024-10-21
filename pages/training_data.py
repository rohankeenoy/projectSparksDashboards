from dash import dcc, html, Input, Output, callback, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import random
from PIL import Image
import os

# Load the data
df = pd.read_csv("assets/FinalHistoGramFixed.csv")

# Clean the DataFrame
df_cleaned = df.drop(columns=['Lats', 'Lons', '.geo', 'system:index', 'filename', 'geometry_type'])
columns_order = ['catalogid', 'index'] + [col for col in df_cleaned.columns if col not in ['catalogid', 'index']]
df_cleaned = df_cleaned[columns_order]

# Land class dictionary
landClassDict = {
    10: "TreeCover",
    20: "ShrubLand",
    30: "Grassland",
    40: "Cropland",
    50: "Urban",
    60: "SpareVeg",
    70: "SnowIce",
    80: "Water",
    90: "WetLands",
    95: "Mangroves",
    100: "MossLichen"
}

# Function to convert TIFF to PNG
def convert_tiff_to_png(tiff_path):
    png_path = tiff_path.replace('.tif', '.png')
    if not os.path.exists(png_path):  # Convert only if PNG doesn't exist
        with Image.open(tiff_path) as img:
            img.save(png_path)
    return png_path

# Layout of the Dash app
layout = html.Div([
    html.H1('Final Training Data Evaluation:', className="pageHeader2"),
    html.P("Static Cumulative Visualizations", className="pInstruct"),

    # Create a div for the graphs to be displayed side by side
    html.Div([
        dcc.Graph(id='cloud-coverage-histogram'),
        dcc.Graph(id='scene-type-histogram'),
        dcc.Graph(id="land-class-histogram")
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

    html.H1("Individual Evaluation:", className="pageHeader2"),
    html.P("All data selected by default, click on one or more checkboxes to look individually", className="pInstruct"),

    dash_table.DataTable(
        data=df_cleaned.to_dict('records'),
        page_size=10,
        id='data-table',
        columns=[{'name': col, 'id': col} for col in df_cleaned.columns],
        row_selectable='multi',
        selected_rows=[],
    ),
    html.Div(id='image-container', style={'margin-top': '20px'}),
    html.Div(id='map-container', style={'margin-top': '20px'}),
])

# Function to create cloud coverage histogram
def create_cloud_coverage_histogram(data):
    df = pd.DataFrame(data)
    fig = px.histogram(df, x='CloudCover', nbins=10, title='Cloud Coverage Distribution Cumulative',
                       color_discrete_sequence=["#008f70"])
    fig.update_layout(
        xaxis_title='Cloud Coverage (%)',
        yaxis_title='Frequency',
        bargap=0.1,
        template='plotly'
    )
    return fig

# Function to create histogram by land type
def create_land_type_histogram(data):
    df = pd.DataFrame(data)
    colorMap = {
        "Coastal": "blue",
        "Urban": "red",
        "Land": "green"
    }
    fig = go.Figure()
    for land_type in colorMap.keys():
        filtered_df = df[df["CostalType"] == land_type]
        fig.add_trace(go.Bar(
            x=filtered_df['index'],
            y=filtered_df['CloudCover'],
            name=land_type,
            marker_color=colorMap[land_type]
        ))
    fig.update_layout(
        title="Cloud Coverage For Scene Type (Sampled from Satellite) per Indexed Image",
        xaxis_title='Index',
        yaxis_title='Cloud Coverage (%)',
        barmode='stack',
        legend_title="Land Type",
        template='plotly'
    )
    return fig

# Function to create land class histogram
def create_land_class_histogram(data):
    df = pd.DataFrame(data)
    extractFrom = {}
    for index, row in df.iterrows():
        reqHistoOneRow = row['frequencyHistogram'].strip('{}')
        freqHistoOneRow = reqHistoOneRow.split(',')
        for item in freqHistoOneRow:
            key, value = item.split('=')
            key = int(key.strip())
            value = float(value.strip())
            if key in extractFrom:
                extractFrom[key] += value
            else:
                extractFrom[key] = value
    
    # Create a DataFrame from the extracted data
    df1 = pd.DataFrame(list(extractFrom.items()), columns=['key', 'value'])
    df1["Landclass"] = df1["key"].map(landClassDict)

    # Create the bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df1["Landclass"],
        y=df1["value"],
        marker_color="#008f70"
    ))

    fig.update_layout(
        title='Land classification for all polygons (frequency in all scenes)',
        xaxis_title='Land Class Type',
        yaxis_title='Sum of Pixels',
        xaxis_tickangle=-45,
        template='plotly'
    )
    return fig

def create_polygon_map(df):
    def extract_polygon_points(coords):
        if isinstance(coords, str):
            coords = eval(coords)
        if isinstance(coords, list) and len(coords) > 0:
            return coords[0]
        return []

    polygonPoints = df['coordinates'].apply(extract_polygon_points)
    fig = go.Figure()

    for index, polygon in polygonPoints.items():
        if polygon:
            xCoords = [point[0] for point in polygon]
            yCoords = [point[1] for point in polygon]
            hoverText = (
                f"Index: {df['index'].iloc[index]}<br>"
                f"landClass: {df['CostalType'].iloc[index]}<br>"
                f"Catalog ID: {df['catalogid'].iloc[index]}<br>"
                f"Cloud Coverage: {df['CloudCover'].iloc[index]}%<br>"
                f"Sun Azimuth: {df['SunAzimuth'].iloc[index]}<br>"
                f"Sun Elevation: {df['SunElevation'].iloc[index]}<br>"
                f"Off Nadir: {df['OffNadir'].iloc[index]}<br>"
                f"Target Azimuth: {df['TargetAzimuth'].iloc[index]}<br>"
                f"Sensor: {df['Sensor'].iloc[index]}<br>"
                f"Collecte DateTime: {df['CollecteDateTime'].iloc[index]}<br>"
            )

            fig.add_trace(go.Scattermapbox(
                mode='lines',
                lon=xCoords + [xCoords[0]],
                lat=yCoords + [yCoords[0]],
                marker=dict(size=10),
                line=dict(width=2, color='blue'),
                fill='toself',
                fillcolor='rgba(0,0,255,0.2)',
                name=str(df["index"].iloc[index]),
                hoverinfo='text',
                text=hoverText
            ))

    fig.update_layout(
        title='Polygons on Map',
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            style='carto-positron',
            bearing=0,
            center=dict(
                lat=df['coordinates'].apply(lambda x: eval(x)[0][0][1]).mean(),
                lon=df['coordinates'].apply(lambda x: eval(x)[0][0][0]).mean()
            ),
            pitch=0,
        ),
        showlegend=True
    )
    return fig

@callback(
    Output('cloud-coverage-histogram', 'figure'),
    Output('scene-type-histogram', 'figure'),
    Output('land-class-histogram', 'figure'),
    Output('image-container', 'children'),
    Output('map-container', 'children'),
    Input('data-table', 'selected_rows'),
    Input('data-table', 'data')
)
def update_histograms(selected_rows, data):
    df = pd.DataFrame(data)  # Convert the data to a DataFrame

    # If no rows are selected
    if not selected_rows:
        # Get a random image from the assets directory
        random_image = random.choice(df['catalogid'].tolist())
        random_image_src = f"assets/satImagesRunNum7PossiblyMessedUp/{random_image}.tif"  # Ensure the image has the correct extension
        #png_image_src = convert_tiff_to_png(random_image_src)  # Convert to PNG

        image_div = html.Div([
            html.Img(src=png_image_src.replace('.tif', '.png'), style={'width': '300px', 'height': 'auto', 'margin': '10px'})
        ])

        # Show all locations on the map
        map_figure = create_polygon_map(df)

        # Return default figures and random image
        return (
            create_cloud_coverage_histogram(data),
            create_land_type_histogram(data),
            create_land_class_histogram(data),
            image_div,
            dcc.Graph(figure=map_figure)  # Wrap the figure in a Graph component
        )

    # If rows are selected
    selected_data = df.iloc[selected_rows]

    # Display images based on selected rows
    images = []
    for _, row in selected_data.iterrows():
        image_src = f"assets/satImagesRunNum7PossiblyMessedUp/{row['catalogid']}.tif"  # Ensure the image has the correct extension
        png_image_src = convert_tiff_to_png(image_src)  # Convert to PNG
        images.append(html.Img(src=png_image_src.replace('.tif', '.png'), style={'width': '300px', 'height': 'auto', 'margin': '10px'}))
        print(f"Selected image source path: {png_image_src}") 
    image_div = html.Div(images)

    # Create map with polygons for selected rows
    map_figure = create_polygon_map(selected_data)

    # Return updated figures and new content
    cloud_coverage_fig = create_cloud_coverage_histogram(selected_data)
    land_type_fig = create_land_type_histogram(selected_data)
    land_class_fig = create_land_class_histogram(selected_data)

    return (
        cloud_coverage_fig,
        land_type_fig,
        land_class_fig,
        image_div,
        dcc.Graph(figure=map_figure)  # Wrap the figure in a Graph component
    )

# Render default figures on page load
cloud_coverage_fig = create_cloud_coverage_histogram(df_cleaned)
scene_type_fig = create_land_type_histogram(df_cleaned)
land_class_fig = create_land_class_histogram(df)
