from dash import dcc, html, Input, Output, callback

layout = html.Div([
    html.H1('Welcome to Project Sparks, a geodata colaborative project.',className = "pageHeader"),
    html.P("At any point in time, roughly 70% of the Earth is cloud covered and obscured from satellite view.  The AI Cloud Detection Project aims to advance efforts on the development of automated and accurate methods for the detection of clouds from commercial satellite imagery. Current algorithms use computer vision routines to automatically detect and label clouds from remote sensing imagery. This work will evaluate per-pixel cloud metrics to ensuring only the best available imaging data is used in subsequent geospatial processing routines."),
    html.Img(src='/assets/GAIA LAB.png', alt='GAIA LAB logo', style={'width': '500px', 'height': 'auto', 'display': 'block', 'margin': 'auto'}),
    
    html.Img(src='/assets/umsl.png', alt='UMSL logo', style={'width': '500px', 'height': 'auto', 'display': 'block', 'margin': 'auto'})
])


