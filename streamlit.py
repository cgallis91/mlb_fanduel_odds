def format_team_nickname(nickname, full):
    # Handle Athletics Athletics
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
        return f"{prefix} {dt.strftime('%-I:%M%p EST').lower().replace('est', 'EST')}"
    except Exception:
        return dt_str

# ...existing code...

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
                away_nick = format_team_nickname(row['away_team_nickname'], row['away_team_full'])
                home_nick = format_team_nickname(row['home_team_nickname'], row['home_team_full'])
                away_full = format_team_nickname(row['away_team_full'], row['away_team_full'])
                home_full = format_team_nickname(row['home_team_full'], row['home_team_full'])
                venue = row['venue']
                city = row['venue_city']
                state = row['venue_state']
                # Format start time in ET
                try:
                    dt_et = pd.to_datetime(row['start_date']).tz_convert('US/Eastern')
                    start_time_str = dt_et.strftime('%-I:%M %p EST')
                except Exception:
                    start_time_str = row['start_date']

                st.markdown(
                    f"""
                    <div style="border:1.5px solid #888; border-radius:10px; margin-bottom:1.5em; background-color:#FAFAFA; box-shadow:0 2px 8px #EEE;">
                        <div style="padding:1em 1em 0.5em 1em;">
                            <div style="font-size:1.2em; font-weight:600;">{away_full} at {home_full}</div>
                            <div style="color:#555; font-size:0.95em; margin-bottom:0.5em;">
                                {start_time_str} | {venue} | {city}, {state}
                            </div>
                            <table style="width:100%; border-collapse:collapse; margin-bottom:0.5em;">
                                <tr style="background-color:#f0f2f6;">
                                    <th rowspan="2" style="text-align:center; padding:6px 8px; border: 2px solid #888; border-bottom: none;">Team</th>
                                    <th colspan="2" style="text-align:center; padding:6px 8px; border-top: 2px solid #888; border-bottom: none; border-right: 2px solid #888; border-left: 2px solid #888;">Money Line</th>
                                    <th colspan="2" style="text-align:center; padding:6px 8px; border-top: 2px solid #888; border-bottom: none; border-right: 2px solid #888;">Run Line</th>
                                    <th colspan="2" style="text-align:center; padding:6px 8px; border-top: 2px solid #888; border-bottom: none;">Total</th>
                                </tr>
                                <tr style="background-color:#f0f2f6;">
                                    <th style="text-align:center; padding:4px 8px; border-bottom: 1px solid #EEE; border-right: 1px solid #EEE;">Open</th>
                                    <th style="text-align:center; padding:4px 8px; border-bottom: 1px solid #EEE; border-right: 2px solid #888;">Current</th>
                                    <th style="text-align:center; padding:4px 8px; border-bottom: 1px solid #EEE; border-right: 1px solid #EEE;">Open</th>
                                    <th style="text-align:center; padding:4px 8px; border-bottom: 1px solid #EEE; border-right: 2px solid #888;">Current</th>
                                    <th style="text-align:center; padding:4px 8px; border-bottom: 1px solid #EEE; border-right: 1px solid #EEE;">Open</th>
                                    <th style="text-align:center; padding:4px 8px; border-bottom: 1px solid #EEE;">Current</th>
                                </tr>
                                <tr>
                                    <td style="text-align:center; padding:4px 8px; border-top: 2px solid #888; border-left: 2px solid #888;">{away_nick}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 1px solid #EEE;">{format_odds(row['ml_opening_away'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 2px solid #888;">{format_odds(row['ml_current_away'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 1px solid #EEE;">{format_run_line(row['rl_opening_away_spread'], row['rl_opening_away_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 2px solid #888;">{format_run_line(row['rl_current_away_spread'], row['rl_current_away_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 1px solid #EEE;">{format_total_line("Over", row['total_opening_line'], row['total_opening_over_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 2px solid #888;">{format_total_line("Over", row['total_current_line'], row['total_current_over_odds'])}</td>
                                </tr>
                                <tr style="background-color:#f8f8fa;">
                                    <td style="text-align:center; padding:4px 8px; border-left: 2px solid #888; border-bottom: 2px solid #888;">{home_nick}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 1px solid #EEE;">{format_odds(row['ml_opening_home'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 2px solid #888;">{format_odds(row['ml_current_home'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 1px solid #EEE;">{format_run_line(row['rl_opening_home_spread'], row['rl_opening_home_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 2px solid #888;">{format_run_line(row['rl_current_home_spread'], row['rl_current_home_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 1px solid #EEE;">{format_total_line("Under", row['total_opening_line'], row['total_opening_under_odds'])}</td>
                                    <td style="text-align:center; padding:4px 8px; border-right: 2px solid #888; border-bottom: 2px solid #888;">{format_total_line("Under", row['total_current_line'], row['total_current_under_odds'])}</td>
                                </tr>
                            </table>
                            <div style="font-size:0.85em; color:#888; margin-top:0.5em;">
                                Open: {format_time_footer(row['ml_opening_time'])} &nbsp;|&nbsp; Current Update: {format_time_footer(row['last_line_update'])}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
