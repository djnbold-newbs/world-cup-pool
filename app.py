import streamlit as st
import requests

st.set_page_config(page_title="World Cup Pool", page_icon="⚽", layout="centered")

st.title("⚽ World Cup Wins Pool 2026")
st.write("Welcome to Newb Tube's 1st Annual World Cup Wins Pool!")

# 1. Define Friends and Draft Assignments
# Edit these country lists right here in GitHub after your live draft night!
draft_data = {
    "Josh": ["Spain", "Colombia", "Norway", "Turkey", "Sweden", "Iran"],
    "Aaron": ["Brazil", "USA", "Japan", "Ecuador", "Senegal", "Ghana"],
    "Alex": ["France", "Germany", "Belgium", "Switzerland", "Austria", "Scotland"],
    "Dan": ["England", "Netherlands", "Mexico", "Morocco", "Canada", "Ivory Coast"],
    "Chris": ["Argentina", "Portugal", "Uruguay", "Croatia", "Czech Republic", "South Korea"]
}

# 2. Fetch Tournament Match Data
DATA_URL = "https://raw.githubusercontent.com/openfootball/world-cup.json/master/2026/worldcup.json"

@st.cache_data(ttl=600) # Caches data for 10 minutes to save bandwidth
@st.cache_data(ttl=10)
def get_live_scores():
    # 🌟 MANUAL GAME DAY OVERRIDES 🌟
    # If the official repo is lagging, type the live scores right here!
    # This will override or supplement any matches automatically.
    live_overrides = {
        "usa": 3,       # e.g., USA won their game, manually adding 3 pts
        "mexico": 1,    # e.g., Mexico drew, adding 1 pt
    }

    team_points = {}
    
    # Apply manual overrides as the starting baseline
    for team, points in live_overrides.items():
        team_points[team.strip().lower()] = points

    try:
        response = requests.get(DATA_URL)
        if response.status_code == 200:
            data = response.json()
            for round_data in data.get('rounds', []):
                for match in round_data.get('matches', []):
                    if match.get('score1') is not None and match.get('score2') is not None:
                        t1 = match['team1']['name'].strip().lower()
                        t2 = match['team2']['name'].strip().lower()
                        s1 = int(match['score1'])
                        s2 = int(match['score2'])
                        
                        # Only apply automated data if we haven't manually overridden it
                        if t1 not in live_overrides:
                            team_points[t1] = team_points.get(t1, 0)
                            if s1 > s2: team_points[t1] += 3
                            elif s1 == s2: team_points[t1] += 1
                                
                        if t2 not in live_overrides:
                            team_points[t2] = team_points.get(t2, 0)
                            if s2 > s1: team_points[t2] += 3
                            elif s1 == s2: team_points[t2] += 1
            return team_points
    except Exception:
        pass
    
    return team_points

# 3. Calculate Leaderboard Standings
standings = {}
for player, teams in draft_data.items():
    total_score = sum(live_scores.get(team, 0) for team in teams)
    standings[player] = total_score

# Sort leaderboard descending
sorted_standings = sorted(standings.items(), key=lambda x: x[1], reverse=True)

# 4. Display the Visual Web Leaderboard
st.header("🏆 Current Standings")
for rank, (player, points) in enumerate(sorted_standings, start=1):
    # Highlight the current leader
    medal = "🥇" if rank == 1 else "🔹"
    st.subheader(f"{medal} Rank {rank}: {player} — {points} pts")
    
    # Show the teams owned by this player and their individual contributions
    teams_str = ", ".join([f"{t} ({live_scores.get(t, 0)}pts)" for t in draft_data[player]])
    st.caption(f"Drafted Teams: {teams_str}")
    st.markdown("---")

st.info("🔄 Refresh the page anytime to fetch live point updates. Scoring: Win = 3pts, Draw = 1pt.")
