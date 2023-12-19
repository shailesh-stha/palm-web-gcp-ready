import streamlit as st
import numpy as np
import plotly.graph_objects as go

def bar_graph(dataframe_1, dataframe_2, band_sequence, time_sequence, variable_description, variable_unit, lang_dict):
    # Create a Plotly bar graph using traces
    fig = go.Figure()
    
    # Filter data points from dataframe_1 and dataframe_2 based on the band_index
    filtered_df1 = dataframe_1[dataframe_1['band_index'].isin(band_sequence)]
    filtered_df2 = dataframe_2[dataframe_2['band_index'].isin(band_sequence)]
    
    value_max = int(np.ceil(np.maximum(np.max(filtered_df1['mean']), np.max(filtered_df2['mean']))))
    value_min = int(np.floor(np.minimum(np.min(filtered_df1['mean']), np.min(filtered_df2['mean']))))
    
    # Add bar traces to the figure for each band
    fig.add_trace(go.Bar(x=filtered_df1['band_index'],
                         y=filtered_df1['mean'],
                         name=f"{lang_dict['current_state']}",))
    
    fig.add_trace(go.Bar(x=filtered_df2['band_index'],
                         y=filtered_df2['mean'],
                         name=f"{lang_dict['after_change']}",))
    
    fig.update_layout(height = 450, # width=500,
                      margin=dict(l=20, r=20, t=20, b=20),
                      plot_bgcolor='white',
                      paper_bgcolor="#F2F2F2",
                      legend_x = 0,
                      legend_y = 1,
                      legend=dict(bgcolor='rgba(0,0,0,0)'),
                      legend_font = dict(size=14),
                      )
    
    fig.update_xaxes(title='Zeit',
                     title_font = dict(size=18),
                     tickfont = dict(size=14),
                     tickangle = 90,
                     tickmode = 'array',
                     tickvals = band_sequence,
                     ticktext = time_sequence,
                     )
    
    legend_increase = 2
    if variable_description == "Oberflächentemperatur" or "Surface Temperature":
        legend_increase = 3
    elif variable_description == "Windgeschwindigkeit" or "10-m wind speed":
        legend_increase = 0.1
    elif variable_description == "Nettostrahlung" or "Net radiation flux at the surface":
        legend_increase = 75
    elif variable_description == "Thermal Sensation Index":
        legend_increase = 0

    fig.update_yaxes(title= f'{variable_description} [{variable_unit}]',
                     title_font = dict(size=18),
                     tickfont = dict(size=14),
                     range=[value_min, value_max+legend_increase], # increasement of legend
                     nticks=10,
                     showspikes=True,)
    
    st.plotly_chart(fig, use_container_width=True)