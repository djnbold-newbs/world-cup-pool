import streamlit as st
import requests

st.set_page_config(page_title="World Cup Pool", page_icon="⚽", layout="centered")

st.title("⚽ NT's World Cup Pool")
st.write("Live-syncing directly with official tournament match scores!")

# ==========================================
# 1. DEFINE FRIENDS & DRAFT ASSIGNMENTS
# ==========================================
draft_data = {
    "Josh": ["Spain", "Colombia", "Norway", "Turkey", "Sweden", "Iran"],
    "Aaron": ["Brazil", "USA", "Japan", "Ecuador", "Senegal", "Ghana"],
    "Alex": ["France", "Germany", "Belgium", "Switzerland", "Austria", "Scotland"],
    "Dan": ["England", "Netherlands", "Mexico", "Morocco", "Canada", "Ivory Coast"],
    "Chris": ["Argentina", "Portugal", "Uruguay", "Croatia", "Czechia", "South Korea"]
}

# ==========================================
# 2. LIVE REFRESH DATA ENGINE
# ==========================================
API_TOKEN = "46364d6dcc9541a6b46495cc30f3c3c6"
MATCHES_URL = "https://api.football-data.org/v4/competitions/WC/matches"

@st.cache_data(ttl=30) # Refresh the server feed every 30 seconds
def get_official_scores():
    team_points = {}
    headers = { "X-Auth-Token": API_TOKEN }
    
    try:
        response = requests.get(MATCHES_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            for match in data.get('matches', []):
                status = match.get('status')
                
                # Check if the game is currently live or has ended
                if status in ['FINISHED', 'IN_PLAY', 'PAUSED']:
                    # Store names in clean lowercase keys to guarantee an exact match
                    home_team = match['homeTeam']['name'].strip().lower()
                    away_team = match['awayTeam']['name'].strip().lower()
                    
                    if home_team not in team_points: team_points[home_team] = 0
                    if away_team not in team_points: team_points[away_team] = 0
                    
                    winner = match.get('score', {}).get('winner')
                    
                    if winner == 'HOME_TEAM':
                        team_points[home_team] += 3
                    elif winner == 'AWAY_TEAM':
                        team_points[away_team] += 3
                    elif winner == 'DRAW':
                        team_points[home_team] += 1
                        team_points[away_team] += 1
            return team_points
        else:
            st.sidebar.error(f"API Error: Status {response.status_code}.")
    except Exception as e:
        st.sidebar.error(f"Connection Exception: {str(e)}")
        
    return team_points

# Pull calculated points dictionary (All lowercase keys)
live_scores = get_official_scores()

# ==========================================
# 3. CALCULATE LEADERBOARD STANDINGS
# ==========================================
standings = {}
for player, teams in draft_data.items():
    total_score = 0
    for team in teams:
        norm_team = team.strip().lower()
        
        # Intercept variations and map to the EXACT lowercase key in live_scores
        if norm_team in ["usa", "united states"]: 
            norm_team = "united states"
        if norm_team in ["south korea", "korea republic", "korea", "south korea republic", "s.korea", "republic of korea"]: 
            norm_team = "south korea"
            
        total_score += live_scores.get(norm_team, 0)
    standings[player] = total_score

sorted_standings = sorted(standings.items(), key=lambda x: x[1], reverse=True)

# ==========================================
# 4. DISPLAY THE VISUAL WEB LEADERBOARD
# ==========================================
st.header("🏆 Live Leaderboard")
for rank, (player, points) in enumerate(sorted_standings, start=1):
    medal = "🥇" if rank == 1 else "🔹"
    st.subheader(f"{medal} Rank {rank}: {player} — {points} pts")
    
    teams_list = []
    for t in draft_data[player]:
        norm_t = t.strip().lower()
        
        if norm_t in ["usa", "united states"]: 
            norm_t = "united states"
        if norm_t in ["south korea", "korea republic", "korea", "south korea republic", "s.korea", "republic of korea"]: 
            norm_t = "south korea"
            
        t_pts = live_scores.get(norm_t, 0)
        teams_list.append(f"{t} ({t_pts}pts)")
        
    teams_str = ", ".join(teams_list)
    st.caption(f"Drafted Teams: {teams_str}")
    st.markdown("---")

st.info("⚡ Live Connection Active. Data updates from the stadium every 30 seconds upon page interaction.")
