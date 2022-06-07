import pandas as pd
import streamlit as st
import numpy as np
from plotnine import ggplot, geom_point, aes, stat_smooth, facet_wrap, geom_bar
import plotly.express as px

# read data
dataset = pd.read_csv('data/data.csv')



"""
# Formula 1 Circuit Stats 
STATS 1950-2021
"""

## Sidebar
circuit_input = st.sidebar.selectbox('Pick a circuit', dataset['name_x'].unique())
season_input = st.sidebar.selectbox('Pick a season', np.sort(dataset[dataset['name_x']==circuit_input]['year'].unique()))

## Main panel
df_team_points = dataset[dataset['name_x'] == circuit_input][dataset['year'] == season_input].groupby(by='name')['points'].sum()
df_team_points.columns = ['team', 'points']
df_team_points = df_team_points.to_frame()


team_points_graph = ggplot(df_team_points, aes(x="0", y="points")) + geom_bar(stat = "identity")

st.write(team_points_graph)