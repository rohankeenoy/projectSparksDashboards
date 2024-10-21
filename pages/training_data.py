from dash import dcc, html, Input, Output, callback, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

# Load the data
df = pd.read_csv("assets/FinalHistoGramFixed.csv")

# Clean the DataFrame
df_cleaned = df.drop(columns=['Lats', 'Lons', 'coordinates', '.geo', 'system:index', 'filename', 'frequencyHistogram', 'geometry_type'])
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
    
    # Set the color using color_discrete_sequence
    fig = px.histogram(df, x='CloudCover', nbins=10, title='Cloud Coverage Distribution Cumulative', 
                       color_discrete_sequence=["#008f70"])  # Add marker color here
    
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
        title="Cloud Coverage For Scene Type (Sampled from Sattelite) per Indexed Image",
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



def update_histograms(data):
    cloud_coverage_fig = create_cloud_coverage_histogram(data)
    land_type_fig = create_land_type_histogram(data)
    land_class_fig = create_land_class_histogram(df)
    return cloud_coverage_fig, land_type_fig, land_class_fig

# Render default figures on page load
cloud_coverage_fig = create_cloud_coverage_histogram(df_cleaned)  
scene_type_fig = create_land_type_histogram(df_cleaned)
land_class_fig = create_land_class_histogram(df)
