import os
import pandas as pd
import random
from datetime import datetime, timedelta

import dash
from dash import html, dcc, Input, Output, State
import dash_daq as daq
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "SO₂ Gas Monitoring Dashboard"
server = app.server

# Generate initial mock data
start_time = datetime.now() - timedelta(minutes=100)
df = pd.DataFrame({
    "Time": [start_time + timedelta(minutes=i) for i in range(100)],
    "SO2": [500 + random.randint(-50, 50) for _ in range(100)],
})

# Sensor Threshold Defaults
sensor_limits = {
    "SO2": {"lsl": 300, "usl": 800, "lcl": 400, "ucl": 700}
}

# Tab Layouts

def sensor_settings_tab():
    return dbc.Card([
        dbc.CardHeader("Sensor Settings"),
        dbc.CardBody([
            html.Label("SO₂ Thresholds"),
            dbc.Row([
                dbc.Col(daq.NumericInput(id="lsl", label="LSL", value=sensor_limits["SO2"]["lsl"])),
                dbc.Col(daq.NumericInput(id="lcl", label="LCL", value=sensor_limits["SO2"]["lcl"])),
                dbc.Col(daq.NumericInput(id="ucl", label="UCL", value=sensor_limits["SO2"]["ucl"])),
                dbc.Col(daq.NumericInput(id="usl", label="USL", value=sensor_limits["SO2"]["usl"])),
            ]),
            html.Br(),
            dbc.Button("Update Settings", id="update-settings", color="info"),
        ])
    ])

def live_chart_tab():
    return dbc.Card([
        dbc.CardHeader("Live SO₂ Chart & AI Panel"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id="live-chart")
                ], width=9),
                dbc.Col([
                    html.H5("SO₂ Level (ppm)"),
                    html.H3(id="current-so2", style={"color": "cyan"}),
                    html.H5("AI Model Prediction"),
                    html.Div(id="ai-status", style={"fontSize": 28, "color": "lime"}),
                    html.Br(),
                    daq.Indicator(id="ai-indicator", color="green", value=True),
                    html.Br(),
                    dbc.Button("Run AI Prediction", id="run-ai", color="primary", style={"display": "none"}),
                ], width=3)
            ])
        ])
    ])

def history_tab():
    return dbc.Card([
        dbc.CardHeader("Historical Trends and Report"),
        dbc.CardBody([
            dcc.Graph(id="history-chart", figure=go.Figure(
                data=[go.Scatter(x=df["Time"], y=df["SO2"], mode="lines")],
                layout=go.Layout(title="SO₂ Historical Data", paper_bgcolor="black", font={"color": "white"})
            )),
            dbc.Button("Export PDF Report", id="export-pdf", color="warning")
        ])
    ])

# App Layout
app.layout = dbc.Container([
    html.H2("SO₂ Gas Monitoring Dashboard", className="text-center my-4"),
    dcc.Tabs(id="tabs", value="settings", children=[
        dcc.Tab(label="Sensor Settings", value="settings"),
        dcc.Tab(label="Live Control Chart", value="live"),
        dcc.Tab(label="Historical Trends", value="history"),
    ], className="mb-3"),
    html.Div(id="tab-content"),
    dcc.Interval(id="interval", interval=5000, n_intervals=0)  # Every 5 seconds
], fluid=True)

# Tab Switcher
@app.callback(Output("tab-content", "children"), Input("tabs", "value"))
def switch_tabs(tab):
    if tab == "settings":
        return sensor_settings_tab()
    elif tab == "live":
        return live_chart_tab()
    elif tab == "history":
        return history_tab()

# Update Sensor Settings
@app.callback(
    Output("lsl", "value"), Output("lcl", "value"),
    Output("ucl", "value"), Output("usl", "value"),
    Input("update-settings", "n_clicks"),
    State("lsl", "value"), State("lcl", "value"),
    State("ucl", "value"), State("usl", "value")
)
def update_settings(n, lsl, lcl, ucl, usl):
    if n:
        sensor_limits["SO2"] = {"lsl": lsl, "lcl": lcl, "ucl": ucl, "usl": usl}
    return lsl, lcl, ucl, usl

# Run Mock AI Prediction
# @app.callback(
#     Output("ai-status", "children"),
#     Output("ai-indicator", "color"),
#     Output("ai-indicator", "value"),
#     Input("run-ai", "n_clicks")
# )
# def run_ai_model(n):
#     if n:
#         latest_value = df["SO2"].iloc[-1]
#         if latest_value > sensor_limits["SO2"]["usl"]:
#             return "DANGER", "red", True
#         elif latest_value > sensor_limits["SO2"]["ucl"]:
#             return "WARNING", "orange", True
#         else:
#             return "SAFE", "green", True
#     return "", "green", False
@app.callback(
    Output("ai-status", "children"),
    Output("ai-indicator", "color"),
    Output("ai-indicator", "value"),
    Input("interval", "n_intervals")
)
def run_ai_model(n):
    if not df.empty:
        latest_value = df["SO2"].iloc[-1]
        if latest_value > sensor_limits["SO2"]["usl"]:
            return "DANGER", "red", True
        elif latest_value > sensor_limits["SO2"]["ucl"]:
            return "WARNING", "orange", True
        else:
            return "SAFE", "green", True
    return "", "green", False

# Live Chart with Simulated Data
@app.callback(
    Output("live-chart", "figure"),
    Input("interval", "n_intervals")
)
def update_live_chart(n):
    global df
    # Simulate new data
    new_time = datetime.now()
    new_so2 = 500 + random.randint(-100, 150)
    new_row = pd.DataFrame({"Time": [new_time], "SO2": [new_so2]})
    df = pd.concat([df, new_row], ignore_index=True).iloc[-100:]

    limits = sensor_limits["SO2"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Time"], y=df["SO2"], mode="lines+markers", name="SO₂"))
    fig.add_hline(y=limits["usl"], line_dash="dot", line_color="red", annotation_text="USL")
    fig.add_hline(y=limits["lsl"], line_dash="dot", line_color="blue", annotation_text="LSL")
    fig.add_hline(y=limits["ucl"], line_dash="dash", line_color="orange", annotation_text="UCL")
    fig.add_hline(y=limits["lcl"], line_dash="dash", line_color="lightblue", annotation_text="LCL")
    fig.update_layout(title="Live SO₂ Chart", paper_bgcolor="black", font={"color": "white"}, template="plotly_dark")
    return fig

@app.callback(
    Output("current-so2", "children"),
    Input("interval", "n_intervals")
)
def update_current_so2(n):
    if not df.empty:
        latest = df["SO2"].iloc[-1]
        return f"{latest:.1f} ppm"
    return "N/A"

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
