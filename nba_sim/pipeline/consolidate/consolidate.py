
import sys
import os
from pathlib import Path
import time

# consolidate.py -> consolidate/ -> pipeline/ -> nba_sim/ -> BASKETBALL MANAGER/
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from nba_sim.pipeline.extract.extract import *
import pandas as pd

SEASONS = ['2023-24', '2024-25', '2025-26']

def build_boxscore_player_combined(season: str):

    boxscoreBase = BoxScorePlayer(season, 'PerGame', 'Base')
    boxscoreAdv = BoxScorePlayer(season, 'PerGame', 'Advanced')

    sources = [
        (boxscoreBase, ['PLAYER_NAME', 'TEAM_ID', 'AGE', 'GP', 'W', 'L', 
            'MIN', 'FGM', 'FGA', 'FGM', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 
            'FTA', 'FT_PCT', 'OREB', 'DREB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 
            'PF', 'PFD', 'PTS', 'PLUS_MINUS', 'DD2', 'TD3', 'NBA_FANTASY_PTS', 
            'TEAM_COUNT']),
        (boxscoreAdv, ['OFF_RATING', 'E_OFF_RATING', 'DEF_RATING', 
            'E_DEF_RATING', 'NET_RATING', 'E_NET_RATING', 'AST_PCT', 'AST_TO',
            'AST_RATIO', 'OREB_PCT', 'DREB_PCT', 'REB_PCT', 'TM_TOV_PCT', 
            'EFG_PCT', 'TS_PCT', 'USG_PCT', 'E_PACE', 'PACE', 'PIE','POSS'])
    ]

    key = "PLAYER_ID"
    combined = None

    for df, cols in sources:
        subset = df[[key] + cols]   # always include the key so merge can match rows
        if combined is None:
            combined = subset
        else:
            combined = combined.merge(subset, on=key)

    return combined

# save player box score data for all seasons as csv
def build_boxscore(save: bool):
    columns = ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'SEASON', 'AGE', 'GP', 'W', 'L', 
               'MIN', 'FGM', 'FGA', 'FGM', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 
               'FTA', 'FT_PCT', 'OREB', 'DREB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 
               'PF', 'PFD', 'PTS', 'PLUS_MINUS', 'DD2', 'TD3', 'NBA_FANTASY_PTS', 
               'TEAM_COUNT', 'OFF_RATING', 'E_OFF_RATING', 'DEF_RATING', 
               'E_DEF_RATING', 'NET_RATING', 'E_NET_RATING', 'AST_PCT', 'AST_TO',
               'AST_RATIO', 'OREB_PCT', 'DREB_PCT', 'REB_PCT', 'TM_TOV_PCT', 
               'EFG_PCT', 'TS_PCT', 'USG_PCT', 'E_PACE', 'PACE', 'PIE','POSS']
    
    df = pd.DataFrame(columns=columns)

    all_seasons = []

    for season in SEASONS:
        combined = build_boxscore_player_combined(season)
        combined.insert(0, "SEASON", season)
        if (save):
            combined.to_csv(f'nba_sim/data/raw/{season}/boxscore_player.csv', index=False)

        all_seasons.append(combined)


def build_boxscore_team_combined(season: str):

    boxscoreBase = BoxScoreTeam(season, 'PerGame', 'Base')
    boxscoreAdv = BoxScoreTeam(season, 'PerGame', 'Advanced')

    combined = boxscoreBase.merge(boxscoreAdv, on="TEAM_ID")

    return combined

# save team box score data for all seasons as csv
def build_boxscore_team(save: bool):

    for season in SEASONS:
        combined = build_boxscore_team_combined(season)
        combined.insert(0, "SEASON", season)
        combined.to_csv(f'nba_sim/data/raw/{season}/boxscore_team.csv', index=False)

# save shot location data for all seasons as csv
def build_shot_locations(save: bool):

    for season in SEASONS:
        locations = ShotLocations(season, 0, 0, 'FGA')
        locations.insert(0, "SEASON", season)
        if (save):
            locations.to_csv(f'nba_sim/data/raw/{season}/shotLocations.csv', index=False)

