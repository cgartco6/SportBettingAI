from dash import html, dcc
import dash_bootstrap_components as dbc

def create_layout(report_data):
    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("AI Sports Betting Dashboard", className="text-center my-4"), width=12)
        ]),
        
        # Performance Metrics
        dbc.Row([
            dbc.Col(create_performance_card(report_data), width=12
        ]),
        
        # Value Bets Table
        dbc.Row([
            dbc.Col(create_value_bets_table(report_data), width=12
        ]),
        
        # Performance Graph
        dbc.Row([
            dbc.Col(dcc.Graph(id='performance-graph'), width=12
        ]),
        
        # Refresh control
        dbc.Row([
            dbc.Col(dcc.Interval(id='refresh-interval', interval=15*60*1000, n_intervals=0))
        ])
    ], fluid=True)

def create_performance_card(report_data):
    perf = report_data['performance']
    win_rate = perf['win_rate']
    roi = perf['roi']
    
    win_color = "#2EFE2E" if win_rate > 0.55 else "#F7FE2E" if win_rate > 0.5 else "#FE2E2E"
    roi_color = "#2EFE2E" if roi > 0 else "#FE2E2E"
    
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4("Win Rate", className="card-title"),
                    html.H2(f"{win_rate:.2%}", style={"color": win_color})
                ], width=4),
                
                dbc.Col([
                    html.H4("ROI", className="card-title"),
                    html.H2(f"{roi:.2%}", style={"color": roi_color})
                ], width=4),
                
                dbc.Col([
                    html.H4("Active Agents", className="card-title"),
                    html.H2("12", style={"color": "#2ECCFA"})
                ], width=4)
            ])
        ])
    ])

def create_value_bets_table(report_data):
    rows = []
    for bet in report_data['value_bets']:
        value_color = "#2EFE2E" if bet['value_score'] > 0 else "#FE2E2E"
        confidence_color = "#2EFE2E" if bet['confidence'] > 0.7 else "#F7FE2E" if bet['confidence'] > 0.6 else "#FE2E2E"
        
        rows.append(dbc.Tr([
            dbc.Td(f"{bet['home_team']} vs {bet['away_team']}"),
            dbc.Td(bet['bet_type'], style={"color": value_color}),
            dbc.Td(f"{bet['bookmaker_odds']:.2f}"),
            dbc.Td(f"{bet['confidence']:.0%}", style={"color": confidence_color}),
            dbc.Td(f"{bet['value_score']:.3f}", style={"color": value_color})
        ]))
    
    return dbc.Card([
        dbc.CardHeader("Value Bet Recommendations"),
        dbc.CardBody([
            dbc.Table([
                html.Thead(html.Tr([
                    html.Th("Match"), 
                    html.Th("Bet Type"), 
                    html.Th("Odds"), 
                    html.Th("Confidence"), 
                    html.Th("Value Score")
                ])),
                html.Tbody(rows)
            ], bordered=True, hover=True)
        ])
    ])
