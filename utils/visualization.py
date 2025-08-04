import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from config import Config

def create_performance_history(performance_log):
    """
    Create a performance history line chart with win/loss indicators
    
    Args:
        performance_log (list): List of performance records from conductor
        
    Returns:
        plotly.graph_objs._figure.Figure: Performance history figure
    """
    if not performance_log:
        return create_empty_plot("No performance data available")
    
    # Create DataFrame from performance log
    df = pd.DataFrame(performance_log)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    
    # Calculate cumulative win rate
    df['win'] = df['result'] == 'win'
    df['cumulative_wins'] = df['win'].cumsum()
    df['total_bets'] = np.arange(1, len(df) + 1)
    df['win_rate'] = df['cumulative_wins'] / df['total_bets']
    
    # Create colors based on win/loss
    colors = ['#2EFE2E' if res == 'win' else '#FE2E2E' for res in df['result']]
    
    # Create figure
    fig = go.Figure()
    
    # Add win rate line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['win_rate'],
        mode='lines+markers',
        name='Win Rate',
        line=dict(color='#2ECCFA', width=4),
        marker=dict(size=8),
        hovertemplate='%{y:.2%} Win Rate<extra></extra>'
    ))
    
    # Add profit threshold
    fig.add_trace(go.Scatter(
        x=[df['timestamp'].min(), df['timestamp'].max()],
        y=[0.55, 0.55],
        mode='lines',
        name='Profit Threshold',
        line=dict(color='#2EFE2E', width=2, dash='dash'),
        hovertemplate='Profit Threshold<extra></extra>'
    ))
    
    # Add individual bet markers
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=[0.05] * len(df),
        mode='markers',
        name='Bets',
        marker=dict(
            color=colors,
            size=12,
            line=dict(width=2, color='DarkSlateGrey')
        ),
        hovertext=df.apply(
            lambda row: f"{row['result'].upper()} - Confidence: {row['confidence']:.0%}", 
            axis=1
        ),
        hoverinfo='text'
    ))
    
    # Update layout
    fig.update_layout(
        title='Performance History',
        xaxis_title='Date',
        yaxis_title='Win Rate',
        yaxis_tickformat='.0%',
        yaxis_range=[0, 1.05],
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
        height=500
    )
    
    return fig

def create_value_bets_plot(value_bets):
    """
    Create a scatter plot of value bets showing odds vs confidence
    
    Args:
        value_bets (list): List of value bet dictionaries
        
    Returns:
        plotly.graph_objs._figure.Figure: Value bets visualization
    """
    if not value_bets:
        return create_empty_plot("No value bets available")
    
    df = pd.DataFrame(value_bets)
    
    # Create color based on bet type
    df['color'] = df['bet_type'].apply(
        lambda x: '#2EFE2E' if x == 'UNDERVALUE' else '#FE2E2E'
    )
    
    # Create size based on value score (absolute value)
    df['size'] = (abs(df['value_score']) * 100).clip(10, 50)
    
    # Create hover text
    df['hover_text'] = df.apply(
        lambda row: (
            f"{row['home_team']} vs {row['away_team']}<br>"
            f"Odds: {row['bookmaker_odds']:.2f}<br>"
            f"Confidence: {row['confidence']:.0%}<br>"
            f"Value Score: {row['value_score']:.3f}"
        ), 
        axis=1
    )
    
    fig = go.Figure()
    
    # Add undervalue bets
    undervalue = df[df['bet_type'] == 'UNDERVALUE']
    if not undervalue.empty:
        fig.add_trace(go.Scatter(
            x=undervalue['bookmaker_odds'],
            y=undervalue['confidence'],
            mode='markers',
            name='Undervalue',
            marker=dict(
                color='#2EFE2E',
                size=undervalue['size'],
                line=dict(width=2, color='DarkSlateGrey'),
                opacity=0.8
            ),
            text=undervalue['hover_text'],
            hoverinfo='text'
        ))
    
    # Add overvalue bets
    overvalue = df[df['bet_type'] == 'OVERVALUE']
    if not overvalue.empty:
        fig.add_trace(go.Scatter(
            x=overvalue['bookmaker_odds'],
            y=overvalue['confidence'],
            mode='markers',
            name='Overvalue',
            marker=dict(
                color='#FE2E2E',
                size=overvalue['size'],
                line=dict(width=2, color='DarkSlateGrey'),
                opacity=0.8
            ),
            text=overvalue['hover_text'],
            hoverinfo='text'
        ))
    
    # Add recommendation zones
    fig.add_shape(
        type="rect",
        x0=1.5, x1=4, y0=0.7, y1=1,
        line=dict(color="#2EFE2E", width=2, dash="dot"),
        fillcolor="rgba(46, 254, 46, 0.1)",
        name="Recommended Zone"
    )
    
    fig.add_annotation(
        x=2.5, y=0.85,
        text="Recommended Bets",
        showarrow=False,
        font=dict(color="#2EFE2E", size=12)
    )
    
    # Update layout
    fig.update_layout(
        title='Value Bet Analysis',
        xaxis_title='Bookmaker Odds',
        yaxis_title='Model Confidence',
        yaxis_tickformat='.0%',
        template='plotly_dark',
        hovermode='closest',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        height=600
    )
    
    return fig