# save play by play tracking data a game
def build_playByPlay(save: bool):

    for season in SEASONS:

        season_games = []

        games = gameFinder(season)['GAME_ID'].unique()
        print(games)

        for game in games:
            plays = PlayByPlay(game)
            plays.insert(0, "SEASON", season)

            

            season_gamesPD = pd.concat(season_games, ignore_index=True)

            if (save):
                locations.to_csv(f'LOCATION', index=False)

# save player tracking data for all seasons as csv
def build_player_tracking(save: bool):

    types = ['SpeedDistance', 'Rebounding', 'Possessions', 'CatchShoot', 
             'PullUpShot', 'Defense', 'Drives', 'Passing', 'ElbowTouch', 
             'PostTouch', 'PaintTouch', 'Efficiency']

    for season in SEASONS:

        for type in types:
            tracking = PlayerTracking(season, type)
            tracking.insert(0, "SEASON", season)
            if (save):
                tracking.to_csv(f'nba_sim/data/raw/{season}/player_tracking/{type}.csv', index=False)
                print(f"Saved nba_sim/data/raw/{season}/player_tracking/{type}.csv")
                time.sleep(2)
            
def build_play_types(save: bool):

    play_types = ['Isolation', 'PRBallHandler', 'PRRollman', 'Postup', 
                  'Spotup', 'Handoff', 'Cut', 'OffScreen', 'Transition', 
                  'OffRebound', 'Misc']

    frames = []

    for season in SEASONS:
        for play_type in play_types:
            df = PlayTypes(season, play_type)
            df.insert(0, "SEASON", season)
            frames.append(df)
            time.sleep(0.6)

        all_play_types = pd.concat(frames, ignore_index=True)

        if save:
            all_play_types.to_csv(f'nba_sim/data/raw/{season}/playTypes.csv', index=False)

def build_hustle(save: bool):

    for season in SEASONS:
        hustle = Hustle(season)
        hustle.insert(0, "SEASON", season)
        if (save):
            hustle.to_csv(f'nba_sim/data/raw/{season}/hustle.csv', index=False)

# TO DOOOOOOOO
def build_PTDefense(save: bool):

    for season in SEASONS:

        #nba_sim/data/raw/2023-24/boxscore_player.csv
        df = pd.read_csv(f'nba_sim/data/raw/{season}/boxscore_player.csv')
        player_ids = df['PLAYER_ID'].tolist()

        current_season_list = []

        for id in player_ids:
            defense = PTDefense(season, id)
            time.sleep(2)
            defense.insert(0, "SEASON", season)
            current_season_list.append(defense)

        curr_season = pd.concat(current_season_list, ignore_index=True)

        if (save):
            curr_season.to_csv(f'nba_sim/data/raw/{season}/PTDefense.csv', index=False)
            print(f"Saved nba_sim/data/raw/{season}/PTDefense.csv")

# TO DOOOOOOOO
def build_matchups(save: bool):

    for season in SEASONS:

        #nba_sim/data/raw/2023-24/boxscore_player.csv
        df = pd.read_csv(f'nba_sim/data/raw/{season}/boxscore_player.csv')
        player_ids = df['PLAYER_ID'].tolist()

        current_season_list = []

        for id in player_ids:
            matchups = Matchups(season, id)
            time.sleep(2)
            matchups.insert(0, "SEASON", season)
            current_season_list.append(matchups)

        curr_season = pd.concat(current_season_list, ignore_index=True)

        if (save):
            curr_season.to_csv(f'nba_sim/data/raw/{season}/matchups.csv', index=False)
            print(f"Saved nba_sim/data/raw/{season}/matchups.csv")

def build_team_opp_offense(save: bool):

    for season in SEASONS:

        teamDef = OppOffense(season, '0')
        teamDef.insert(0, "SEASON", season)
        if (save):
            teamDef.to_csv(f'nba_sim/data/raw/{season}/teamDef.csv', index=False)
            print(f"Saved nba_sim/data/raw/{season}/teamDef.csv")

