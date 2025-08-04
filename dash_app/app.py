from dash import Dash
from .layout import create_layout
from .callbacks import register_callbacks
import plotly.io as pio

# Custom color scheme
pio.templates["sports"] = pio.templates["plotly_dark"]
pio.templates["sports"].layout.colorway = ["#2EFE2E", "#FE2E2E", "#2ECCFA", "#F7FE2E"]

def run_dashboard(report_data):
    app = Dash(__name__)
    app.title = "Sports Betting AI Dashboard"
    
    app.layout = create_layout(report_data)
    register_callbacks(app, report_data)
    
    app.run_server(host='0.0.0.0', port=8050, debug=False)
