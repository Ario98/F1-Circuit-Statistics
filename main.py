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
    layout="wide"
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

col8, col9 = st.columns(2)



df_team_points = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
df_team_points = df_team_points.groupby(['name']).sum()
df_team_points = df_team_points.reset_index()
df_team_points = df_team_points.sort_values(by=['points'], ascending=False)
df_team_points.rename(columns={ df_team_points.columns[0]: "name" }, inplace = True)
df_team_points = df_team_points[['name','points']]


fig = px.bar(df_team_points, y="points", x="name",
             color="name",
             labels={
                     "points": "Points won",
                     "name": "Team"
                 },
             title="Team performance"
             )

# Qualifying vs Race position
df_quali_race = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
df_quali_race = df_quali_race[['full_name', 'grid', 'positionOrder']]

fig1 = go.Figure(data=[
    go.Bar(name='Qualifying position', x=df_quali_race['full_name'], y=df_quali_race['grid']),
    go.Bar(name='Race position', x=df_quali_race['full_name'], y=df_quali_race['positionOrder'])
])
# Change the bar mode
fig1.update_layout(barmode='group', title="Driver performance")
fig1.update_xaxes(tickangle=60)
st.header("Data Visualisation 📊")


col8, col9 = st.columns(2)

with col8:
    st.plotly_chart(fig)

with col9:
    st.plotly_chart(fig1)


# driver performance graph
df_driver_performance = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
df_driver_performance = df_driver_performance[['full_name', 'points', 'grid', 'fastestLapTime', 'name']]

fig3 = px.scatter(df_driver_performance, x="points", y="grid", color="full_name",
                 size="points", hover_data=['fastestLapTime', 'name'], labels = {'points':"Points scored",
              'grid':'Qualifying position'})

fig3.update_yaxes(autorange="reversed")
fig3.update_layout(title="Driver performance (displays drivers who scored points)", legend_title="Drivers")
st.plotly_chart(fig3)

## form graph
df_form = dataset.loc[dataset['year'] == season_input]

"convert a dataframe column to date and sort by date"
df_form['date'] = pd.to_datetime(df_form['date'])

"sort a dataframe and save it to the same dataframe"
df_form = df_form.sort_values(by=['date'])


df_team_form = df_form.groupby(['name', 'name_x']).sum()

min_repeat = 3
vc = df_form['full_name'].value_counts()
df_driver_form = df_form[df_form['full_name'].isin(vc[vc >= min_repeat].index)]


df_team_form = df_team_form.reset_index()

form_picker = st.selectbox("Check from for team or driver", ['Team', 'Driver'])
if (form_picker == 'Team'):
    team_selection = st.multiselect("Select a team", df_form['name'].unique(), default=df_form['name'].unique())
    df_team_form = df_team_form.reset_index()
    df_team_form = df_team_form[df_team_form['name'].isin(team_selection)]
    fig4 = px.line(df_team_form, x="name_x", y="points", color="name")
    fig4.add_vline(x=circuit_input, line_width=5, line_dash="dash", line_color="yellow")
    st.plotly_chart(fig4)
elif (form_picker == 'Driver'):
    driver_selection = st.multiselect("Select a driver", df_form['full_name'].unique(),
                                      default=df_form['full_name'].unique())
    df_driver_form = df_driver_form[df_driver_form['full_name'].isin(driver_selection)]
    fig5 = px.line(df_driver_form, x="name_x", y="points", color="full_name")
    fig5.add_vline(x=circuit_input, line_width=5, line_dash="dash", line_color="yellow")
    st.plotly_chart(fig5)


