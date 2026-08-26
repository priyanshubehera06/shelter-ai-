import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def plot_diurnal_trajectory(hours, t_outdoor, t_indoor, t_sol_air=None):
    fig = go.Figure()
    
    # Target ASHRAE Comfort Band (20°C - 26°C)
    fig.add_hrect(
        y0=20.0, y1=26.0,
        fillcolor="rgba(46, 204, 113, 0.15)",
        line_width=0,
        annotation_text="ASHRAE 55 Comfort Zone (20-26°C)",
        annotation_position="top left"
    )

    fig.add_trace(go.Scatter(
        x=hours, y=t_outdoor,
        mode="lines+markers",
        name="Outdoor Temp (°C)",
        line=dict(color="#e67e22", width=2, dash="dash")
    ))
    
    if t_sol_air is not None:
        fig.add_trace(go.Scatter(
            x=hours, y=t_sol_air,
            mode="lines",
            name="Sol-Air Envelope Temp (°C)",
            line=dict(color="#e74c3c", width=1.5, dash="dot")
        ))
        
    fig.add_trace(go.Scatter(
        x=hours, y=t_indoor,
        mode="lines+markers",
        name="Indoor Temp (°C)",
        line=dict(color="#2ecc71", width=3.5)
    ))

    fig.update_layout(
        title="24-Hour Temperature Trajectory & Passive Thermal Lag",
        xaxis_title="Hour of Day",
        yaxis_title="Temperature (°C)",
        hovermode="x unified",
        margin=dict(l=30, r=30, t=40, b=30),
        template="plotly_dark"
    )
    return fig

def plot_pareto_front(all_candidates, pareto_front):
    df_all = [
        {
            "Cost (₹)": c["cost_inr"],
            "Carbon (kgCO2)": c["carbon_kg"],
            "PMV Discomfort": c["discomfort_pmv"],
            "Wall Material": c["candidate"]["wall_mat_id"],
            "Type": "Pareto Optimal" if c.get("is_pareto") else "Exploratory Point"
        }
        for c in all_candidates
    ]
    
    fig = px.scatter(
        df_all,
        x="Cost (₹)",
        y="Carbon (kgCO2)",
        color="Type",
        size="PMV Discomfort",
        hover_data=["Wall Material", "PMV Discomfort"],
        color_discrete_map={"Pareto Optimal": "#00ffcc", "Exploratory Point": "#7f8c8d"},
        title="Multi-Objective Optimization Pareto Frontier (Cost vs Carbon vs PMV)"
    )
    fig.update_layout(template="plotly_dark", margin=dict(l=30, r=30, t=40, b=30))
    return fig

def plot_cost_carbon_breakdown(boq):
    components = [b["component"] for b in boq]
    costs = [b["cost_inr"] for b in boq]
    carbons = [b["carbon_kgco2"] for b in boq]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=components, y=costs, name="Cost (₹)", marker_color="#3498db"))
    fig.add_trace(go.Bar(x=components, y=carbons, name="Embodied Carbon (kgCO2)", marker_color="#e74c3c", yaxis="y2"))

    fig.update_layout(
        title="Itemized Envelope Bill of Quantities & Carbon Footprint",
        yaxis=dict(title="Cost (INR ₹)"),
        yaxis2=dict(title="Embodied Carbon (kgCO₂)", overlaying="y", side="right"),
        barmode="group",
        template="plotly_dark",
        margin=dict(l=30, r=30, t=40, b=30)
    )
    return fig

def plot_mcda_radar(pillars):
    categories = list(pillars.keys())
    values = list(pillars.values())
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(46, 204, 113, 0.3)',
        line=dict(color='#2ecc71', width=3)
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title="5-Pillar Shelter Sustainability & Performance Score",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    return fig
