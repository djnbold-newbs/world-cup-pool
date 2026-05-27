import streamlit as st
import requests

st.set_page_config(page_title="World Cup Pool", page_icon="⚽", layout="centered")

st.title("⚽ World Cup Snake Draft Pool")
st.write("Welcome to our 5-friend live tournament tracker!")

# 1. Define Friends and Draft Assignments
# Edit these country lists right here in GitHub after your live draft night!
draft_data = {
    "Josh": ["Brazil", "USA", "Japan"],
    "Aaron": ["Argentina", "Canada", "Morocco"],
    "Alex": ["France", "Mexico", "Switzerland"],
    "Dan": ["England", "Croatia", "South Korea"],
    "Chris": ["Spain", "Germany", "South Africa"]
}

# 2. Fetch Tournament Match Data
DATA_URL = "https://raw.githubusercontent.com/openfootball/world-cup.json/master/2026/worldcup.json"

@st.cache_data(ttl=600) # Caches data for 10 minutes to save bandwidth
def get_live_scores():
    team_points = {}
    try:
        response = requests.get(DATA_URL)
        if response.status_code == 200:
            data = response.json()
            for round_data in data.get('rounds', []):
                for match in round_data.get('matches', []):
                    # Check if match has concluded
                    if match.get('score1') is not None and match.get('score2') is not None:
                        t1 = match['team1']['name'].strip()
                        t2 = match['team2']['name'].strip()
                        s1 = int(match['score1'])
                        s2 = int(match['score2'])
                        
                        team_points[t1] = team_points.get(t1, 0)
                        team_points[t2] = team_points.get(t2, 0)
                        
                        if s1 > s2:
                            team_points[t1] += 3
                        elif s2 > s1:
                            team_points[t2] += 3
                        else:
                            team_points[t1] += 1
                            team_points[t2] += 1
            return team_points
    except Exception:
        pass
    
    # Fallback pre-tournament mock scores
    return {"Brazil": 9, "Argentina": 9, "Spain": 7, "Mexico": 7, "France": 6, "England": 5, "USA": 4, "Canada": 3}

live_scores = get_live_scores()

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
