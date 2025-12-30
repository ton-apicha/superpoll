"""
QuickPoll Charts Module
Chart generation utilities using Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
import pandas as pd


# Thai-friendly color palette
CHART_COLORS = [
    '#FF6B6B',  # Coral Red
    '#4ECDC4',  # Teal
    '#45B7D1',  # Sky Blue
    '#96CEB4',  # Sage Green
    '#FFEAA7',  # Pale Yellow
    '#DDA0DD',  # Plum
    '#98D8C8',  # Mint
    '#F7DC6F',  # Mustard
    '#BB8FCE',  # Light Purple
    '#85C1E9',  # Light Blue
]


def create_pie_chart(question_text: str, options_data: List[Dict[str, Any]], 
                     show_percentage: bool = True) -> go.Figure:
    """
    Create a pie chart for question results
    
    Args:
        question_text: Question title
        options_data: List of dicts with 'text', 'count', 'percentage' keys
        show_percentage: Whether to show percentage in labels
    """
    labels = [opt['text'] for opt in options_data]
    values = [opt['count'] for opt in options_data]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,  # Donut style
        marker=dict(colors=CHART_COLORS[:len(labels)]),
        textinfo='percent+label' if show_percentage else 'label',
        textposition='outside',
        textfont=dict(size=12),
        hovertemplate="<b>%{label}</b><br>จำนวน: %{value}<br>สัดส่วน: %{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        title=dict(
            text=question_text,
            font=dict(size=16),
            x=0.5
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=60, b=100, l=20, r=20),
        height=400
    )
    
    return fig


def create_bar_chart(question_text: str, options_data: List[Dict[str, Any]], 
                     horizontal: bool = True) -> go.Figure:
    """
    Create a bar chart for question results
    
    Args:
        question_text: Question title
        options_data: List of dicts with 'text', 'count', 'percentage' keys
        horizontal: Whether to use horizontal bars
    """
    labels = [opt['text'] for opt in options_data]
    values = [opt['count'] for opt in options_data]
    percentages = [opt['percentage'] for opt in options_data]
    
    if horizontal:
        fig = go.Figure(data=[go.Bar(
            y=labels,
            x=values,
            orientation='h',
            marker=dict(color=CHART_COLORS[:len(labels)]),
            text=[f"{v} ({p}%)" for v, p in zip(values, percentages)],
            textposition='outside',
            hovertemplate="<b>%{y}</b><br>จำนวน: %{x}<extra></extra>"
        )])
    else:
        fig = go.Figure(data=[go.Bar(
            x=labels,
            y=values,
            marker=dict(color=CHART_COLORS[:len(labels)]),
            text=[f"{v} ({p}%)" for v, p in zip(values, percentages)],
            textposition='outside',
            hovertemplate="<b>%{x}</b><br>จำนวน: %{y}<extra></extra>"
        )])
    
    fig.update_layout(
        title=dict(
            text=question_text,
            font=dict(size=16),
            x=0.5
        ),
        xaxis_title="จำนวนผู้ตอบ" if horizontal else None,
        yaxis_title=None if horizontal else "จำนวนผู้ตอบ",
        margin=dict(t=60, b=40, l=150 if horizontal else 40, r=40),
        height=max(300, len(labels) * 50) if horizontal else 400
    )
    
    return fig


def create_demographic_bar_chart(demographic_label: str, 
                                  data: List[Dict[str, Any]]) -> go.Figure:
    """
    Create a bar chart for demographic breakdown
    
    Args:
        demographic_label: Label for the demographic field
        data: List of dicts with 'value' and 'count' keys
    """
    labels = [d['value'] for d in data]
    values = [d['count'] for d in data]
    total = sum(values)
    percentages = [round(v/total*100, 1) if total > 0 else 0 for v in values]
    
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker=dict(
            color=CHART_COLORS[:len(labels)],
            line=dict(color='white', width=1)
        ),
        text=[f"{v}<br>({p}%)" for v, p in zip(values, percentages)],
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>จำนวน: %{y}<extra></extra>"
    )])
    
    fig.update_layout(
        title=dict(
            text=f"การกระจายตาม{demographic_label}",
            font=dict(size=16),
            x=0.5
        ),
        xaxis_title=demographic_label,
        yaxis_title="จำนวนผู้ตอบ",
        margin=dict(t=60, b=80, l=60, r=40),
        height=400,
        xaxis=dict(tickangle=-45)
    )
    
    return fig


def create_cross_tab_chart(question_text: str, demographic_label: str,
                           cross_data: Dict[str, List[Dict[str, Any]]]) -> go.Figure:
    """
    Create a grouped bar chart for cross-tabulation analysis
    
    Args:
        question_text: Question being analyzed
        demographic_label: Demographic field used for grouping
        cross_data: Dict mapping demographic values to option counts
    """
    fig = go.Figure()
    
    demo_values = list(cross_data.keys())
    if not demo_values:
        return fig
    
    # Get all option names from first demographic value
    option_names = [opt['text'] for opt in cross_data[demo_values[0]]]
    
    for i, option_name in enumerate(option_names):
        values = []
        for demo_val in demo_values:
            opt_data = next((o for o in cross_data[demo_val] if o['text'] == option_name), None)
            values.append(opt_data['count'] if opt_data else 0)
        
        fig.add_trace(go.Bar(
            name=option_name,
            x=demo_values,
            y=values,
            marker_color=CHART_COLORS[i % len(CHART_COLORS)]
        ))
    
    fig.update_layout(
        title=dict(
            text=f"{question_text}<br><sub>แยกตาม{demographic_label}</sub>",
            font=dict(size=14),
            x=0.5
        ),
        barmode='group',
        xaxis_title=demographic_label,
        yaxis_title="จำนวนผู้ตอบ",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.4,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=80, b=120, l=60, r=40),
        height=500
    )
    
    return fig


    return fig


def create_gauge_chart(label: str, current: int, target: int) -> go.Figure:
    """
    Create a gauge chart for quota tracking
    """
    percentage = (current / target * 100) if target > 0 else 0
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = current,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"{label}<br><span style='font-size:0.8em;color:gray'>เป้าหมาย: {target}</span>", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [None, target], 'tickwidth': 1},
            'bar': {'color': "#6366f1"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e2e8f0",
            'steps': [
                {'range': [0, target * 0.5], 'color': '#fee2e2'},
                {'range': [target * 0.5, target * 0.8], 'color': '#fef3c7'},
                {'range': [target * 0.8, target], 'color': '#dcfce7'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target
            }
        }
    ))

    fig.update_layout(height=250, margin=dict(t=50, b=20, l=30, r=30))
    return fig


def create_live_counter(count: int, label: str = "ผู้ตอบทั้งหมด") -> str:
    """
    Create HTML for live counter display
    
    Args:
        count: Current vote count
        label: Counter label
    """
    return f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    ">
        <div style="font-size: 48px; font-weight: bold; margin-bottom: 8px;">
            {count:,}
        </div>
        <div style="font-size: 16px; opacity: 0.9;">
            👥 {label}
        </div>
    </div>
    """