def build_combineInfo(save: bool):

    years = [str(y) for y in range(2003, 2027)]

    # put all combine info into combine_frames for every year
    combine_frames = []
    for year in years:
        print(f"{year}...")
        try:
            combine = CombineInfo(year)
            combine.insert(0, "COMBINE_YEAR", int(year))
            combine_frames.append(combine)
        except Exception as e:
            print(f"Failed: {year} -> {e}")
        time.sleep(1)

    all_combine = pd.concat(combine_frames, ignore_index=True)
    all_combine["PLAYER_ID"] = pd.to_numeric(all_combine["PLAYER_ID"], errors="coerce").astype("Int64")
    all_combine = all_combine.dropna(subset=["PLAYER_ID"])
    all_combine = all_combine.drop_duplicates(subset="PLAYER_ID", keep="last")
    
    # Keep only players who appear in your season boxscores
    player_ids = set()
    for season in SEASONS:
        ids = pd.read_csv(f'nba_sim/data/raw/{season}/boxscore_player.csv')
        player_ids.update(ids["PLAYER_ID"].astype(int))

    df = all_combine[all_combine["PLAYER_ID"].isin(player_ids)].reset_index(drop=True)

    print(f"Matched {len(df)} of {len(player_ids)} players")

    if save:
        df.to_csv(f'nba_sim/data/raw/{season}/combine_info.csv', index=False)

    return df

def build_combineResults(save: bool):

    years = [str(y) for y in range(2003, 2027)]

    # put all combine info into combine_frames for every year
    combine_frames = []
    for year in years:
        print(f"{year}...")
        try:
            combine = CombineDrillResults(year)
            combine.insert(0, "COMBINE_YEAR", int(year))
            combine_frames.append(combine)
        except Exception as e:
            print(f"Failed: {year} -> {e}")
        time.sleep(1)

    all_combine = pd.concat(combine_frames, ignore_index=True)
    all_combine["PLAYER_ID"] = pd.to_numeric(all_combine["PLAYER_ID"], errors="coerce").astype("Int64")
    all_combine = all_combine.dropna(subset=["PLAYER_ID"])
    all_combine = all_combine.drop_duplicates(subset="PLAYER_ID", keep="last")
    
    # Keep only players who appear in your season boxscores
    player_ids = set()
    for season in SEASONS:
        ids = pd.read_csv(f'nba_sim/data/raw/{season}/boxscore_player.csv')
        player_ids.update(ids["PLAYER_ID"].astype(int))

    df = all_combine[all_combine["PLAYER_ID"].isin(player_ids)].reset_index(drop=True)

    print(f"Matched {len(df)} of {len(player_ids)} players")

    if save:
        df.to_csv(f'nba_sim/data/raw/{season}/combine_drill_results.csv', index=False)

    return df

def build_lineups(save: bool):

    for season in SEASONS:

        df = pd.read_csv(f'nba_sim/data/raw/{season}/teamDef.csv')
        team_ids = df['TEAM_ID'].tolist()

        current_season_teams = []

        for id in team_ids:
            matchups = LeagueLineups(season, id)
            time.sleep(2)
            matchups.insert(0, "SEASON", season)
            current_season_teams.append(matchups)

        curr_season = pd.concat(current_season_teams, ignore_index=True)

        if (save):
            curr_season.to_csv(f'nba_sim/data/raw/{season}/lineups.csv', index=False)


def main() -> int:

    #build_boxscore_team(False)
    #build_shot_locations(True)
    build_playByPlay(False)
    #build_player_tracking(True)
    #build_play_types(True)
    #build_hustle(True)
    #build_PTDefense(True)
    #build_team_opp_offense(True)
    #build_combineInfo(True)
    #build_combineResults(True)
    #build_lineups(True)

    return 0

if __name__ == "__main__":
    sys.exit(main())