import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px

# read data
dataset = pd.read_csv('data/data.csv')

st.set_page_config(
    page_title="F1 Circuit Stats",
    page_icon="🏎️",
    layout="wide"
)

# Sidebar
st.sidebar.header('Formula 1 Circuit Stats')
circuit_input = st.sidebar.selectbox('Pick a circuit 🌎', dataset['name_x'].unique())

# Season input - has to be reversed to show latest season first
seasons_reverse = np.sort(dataset[dataset['name_x']==circuit_input]['year'].unique())
seasons = seasons_reverse[::-1]
season_input = st.sidebar.selectbox('Pick a season 🗓️', seasons)

# Main panel
st.header(circuit_input)
st.write("*Season:*", season_input)

# Circuit map
mapData = dataset[dataset['name_x']==circuit_input]
st.map(mapData)

# Writes the podium and the fastest lap
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

# Full race results as expandable component
race_result = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
race_result = race_result.sort_values(by=['positionOrder'], ascending=True)
race_result = race_result[['full_name', 'name', 'grid', 'positionOrder', 'points', 'fastestLapTime', 'fastestLapSpeed', 'laps']]
race_result.columns = ['Driver', 'Team', 'Starting position', 'Finishing position', 'Points', 'Fastest lap', 'Fastest lap speed', 'Laps completed']

with st.expander("Full race result"):
    st.dataframe(race_result.reset_index(drop=True))

# Race facts
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

# Data querying for graphs
# Team points (#1 graph)
df_team_points = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
df_team_points = df_team_points.groupby(['name']).sum()
df_team_points = df_team_points.reset_index()
df_team_points = df_team_points.sort_values(by=['points'], ascending=False)
df_team_points.rename(columns={ df_team_points.columns[0]: "name" }, inplace = True)
df_team_points = df_team_points[['name','points']]

# Driver performance (Quali vs Race position) (#2 graph)
df_quali_race = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
df_quali_race = df_quali_race[['full_name', 'grid', 'positionOrder']]
df_quali_race['positions_gained_lost'] = df_quali_race['grid'] - df_quali_race['positionOrder']
df_quali_race["color"] = np.where(df_quali_race["positions_gained_lost"]<0, 'Positions lost', 'Positions gained')

# Driver performance graph (Scatterplot) (#3 Graph)
df_driver_performance = dataset.loc[(dataset['year'] == season_input) & (dataset['name_x'] == circuit_input)]
df_driver_performance = df_driver_performance[['full_name', 'points', 'grid', 'fastestLapTime', 'name']]

# Form graph (#4 Graph)
df_form = dataset.loc[dataset['year'] == season_input]
df_team_form = df_form.groupby(['name', 'name_x']).sum()
min_repeat = 3
vc = df_form['full_name'].value_counts()
df_driver_form = df_form[df_form['full_name'].isin(vc[vc >= min_repeat].index)]
df_team_form = df_team_form.reset_index()

# Graph definitions
fig = px.bar(df_team_points, y="points", x="name", color="name", labels={"points": "Points won", "name": "Team"})

fig1 = px.bar(df_quali_race, x='positions_gained_lost', y='full_name', color='color', labels={"full_name": "Driver", "positions_gained_lost": "Position Gain/Loss", "color": "Position Gain/Loss"})

fig3 = px.scatter(df_driver_performance, x="points", y="grid", color="full_name", size="points", hover_data=['fastestLapTime', 'name'], labels = {'points':"Points scored",'grid':'Qualifying position', 'full_name':'Driver', 'fastestLapTime':'Fastest lap time'})
fig3.update_yaxes(autorange="reversed")
fig3.update_layout(legend_title="Drivers")


# Display graphs
st.header("Performance  📊")
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig)
with col2:
    st.plotly_chart(fig3)

st.header("Position gain/loss ↕️")
st.plotly_chart(fig1, use_container_width=True)

st.header("Form 🏆")
st.write('The following visualisation shows the form of the teams/drivers in the circuits during the season. The yellow dashed line represent the currently selected circuit. The visualisation starts with a lower number of entries, however, you are welcome to add teams or drivers you want to analyze.')
form_picker = st.selectbox("Do you want to see the visualisation for drivers or teams?", ['Team', 'Driver'])
if (form_picker == 'Team'):
    top_10_teams = df_team_form.sort_values(by=['points'], ascending=False)
    team_selection = st.multiselect("Select the teams", df_form['name'].unique(), default=top_10_teams['name'].head().unique())
    df_team_form = df_team_form.reset_index()
    df_team_form = df_team_form[df_team_form['name'].isin(team_selection)]
    fig4 = px.line(df_team_form, x="name_x", y="points", color="name", labels = {'points':"Points scored",'name_x':'Circuit', 'name':'Team'})
    fig4.add_vline(x=circuit_input, line_width=5, line_dash="dash", line_color="yellow")
    st.plotly_chart(fig4, use_container_width=True)
elif (form_picker == 'Driver'):
    top_5_drivers = df_driver_form.sort_values(by=['points'], ascending=False)
    driver_selection = st.multiselect("Select the drivers", df_form['full_name'].unique(),
                                      default=top_5_drivers.head()['full_name'].unique())
    df_driver_form = df_driver_form[df_driver_form['full_name'].isin(driver_selection)]
    fig5 = px.line(df_driver_form, x="name_x", y="points", color="full_name", labels = {'points':"Points scored",'name_x':'Circuit', 'name':'Team', 'full_name':'Driver'})
    fig5.add_vline(x=circuit_input, line_width=5, line_dash="dash", line_color="yellow")
    st.plotly_chart(fig5, use_container_width=True)


