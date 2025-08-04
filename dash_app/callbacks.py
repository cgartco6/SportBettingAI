from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

def register_callbacks(app):
    """Register all callbacks for the Dash application."""
    
    @app.callback(
        Output('report-data-store', 'data'),
        [Input('interval-component', 'n_intervals')]
    )
    def load_report_data(n_intervals):
        """Load the report data from the app's config or from a file."""
        # In a real app, we might fetch from an API or database
        # For now, we'll use the data passed when starting the app
        if hasattr(app, 'config') and 'report_data' in app.config:
            return app.config['report_data']
        # Otherwise, try to load from file (for demonstration)
        try:
            return pd.read_json("sports_betting_report.json").to_dict()
        except:
            return None
    
    @app.callback(
        [Output('performance-cards', 'children'),
         Output('value-bets-table', 'children'),
         Output('performance-graph', 'figure')],
        [Input('report-data-store', 'data')]
    )
    def update_layout(report_data):
        """Update the layout components with the latest report data."""
        if report_data is None:
            return dbc.Alert("No report data available", color="danger"), [], go.Figure()
        
        # Create performance cards
        win_rate = report_data.get('performance', {}).get('win_rate', 0)
        roi = report_data.get('performance', {}).get('roi', 0)
        win_color = "#2EFE2E" if win_rate > 0.55 else "#F7FE2E" if win_rate > 0.5 else "#FE2E2E"
        roi_color = "#2EFE2E" if roi > 0 else "#FE2E2E"
        
        cards = dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Win Rate"),
                    dbc.CardBody(
                        html.H2(f"{win_rate:.2%}", style={"color": win_color}, className="card-title")
                    )
                ]),
                width=4
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("ROI"),
                    dbc.CardBody(
                        html.H2(f"{roi:.2%}", style={"color": roi_color}, className="card-title")
                    )
                ]),
                width=4
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Active Agents"),
                    dbc.CardBody(
                        html.H2("12", style={"color": "#2ECCFA"}, className="card-title")
                    )
                ]),
                width=4
            )
        ])
        
        # Create value bets table
        value_bets = report_data.get('value_bets', [])
        if value_bets:
            table = dbc.Table(
                # Header
                header=[
                    html.Thead(html.Tr([
                        html.Th("Match"), 
                        html.Th("Bet Type"), 
                        html.Th("Odds"), 
                        html.Th("Confidence"), 
                        html.Th("Value Score")
                    ]))
                ],
                # Body
                children=[
                    html.Tbody([
                        html.Tr([
                            html.Td(f"{bet['home_team']} vs {bet['away_team']}"),
                            html.Td(bet['bet_type'], style={"color": "#2EFE2E" if bet['bet_type'] == "UNDERVALUE" else "#FE2E2E"}),
                            html.Td(f"{bet['bookmaker_odds']:.2f}"),
                            html.Td(f"{bet['confidence']:.0%}", style={"color": "#2EFE2E" if bet['confidence'] > 0.7 else "#F7FE2E" if bet['confidence'] > 0.6 else "#FE2E2E"}),
                            html.Td(f"{bet['value_score']:.3f}", style={"color": "#2EFE2E" if bet['value_score'] > 0 else "#FE2E2E"})
                        ]) for bet in value_bets
                    ])
                ],
                bordered=True,
                hover=True,
                responsive=True
            )
        else:
            table = dbc.Alert("No value bets identified", color="warning")
        
        # Create performance graph
        # For demo, we'll show a sample graph. In a real app, we would use historical data.
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=[1, 2, 3, 4, 5, 6, 7],
                    y=[0.45, 0.50, 0.52, 0.55, 0.60, 0.62, 0.65],
                    mode='lines+markers',
                    name='Win Rate',
                    line=dict(color='#2EFE2E', width=4)
                )
            ],
            layout=go.Layout(
                title='Performance Trend',
                xaxis_title='Day',
                yaxis_title='Win Rate',
                template='plotly_dark',
                yaxis=dict(tickformat=".0%"),
                height=400
            )
        )
        
        return cards, table, fig