def create_feature_importance_plot(feature_importances):
    """
    Create horizontal bar chart of feature importances
    
    Args:
        feature_importances (pd.Series): Feature importance scores
        
    Returns:
        plotly.graph_objs._figure.Figure: Feature importance plot
    """
    if feature_importances is None or feature_importances.empty:
        return create_empty_plot("No feature importance data")
    
    # Get top 15 features
    top_features = feature_importances.head(15)
    
    # Create color gradient from blue to green
    colors = px.colors.sample_colorscale("BluGrn", len(top_features))
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_features.index,
        x=top_features.values,
        orientation='h',
        marker=dict(color=colors),
        hoverinfo='x',
        name='Feature Importance'
    ))
    
    fig.update_layout(
        title='Top Predictive Features',
        xaxis_title='Importance Score',
        yaxis_title='Feature',
        template='plotly_dark',
        height=600
    )
    
    return fig

def create_win_loss_pie(performance_log):
    """
    Create a pie chart showing win/loss distribution
    
    Args:
        performance_log (list): List of performance records
        
    Returns:
        plotly.graph_objs._figure.Figure: Win/loss pie chart
    """
    if not performance_log:
        return create_empty_plot("No performance data available")
    
    df = pd.DataFrame(performance_log)
    win_count = (df['result'] == 'win').sum()
    loss_count = (df['result'] == 'loss').sum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=['Wins', 'Losses'],
        values=[win_count, loss_count],
        marker=dict(colors=['#2EFE2E', '#FE2E2E']),
        hole=0.4,
        textinfo='percent+value',
        hoverinfo='label+percent+value',
        name='Win/Loss'
    ))
    
    fig.update_layout(
        title='Win/Loss Distribution',
        template='plotly_dark',
        height=400
    )
    
    return fig

def create_roi_trend(performance_log, initial_budget):
    """
    Create ROI trend chart over time
    
    Args:
        performance_log (list): List of performance records
        initial_budget (float): Starting budget
        
    Returns:
        plotly.graph_objs._figure.Figure: ROI trend chart
    """
    if not performance_log:
        return create_empty_plot("No performance data available")
    
    df = pd.DataFrame(performance_log)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.sort_values('timestamp', inplace=True)
    
    # Calculate cumulative ROI
    df['profit'] = df['cost'].apply(
        lambda cost: cost * 10 if df.loc[df.index[0], 'result'] == 'win' else -cost * 10
    )
    df['cumulative_profit'] = df['profit'].cumsum()
    df['roi'] = df['cumulative_profit'] / initial_budget
    
    # Create colors for markers
    colors = ['#2EFE2E' if res == 'win' else '#FE2E2E' for res in df['result']]
    
    fig = go.Figure()
    
    # Add ROI line
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['roi'],
        mode='lines',
        name='ROI',
        line=dict(color='#2ECCFA', width=4),
        hovertemplate='ROI: %{y:.2%}<extra></extra>'
    ))
    
    # Add markers for individual bets
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['roi'],
        mode='markers',
        name='Bets',
        marker=dict(
            color=colors,
            size=10,
            line=dict(width=2, color='DarkSlateGrey')
        ),
        hovertext=df.apply(
            lambda row: f"{row['result'].upper()} - Profit: R{row['profit']:.2f}", 
            axis=1
        ),
        hoverinfo='text'
    ))
    
    # Add break-even line
    fig.add_shape(
        type="line",
        x0=df['timestamp'].min(),
        x1=df['timestamp'].max(),
        y0=0,
        y1=0,
        line=dict(color="white", width=2, dash="dash"),
        name="Break-even"
    )
    
    fig.update_layout(
        title='ROI Trend',
        xaxis_title='Date',
        yaxis_title='Return on Investment',
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
        height=500
    )
    
    return fig

def create_empty_plot(message="No data available"):
    """
    Create an empty plot with a message
    
    Args:
        message (str): Message to display
        
    Returns:
        plotly.graph_objs._figure.Figure: Empty plot figure
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=20)
    )
    fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        template='plotly_dark'
    )
    return fig
