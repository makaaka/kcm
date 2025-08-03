# app.py
import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import datetime
import random

# Load mock data
def generate_dummy_data():
    now = datetime.datetime.now()
    timestamps = [now - datetime.timedelta(seconds=10 * i) for i in range(60)]
    timestamps.reverse()
    return pd.DataFrame({
        'timestamp': timestamps,
        'SO2': np.random.normal(2, 0.3, 60).clip(0, 20),
        'CO2': np.random.normal(350, 20, 60),
        'CO': np.random.normal(10, 1, 60),
        'H2S': np.random.normal(5, 0.5, 60),
        'O2': np.random.normal(20, 1, 60)
    })

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Gas Monitoring Dashboard"
df = generate_dummy_data()

GASES = ['SO2', 'CO2', 'CO', 'H2S', 'O2']

# Mock AI model logic
def mock_ai_classification(row):
    risk = "Safe"
    if row['SO2'] > 5 or row['H2S'] > 8:
        risk = "Warning"
    if row['SO2'] > 10 or row['H2S'] > 15:
        risk = "Danger"
    return risk

# App Layout
app.layout = html.Div(id='big-app-container', children=[
    html.Div(className="banner", children=[
        html.H5("Gas Monitoring Dashboard"),
        html.Div(id='live-time')
    ]),

    html.Div(id='app-container', children=[
        dcc.Tabs(id='tabs', value='tab2', className='custom-tabs', children=[
            dcc.Tab(label='Sensor Settings', value='tab1', className='custom-tab', selected_className='custom-tab--selected'),
            dcc.Tab(label='Live Monitoring', value='tab2', className='custom-tab', selected_className='custom-tab--selected'),
            dcc.Tab(label='Reports', value='tab3', className='custom-tab', selected_className='custom-tab--selected'),
        ]),

        html.Div(id='tab-content')
    ]),

    dcc.Interval(id='update-interval', interval=5 * 1000, n_intervals=0),
])

@app.callback(Output('live-time', 'children'), Input('update-interval', 'n_intervals'))
def update_time(n):
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

@app.callback(Output('tab-content', 'children'), Input('tabs', 'value'))
def render_tabs(tab):
    if tab == 'tab1':
        return html.Div("Sensor Settings Coming Soon", className="section-banner")

    elif tab == 'tab2':
        latest = df.iloc[-1]
        ai_status = mock_ai_classification(latest)

        return html.Div(children=[
            html.Div(className="row", children=[
                html.Div(id="card-1", children=[
                    html.P("SO₂ Level"),
                    html.H3(f"{latest['SO2']:.2f} ppm")
                ]),
                html.Div(id="card-2", children=[
                    html.P("AI Risk Level"),
                    html.H3(ai_status)
                ]),
                html.Div(id="utility-card", children=[
                    html.Button("Export PDF Report", id="export-btn", className="button button-primary")
                ])
            ]),

            html.Div(id="graphs-container", children=[
                dcc.Graph(
                    id='live-chart',
                    figure=px.line(df, x='timestamp', y=GASES, title="Live Gas Readings")
                        .update_layout(paper_bgcolor="#161a28", plot_bgcolor="#161a28", font_color="white")
                )
            ])
        ])

    elif tab == 'tab3':
        return html.Div("Historical Analysis Coming Soon", className="section-banner")

@app.callback(Output("export-btn", "children"), Input("export-btn", "n_clicks"), prevent_initial_call=True)
def generate_pdf(n):
    return "PDF Exported ✔"

if __name__ == '__main__':
    app.run_server(debug=True)
