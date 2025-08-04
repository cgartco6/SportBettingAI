from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime
import plotly.graph_objects as go

def create_layout(report_data=None):
    """Create the layout for the Dash application."""
    # Default values if no report data
    win_rate = report_data['performance']['win_rate'] if report_data else 0.0
    roi = report_data['performance']['roi'] if report_data else 0.0
    value_bets = report_data['value_bets'] if report_data else []
    
    # Calculate win colors
    win_color = '#2EFE2E'  # Neon green
    loss_color = '#FE2E2E'  # Red
    
    return dbc.Container(
        fluid=True,
        children=[
            # Header
            dbc.Row(
                dbc.Col(
                    html.H1("AI Sports Betting Dashboard", 
                            className="text-center my-4",
                            style={"color": "#2ECCFA"}),  # Light blue
                    width=12
                )
            ),
            
            # Performance Metrics
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Win Rate", className="text-center"),
                        dbc.CardBody(
                            html.H2(f"{win_rate:.2%}", 
                                    className="card-title text-center",
                                    style={"color": win_color if win_rate > 0.5 else loss_color})
                        )
                    ]),
                    width=4
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("ROI", className="text-center"),
                        dbc.CardBody(
                            html.H2(f"{roi:.2%}", 
                                    className="card-title text-center",
                                    style={"color": win_color if roi > 0 else loss_color})
                        )
                    ]),
                    width=4
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Active Agents", className="text-center"),
                        dbc.CardBody(
                            html.H2("12", 
                                    className="card-title text-center",
                                    style={"color": "#2ECCFA"})  # Light blue
                        )
                    ]),
                    width=4
                )
            ], className="mb-4"),
            
            # Value Bets Table
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Value Bet Recommendations", className="text-center"),
                        dbc.CardBody(
                            create_value_bets_table(value_bets)
                    ]),
                    width=12
                )
            ),
            
            # Performance Graph
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Performance History", className="text-center"),
                        dbc.CardBody(
                            dcc.Graph(
                                id='performance-graph',
                                figure=create_performance_graph(report_data)
                        )
                    ]),
                    width=12
                ), className="mt-4"
            ),
            
            # System Controls
            dbc.Row(
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("System Controls", className="text-center"),
                        dbc.CardBody([
                            dbc.Button("Refresh Data", id="refresh-button", color="primary", className="mr-2"),
                            dbc.Button("Trigger Retraining", id="retrain-button", color="warning", className="mr-2"),
                            dbc.Button("Manual Approval", id="approval-button", color="success"),
                            dcc.Interval(
                                id='interval-component',
                                interval=15*60*1000,  # 15 minutes
                                n_intervals=0
                            )
                        ], className="d-flex justify-content-center")
                    ]),
                    width=12
                ), className="mt-4"
            ),
            
            # Hidden div for storing report data
            dcc.Store(id='report-data-store', data=report_data),
            
            # Status alerts
            html.Div(id='status-alert')
        ],
        style={"backgroundColor": "#121212"}  # Dark background
    )

def create_value_bets_table(value_bets):
    """Create table for value bet recommendations."""
    if not value_bets:
        return html.P("No value bets identified", className="text-center")
    
    rows = []
    for bet in value_bets:
        value_color = '#2EFE2E' if bet['value_score'] > 0 else '#FE2E2E'
        confidence_color = '#2EFE2E' if bet['confidence'] > 0.7 else '#F7FE2E' if bet['confidence'] > 0.6 else '#FE2E2E'
        
        rows.append(html.Tr([
            html.Td(f"{bet['home_team']} vs {bet['away_team']}"),
            html.Td(bet['bet_type'], style={"color": value_color}),
            html.Td(f"{bet['bookmaker_odds']:.2f}"),
            html.Td(f"{bet['confidence']:.0%}", style={"color": confidence_color}),
            html.Td(f"{bet['value_score']:.3f}", style={"color": value_color})
        ]))
    
    return dbc.Table([
        html.Thead(html.Tr([
            html.Th("Match"), 
            html.Th("Bet Type"), 
            html.Th("Odds"), 
            html.Th("Confidence"), 
            html.Th("Value Score")
        ])),
        html.Tbody(rows)
    ], bordered=True, hover=True, responsive=True, striped=True)

def create_performance_graph(report_data):
    """Create performance history graph."""
    # Sample data - in real app this would come from historical records
    dates = pd.date_range(end=datetime.today(), periods=30, freq='D')
    win_rates = [0.45, 0.48, 0.50, 0.52, 0.55, 0.57, 0.60, 0.62, 0.65, 0.63, 
                 0.66, 0.68, 0.70, 0.72, 0.71, 0.73, 0.75, 0.74, 0.76, 0.77,
                 0.75, 0.76, 0.78, 0.79, 0.80, 0.79, 0.81, 0.82, 0.83, 0.82]
    
    # Create colors based on win rate
    colors = ['#2EFE2E' if rate > 0.55 else '#F7FE2E' if rate > 0.5 else '#FE2E2E' 
              for rate in win_rates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=win_rates,
        mode='lines+markers',
        name='Win Rate',
        line=dict(color='#2ECCFA', width=4),
        marker=dict(color=colors, size=8),
        hovertemplate='%{y:.0%} Win Rate<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=[0.55] * len(dates),
        mode='lines',
        name='Profit Threshold',
        line=dict(color='#2EFE2E', width=2, dash='dash'),
        hovertemplate='Profit Threshold<extra></extra>'
    ))
    
    fig.update_layout(
        title='Win Rate History',
        xaxis_title='Date',
        yaxis_title='Win Rate',
        yaxis_tickformat='.0%',
        template='plotly_dark',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=400
    )
    
    return fig
