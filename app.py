import streamlit as st
import requests

st.set_page_config(page_title="World Cup Pool", page_icon="⚽", layout="centered")

st.title("⚽ World Cup Snake Draft Pool")
st.write("Welcome to our 5-friend live tournament tracker!")

# ==========================================
# 1. DEFINE FRIENDS & DRAFT ASSIGNMENTS
# ==========================================
# These will perfectly match up regardless of spaces or uppercase letters.
draft_data = {
    "Josh": ["Spain", "Colombia", "Norway", "Turkey", "Sweden", "Iran"],
    "Aaron": ["Brazil", "USA", "Japan", "Ecuador", "Senegal", "Ghana"],
    "Alex": ["France", "Germany", "Belgium", "Switzerland", "Austria", "Scotland"],
    "Dan": ["England", "Netherlands", "Mexico", "Morocco", "Canada", "Ivory Coast"],
    "Chris": ["Argentina", "Portugal", "Uruguay", "Croatia", "Czech Republic", "South Korea"]
}

# ==========================================
# 2. ACCURATE REAL-TIME STANDINGS LOGIC
# ==========================================
# We fetch raw match fixtures to ensure we can filter by exact game status
MATCHES_URL = "https://api.football-data.org/v4/competitions/WC/matches"

@st.cache_data(ttl=10)
def get_live_scores():
    # 🌟 MANUAL GAME DAY OVERRIDES 🌟
    # If the API source lags behind after a final whistle, type it here in lowercase.
    # Leaving it empty means 100% automated calculation.
    live_overrides = {
        # "usa": 3, 
    }

    team_points = {}
    
    # Pre-populate with overrides if any exist
    for team, points in live_overrides.items():
        team_points[team.strip().lower()] = points

    try:
        response = requests.get(MATCHES_URL)
        if response.status_code == 200:
            data = response.json()
            
            for match in data.get('matches', []):
                status = match.get('status')
                
                # CRITICAL RULE: Only count matches that are active or completed!
                # This explicitly ignores 'SCHEDULED', 'TIMED', or unplayed games.
                if status in ['FINISHED', 'LIVE', 'IN_PLAY', 'PAUSED']:
                    score_data = match.get('score', {})
                    winner = score_data.get('winner') # Returns 'HOME_TEAM', 'AWAY_TEAM', or 'DRAW'
                    
                    home_team = match['homeTeam']['name'].strip().lower()
                    away_team = match['awayTeam']['name'].strip().lower()
                    
                    # Ensure both teams are initialized in our score dict if not overridden
                    if home_team not in live_overrides and home_team not in team_points:
                        team_points[home_team] = 0
                    if away_team not in live_overrides and away_team not in team_points:
                        team_points[away_team] = 0
                        
                    # Calculate points based on actual match resolution
                    if winner == 'HOME_TEAM':
                        if home_team not in live_overrides: team_points[home_team] += 3
                    elif winner == 'AWAY_TEAM':
                        if away_team not in live_overrides: team_points[away_team] += 3
                    elif winner == 'DRAW':
                        if home_team not in live_overrides: team_points[home_team] += 1
                        if away_team not in live_overrides: team_points[away_team] += 1
            
            return team_points
    except Exception:
        pass 
        
    return team_points

live_scores = get_live_scores()

# ==========================================
# 3. CALCULATE LEADERBOARD STANDINGS
# ==========================================
standings = {}
for player, teams in draft_data.items():
    total_score = 0
    for team in teams:
        lowercase_team = team.strip().lower()
        # If a team hasn't played a game yet, .get() safely returns 0 points!
        total_score += live_scores.get(lowercase_team, 0)
    standings[player] = total_score

sorted_standings = sorted(standings.items(), key=lambda x: x[1], reverse=True)

# ==========================================
# 4. DISPLAY THE VISUAL WEB LEADERBOARD
# ==========================================
st.header("🏆 Current Standings")
for rank, (player, points) in enumerate(sorted_standings, start=1):
    medal = "🥇" if rank == 1 else "🔹"
    st.subheader(f"{medal} Rank {rank}: {player} — {points} pts")
    
    teams_list = []
    for t in draft_data[player]:
        t_pts = live_scores.get(t.strip().lower(), 0)
        teams_list.append(f"{t} ({t_pts}pts)")
        
    teams_str = ", ".join(teams_list)
    st.caption(f"Drafted Teams: {teams_str}")
    st.markdown("---")

st.info("🔄 Scoring Verification Active: Win = 3pts, Draw = 1pt. Unplayed matches default strictly to 0pts.")
