import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

def create_layout():
    """Create the layout for the Dash application."""
    return dbc.Container(
        fluid=True,
        children=[
            # Header
            dbc.Row(
                dbc.Col(
                    html.H1("AI Sports Betting Dashboard", className="text-center my-4"),
                    width=12
                )
            ),
            
            # Performance Metrics Cards
            dbc.Row(
                id="performance-cards",
                className="mb-4"
            ),
            
            # Value Bets Table
            dbc.Row(
                dbc.Col(
                    id="value-bets-table",
                    width=12
                )
            ),
            
            # Performance Graph
            dbc.Row(
                dbc.Col(
                    dcc.Graph(id='performance-graph'),
                    width=12
                )
            ),
            
            # Interval component for live updates
            dcc.Interval(
                id='interval-component',
                interval=15*60*1000,  # 15 minutes
                n_intervals=0
            ),
            
            # Store for report data
            dcc.Store(id='report-data-store')
        ]
    )
