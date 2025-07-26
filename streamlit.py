import streamlit as st
from scrape_odds import scrape_odds

st.set_page_config(page_title="MLB FanDuel Odds", layout="wide")
st.title("MLB FanDuel Odds")

@st.cache_data(show_spinner=True)
def get_data():
    return scrape_odds()

st.info("Fetching latest MLB odds from FanDuel. This may take a few seconds...")

df = get_data()

if df.empty:
    st.warning("No data available. Please try again later.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filter Games")
dates = df['date'].dropna().unique()
selected_date = st.sidebar.selectbox("Select Date", sorted(dates))

teams = sorted(set(df['home_team_full'].dropna().unique()) | set(df['away_team_full'].dropna().unique()))
selected_team = st.sidebar.selectbox("Filter by Team (optional)", ["All"] + teams)

# Filter dataframe
filtered_df = df[df['date'] == selected_date]
if selected_team != "All":
    filtered_df = filtered_df[
        (filtered_df['home_team_full'] == selected_team) | (filtered_df['away_team_full'] == selected_team)
    ]

# Main table
st.subheader(f"Games for {selected_date}")
if filtered_df.empty:
    st.info("No games found for the selected filters.")
else:
    st.dataframe(filtered_df, use_container_width=True)

    # Expanders for details
    for idx, row in filtered_df.iterrows():
        with st.expander(f"{row['away_team_full']} @ {row['home_team_full']} ({row['start_date']})"):
            st.write(f"**Venue:** {row['venue']} ({row['venue_city']}, {row['venue_state']})")
            st.write(f"**Score:** {row['away_team_full']} {row['score_away']} - {row['home_team_full']} {row['score_home']}")
            st.write("**Consensus:**", row['consensus'])
            st.write("**Last Line Update:**", row['last_line_update'])

            st.markdown("#### Moneyline")
            st.write(f"Opening: {row['ml_opening_away']} / {row['ml_opening_home']} (Time: {row['ml_opening_time']})")
            st.write(f"Current: {row['ml_current_away']} / {row['ml_current_home']} (Time: {row['ml_current_time']})")

            st.markdown("#### Run Line")
            st.write(f"Opening: Away {row['rl_opening_away_spread']} ({row['rl_opening_away_odds']}), Home {row['rl_opening_home_spread']} ({row['rl_opening_home_odds']}) (Time: {row['rl_opening_time']})")
            st.write(f"Current: Away {row['rl_current_away_spread']} ({row['rl_current_away_odds']}), Home {row['rl_current_home_spread']} ({row['rl_current_home_odds']}) (Time: {row['rl_current_time']})")

            st.markdown("#### Total")
            st.write(f"Opening: {row['total_opening_line']} (Over {row['total_opening_over_odds']}, Under {row['total_opening_under_odds']}) (Time: {row['total_opening_time']})")
            st.write(f"Current: {row['total_current_line']} (Over {row['total_current_over_odds']}, Under {row['total_current_under_odds']}) (Time: {row['total_current_time']})")
