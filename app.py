import streamlit as st
import requests

st.set_page_config(page_title="World Cup Pool", page_icon="⚽", layout="centered")

st.title("⚽ World Cup Snake Draft Pool")
st.write("Welcome to our 5-friend live tournament tracker!")

# ==========================================
# 1. DEFINE FRIENDS & DRAFT ASSIGNMENTS
# ==========================================
# Feel free to change these country names after your draft night.
# The code below will automatically handle spacing and capitalization!
draft_data = {
    "Josh": ["Spain", "Colombia", "Norway", "Turkey", "Sweden", "Iran"],
    "Aaron": ["Brazil", "USA", "Japan", "Ecuador", "Senegal", "Ghana"],
    "Alex": ["France", "Germany", "Belgium", "Switzerland", "Austria", "Scotland"],
    "Dan": ["England", "Netherlands", "Mexico", "Morocco", "Canada", "Ivory Coast"],
    "Chris": ["Argentina", "Portugal", "Uruguay", "Croatia", "Czech Republic", "South Korea"]
}

# ==========================================
# 2. LIVE MATCH DATA FETCHING WITH OVERRIDES
# ==========================================
DATA_URL = "https://raw.githubusercontent.com/openfootball/world-cup.json/master/2026/worldcup.json"

@st.cache_data(ttl=10) # Checks the internet every 10 seconds on refresh
def get_live_scores():
    # 🌟 MANUAL GAME DAY OVERRIDES 🌟
    # If the official repo is lagging, type the live scores right here!
    # Always type the country names in LOWERCASE here.
    live_overrides = {
        "usa": 3,       # e.g., USA won their game, manually adding 3 pts
        "mexico": 1,    # e.g., Mexico drew, adding 1 pt
    }

    team_points = {}
    
    # Initialize team points with manual overrides
    for team, points in live_overrides.items():
        team_points[team.strip().lower()] = points

    try:
        response = requests.get(DATA_URL)
        if response.status_code == 200:
            data = response.json()
            for round_data in data.get('rounds', []):
                for match in round_data.get('matches', []):
                    # Check if match has concluded
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
        pass # If network fails, return whatever we have in team_points
    
    # Fallback default values if the internet data source is completely empty or down
    fallback_defaults = {
        "brazil": 9, "argentina": 9, "spain": 7, "mexico": 7, 
        "france": 6, "england": 5, "usa": 4, "canada": 3
    }
    
    # Fill in fallback data for teams that don't have points yet
    for team, points in fallback_defaults.items():
        if team not in team_points:
            team_points[team] = points
            
    return team_points

# Run the secure data retrieval
live_scores = get_live_scores()

# ==========================================
# 3. CALCULATE LEADERBOARD STANDINGS
# ==========================================
standings = {}
for player, teams in draft_data.items():
    total_score = 0
    for team in teams:
        # Convert drafted team name to lowercase to safely match live_scores keys
        lowercase_team = team.strip().lower()
        total_score += live_scores.get(lowercase_team, 0)
    standings[player] = total_score

# Sort leaderboard descending (highest points first)
sorted_standings = sorted(standings.items(), key=lambda x: x[1], reverse=True)

# ==========================================
# 4. DISPLAY THE VISUAL WEB LEADERBOARD
# ==========================================
st.header("🏆 Current Standings")
for rank, (player, points) in enumerate(sorted_standings, start=1):
    # Highlight the leader with a gold medal
    medal = "🥇" if rank == 1 else "🔹"
    st.subheader(f"{medal} Rank {rank}: {player} — {points} pts")
    
    # Show the teams owned by this player and their individual points safely
    teams_list = []
    for t in draft_data[player]:
        t_pts = live_scores.get(t.strip().lower(), 0)
        teams_list.append(f"{t} ({t_pts}pts)")
        
    teams_str = ", ".join(teams_list)
    st.caption(f"Drafted Teams: {teams_str}")
    st.markdown("---")

st.info("🔄 Refresh the page anytime to fetch live point updates. Scoring: Win = 3pts, Draw = 1pt.")
