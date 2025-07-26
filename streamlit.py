# ...inside your for _, row in games.iterrows(): loop...

status = row.get("game_status_text", "")
score_home = row.get("score_home")
score_away = row.get("score_away")
home_nick = format_team_nickname(row['home_team_nickname'], row['home_team_full'])
away_nick = format_team_nickname(row['away_team_nickname'], row['away_team_full'])

# Determine if game is final, in progress, or not started
is_final = status.lower().startswith("final")
is_in_progress = not is_final and status and not status.lower().startswith("scheduled") and not status.lower().startswith("not started")

score_str = ""
if is_final or is_in_progress:
    # Only show score if available
    if score_home is not None and score_away is not None:
        score_str = f"<div style='font-size:1.1em; font-weight:600; margin-bottom:0.5em;'>{away_nick} {score_away}, {home_nick} {score_home}</div>"

status_str = f"<div style='color:#2176ae; font-size:1em; margin-bottom:0.5em;'>{status}</div>" if status else ""

# For final games, you may want to gray out the odds table
odds_table_opacity = "0.5" if is_final else "1"

st.markdown(
    f"""
    <div style="border:1.5px solid #888; border-radius:10px; margin-bottom:1.5em; background-color:#FAFAFA; box-shadow:0 4px 16px #d0d6e1;">
        <div style="padding:1em 1em 0.5em 1em;">
            <div style="font-size:1.2em; font-weight:600;">{away_nick} at {home_nick}</div>
            <div style="color:#555; font-size:0.95em; margin-bottom:0.5em;">
                {row['start_time_et']} | {row['venue']} | {row['venue_city']}, {row['venue_state']}
            </div>
            {score_str}
            {status_str}
            <div style="opacity:{odds_table_opacity};">
                <!-- odds table here -->
            </div>
            <div style="font-size:0.85em; color:#888; margin-top:0.5em;">
                Open: {format_time_footer(row['ml_opening_time'])} &nbsp;|&nbsp; Current Update: {format_time_footer(row['last_line_update'])}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
