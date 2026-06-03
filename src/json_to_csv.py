import os
import json
import pandas as pd

def process_cricsheet_data(folder_path, output_csv_path):
    """
    Parses Cricsheet JSON files and flattens them into a structured CSV.
    """
    all_deliveries = []
    
    # Target columns as requested
    columns = [
        'match_id', 'date', 'season', 'event', 'venue', 'city', 'team1', 'team2', 
        'toss_winner', 'toss_decision', 'winner', 'win_by_runs', 'win_by_wickets', 
        'player_of_match', 'innings', 'batting_team', 'over', 'ball', 'batter', 
        'bowler', 'non_striker', 'runs_batter', 'runs_extras', 'runs_total', 
        'extras_wides', 'extras_noballs', 'extras_byes', 'extras_legbyes', 
        'wicket_kind', 'wicket_player_out'
    ]

    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    print(f"Found {len(json_files)} JSON files. Starting extraction...")

    for filename in json_files:
        file_path = os.path.join(folder_path, filename)
        
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping {filename}: Invalid JSON format.")
                continue
                
        # ==========================================
        # 1. Match-Level Metadata Extraction
        # ==========================================
        match_id = filename.split('.')[0]
        info = data.get('info', {})
        
        # Safely extract match metadata
        date = info.get('dates', [None])[0]
        season = info.get('season')
        event = info.get('event', {}).get('name')
        venue = info.get('venue')
        city = info.get('city')
        
        teams = info.get('teams', [None, None])
        team1 = teams[0] if len(teams) > 0 else None
        team2 = teams[1] if len(teams) > 1 else None
        
        toss_winner = info.get('toss', {}).get('winner')
        toss_decision = info.get('toss', {}).get('decision')
        
        outcome = info.get('outcome', {})
        
        # 1. Try to get the winner
        winner = outcome.get('winner')
        
        # 2. If winner is missing, check for a 'result' (tie / no result)
        if winner is None:
            winner = outcome.get('result')
            
        win_by_runs = outcome.get('by', {}).get('runs', 0)
        win_by_wickets = outcome.get('by', {}).get('wickets', 0)
        
        pom_list = info.get('player_of_match', [None])
        player_of_match = pom_list[0] if pom_list else None

        # ==========================================
        # 2. Delivery-Level Data Extraction
        # ==========================================
        for inning_idx, inning in enumerate(data.get('innings', []), start=1):
            batting_team = inning.get('team')
            
            for over_data in inning.get('overs', []):
                over_num = over_data.get('over')
                
                for ball_idx, delivery in enumerate(over_data.get('deliveries', []), start=1):
                    runs_dict = delivery.get('runs', {})
                    extras_dict = delivery.get('extras', {})
                    
                    # Initialize row with safe defaults
                    row = {
                        'match_id': match_id,
                        'date': date,
                        'season': season,
                        'event': event,
                        'venue': venue,
                        'city': city,
                        'team1': team1,
                        'team2': team2,
                        'toss_winner': toss_winner,
                        'toss_decision': toss_decision,
                        'winner': winner,
                        'win_by_runs': win_by_runs,
                        'win_by_wickets': win_by_wickets,
                        'player_of_match': player_of_match,
                        'innings': inning_idx,
                        'batting_team': batting_team,
                        'over': over_num,
                        'ball': ball_idx,
                        'batter': delivery.get('batter'),
                        'bowler': delivery.get('bowler'),
                        'non_striker': delivery.get('non_striker'),
                        'runs_batter': runs_dict.get('batter', 0),
                        'runs_extras': runs_dict.get('extras', 0),
                        'runs_total': runs_dict.get('total', 0),
                        'extras_wides': extras_dict.get('wides', 0),
                        'extras_noballs': extras_dict.get('noballs', 0),
                        'extras_byes': extras_dict.get('byes', 0),
                        'extras_legbyes': extras_dict.get('legbyes', 0),
                        'wicket_kind': None,
                        'wicket_player_out': None
                    }
                    
                    # Handle Wickets safely
                    if 'wickets' in delivery and len(delivery['wickets']) > 0:
                        row['wicket_kind'] = delivery['wickets'][0].get('kind')
                        row['wicket_player_out'] = delivery['wickets'][0].get('player_out')
                        
                    all_deliveries.append(row)

    # ==========================================
    # 3. Export to CSV
    # ==========================================
    if all_deliveries:
        df = pd.DataFrame(all_deliveries, columns=columns)

        city_map = {
            # UAE Venues are missing the city value
            'Dubai International Cricket Stadium': 'Dubai',
            'Sharjah Cricket Stadium': 'Sharjah',
        }

        # only fill where city is missing
        df['city'] = df['city'].fillna(df['venue'].map(city_map))
        df.to_csv(output_csv_path, index=False)
        print(f"Extraction complete! Saved {len(df)} rows to '{output_csv_path}'.")
        return df
    else:
        print("No data extracted. Please check the JSON files and folder path.")
        return pd.DataFrame()