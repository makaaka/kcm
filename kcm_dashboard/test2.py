import os
import pandas as pd
import dash
from dash import html, dcc, Input, Output, State, callback_context
import dash_daq as daq
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from xhtml2pdf import pisa
from io import BytesIO
import base64
from flask import send_file
import tempfile

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "SO₂ Gas Monitoring Dashboard"
server = app.server

# Mock Data Initialization
df = pd.DataFrame({
    "Time": pd.date_range(start="2025-01-01", periods=100, freq="T"),
    "SO2": [500 + i % 100 for i in range(100)],
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
                    html.H5("AI Model Prediction"),
                    html.Div(id="ai-status", style={"fontSize": 28, "color": "lime"}),
                    html.Br(),
                    daq.Indicator(id="ai-indicator", color="green", value=True),
                    html.Br(),
                    dbc.Button("Run AI Prediction", id="run-ai", color="primary"),
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
            dbc.Button("Export PDF Report", id="export-pdf", color="warning"),
            dcc.Download(id="download-pdf")
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
    html.Div(id="tab-content")
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
@app.callback(
    Output("ai-status", "children"),
    Output("ai-indicator", "color"),
    Output("ai-indicator", "value"),
    Input("run-ai", "n_clicks")
)
def run_ai_model(n):
    if n:
        latest_value = df["SO2"].iloc[-1]
        if latest_value > sensor_limits["SO2"]["usl"]:
            return "DANGER", "red", True
        elif latest_value > sensor_limits["SO2"]["ucl"]:
            return "WARNING", "orange", True
        else:
            return "SAFE", "green", True
    return "", "green", False

# Live Chart
@app.callback(
    Output("live-chart", "figure"), Input("run-ai", "n_clicks")
)
def update_live_chart(n):
    limits = sensor_limits["SO2"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Time"], y=df["SO2"], mode="lines+markers", name="SO₂"))
    fig.add_hline(y=limits["usl"], line_dash="dot", line_color="red", annotation_text="USL")
    fig.add_hline(y=limits["lsl"], line_dash="dot", line_color="blue", annotation_text="LSL")
    fig.add_hline(y=limits["ucl"], line_dash="dash", line_color="orange", annotation_text="UCL")
    fig.add_hline(y=limits["lcl"], line_dash="dash", line_color="lightblue", annotation_text="LCL")
    fig.update_layout(title="Live SO₂ Chart", paper_bgcolor="black", font={"color": "white"})
    return fig

# Export PDF Report
@app.callback(
    Output("download-pdf", "data"),
    Input("export-pdf", "n_clicks"),
    prevent_initial_call=True
)
def export_pdf(n):
    if n:
        summary = df["SO2"].describe().to_frame()
        alerts = len(df[df["SO2"] > sensor_limits["SO2"]["usl"]])

        html_string = f"""
        <html>
        <body>
        <h1>SO₂ Monitoring Report</h1>
        <h3>Sensor Thresholds</h3>
        <ul>
        <li>LSL: {sensor_limits['SO2']['lsl']}</li>
        <li>LCL: {sensor_limits['SO2']['lcl']}</li>
        <li>UCL: {sensor_limits['SO2']['ucl']}</li>
        <li>USL: {sensor_limits['SO2']['usl']}</li>
        </ul>
        <h3>Summary Statistics</h3>
        <p>Mean: {summary.loc['mean', 'SO2']:.2f}</p>
        <p>Min: {summary.loc['min', 'SO2']:.2f}</p>
        <p>Max: {summary.loc['max', 'SO2']:.2f}</p>
        <p>Readings above USL: {alerts}</p>
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pisa.CreatePDF(html_string, dest=tmp_pdf)
            tmp_pdf.close()
            return dcc.send_file(tmp_pdf.name)

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
