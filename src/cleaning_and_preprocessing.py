import pandas as pd

def standardize_cities(df):
    """Standardizes city names."""

    city_rebrands = {'Bangalore': 'Bengaluru', 'Mohali': 'Chandigarh', 'New Chandigarh': 'Chandigarh'}
    df['city'] = df['city'].replace(city_rebrands)
    print(f"Cities reduced to {len(df['city'].dropna().unique())}")
    return df

def standardize_venues(df):
    """Standardizes venue names."""
    venue_rebrands = {
        'M.Chinnaswamy Stadium': 'M Chinnaswamy Stadium',
        'M Chinnaswamy Stadium, Bengaluru': 'M Chinnaswamy Stadium',
        'Feroz Shah Kotla': 'Arun Jaitley Stadium',
        'Arun Jaitley Stadium, Delhi': 'Arun Jaitley Stadium',
        'Brabourne Stadium, Mumbai': 'Brabourne Stadium',
        'Dr DY Patil Sports Academy, Mumbai': 'Dr DY Patil Sports Academy',
        'Wankhede Stadium, Mumbai': 'Wankhede Stadium',
        'MA Chidambaram Stadium, Chepauk': 'MA Chidambaram Stadium',
        'MA Chidambaram Stadium, Chepauk, Chennai': 'MA Chidambaram Stadium',
        'Sardar Patel Stadium, Motera': 'Narendra Modi Stadium',
        'Narendra Modi Stadium, Ahmedabad': 'Narendra Modi Stadium',
        'Subrata Roy Sahara Stadium': 'Maharashtra Cricket Association Stadium',
        'Maharashtra Cricket Association Stadium, Pune': 'Maharashtra Cricket Association Stadium',
        'Punjab Cricket Association Stadium, Mohali': 'Punjab Cricket Association IS Bindra Stadium',
        'Punjab Cricket Association IS Bindra Stadium, Mohali': 'Punjab Cricket Association IS Bindra Stadium',
        'Punjab Cricket Association IS Bindra Stadium, Mohali, Chandigarh': 'Punjab Cricket Association IS Bindra Stadium',
        'Maharaja Yadavindra Singh International Cricket Stadium, Mullanpur': 'Maharaja Yadavindra Singh International Cricket Stadium',
        'Maharaja Yadavindra Singh International Cricket Stadium, New Chandigarh': 'Maharaja Yadavindra Singh International Cricket Stadium',
        'Rajiv Gandhi International Stadium, Uppal': 'Rajiv Gandhi International Stadium',
        'Rajiv Gandhi International Stadium, Uppal, Hyderabad': 'Rajiv Gandhi International Stadium',
        'Eden Gardens, Kolkata': 'Eden Gardens',
        'Sawai Mansingh Stadium, Jaipur': 'Sawai Mansingh Stadium',
        'Himachal Pradesh Cricket Association Stadium, Dharamsala': 'Himachal Pradesh Cricket Association Stadium',
        'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam': 'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium',
        'Zayed Cricket Stadium, Abu Dhabi': 'Sheikh Zayed Stadium'
    }
    df['venue'] = df['venue'].replace(venue_rebrands)
    print(f"Venues reduced to {len(df['venue'].dropna().unique())}")
    return df

def standardize_teams(df):
    """Updates legacy team names to their current franchise names."""
    team_rebrands = {
        'Delhi Daredevils': 'Delhi Capitals',
        'Kings XI Punjab': 'Punjab Kings',
        'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
        'Rising Pune Supergiants': 'Rising Pune Supergiant'
    }
    #applying to all columns which use team names
    cols = ['team1', 'team2', 'toss_winner', 'winner', 'batting_team']
    for col in cols:
        df[col] = df[col].replace(team_rebrands)
    print(f"Teams reduced to {len(pd.concat([df['team1'], df['team2']]).dropna().unique())}")
    return df

def format_dates_and_sort(df):
    """Converts dates, extracts season, and sorts chronologically."""
    #set the date column to datetime object
    df['date'] = pd.to_datetime(df['date'])
    #extract year from the date column to fix seasons
    df['season'] = df['date'].dt.year
    # sort the data chronologically
    # 1st: The calendar day
    # 2nd: To separate afternoon vs evening games on the same day
    # 3rd: 1st innings before 2nd innings
    # 4th: Over 0 to Over 19
    # 5th: Ball 1 to Ball 6 (or 7/8 for extras)
    df = df.sort_values(by=['date', 'match_id', 'innings', 'over', 'ball'])
    #rest index to 0
    return df.reset_index(drop=True)

def handle_missing_values(df):
    """Fills nulls in wicket and award columns."""
    df['wicket_kind'] = df['wicket_kind'].fillna('No Wicket')
    df['wicket_player_out'] = df['wicket_player_out'].fillna('Nobody')
    df['player_of_match'] = df['player_of_match'].fillna('No Result')
    return df

def standardize_player_names(df):
    """Fixes specific typos in player names."""
    fuzzy_corrections = {
        'Arshad Khan (2)': 'Arshad Khan',
        'NA Saini': 'N Saini',
        'R Bishnoi': 'Ravi Bishnoi',
        'M.S. Dhoni': 'MS Dhoni',
        'M S Dhoni': 'MS Dhoni'
    }
    # Apply the corrections across all player columns
    cols = ['batter', 'bowler', 'non_striker', 'player_of_match', 'wicket_player_out']
    for col in cols:
        df[col] = df[col].replace(fuzzy_corrections)
    return df

def clean_ipl_data(df):
    """
    Master pipeline: Executes the full cleaning process.
    """
    # .copy() prevents Pandas warnings about modifying slices of data
    df = df.copy() 
    
    df = standardize_cities(df)
    df = standardize_teams(df)
    df = format_dates_and_sort(df)
    df = handle_missing_values(df)
    df = standardize_player_names(df)
    
    return df