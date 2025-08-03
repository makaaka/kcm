# so2_dashboard.py (styled with custom CSS)

import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import datetime

# Generate dummy data (replace with real-time data as needed)
def generate_dummy_data():
    np.random.seed(42)
    now = datetime.datetime.now()
    timestamps = [now - datetime.timedelta(minutes=10 * i) for i in range(144)]
    timestamps.reverse()
    return pd.DataFrame({
        'timestamp': timestamps,
        'SO2_ppm': np.clip(np.random.normal(loc=2, scale=0.5, size=144), 0, 20),
        'zone': np.random.choice(['Zone A', 'Zone B', 'Zone C'], size=144)
    })

# Dash app with custom CSS (base-styles.css & spc-custom-styles.css in assets/)
app = dash.Dash(__name__, assets_folder='assets')
app.title = "SO₂ Monitoring Dashboard"

# Dummy dataset
df = generate_dummy_data()

# Layout
app.layout = html.Div(id="big-app-container", children=[
    html.Div(className="banner", children=[
        html.H5("SO₂ Monitoring Dashboard"),
        html.Div(id='current-time')
    ]),

    html.Div(id="app-container", children=[
        html.Div(id="top-section-container", children=[

            html.Div(id="card-1", children=[
                html.H4("Latest SO₂ Reading"),
                html.P(id='latest-so2', className="metric-value"),
                html.P("ppm")
            ]),

            html.Div(id="card-2", children=[
                html.H4("Zone with Highest Average"),
                html.P(id='worst-zone', className="metric-value"),
                html.P("(Last 24 hours)")
            ]),

            html.Div(id="utility-card", children=[
                html.H4("AI-Based Status"),
                html.P(id='ai-status', className="metric-value"),
                html.P("Risk Level")
            ])
        ]),

        html.Div(id="status-container", children=[
            html.Div(id="graphs-container", children=[
                dcc.Graph(id='so2-timeseries'),
                dcc.Graph(id='so2-by-zone')
            ])
        ]),

        html.Div(id="ai-explanation", children=[
            html.H5("AI Inference Explanation"),
            html.P("Our AI model classifies SO₂ exposure into risk levels based on statistical patterns, trends, and threshold exceedances.",
                   className="text-muted")
        ])
    ])
])

# Callbacks
@app.callback(
    Output('latest-so2', 'children'),
    Output('worst-zone', 'children'),
    Output('so2-timeseries', 'figure'),
    Output('so2-by-zone', 'figure'),
    Output('ai-status', 'children'),
    Output('current-time', 'children'),
    Input('so2-timeseries', 'id')
)
def update_dashboard(_):
    latest_reading = df.iloc[-1]['SO2_ppm']
    latest_str = f"{latest_reading:.2f}"

    recent_df = df[df['timestamp'] > df['timestamp'].max() - pd.Timedelta("1 day")]
    zone_avg = recent_df.groupby('zone')['SO2_ppm'].mean()
    worst_zone = zone_avg.idxmax()

    fig_ts = px.line(df, x='timestamp', y='SO2_ppm', color='zone',
                     title="SO₂ Levels Over Time",
                     labels={'SO2_ppm': 'SO₂ (ppm)', 'timestamp': 'Time'})
    fig_ts.update_layout(paper_bgcolor="#161a28", plot_bgcolor="#161a28", font_color="white")

    zone_bar = px.bar(zone_avg.reset_index(), x='zone', y='SO2_ppm',
                      title="Average SO₂ by Zone (Last 24h)",
                      labels={'SO2_ppm': 'SO₂ (ppm)', 'zone': 'Zone'},
                      color='zone')
    zone_bar.update_layout(paper_bgcolor="#161a28", plot_bgcolor="#161a28", font_color="white")

    if latest_reading < 5:
        status = "Safe"
    elif latest_reading < 10:
        status = "Warning"
    else:
        status = "Danger"

    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return latest_str, worst_zone, fig_ts, zone_bar, status, now_str

if __name__ == '__main__':
    app.run_server(debug=True)
