import requests
import re
import json
import pandas as pd
from datetime import datetime, timedelta
from pytz import timezone
import time
import random

def extract_team_info(team):
    return {
        "fullName": team.get("fullName", ""),
        "shortName": team.get("shortName", ""),
        "nickname": team.get("nickname", ""),
        "name": team.get("name", "")
    }

def get_first_last(history):
    if history and len(history) > 0:
        return history[0], history[-1]
    return {}, {}

def scrape_odds():
    session = requests.Session()
    session.headers.update({
        'Accept-Encoding': 'identity',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    })

    et = timezone('US/Eastern')
    now_et = datetime.now(et)
    today = now_et.strftime("%Y-%m-%d")
    tomorrow = (now_et + timedelta(days=1)).strftime("%Y-%m-%d")
    all_games = []

    for date_str in [today, tomorrow]:
        main_url = f"https://www.sportsbookreview.com/betting-odds/mlb-baseball/?date={date_str}"
        try:
            response = session.get(main_url, timeout=15)
            if response.status_code != 200:
                print(f"Failed to fetch {main_url}")
                continue

            pattern = r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>'
            match = re.search(pattern, response.text, re.DOTALL)
            if not match:
                print(f"No JSON found on {main_url}")
                continue

            json_data = json.loads(match.group(1))
            odds_tables = json_data['props']['pageProps'].get('oddsTables', [])
            if not odds_tables:
                print(f"No odds tables for {date_str}")
                continue
            odds_table_model = odds_tables[0]['oddsTableModel']
            game_rows = odds_table_model.get('gameRows', [])
            if not game_rows:
                print(f"No games for {date_str}")
                continue
        except Exception as e:
            print(f"Error loading main page for {date_str}: {e}")
            continue

        for game in game_rows:
            try:
                game_view = game.get('gameView', {})
                away_team = extract_team_info(game_view.get('awayTeam', {}))
                home_team = extract_team_info(game_view.get('homeTeam', {}))
                game_id = game_view.get('gameId')
                start_date = game_view.get('startDate', '')
                venue = game_view.get('venueName', '')
                venue_city = game_view.get('city', '')
                venue_state = game_view.get('state', '')
                consensus = game_view.get('consensus', {})

                # New: Extract game status and scores
                game_status_text = game_view.get('gameStatusText', '')
                score = {
                    "away": game_view.get("awayTeamScore"),
                    "home": game_view.get("homeTeamScore")
                }

                # Default: all odds fields None
                ml_opening = ml_current = {}
                spread_opening = spread_current = {}
                total_opening = total_current = {}
                last_line_update = None

                # Try to get FanDuel odds if available
                fanduel_data = None
                try:
                    if game_id:
                        line_history_url = f"https://www.sportsbookreview.com/betting-odds/mlb-baseball/line-history/{game_id}/"
                        time.sleep(random.uniform(0.2, 0.5))
                        line_response = session.get(line_history_url, timeout=10)
                        if line_response.status_code == 200:
                            line_match = re.search(pattern, line_response.text, re.DOTALL)
                            if line_match:
                                line_json = json.loads(line_match.group(1))
                                page_props = line_json['props']['pageProps']
                                line_history_model = page_props.get('lineHistoryModel', {})
                                odds_views = []
                                top_level_odds_views = line_history_model.get('oddsViews', [])
                                line_history = line_history_model.get('lineHistory', {})
                                line_history_odds_views = line_history.get('oddsViews', []) if line_history else []
                                if top_level_odds_views:
                                    odds_views = top_level_odds_views
                                elif line_history_odds_views:
                                    odds_views = line_history_odds_views
                                else:
                                    # Recursive search for oddsViews
                                    def find_odds_views_recursive(obj):
                                        if isinstance(obj, dict):
                                            if 'oddsViews' in obj and isinstance(obj['oddsViews'], list):
                                                return obj['oddsViews']
                                            for value in obj.values():
                                                found = find_odds_views_recursive(value)
                                                if found:
                                                    return found
                                        elif isinstance(obj, list):
                                            for item in obj:
                                                found = find_odds_views_recursive(item)
                                                if found:
                                                    return found
                                        return None
                                    found_odds_views = find_odds_views_recursive(line_json)
                                    if found_odds_views:
                                        odds_views = found_odds_views
                                for view in odds_views:
                                    if view.get('sportsbook', '').lower() == 'fanduel':
                                        fanduel_data = view
                                        break
                                if fanduel_data:
                                    ml_opening, ml_current = get_first_last(fanduel_data.get('moneyLineHistory', []))
                                    spread_opening, spread_current = get_first_last(fanduel_data.get('spreadHistory', []))
                                    total_opening, total_current = get_first_last(fanduel_data.get('totalHistory', []))
                                    odds_dates = [
                                        ml_current.get("oddsDate"),
                                        spread_current.get("oddsDate"),
                                        total_current.get("oddsDate")
                                    ]
                                    last_line_update = max([d for d in odds_dates if d], default="")
                except Exception as e:
                    print(f"Error extracting FanDuel odds for game {game_id}: {e}")

                game_info = {
                    "date": date_str,
                    "game_id": game_id,
                    "start_date": start_date,
                    "venue": venue,
                    "venue_city": venue_city,
                    "venue_state": venue_state,
                    "away_team_full": away_team["fullName"],
                    "away_team_short": away_team["shortName"],
                    "away_team_nickname": away_team["nickname"],
                    "away_team_name": away_team["name"],
                    "home_team_full": home_team["fullName"],
                    "home_team_short": home_team["shortName"],
                    "home_team_nickname": home_team["nickname"],
                    "home_team_name": home_team["name"],
                    # New fields
                    "game_status_text": game_status_text,
                    "score_away": score["away"],
                    "score_home": score["home"],
                    "consensus": consensus if consensus else None,
                    "last_line_update": last_line_update,
                    # Moneyline
                    "ml_opening_away": ml_opening.get("awayOdds"),
                    "ml_opening_home": ml_opening.get("homeOdds"),
                    "ml_opening_time": ml_opening.get("oddsDate"),
                    "ml_current_away": ml_current.get("awayOdds"),
                    "ml_current_home": ml_current.get("homeOdds"),
                    "ml_current_time": ml_current.get("oddsDate"),
                    # Run Line
                    "rl_opening_away_spread": spread_opening.get("awaySpread"),
                    "rl_opening_away_odds": spread_opening.get("awayOdds"),
                    "rl_opening_home_spread": spread_opening.get("homeSpread"),
                    "rl_opening_home_odds": spread_opening.get("homeOdds"),
                    "rl_opening_time": spread_opening.get("oddsDate"),
                    "rl_current_away_spread": spread_current.get("awaySpread"),
                    "rl_current_away_odds": spread_current.get("awayOdds"),
                    "rl_current_home_spread": spread_current.get("homeSpread"),
                    "rl_current_home_odds": spread_current.get("homeOdds"),
                    "rl_current_time": spread_current.get("oddsDate"),
                    # Total
                    "total_opening_line": total_opening.get("total"),
                    "total_opening_over_odds": total_opening.get("overOdds"),
                    "total_opening_under_odds": total_opening.get("underOdds"),
                    "total_opening_time": total_opening.get("oddsDate"),
                    "total_current_line": total_current.get("total"),
                    "total_current_over_odds": total_current.get("overOdds"),
                    "total_current_under_odds": total_current.get("underOdds"),
                    "total_current_time": total_current.get("oddsDate"),
                }
                all_games.append(game_info)
            except Exception as e:
                print(f"Error processing game row: {e}")
                continue

    return pd.DataFrame(all_games)
