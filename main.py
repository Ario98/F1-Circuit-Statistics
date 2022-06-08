import pandas as pd
import streamlit as st
import numpy as np
from plotnine import ggplot, geom_point, aes, stat_smooth, facet_wrap, geom_bar
import plotly.express as px

# read data
dataset = pd.read_csv('data/data.csv')

## Sidebar
st.sidebar.header('Formula 1 Circuit Stats')
circuit_input = st.sidebar.selectbox('Pick a circuit', dataset['name_x'].unique())

#fix so modern first
season_input = st.sidebar.selectbox('Pick a season', np.sort(dataset[dataset['name_x']==circuit_input]['year'].unique()))

## Main panel
st.header(circuit_input, season_input)

# Map
# have to rename to use in map. Renamed manually in csv dataset.
mapData = dataset[dataset['name_x']==circuit_input]
st.map(mapData)

## Main circuit info
col1, col2, col3 = st.columns(3)
st.markdown("""---""")
col4, col5, col6 = st.columns(3)

with col1:
    winnerDataset = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
    winnerDataset = winnerDataset.sort_values(by=['positionOrder'], ascending=True)
    winner = winnerDataset['full_name'].iloc[0]
    winnerPoints = winnerDataset['points'].iloc[0]
    secondDriver = winnerDataset['full_name'].iloc[1]
    secondPoints = winnerDataset['points'].iloc[1]
    thirdDriver = winnerDataset['full_name'].iloc[2]
    thirdPoints = winnerDataset['points'].iloc[2]
    st.write("Podium")
    st.write('1. ' + winner + ', ' + str(winnerPoints) + ' points')
    st.write('2. ' + secondDriver + ', ' + str(secondPoints) + ' points')
    st.write('3. ' + thirdDriver + ', ' + str(thirdPoints) + ' points')

#fix when fastest lap empty
with col2:
    fastestLapDataset = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
    fastestLapDataset['rank'] = fastestLapDataset['rank'].astype('int')
    fastestLapDataset = fastestLapDataset.sort_values(by=['rank'], ascending=True)
    fastestLapDataset = fastestLapDataset[fastestLapDataset['rank']==1]
    fastestDriver = fastestLapDataset['full_name'].iloc[0]
    fastestTime = fastestLapDataset['fastestLapTime'].iloc[0]
    st.write("Fastest lap")
    st.write(fastestDriver)
    st.write(fastestTime)

with col4:
    laps_total = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
    laps = laps_total['laps'].max()
    st.write("Laps")
    st.write(laps)

with col4:
    st.write("Season")
    st.write(season_input)

with col5:
    numTeams = len(pd.unique(dataset[dataset['year']==season_input]['name']))
    st.write("Teams")
    st.write(numTeams)

with col6:
    numDrivers = len(pd.unique(dataset[dataset['year'] == season_input]['full_name']))
    st.write("Drivers")
    st.write(numDrivers)

# Data for graphing
df_team_points = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
df_team_points = df_team_points.groupby(['name']).sum()
df_team_points = df_team_points.reset_index()
df_team_points = df_team_points.sort_values(by=['points'], ascending=False)
df_team_points.rename(columns={ df_team_points.columns[0]: "name" }, inplace = True)
df_team_points = df_team_points[['name','points']]


st.write()
fig = px.bar(df_team_points, y="points", x="name",
             color="name",
             )
st.header("Team Performance")
st.plotly_chart(fig)


st.write(dataset.head(10))
