import streamlit as st
from scrape_odds import scrape_odds
import pandas as pd
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="MLB FanDuel Odds Tracker", layout="wide")
st.title("MLB FanDuel Odds Tracker")

@st.cache_data(show_spinner=True)
def get_data():
    return scrape_odds()

if st.button("Update Data", type="primary"):
    st.cache_data.clear()
    st.experimental_rerun()

df = get_data()

if df.empty:
    st.warning("No data available. Please try again later.")
    st.stop()

et = pytz.timezone("US/Eastern")
now_et = datetime.now(et)
today = now_et.date()
tomorrow = today + timedelta(days=1)
tab_labels = [
    f"Today - {today.strftime('%A %B %d')}",
    f"Tomorrow - {tomorrow.strftime('%A %B %d')}"
]
tab_dates = [today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d")]

def format_team_nickname(nickname, full):
    if full == "Athletics Athletics" or nickname == "Athletics Athletics":
        return "Athletics"
    return nickname

def format_odds(val):
    if val is None or pd.isna(val):
        return "-"
    val = int(val) if float(val).is_integer() else val
    if isinstance(val, (int, float)):
        if val > 0:
            return f"+{val}"
        return f"{val}"
    return str(val)

def format_line(val):
    if val is None or pd.isna(val):
        return "-"
    val = float(val)
    if val.is_integer():
        return str(int(val))
    return str(val)

def format_run_line(spread, odds):
    if spread is None or pd.isna(spread) or odds is None or pd.isna(odds):
        return "-"
    return f"{format_line(spread)} ({format_odds(odds)})"

def format_total_line(overunder, line, odds):
    if line is None or pd.isna(line) or odds is None or pd.isna(odds):
        return "-"
    return f"{overunder} {format_line(line)} ({format_odds(odds)})"

def format_time_footer(dt_str):
    if not dt_str or pd.isna(dt_str):
        return "-"
    try:
        dt = pd.to_datetime(dt_str).tz_convert('US/Eastern')
        now = datetime.now(et)
        date_only = dt.date()
        now_date = now.date()
        if date_only == now_date:
            prefix = "Today"
        elif date_only == now_date - timedelta(days=1):
            prefix = "Yesterday"
        else:
            prefix = dt.strftime("%A")
        return f"{prefix} {dt.strftime('%-I:%M%p EST').replace('est', 'EST')}"
    except Exception:
        return dt_str

tab1, tab2 = st.tabs(tab_labels)
tabs = [tab1, tab2]

for tab, date_str in zip(tabs, tab_dates):
    with tab:
        games = df[df['date'] == date_str].copy()
        if games.empty:
            st.info("No games found for this day.")
        else:
            games['start_time_et'] = pd.to_datetime(games['start_date']).dt.tz_convert('US/Eastern').dt.strftime('%-I:%M %p EST')
            games = games.sort_values('start_date')
            for _, row in games.iterrows():
                away_nick = format_team_nickname(row['away_team_nickname'], row['away_team_full'])
                home_nick = format_team_nickname(row['home_team_nickname'], row['home_team_full'])
                away_full = format_team_nickname(row['away_team_full'], row['away_team_full'])
                home_full = format_team_nickname(row['home_team_full'], row['home_team_full'])
                venue = row['venue']
                city = row['venue_city']
                state = row['venue_state']

                # --- LOGIC FOR STATUS, SCORES, HEADERS ---
                status = row['game_status_text'] if 'game_status_text' in row else ""
                score_home = row['score_home'] if 'score_home' in row else None
                score_away = row['score_away'] if 'score_away' in row else None

                is_final = isinstance(status, str) and status.lower().startswith("final")
                is_in_progress = isinstance(status, str) and not is_final and status and not status.lower().startswith("scheduled") and not status.lower().startswith("not started")
                has_started = is_final or is_in_progress

                # Header: show time if not started, else status text
                header_time_or_status = status if has_started and status else row['start_time_et']

                # Table "Current" -> "Close" if started
                current_label = "Close" if has_started else "Current"

                # Team column: add score if started, else blank
                away_score = f"<span style='color:#2176ae; font-weight:600;'>{score_away}</span>" if has_started and score_away is not None else "&nbsp;&nbsp;"
                home_score = f"<span style='color:#2176ae; font-weight:600;'>{score_home}</span>" if has_started and score_home is not None else "&nbsp;&nbsp;"

                # Footer: "Current Update" -> "Close" if started
                footer_update_label = "Close" if has_started else "Current Update"

                st.markdown(
                    f"""
                    <div style="border:1.5px solid #888; border-radius:10px; margin-bottom:1.5em; background-color:#FAFAFA; box-shadow:0 2px 8px #EEE;">
                        <div style="padding:1em 1em 0.5em 1em;">
                            <div style="font-size:1.2em; font-weight:600;">{away_full} at {home_full}</div>
                            <div style="color:#555; font-size:0.95em; margin-bottom:0.5em;">
                                {header_time_or_status} | {venue} | {city}, {state}
                            </div>
                            <table style="width:100%; border-collapse:collapse; margin-bottom:0.5em;">
                                <tr style="background-color:#f0f2f6;">
                                    <th rowspan="2" style="text-align:center; padding:6px 8px; border-left:2px solid #888; border-top:2px solid #888; border-bottom:none; min-width:120px;">Team</th>
                                    <th colspan="2" style="text-align:center; padding:6px 8px; border-left:2px solid #888; border-top:2px solid #888; border-bottom:none;">Money Line</th>
                                    <th colspan="2" style="text-align:center; padding:6px 8px; border-left:2px solid #888; border-top:2px solid #888; border-bottom:none;">Run Line</th>
                                    <th colspan="2" style="text-align:center; padding:6px 8px; border-left:2px solid #888; border-top:2px solid #888; border-right:2px solid #888; border-bottom:none;">Total</th>
                                </tr>
                                <tr style="background-color:#f0f2f6;">
                                    <th style="text-align:center; padding:4px 8px; border-bottom:none; border-left:2px solid #888;">Open</th>
                                    <th style="text-align:center; padding:4px 8px; border-bottom:none; border-left:1px solid #EEE;">{current_label}</th>
                                    <th style="text-align:center; padding:4px 8px; border-bottom:none; border-left:2px solid #888;">Open</th>
                                    <th style="text-align:center; padding:4px 8px; border-bottom:none; border-left:1px solid #EEE;">{current_label}</th>
                                    <th style="text-align:center; padding:4px 8px; border-bottom:none; border-left:2px solid #888;">Open</th>
                                    <th style="text-align:center; padding:4px 8px; border-bottom:none; border-left:1px solid #EEE; border-right:2px solid #888;">{current_label}</th>
                                </tr>
                                <tr>
                                    <td style="text-align:center; padding:4px 8px; border-top:none; border-left:2px solid #888;">{away_nick} {away_score}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:2px solid #888;">{format_odds(row['ml_opening_away'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:1px solid #EEE;">{format_odds(row['ml_current_away'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:2px solid #888;">{format_run_line(row['rl_opening_away_spread'], row['rl_opening_away_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:1px solid #EEE;">{format_run_line(row['rl_current_away_spread'], row['rl_current_away_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:2px solid #888;">{format_total_line("Over", row['total_opening_line'], row['total_opening_over_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:1px solid #EEE; border-right:2px solid #888;">{format_total_line("Over", row['total_current_line'], row['total_current_over_odds'])}</td>
                                </tr>
                                <tr style="background-color:#f8f8fa;">
                                    <td style="text-align:center; padding:4px 8px; border-left:2px solid #888; border-bottom:2px solid #888;">{home_nick} {home_score}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:2px solid #888; border-bottom:2px solid #888;">{format_odds(row['ml_opening_home'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:1px solid #EEE; border-bottom:2px solid #888;">{format_odds(row['ml_current_home'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:2px solid #888; border-bottom:2px solid #888;">{format_run_line(row['rl_opening_home_spread'], row['rl_opening_home_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:1px solid #EEE; border-bottom:2px solid #888;">{format_run_line(row['rl_current_home_spread'], row['rl_current_home_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:2px solid #888; border-bottom:2px solid #888;">{format_total_line("Under", row['total_opening_line'], row['total_opening_under_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-left:1px solid #EEE; border-right:2px solid #888; border-bottom:2px solid #888;">{format_total_line("Under", row['total_current_line'], row['total_current_under_odds'])}</td>
                                </tr>
                            </table>
                            <div style="font-size:0.85em; color:#888; margin-top:0.5em;">
                                Open: {format_time_footer(row['ml_opening_time'])} &nbsp;|&nbsp; {footer_update_label}: {format_time_footer(row['last_line_update'])}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
