from dash import Dash, callback, Input, Output, State
import dash_bootstrap_components as dbc
from .layout import create_layout
from .callbacks import register_callbacks
import os
import json
import pandas as pd
import plotly.express as px

def create_app(report_data=None):
    """Create and configure the Dash application."""
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.DARKLY],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
    
    app.title = "Sports Betting AI Dashboard"
    app.layout = create_layout(report_data)
    
    # Register callbacks
    register_callbacks(app)
    
    # Store report data in app config
    app.report_data = report_data
    
    return app

def run_dashboard(report_data=None):
    """Run the dashboard application."""
    app = create_app(report_data)
    app.run_server(host='0.0.0.0', port=8050, debug=False)
