# Python file to extract raw data from all APIs
# stored in ../../data/raw
import pandas as pd
from nba_api.stats.endpoints import leaguedashplayerstats, leaguedashteamstats, shotchartdetail, playbyplayv3, leaguedashptstats, synergyplaytypes, leaguehustlestatsplayer, leaguedashptdefend, leagueseasonmatchups, leaguedashoppptshot, draftcombineplayeranthro, draftcombinedrillresults, leaguedashlineups, leaguegamefinder
from basketball_reference_web_scraper import client

# Box Score Player
def BoxScorePlayer(season: str, mode: str, type:str):
    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=season, # '2025-26' or '2024-25' or '2023-24'
        per_mode_detailed=mode,  # Use 'Totals' or 'PerGame'
        measure_type_detailed_defense=type  # Use 'Base', 'Advanced', etc.
    )

    # Convert the response to a Pandas DataFrame
    df = stats.get_data_frames()[0]

    return df


# Box Score Team
def BoxScoreTeam(season: str, mode: str, type:str):
    stats = leaguedashteamstats.LeagueDashTeamStats(
        season=season, # '2025-26' or '2024-25' or '2023-24'
        per_mode_detailed=mode,  # Use 'Totals' or 'PerGame'
        measure_type_detailed_defense=type  # Use 'Base', 'Advanced', etc.
    )

    # Convert the response to a Pandas DataFrame
    df = stats.get_data_frames()[0]

    return df


# Shot Locations
def ShotLocations(season: str, player_id: int, team_id: int, metric: str):

    chart = shotchartdetail.ShotChartDetail(
        season_nullable=season, # '2025-26' or '2024-25' or '2023-24'
        player_id=player_id, # keep 0 for general query, id retrieved from BoxScorePlayer
        team_id=team_id, # keep 0 for general query, team id retrieved from BoxScoreTeam
        context_measure_simple=metric # retrived metric, 'FGA', 'PTS', 'PTS_FB' fastbreak, 'PTS_OFF_TOV', 'PTS_2ND_CHANCE'
    )

    # Conver to pandas dataframe
    df = chart.get_data_frames()[0]

    return df


# Play by Play
def PlayByPlay(game_id: str):
    playbyplay = playbyplayv3.PlayByPlayV3(
        game_id=game_id,
    )

    # Convert to pandas dataframe
    df = playbyplay.get_data_frames()[0]

    return df


# Player Tracking Stats
def PlayerTracking(season:str, mode: str, measure_type: str):
    playertracking = leaguedashptstats.LeagueDashPtStats(
        per_mode_simple=mode,
        pt_measure_type=measure_type, # (SpeedDistance)|(Rebounding)|(Possessions)|(CatchShoot)|(PullUpShot)|(Defense)|(Drives)|(Passing)|(ElbowTouch)|(PostTouch)|(PaintTouch)|(Efficiency)
        player_or_team='Player',
        season=season
    )

    df = playertracking.get_data_frames()[0]

    return df


# play types
def PlayTypes(season: str, mode: str, playType: str):

    playTypes = synergyplaytypes.SynergyPlayTypes(
        per_mode_simple=mode,
        player_or_team_abbreviation='P',
        season_type_all_star="Regular Season",
        type_grouping_nullable="offensive",
        season=season,
        play_type_nullable=playType # Isolation, PRBallHandler (Pick & Roll Ball Handler), PRRollman (Pick & Roll Roll Man), Postup, SpotUp, Handoff, Cut, OffScreen, Transition, Putbacks, and Misc
    )

    df = playTypes.get_data_frames()[0]

    return df


# Hustle
def Hustle(season: str):

    hustle = leaguehustlestatsplayer.LeagueHustleStatsPlayer(
        per_mode_time='Totals',
        season=season
    )

    df = hustle.get_data_frames()[0]

    return df


# defense and rim protection player tracking
def PTDefense(season: str, player_id: str):

    hustle = leaguedashptdefend.LeagueDashPtDefend(
        season=season,
        player_id_nullable=player_id
    )

    df = hustle.get_data_frames()[0]

    return df


# player matchups
def Matchups(season: str, player_id: str):

    hustle = leagueseasonmatchups.LeagueSeasonMatchups(
        season=season,
        def_player_id_nullable=player_id,
        per_mode_simple="Totals"
    )

    df = hustle.get_data_frames()[0]

    return df


# Opponent offensive stats
def OppOffense(season: str, mode: str, team_id: str):

    hustle = leaguedashoppptshot.LeagueDashOppPtShot(
        season=season,
        per_mode_simple=mode,
        season_type_all_star="Regular Season",
        team_id_nullable=int(team_id)
    )

    df = hustle.get_data_frames()[0]

    return df


# nba combine antro
# need to provide year, so might require going through each year and finding player id to impute data
def CombineInfo(year: str):

    hustle = draftcombineplayeranthro.DraftCombinePlayerAnthro(
        league_id='00',
        season_year=year,
    )

    df = hustle.get_data_frames()[0]

    return df


# nba combine drill results
# need to provide year, so might require going through each year and finding player id to impute data
def CombineDrillResults(year: str):

    hustle = draftcombinedrillresults.DraftCombineDrillResults(
        league_id='00',
        season_year=year
    )

    df = hustle.get_data_frames()[0]

    #return df.loc[df['PLAYER_ID'] == int(player_id)]
    return df


# league lineups
def LeagueLineups(season: str, team_id: str):

    hustle = leaguedashlineups.LeagueDashLineups(
        season=season,
        team_id_nullable=team_id,
        per_mode_detailed='Totals'
    )

    df = hustle.get_data_frames()[0]

    return df


def gameFinder(season: str, game_type: str = "Regular Season"):

    df = leaguegamefinder.LeagueGameFinder(
        season_nullable=season,
        season_type_nullable=game_type,
        league_id_nullable="00",
    ).get_data_frames()[0]

    df["IS_HOME"] = df["MATCHUP"].str.contains("vs.", regex=False)
    df = df.sort_values(["GAME_ID", "IS_HOME"], ascending=[True, False])
    df["SIDE"] = df.groupby("GAME_ID").cumcount().map({0: "HOME", 1: "AWAY"})

    home = df[df["SIDE"] == "HOME"].drop(columns=["IS_HOME", "SIDE"])
    away = df[df["SIDE"] == "AWAY"].drop(columns=["IS_HOME", "SIDE"])

    return home.merge(away, on="GAME_ID", suffixes=("_HOME", "_AWAY"))

#BoxScoreTeam('2025-26', 'PerGame', 'Base')

#PlayerTracking('2025-26', '203468') # CJ mccollum

#PlayTypes('2025-26', 'Isolation', '203468')

#print(Hustle('2025-26').columns)

#print(PTDefense('2025-26', '0'))

#print(Matchups('2023-24', '203932')['TEAM_PTS'])

#print(OppOffense('2025-26', '0').columns)

#print(CombineInfo('2022'))

#CombineDrillResults('203468','2013')

#df = LeagueLineups('2025-26','1610612764')

#print(gameFinder('2025-26').columns)
