import streamlit as st
import pandas as pd
import numpy as np
import requests 
import json
import pickle
from datetime import datetime, timezone, timedelta
import os
import plotly.express as px
# from config import API_KEY
API_KEY = st.secrets["API_KEY"]
 
team = st.text_input('Team Name', 'Warriors')
link1 = "https://www.balldontlie.io/api/v1/teams"
res1 = requests.get(link1)
res1 = json.loads(res1.text)["data"]
res1 = [x for x in res1 if team.lower() in x["full_name"].lower()]
team_id = res1[0]["id"]
us = res1[0]["full_name"]

link = "https://www.balldontlie.io/api/v1/games?seasons[]=2023&team_ids[]=" + str(team_id) + "&per_page=100"
res = requests.get(link)
res = json.loads(res.text)["data"]
sorted_json = sorted(res, key=lambda x: x["date"], reverse=True)
sorted_json = [x for x in sorted_json if x["time"] is not None]

games = []
for x in sorted_json:
    if x["home_team"]["id"] == team_id:
        opponent = x["visitor_team"]["full_name"]
        our_score = x["home_team_score"]
        their_score = x["visitor_team_score"]
    else:
        opponent = x["home_team"]["full_name"]
        our_score = x["visitor_team_score"]
        their_score = x["home_team_score"]

    x = {
        "us":  us,
        "opponent": opponent,
        "our_score": our_score,
        "their_score": their_score,
        "margin": our_score - their_score,
        "time": x["time"],
        "quarter": x["period"],
        "date": x["date"][:10]
    }
    games.append(x)
    
df = pd.DataFrame(games)
df['win'] = np.where(df['our_score'] > df['their_score'], 'green', 'red')
# st.write(df)
fig = px.scatter(df, x='date', y='margin', color='win', color_discrete_map={'red': 'red', 'green': 'green'}, hover_data=['opponent', 'date', 'margin'])
fig.update_layout(xaxis_title='Date', yaxis_title='Margin')
fig.update_traces(marker=dict(size=15))

st.header("🏀 {}".format(us))
wins = str(len(df[df['win'] == "green"]))
losses = str(len(df[df['win'] == "red"]))
st.write("### All Games")
header_html = f"<h1 style='position: relative;'>{number} <span style='position: absolute; top: 0; left: 50%; transform: translateX(-50%);'>W</span></h1>"
st.markdown(header_html, unsafe_allow_html=True)
st.plotly_chart(fig)

current_date = datetime.now().strftime("%Y-%m-%d")
today = datetime.now()
yesterday = today - timedelta(days=1)
yesterday_formatted = yesterday.strftime("%Y-%m-%d")
new_link = "https://www.balldontlie.io/api/v1/games?start_date=" + str(yesterday) + "&end_date=" + str(current_date)
new_res = json.loads(requests.get(new_link).text)["data"]
with st.sidebar:
    st.write("## Today's Games")
    for x in new_res:
        if(x["time"] is None):
            x["time"] = "Has not started"
        st.write(x["home_team"]["full_name"] + " (" + str(x["home_team_score"]) + ")" + " vs. " + x["visitor_team"]["full_name"] + " (" + str(x["visitor_team_score"]) + ")")
        st.write(x["time"])
        st.write("-----------------------------------------------------")
    
    
odds = "https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?regions=us&markets=spreads&apiKey=" + API_KEY
odds = json.loads(requests.get(odds).text)
odds = [x["bookmakers"][0]["markets"][0]["outcomes"] for x in odds if x["home_team"] == us or x["away_team"] == us]
if not odds:
    st.write("### No Games Today")
else:
    st.write("### Today's Game")
    if team in odds[0][0]["name"]:
        them = odds[0][1]["name"]
        us_odds = odds[0][0]["point"]
        their_odds = odds[0][1]["point"]
    else:
        us_odds = odds[0][1]["point"]
        their_odds = odds[0][0]["point"]
        them = odds[0][0]["name"]
    st.write(us + " vs. " + them)
    win = "win"
    if(us_odds > their_odds):
        win = "lose"
        st.write("Prediction: " + us + " " + win + " by " + str(us_odds) + " points")
    else:
        st.write("Prediction: " + us + " " + win + " by " + str(their_odds) + " points")


