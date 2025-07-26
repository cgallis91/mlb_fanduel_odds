import streamlit as st
from scrape_odds import scrape_odds
import pandas as pd
from datetime import datetime, timedelta
import pytz
import re

st.set_page_config(page_title="MLB FanDuel Odds Tracker", layout="wide")

# --- Modern CSS Styling & Responsive Table ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@500;700&display=swap');
    body, .main, .block-container { font-family: 'Inter', sans-serif !important; }
    .page-header {
        background: linear-gradient(90deg, #1a365d 0%, #2176ae 100%);
        color: #fff;
        border-radius: 18px;
        padding: 2.2em 2em 1.2em 2em;
        margin-bottom: 2.5em;
        box-shadow: 0 4px 24px #c3d0e6;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .page-header h1 {
        font-size: 2.6em;
        font-weight: 800;
        letter-spacing: 0.03em;
        margin-bottom: 0.15em;
        color: #fff;
        text-shadow: 0 2px 8px #1a365d33;
    }
    .page-header h2 {
        font-size: 1.25em;
        font-weight: 500;
        color: #e3ecf7;
        margin-bottom: 0;
        letter-spacing: 0.01em;
    }
    .odds-card {
        border-radius: 14px;
        box-shadow: 0 2px 12px #e0e7ef;
        border: 1.5px solid #d1d5db;
        background: #fff;
        margin-bottom: 2em;
        transition: box-shadow 0.2s, border-color 0.2s;
        font-family: 'Inter', sans-serif;
    }
    .odds-card:hover {
        box-shadow: 0 6px 24px #b3c6e0;
        border-color: #2176ae;
    }
    .odds-header-main {
        font-size: 1.55em;
        font-weight: 800;
        color: #1a365d;
        margin-bottom: 0.12em;
        letter-spacing: 0.01em;
    }
    .odds-header-sub {
        font-size: 1.13em;
        font-weight: 500;
        color: #3a506b;
        margin-bottom: 0.7em;
    }
    .status-badge {
        display: inline-block;
        padding: 2px 14px;
        border-radius: 12px;
        font-size: 0.97em;
        font-weight: 600;
        letter-spacing: 0.01em;
        margin-right: 0.7em;
        background: #e5e7eb;
        color: #444;
    }
    .status-badge.final { background: #e6f9ea; color: #1b7f3a; }
    .status-badge.progress { background: #e7f0fa; color: #2176ae; }
    .status-badge.notstarted { background: #f3f4f6; color: #888; }
    .odds-table {
        background: #fff;
        border-radius: 10px;
        box-shadow: 0 1px 4px #f0f2f6;
        overflow: hidden;
        margin-bottom: 0.5em;
        width: 100%;
        min-width: 650px;
        table-layout: fixed;
        font-size: 1em;
    }
    .odds-table th {
        background: #f0f4fa;
        font-weight: 700;
        color: #1a365d;
        border-bottom: 2px solid #e5e7eb;
        padding: 8px 8px;
    }
    .odds-table td {
        padding: 7px 8px;
        border-bottom: 1px solid #f3f4f6;
        font-size: 1em;
    }
    .odds-table tr:last-child td {
        border-bottom: none;
    }
    .odds-table tr:nth-child(even) td {
        background: #f8fafc;
    }
    @media (max-width: 900px) {
        .odds-table, .odds-table thead, .odds-table tbody, .odds-table tr, .odds-table th, .odds-table td {
            display: block;
        }
        .odds-table th, .odds-table td {
            width: 100% !important;
            box-sizing: border-box;
        }
        .odds-table tr {
            margin-bottom: 1em;
        }
        .odds-table thead {
            display: none;
        }
    }
    /* Blue tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #e3ecf7;
        border-radius: 10px 10px 0 0;
        padding: 0.2em 0.2em 0 0.2em;
    }
    .stTabs [data-baseweb="tab"] {
        color: #2176ae !important;
        font-weight: 600;
        font-size: 1.08em;
        border-radius: 8px 8px 0 0;
        margin-right: 0.2em;
        background: #e3ecf7 !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: #2176ae !important;
        color: #fff !important;
    }
    /* Blue update button */
    .stButton > button {
        background: linear-gradient(90deg, #2176ae 0%, #1a365d 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 1.1em !important;
        padding: 0.5em 2em !important;
        margin-bottom: 1.5em !important;
        box-shadow: 0 2px 8px #e3ecf7;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #1a365d 0%, #2176ae 100%) !important;
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Impressive Page Header ---
st.markdown(
    """
    <div class="page-header">
        <h1>MLB FanDuel Odds Tracker</h1>
        <h2>Opening and Current FanDuel Lines and Odds for MLB Games</h2>
    </div>
    """,
    unsafe_allow_html=True
)

@st.cache_data(show_spinner=True)
def get_data():
    return scrape_odds()

if st.button("Update Data", type="primary"):
    st.cache_data.clear()
    st.rerun()

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

def format_odds(val, highlight=False):
    if val is None or pd.isna(val):
        return "-"
    val = int(val) if float(val).is_integer() else val
    if isinstance(val, (int, float)):
        if val > 0:
            val_str = f"+{val}"
        else:
            val_str = f"{val}"
    else:
        val_str = str(val)
    # Remove highlight logic
    return val_str

def format_line(val):
    if val is None or pd.isna(val):
        return "-"
    val = float(val)
    if val.is_integer():
        return str(int(val))
    return str(val)

def format_run_line(spread, odds, highlight=False):
    if spread is None or pd.isna(spread) or odds is None or pd.isna(odds):
        return "-"
    odds_str = format_odds(odds)
    return f"{format_line(spread)} ({odds_str})"

def format_total_line(overunder, line, odds, highlight=False):
    if line is None or pd.isna(line) or odds is None or pd.isna(odds):
        return "-"
    odds_str = format_odds(odds)
    return f"{overunder} {format_line(line)} ({odds_str})"

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

def is_time_status(status_text):
    # Matches times like '18:10 ET', '7:05 PM EST', '12:30 PM', etc.
    return bool(re.match(r"^\d{1,2}:\d{2}(\s*[AP]M)?(\s*ET|EST)?$", status_text.strip(), re.IGNORECASE))

def format_display_time(dt_str):
    # Always display as 12-hour time with AM/PM and EST
    try:
        dt = pd.to_datetime(dt_str).tz_convert('US/Eastern')
        return dt.strftime("%-I:%M %p EST")
    except Exception:
        return dt_str

def get_status_badge(status_text):
    if is_time_status(status_text):
        return '<span class="status-badge notstarted">Not Started</span>'
    elif status_text.lower() == "final":
        return '<span class="status-badge final">Final</span>'
    else:
        return '<span class="status-badge progress">In Progress</span>'

tab1, tab2 = st.tabs(tab_labels)
tabs = [tab1, tab2]

# Standard column widths for all cards
col_widths = [
    "180px",  # Team
    "70px", "70px",  # Money Line
    "90px", "90px",  # Run Line
    "110px", "110px" # Total
]

for tab, date_str in zip(tabs, tab_dates):
    with tab:
        games = df[df['date'] == date_str].copy()
        if games.empty:
            st.info("No games found for this day.")
        else:
            games['start_time_et'] = games['start_date'].apply(format_display_time)
            games = games.sort_values('start_date')
            for _, row in games.iterrows():
                away_nick = format_team_nickname(row['away_team_nickname'], row['away_team_full'])
                home_nick = format_team_nickname(row['home_team_nickname'], row['home_team_full'])
                away_full = format_team_nickname(row['away_team_full'], row['away_team_full'])
                home_full = format_team_nickname(row['home_team_full'], row['home_team_full'])
                venue = row['venue']
                city = row['venue_city']
                state = row['venue_state']

                status_text = str(row.get('game_status_text', "")).strip()
                score_home = row.get('score_home', None)
                score_away = row.get('score_away', None)

                # --- LOGIC: Only use status_text ---
                if is_time_status(status_text):
                    has_started = False
                    is_final = False
                elif status_text.lower() == "final":
                    has_started = True
                    is_final = True
                else:
                    has_started = True
                    is_final = False

                status_badge = get_status_badge(status_text)

                # Header: show status if started, else show time
                header_time_or_status = status_text if has_started and status_text else row['start_time_et']

                # Table "Current" -> "Close" if started/final
                current_label = "Close" if has_started else "Current"

                # Team column: add score if started, else blank, right-aligned in fixed-width box
                score_box_style = "display:inline-block; min-width:2.5em; text-align:right; margin-left:1em; color:#2176ae; font-weight:600;"
                away_score_html = f"<span style='{score_box_style}'>{score_away}</span>" if has_started and score_away is not None else "<span style='min-width:2.5em; display:inline-block;'></span>"
                home_score_html = f"<span style='{score_box_style}'>{score_home}</span>" if has_started and score_home is not None else "<span style='min-width:2.5em; display:inline-block;'></span>"

                # Footer: "Current Update" -> "Close" if started/final
                footer_update_label = "Close" if has_started else "Current Update"

                st.markdown(
                    f"""
                    <div class="odds-card">
                        <div style="padding:1.3em 1.3em 0.8em 1.3em;">
                            <div class="odds-header-main">{away_full} at {home_full}</div>
                            <div class="odds-header-sub">
                                {status_badge}
                                <span>{header_time_or_status}</span>
                                &nbsp;|&nbsp; {venue} | {city}, {state}
                            </div>
                            <div style="overflow-x:auto;">
                            <table class="odds-table">
                                <colgroup>
                                    <col style="width:{col_widths[0]};" />
                                    <col style="width:{col_widths[1]};" />
                                    <col style="width:{col_widths[2]};" />
                                    <col style="width:{col_widths[3]};" />
                                    <col style="width:{col_widths[4]};" />
                                    <col style="width:{col_widths[5]};" />
                                    <col style="width:{col_widths[6]};" />
                                </colgroup>
                                <tr>
                                    <th rowspan="2" style="text-align:center;">Team</th>
                                    <th colspan="2" style="text-align:center;">Money Line</th>
                                    <th colspan="2" style="text-align:center;">Run Line</th>
                                    <th colspan="2" style="text-align:center;">Total</th>
                                </tr>
                                <tr>
                                    <th style="text-align:center;">Open</th>
                                    <th style="text-align:center;">{current_label}</th>
                                    <th style="text-align:center;">Open</th>
                                    <th style="text-align:center;">{current_label}</th>
                                    <th style="text-align:center;">Open</th>
                                    <th style="text-align:center;">{current_label}</th>
                                </tr>
                                <tr>
                                    <td style="text-align:left; white-space:nowrap;">
                                        <span style="display:flex; justify-content:space-between; align-items:center;">
                                            <span>{away_nick}</span>
                                            {away_score_html}
                                        </span>
                                    </td>
                                    <td style="text-align:center;">{format_odds(row['ml_opening_away'])}</td>
                                    <td style="text-align:center;">{format_odds(row['ml_current_away'])}</td>
                                    <td style="text-align:center;">{format_run_line(row['rl_opening_away_spread'], row['rl_opening_away_odds'])}</td>
                                    <td style="text-align:center;">{format_run_line(row['rl_current_away_spread'], row['rl_current_away_odds'])}</td>
                                    <td style="text-align:center;">{format_total_line("Over", row['total_opening_line'], row['total_opening_over_odds'])}</td>
                                    <td style="text-align:center;">{format_total_line("Over", row['total_current_line'], row['total_current_over_odds'])}</td>
                                </tr>
                                <tr>
                                    <td style="text-align:left; white-space:nowrap;">
                                        <span style="display:flex; justify-content:space-between; align-items:center;">
                                            <span>{home_nick}</span>
                                            {home_score_html}
                                        </span>
                                    </td>
                                    <td style="text-align:center;">{format_odds(row['ml_opening_home'])}</td>
                                    <td style="text-align:center;">{format_odds(row['ml_current_home'])}</td>
                                    <td style="text-align:center;">{format_run_line(row['rl_opening_home_spread'], row['rl_opening_home_odds'])}</td>
                                    <td style="text-align:center;">{format_run_line(row['rl_current_home_spread'], row['rl_current_home_odds'])}</td>
                                    <td style="text-align:center;">{format_total_line("Under", row['total_opening_line'], row['total_opening_under_odds'])}</td>
                                    <td style="text-align:center;">{format_total_line("Under", row['total_current_line'], row['total_current_under_odds'])}</td>
                                </tr>
                            </table>
                            </div>
                            <div style="font-size:0.92em; color:#888; margin-top:0.7em;">
                                Open: {format_time_footer(row['ml_opening_time'])} &nbsp;|&nbsp; {footer_update_label}: {format_time_footer(row['last_line_update'])}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
