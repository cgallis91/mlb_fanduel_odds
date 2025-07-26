import streamlit as st
from scrape_odds import scrape_odds
import pandas as pd
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="MLB FanDuel Odds Tracker", layout="wide")
st.title("MLB FanDuel Odds Tracker")

# --- Data Handling ---
@st.cache_data(show_spinner=True)
def get_data():
    return scrape_odds()

# Update Data Button
if st.button("Update Data", type="primary"):
    st.cache_data.clear()
    st.experimental_rerun()

# Fetch data
df = get_data()

if df.empty:
    st.warning("No data available. Please try again later.")
    st.stop()

# --- Date Handling for Tabs ---
et = pytz.timezone("US/Eastern")
now_et = datetime.now(et)
today = now_et.date()
tomorrow = today + timedelta(days=1)
tab_labels = [
    f"Today - {today.strftime('%A %B %d')}",
    f"Tomorrow - {tomorrow.strftime('%A %B %d')}"
]
tab_dates = [today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d")]

tab1, tab2 = st.tabs(tab_labels)
tabs = [tab1, tab2]

for tab, date_str in zip(tabs, tab_dates):
    with tab:
        games = df[df['date'] == date_str].copy()
        if games.empty:
            st.info("No games found for this day.")
        else:
            # Sort by start time (Eastern)
            games['start_time_et'] = pd.to_datetime(games['start_date']).dt.tz_convert('US/Eastern').dt.strftime('%I:%M %p')
            games = games.sort_values('start_date')
            for _, row in games.iterrows():
                away = row['away_team_full']
                home = row['home_team_full']
                venue = row['venue']
                city = row['venue_city']
                state = row['venue_state']
                # Format start time in ET
                try:
                    dt_et = pd.to_datetime(row['start_date']).tz_convert('US/Eastern')
                    start_time_str = dt_et.strftime('%-I:%M %p EST')
                except Exception:
                    start_time_str = row['start_date']

                # Card Header
                st.markdown(
                    f"""
                    <div style="border:1px solid #DDD; border-radius:10px; margin-bottom:1.5em; background-color:#FAFAFA; box-shadow:0 2px 8px #EEE;">
                        <div style="padding:1em 1em 0.5em 1em;">
                            <div style="font-size:1.2em; font-weight:600;">{away} at {home}</div>
                            <div style="color:#555; font-size:0.95em; margin-bottom:0.5em;">
                                {start_time_str} | {venue} | {city}, {state}
                            </div>
                            <table style="width:100%; border-collapse:collapse; margin-bottom:0.5em;">
                                <tr style="background-color:#f0f2f6;">
                                    <th rowspan="2" style="text-align:left; padding:6px 8px;">Team</th>
                                    <th colspan="2" style="padding:6px 8px;">Money Line</th>
                                    <th colspan="2" style="padding:6px 8px;">Run Line</th>
                                    <th colspan="2" style="padding:6px 8px;">Total</th>
                                </tr>
                                <tr style="background-color:#f0f2f6;">
                                    <th style="padding:4px 8px;">Open</th>
                                    <th style="padding:4px 8px;">Current</th>
                                    <th style="padding:4px 8px;">Open</th>
                                    <th style="padding:4px 8px;">Current</th>
                                    <th style="padding:4px 8px;">Open</th>
                                    <th style="padding:4px 8px;">Current</th>
                                </tr>
                                <tr>
                                    <td style="padding:4px 8px;">{away}</td>
                                    <td style="padding:4px 8px;">{row['ml_opening_away'] or ''}</td>
                                    <td style="padding:4px 8px;">{row['ml_current_away'] or ''}</td>
                                    <td style="padding:4px 8px;">{row['rl_opening_away_spread'] if row['rl_opening_away_spread'] is not None else ''} {f'({row['rl_opening_away_odds']})' if row['rl_opening_away_odds'] is not None else ''}</td>
                                    <td style="padding:4px 8px;">{row['rl_current_away_spread'] if row['rl_current_away_spread'] is not None else ''} {f'({row['rl_current_away_odds']})' if row['rl_current_away_odds'] is not None else ''}</td>
                                    <td style="padding:4px 8px;">{"Over " + str(row['total_opening_line']) if row['total_opening_line'] is not None else ''} {f'({row["total_opening_over_odds"]})' if row["total_opening_over_odds"] is not None else ''}</td>
                                    <td style="padding:4px 8px;">{"Over " + str(row['total_current_line']) if row['total_current_line'] is not None else ''} {f'({row["total_current_over_odds"]})' if row["total_current_over_odds"] is not None else ''}</td>
                                </tr>
                                <tr style="background-color:#f8f8fa;">
                                    <td style="padding:4px 8px;">{home}</td>
                                    <td style="padding:4px 8px;">{row['ml_opening_home'] or ''}</td>
                                    <td style="padding:4px 8px;">{row['ml_current_home'] or ''}</td>
                                    <td style="padding:4px 8px;">{row['rl_opening_home_spread'] if row['rl_opening_home_spread'] is not None else ''} {f'({row['rl_opening_home_odds']})' if row['rl_opening_home_odds'] is not None else ''}</td>
                                    <td style="padding:4px 8px;">{row['rl_current_home_spread'] if row['rl_current_home_spread'] is not None else ''} {f'({row['rl_current_home_odds']})' if row['rl_current_home_odds'] is not None else ''}</td>
                                    <td style="padding:4px 8px;">{"Under " + str(row['total_opening_line']) if row['total_opening_line'] is not None else ''} {f'({row["total_opening_under_odds"]})' if row["total_opening_under_odds"] is not None else ''}</td>
                                    <td style="padding:4px 8px;">{"Under " + str(row['total_current_line']) if row['total_current_line'] is not None else ''} {f'({row["total_current_under_odds"]})' if row["total_current_under_odds"] is not None else ''}</td>
                                </tr>
                            </table>
                            <div style="font-size:0.85em; color:#888; margin-top:0.5em;">
                                Open: {row['ml_opening_time'] or ''} EST &nbsp;|&nbsp; Last Update: {row['last_line_update'] or ''} EST
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
