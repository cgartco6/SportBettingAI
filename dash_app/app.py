from dash import Dash
import dash_bootstrap_components as dbc
from .layout import create_layout
from .callbacks import register_callbacks

def create_app():
    """Create and configure the Dash application."""
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.DARKLY],
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
    
    app.title = "Sports Betting AI Dashboard"
    app.layout = create_layout()
    
    # Register callbacks
    register_callbacks(app)
    
    return app

def run_dashboard(report_data=None):
    """Run the dashboard application."""
    app = create_app()
    # If report_data is provided, we can store it in the app's config for callbacks to access
    if report_data is not None:
        app.config['report_data'] = report_data
    app.run_server(host='0.0.0.0', port=8050, debug=False)
