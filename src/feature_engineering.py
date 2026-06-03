import pandas as pd
import numpy as np

def add_basic_event_flags(df):
    """Groups simple row-level flags for ball events."""
    df['is_wicket'] = np.where(df['wicket_kind'] == 'No Wicket', 0, 1)
    
    df['is_legal_delivery'] = np.where(
        (df['extras_wides'] > 0) | (df['extras_noballs'] > 0), 0, 1
    )
    
    df['is_dot_ball'] = np.where(df['runs_total'] == 0, 1, 0)
    df['is_boundary'] = np.where(df['runs_batter'].isin([4, 6]), 1, 0)
    
    return df

def add_bowling_team(df):
    """Adds context about the teams"""
    # Bowling Team
    df['bowling_team'] = np.where(
        df['batting_team'] == df['team1'], df['team2'], df['team1']
    )
    return df

def add_match_phases(df):
    """Adds context about phase of the match."""
    # Match Phases
    conditions = [
        (df['over'] <= 5),
        (df['over'] >= 6) & (df['over'] <= 14),
        (df['over'] >= 15)
    ]
    choices = ['Powerplay', 'Middle Overs', 'Death Overs']
    df['phase'] = np.select(conditions, choices, default='Unknown')
    
    return df

def calculate_cumulative_scores(df):
    """Calculates running totals for scores and wickets per innings."""
    df['current_score'] = df.groupby(['match_id', 'innings'])['runs_total'].cumsum()
    df['current_wickets'] = df.groupby(['match_id', 'innings'])['is_wicket'].cumsum()
    return df

def flag_rain_reduced_matches(df):
    """Identifies and flags matches reduced by rain (DLS method)."""
    first_innings = df[df['innings'] == 1].copy()
    
    match_summaries = first_innings.groupby('match_id').agg(
        total_balls=('is_legal_delivery', 'sum'),
        total_wickets=('is_wicket', 'sum')
    ).reset_index()
    
    match_summaries['is_rain_reduced'] = (
        (match_summaries['total_balls'] < 115) & 
        (match_summaries['total_wickets'] < 10)
    ).astype(int)
    
    df = df.merge(match_summaries[['match_id', 'is_rain_reduced']], on='match_id', how='left')
    df['is_rain_reduced'] = df['is_rain_reduced'].fillna(0).astype(int)
    print(f"Total Rain-Reduced Matches Flagged: {df['is_rain_reduced'].sum()}")
    
    return df

def add_run_chase_features(df):
    """Calculates targets, runs needed, and balls remaining for the 2nd innings."""
    # 1. Target Score
    first_innings_totals = df[df['innings'] == 1].groupby('match_id')['runs_total'].sum().reset_index()
    first_innings_totals['target'] = first_innings_totals['runs_total'] + 1
    df = df.merge(first_innings_totals[['match_id', 'target']], on='match_id', how='left')
    
    # 2. Runs Needed
    df['runs_needed'] = np.where(
        df['innings'] == 2, df['target'] - df['current_score'], np.nan
    )
    
    # 3. Balls Remaining
    df['balls_remaining'] = np.where(
        df['innings'] == 2, 120 - df.groupby(['match_id', 'innings'])['is_legal_delivery'].cumsum(), np.nan
    )
    
    return df

def engineer_ipl_features(df):
    """
    Master pipeline: Executes all feature engineering steps in the correct order.
    """
    df = df.copy()
    
    df = add_basic_event_flags(df)
    df = add_bowling_team(df)
    df = add_match_phases(df)
    df = calculate_cumulative_scores(df)
    df = flag_rain_reduced_matches(df)
    df = add_run_chase_features(df)
    
    return df