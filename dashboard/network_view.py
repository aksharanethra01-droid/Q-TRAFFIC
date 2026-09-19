import plotly.graph_objects as go
import streamlit as st

def render_network(states):
    x=[0,1,2,3]; y=[0,0,0,0]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=x,y=y,mode="lines",name="J1 → J2 → J3 → J4"))
    for i,j in enumerate(["J1","J2","J3","J4"]):
        s=states.get(j,{})
        fig.add_trace(go.Scatter(x=[i],y=[0],mode="markers+text",text=[j],textposition="top center",
                                 marker={"size":18},name=j,
                                 hovertext=f"vehicles={s.get('vehicles','-')} queue={s.get('queue','-')}"))
    fig.update_layout(height=280, showlegend=False, xaxis={"visible":False}, yaxis={"visible":False})
    st.plotly_chart(fig, use_container_width=True)
