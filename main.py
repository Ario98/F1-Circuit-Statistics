import pandas as pd
import streamlit as st
import numpy as np
from plotnine import ggplot, geom_point, aes, stat_smooth, facet_wrap, geom_bar
import plotly.express as px
import datagetter
import plotly.graph_objects as go

# read data
dataset = pd.read_csv('data/data.csv')

st.set_page_config(
    page_title="F1 Circuit Stats",
    page_icon="🏎️",
)

## Sidebar
st.sidebar.header('Formula 1 Circuit Stats')
circuit_input = st.sidebar.selectbox('Pick a circuit 🌎', dataset['name_x'].unique())

#fix so modern first - fixed
seasons_reverse = np.sort(dataset[dataset['name_x']==circuit_input]['year'].unique())
seasons_proper = seasons_reverse[::-1]
season_input = st.sidebar.selectbox('Pick a season 🗓️', seasons_proper)

## Main panel
st.header(circuit_input)
st.write("*Season:*", season_input)
# Map
# have to rename to use in map. Renamed manually in csv dataset.
mapData = dataset[dataset['name_x']==circuit_input]
st.map(mapData)

## Main circuit info

col1, col2 = st.columns(2)

with col1:
    winnerDataset = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
    winnerDataset = winnerDataset.sort_values(by=['positionOrder'], ascending=True)
    winner = winnerDataset['full_name'].iloc[0]
    winnerTeam = winnerDataset['name'].iloc[0]
    secondDriver = winnerDataset['full_name'].iloc[1]
    secondTeam = winnerDataset['name'].iloc[1]
    thirdDriver = winnerDataset['full_name'].iloc[2]
    thirdTeam = winnerDataset['name'].iloc[2]
    st.write("### Podium 🏆")
    st.write('**1. ' + winner + '**, **' + str(winnerTeam)+'**')
    st.write('2. ' + secondDriver + ', ' + str(secondTeam))
    st.write('3. ' + thirdDriver + ', ' + str(thirdTeam))

#fix when fastest lap empty
with col2:
    fastestLapDataset = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
    if (fastestLapDataset['rank'].iloc[0] == '\\N'):
        fastestLapDataset['rank'] = fastestLapDataset['rank'].replace('\\N', 'No data for this season')
        fastestDriver = 'No data for this season'
        fastestTime = 'No data for this season'
    else:
        fastestLapDataset['rank'] = fastestLapDataset['rank'].astype('int')
        fastestLapDataset = fastestLapDataset.sort_values(by=['rank'], ascending=True)
        fastestLapDataset = fastestLapDataset[fastestLapDataset['rank'] == 1]
        fastestDriver = fastestLapDataset['full_name'].iloc[0]
        fastestTime = fastestLapDataset['fastestLapTime'].iloc[0]
    st.write("### Fastest lap 🏎️💨")
    st.write('**'+fastestDriver+'**')
    st.write(fastestTime)

# Full Ranking
race_result = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
race_result = race_result.sort_values(by=['positionOrder'], ascending=True)
race_result = race_result[['full_name', 'name', 'grid', 'positionOrder', 'points', 'fastestLapTime', 'fastestLapSpeed', 'laps']]
race_result.columns = ['Driver', 'Team', 'Starting position', 'Finishing position', 'Points', 'Fastest lap', 'Fastest lap speed', 'Laps completed']

with st.expander("Full race result"):
    st.dataframe(race_result.reset_index(drop=True))

st.write("### Race facts 📄")
col4, col5, col6, col7 = st.columns(4)

with col4:
    laps_total = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
    laps = laps_total['laps'].max()
    st.write("Laps")
    st.write(laps)

with col5:
    numTeams = len(race_result['Driver'])
    st.write("Drivers")
    st.write(numTeams)

with col6:
    numTeams = len(pd.unique(dataset[dataset['year']==season_input]['name']))
    st.write("Teams")
    st.write(numTeams)

with col7:
    st.write("Round")
    st.write(fastestLapDataset['round'].iloc[0])

# Data for graphing



df_team_points = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
df_team_points = df_team_points.groupby(['name']).sum()
df_team_points = df_team_points.reset_index()
df_team_points = df_team_points.sort_values(by=['points'], ascending=False)
df_team_points.rename(columns={ df_team_points.columns[0]: "name" }, inplace = True)
df_team_points = df_team_points[['name','points']]


fig = px.bar(df_team_points, y="points", x="name",
             color="name",
             )
st.header("Team Performance")
st.plotly_chart(fig)


# Qualifying vs Race position
df_quali_race = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
df_quali_race = df_quali_race[['full_name', 'grid', 'positionOrder']]

fig1 = go.Figure(data=[
    go.Bar(name='Starting position', x=df_quali_race['full_name'], y=df_quali_race['grid']),
    go.Bar(name='Finishing position', x=df_quali_race['full_name'], y=df_quali_race['positionOrder'])
])
# Change the bar mode
fig1.update_layout(barmode='group')
fig1.update_xaxes(tickangle=60)
st.header("Driver Performance")
st.plotly_chart(fig1)


st.write(dataset.head(10))
