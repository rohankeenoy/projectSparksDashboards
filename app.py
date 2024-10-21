from dash import Dash, dcc, html, Input, Output, callback
from pages import masks, training_data,home
import base64

app = Dash(__name__, suppress_callback_exceptions=True)

def load_svg(path):
    
    with open(path, 'rb') as f:
        return f.read()  

def create_navbar():
    cloud_svg = load_svg('assets/cloud.svg')
    header = html.Div(
        [
            html.Div([
                html.Img(
                    src='data:image/svg+xml;base64,{}'.format(base64.b64encode(cloud_svg).decode()),
                    style={'height': '80px', 'paddingLeft': '10px', 'paddingRight': '10px'}
                ),
                html.H1('Project Sparks Dashboard', style={'margin': '0', 'padding': '20px','color': '#008f70'}),
            ], style={'display': 'flex'}),
             html.Div(
            html.H1("GAIA LAB",style={
        'textAlign': 'center',
        'margin': '0',
        'color': '#008f70',
        'border': '2px solid #008f70',  
        'padding': '10px',  
        'borderRadius': '5px',  
        'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)' } ),
            style={'flex': '1', 'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}
        ),
            html.Div([
                html.Div([
                    dcc.Link(html.Button('Home', className='navbar-button'), href='/'),
                    dcc.Link(html.Button('Final Training Dataset', className='navbar-button'), href='/trainingData'),
                    dcc.Link(html.Button('Masks', className='navbar-button'), href='/masks'),
                    dcc.Link(html.Button('Feature Evaluation',className='navbar-button'), href='/feature-evaluation'),
                    dcc.Link(html.Button('Model Evaluation', className='navbar-button'), href='/model-evaluation'),
                ], style={'display': 'flex', 'justifyContent': 'flex-end'})
            ], style={})
        ],
        style={
            'justifyContent': 'space-between',
            'position': 'fixed',
            'top': '0',
            'left': '0',
            'width': '100%',
            'backgroundColor': '#f8f9fa',
            'boxShadow': '0 2px 4px rgba(0, 0, 0, 0.1)',
            'zIndex': '1000',
            'display': 'flex',
            'alignItems': 'center',
            'padding': '10px'  
        }
    )
    return header

app.layout = html.Div([
    create_navbar(), 
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', style={'margin-top': '100px'})  
])

@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/trainingData':
        return training_data.layout
    elif pathname == '/masks':
        return masks.layout
    elif pathname == '/':
        return home.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run(debug=True)
