"""
Validation checks on the raw parquet data.

Every check is a query that returns the rows that break a rule.
Zero rows means the check passed.

Order: first check within each dataset, then check equivalent data across sets.

Run from the project root:
    python -m nba_sim.pipeline.validate.validate

Notes
-----
Play-by-play vs box score: a few players were off by a single rebound or
turnover, so the play-by-play comparison only flags differences larger than 1
(larger than 2 for blocks).
"""

import sys
sys.path.insert(0, "./nba_sim")

import pandas as pd

from nba_sim.db import get_connection

# (season, player_id) pairs with a known, explained data error.
# Rows for these players are dropped from failing results before reporting.
KNOWN_CORRECTIONS = {
    ("2025-26", 1641711),  # Gradey Dick: TOV moved to Jackson-Davis
    ("2025-26", 1631218),  # Trayce Jackson-Davis
}


CHECKS = {
    # COMPLETENESS
    # _______________
    "boxscore_player: missing IDs":
        "SELECT * FROM boxscore_player WHERE PLAYER_ID IS NULL OR SEASON IS NULL",

    "play_by_play: season doesn't have 1230 games":
        "SELECT SEASON, COUNT(DISTINCT GAME_ID) AS games FROM play_by_play GROUP BY SEASON HAVING games <> 1230",

    "shotlocations: season incomplete":
        "SELECT SEASON, COUNT(DISTINCT GAME_ID) AS games FROM shotlocations GROUP BY SEASON HAVING games <> 1230",

    # UNIQUENESS
    # _______________
    "boxscore_player: player appears twice in a season":
        "SELECT SEASON, PLAYER_ID, COUNT(*) AS n FROM boxscore_player GROUP BY ALL HAVING n > 1",

    "play_by_play: duplicate action in a game":
        "SELECT GAME_ID, ACTION_ID, COUNT(*) AS n FROM play_by_play GROUP BY ALL HAVING n > 1",

    "shotlocations: duplicate shot":
        "SELECT GAME_ID, GAME_EVENT_ID, COUNT(*) AS n FROM shotlocations GROUP BY ALL HAVING n > 1",

    # VALIDITY
    # _______________
    "boxscore_player: percentage out of range": """
        SELECT SEASON, PLAYER_NAME, FG_PCT, FG3_PCT, FT_PCT
        FROM boxscore_player
        WHERE FG_PCT  NOT BETWEEN 0 AND 1
           OR FG3_PCT NOT BETWEEN 0 AND 1
           OR FT_PCT  NOT BETWEEN 0 AND 1
    """,

    "boxscore_player: negative counting stat": """
        SELECT SEASON, PLAYER_NAME FROM boxscore_player
        WHERE LEAST(GP, MIN, FGM, FGA, FG3M, FG3A, FTM, FTA, OREB, DREB,
                    AST, STL, BLK, TOV, PF, PTS) < 0
    """,

    "combine: unrealistic measurements":
        "SELECT PLAYER_NAME, HEIGHT_WO_SHOES, WEIGHT FROM combine "
        "WHERE HEIGHT_WO_SHOES NOT BETWEEN 65 AND 92 OR WEIGHT NOT BETWEEN 150 AND 330",

    "shotlocations: shot type doesn't fit distance": """
        SELECT SEASON, GAME_ID, PLAYER_NAME, SHOT_TYPE, SHOT_DISTANCE FROM shotlocations
        WHERE (SHOT_TYPE = '3PT Field Goal' AND SHOT_DISTANCE < 21)
           OR (SHOT_TYPE = '2PT Field Goal' AND SHOT_DISTANCE > 24)
    """,

    # INTERNAL CONSISTENCY
    # _______________
    "boxscore_player: made more shots than attempted":
        "SELECT SEASON, PLAYER_NAME, FGM, FGA FROM boxscore_player "
        "WHERE FGM > FGA OR FG3M > FG3A OR FTM > FTA",

    "boxscore_player: wins + losses != games played":
        "SELECT SEASON, PLAYER_NAME, GP, W, L FROM boxscore_player WHERE W + L <> GP",

    "boxscore_player: PTS != 2*FGM + FG3M + FTM":
        "SELECT SEASON, PLAYER_NAME, PTS, FGM, FG3M, FTM FROM boxscore_player "
        "WHERE PTS <> 2*FGM + FG3M + FTM",

    "boxscore_team: season isn't 30 teams x 82 games": """
        SELECT SEASON, COUNT(*) AS teams, MIN(GP_x), MAX(GP_x), SUM(W_x), SUM(L_x)
        FROM boxscore_team GROUP BY SEASON
        HAVING COUNT(*) <> 30 OR MIN(GP_x) <> 82 OR MAX(GP_x) <> 82
            OR SUM(W_x) <> 1230 OR SUM(L_x) <> 1230
    """,

    "hustle: parts don't add up to totals": """
        SELECT SEASON, PLAYER_NAME,
            CONTESTED_SHOTS, CONTESTED_SHOTS_2PT + CONTESTED_SHOTS_3PT AS CONTESTED_SUM,
            BOX_OUTS, OFF_BOXOUTS + DEF_BOXOUTS AS BOXOUT_SUM
        FROM hustle
        WHERE CONTESTED_SHOTS <> CONTESTED_SHOTS_2PT + CONTESTED_SHOTS_3PT
           OR OFF_BOXOUTS + DEF_BOXOUTS > BOX_OUTS
           OR BOX_OUTS - (OFF_BOXOUTS + DEF_BOXOUTS) > 3
    """,

    "play_by_play: final score doesn't match made shots": """
        WITH pts AS (
            SELECT GAME_ID, LOCATION,
                   SUM(CASE WHEN SHOT_MADE_FLAG THEN SHOT_VALUE ELSE 0 END) AS PTS
            FROM play_by_play WHERE LOCATION IN ('h', 'v') GROUP BY ALL
        ),
        final AS (
            SELECT GAME_ID, MAX(SCORE_HOME) AS HOME, MAX(SCORE_AWAY) AS AWAY
            FROM play_by_play GROUP BY ALL
        )
        SELECT f.GAME_ID, f.HOME, h.PTS AS HOME_PBP, f.AWAY, a.PTS AS AWAY_PBP
        FROM final f
        LEFT JOIN pts h ON f.GAME_ID = h.GAME_ID AND h.LOCATION = 'h'
        LEFT JOIN pts a ON f.GAME_ID = a.GAME_ID AND a.LOCATION = 'v'
        WHERE f.HOME <> COALESCE(h.PTS, 0) OR f.AWAY <> COALESCE(a.PTS, 0)
    """,

    # CROSS-TABLE: IDS EXIST
    # (ANTI JOIN, not NOT IN: NOT IN silently passes if the subquery holds a NULL)
    # _______________
    "boxscore_player: team id not in teamdef":
        "SELECT b.SEASON, b.PLAYER_ID, b.PLAYER_NAME, b.TEAM_ID FROM boxscore_player b "
        "ANTI JOIN teamdef t ON b.SEASON = t.SEASON AND b.TEAM_ID = t.TEAM_ID",

    "boxscore_player: player missing from lebron":
        "SELECT b.SEASON, b.PLAYER_ID, b.PLAYER_NAME, b.MIN FROM boxscore_player b "
        "ANTI JOIN lebron l ON b.SEASON = l.SEASON AND b.PLAYER_ID = l.PLAYER_ID",

    "boxscore_player: player missing from hustle":
        "SELECT b.SEASON, b.PLAYER_ID, b.PLAYER_NAME, b.MIN FROM boxscore_player b "
        "ANTI JOIN hustle h ON b.SEASON = h.SEASON AND b.PLAYER_ID = h.PLAYER_ID",

    "lebron: player not in that season's boxscore_player":
        "SELECT l.SEASON, l.PLAYER_ID FROM lebron l "
        "ANTI JOIN boxscore_player b ON l.SEASON = b.SEASON AND l.PLAYER_ID = b.PLAYER_ID",

    "tracking: player not in that season's boxscore_player":
        "SELECT t.SEASON, t.PLAYER_ID, t.MEASURE_TYPE FROM tracking t "
        "ANTI JOIN boxscore_player b ON t.SEASON = b.SEASON AND t.PLAYER_ID = b.PLAYER_ID",

    # CROSS-TABLE: EQUIVALENT DATA AGREES
    # _______________
    "boxscore_player vs play_by_play: player totals differ": """
        WITH pbp_totals AS (
            SELECT SEASON, PLAYER_ID,
                SUM(CASE WHEN SHOT_MADE_FLAG THEN SHOT_VALUE ELSE 0 END) AS PBP_PTS,
                COUNT(*) FILTER (WHERE ACTION_TYPE = 'Turnover')         AS PBP_TOV,
                COUNT(*) FILTER (WHERE ACTION_TYPE = 'Rebound')          AS PBP_REB,
                COUNT(*) FILTER (WHERE DESCRIPTION LIKE '%STEAL%')       AS PBP_STL,
                COUNT(*) FILTER (WHERE DESCRIPTION LIKE '%BLOCK%')       AS PBP_BLK
            FROM play_by_play
            GROUP BY SEASON, PLAYER_ID
        )
        SELECT b.SEASON, b.PLAYER_ID, b.PLAYER_NAME,
            b.PTS AS BOX_PTS,           COALESCE(p.PBP_PTS, 0) AS PBP_PTS,
            b.TOV AS BOX_TOV,           COALESCE(p.PBP_TOV, 0) AS PBP_TOV,
            (b.OREB + b.DREB) AS BOX_REB, COALESCE(p.PBP_REB, 0) AS PBP_REB,
            b.STL AS BOX_STL,           COALESCE(p.PBP_STL, 0) AS PBP_STL,
            b.BLK AS BOX_BLK,           COALESCE(p.PBP_BLK, 0) AS PBP_BLK
        FROM boxscore_player b
        LEFT JOIN pbp_totals p ON b.SEASON = p.SEASON AND b.PLAYER_ID = p.PLAYER_ID
        WHERE ABS(b.PTS - COALESCE(p.PBP_PTS, 0)) > 1
           OR ABS(b.TOV - COALESCE(p.PBP_TOV, 0)) > 1
           OR ABS((b.OREB + b.DREB) - COALESCE(p.PBP_REB, 0)) > 1
           OR ABS(b.STL - COALESCE(p.PBP_STL, 0)) > 1
           OR ABS(b.BLK - COALESCE(p.PBP_BLK, 0)) > 2
        ORDER BY ABS(b.PTS - COALESCE(p.PBP_PTS, 0))
               + ABS(b.TOV - COALESCE(p.PBP_TOV, 0))
               + ABS((b.OREB + b.DREB) - COALESCE(p.PBP_REB, 0))
               + ABS(b.STL - COALESCE(p.PBP_STL, 0))
               + ABS(b.BLK - COALESCE(p.PBP_BLK, 0)) DESC
    """,

    "boxscore_player vs shotlocations: field goal points differ": """
        WITH shotloc_points AS (
            SELECT SEASON, PLAYER_ID,
                SUM(CASE WHEN SHOT_TYPE = '3PT Field Goal' THEN 3 ELSE 2 END) AS SHOT_FG_PTS
            FROM shotlocations
            WHERE SHOT_MADE_FLAG = 1
            GROUP BY SEASON, PLAYER_ID
        )
        SELECT b.SEASON, b.PLAYER_ID, b.PLAYER_NAME,
               b.PTS - b.FTM AS BOX_FG_PTS,
               COALESCE(s.SHOT_FG_PTS, 0) AS SHOT_FG_PTS
        FROM boxscore_player b
        LEFT JOIN shotloc_points s ON b.SEASON = s.SEASON AND b.PLAYER_ID = s.PLAYER_ID
        WHERE b.PTS - b.FTM <> COALESCE(s.SHOT_FG_PTS, 0)
    """,

    "boxscore_player vs play_by_play: TEAM_COUNT doesn't match teams seen": """
        WITH pbp_teams AS (
            SELECT SEASON, PLAYER_ID, COUNT(DISTINCT TEAM_ID) AS PBP_TEAMS
            FROM play_by_play
            WHERE PLAYER_ID <> 0
            GROUP BY ALL
        )
        SELECT b.SEASON, b.PLAYER_ID, b.PLAYER_NAME, b.TEAM_COUNT, p.PBP_TEAMS
        FROM boxscore_player b
        JOIN pbp_teams p ON b.SEASON = p.SEASON AND b.PLAYER_ID = p.PLAYER_ID
        WHERE b.TEAM_COUNT <> p.PBP_TEAMS
    """,

    "boxscore_player vs boxscore_team: league points differ": """
        WITH players AS (SELECT SEASON, SUM(PTS) AS PLAYER_PTS FROM boxscore_player GROUP BY SEASON),
             teams   AS (SELECT SEASON, SUM(PTS) AS TEAM_PTS   FROM boxscore_team   GROUP BY SEASON)
        SELECT p.SEASON, p.PLAYER_PTS, t.TEAM_PTS, p.PLAYER_PTS - t.TEAM_PTS AS DIFF
        FROM players p
        JOIN teams t ON p.SEASON = t.SEASON
        WHERE p.PLAYER_PTS <> t.TEAM_PTS
    """,

    "boxscore_player vs boxscore_team: league totals differ": """
        WITH p AS (SELECT SEASON, SUM(FGM) FGM, SUM(FGA) FGA, SUM(FG3M) FG3M, SUM(FTM) FTM,
                          SUM(OREB) OREB, SUM(DREB) DREB, SUM(AST) AST, SUM(STL) STL, SUM(BLK) BLK
                   FROM boxscore_player GROUP BY SEASON),
             t AS (SELECT SEASON, SUM(FGM) FGM, SUM(FGA) FGA, SUM(FG3M) FG3M, SUM(FTM) FTM,
                          SUM(OREB) OREB, SUM(DREB) DREB, SUM(AST) AST, SUM(STL) STL, SUM(BLK) BLK
                   FROM boxscore_team GROUP BY SEASON)
        SELECT * FROM p JOIN t USING (SEASON)
        WHERE p.FGM <> t.FGM OR p.FGA <> t.FGA OR p.FG3M <> t.FG3M OR p.FTM <> t.FTM
           OR p.OREB <> t.OREB OR p.DREB <> t.DREB OR p.AST <> t.AST
           OR p.STL <> t.STL OR p.BLK <> t.BLK
    """,

    "lebron vs boxscore_player: MPG differs": """
        SELECT l.SEASON, l.Player,
            l.MPG                          AS LEB_MPG,
            ROUND(b.MIN / b.GP, 1)         AS BOX_MPG,
            ROUND(b.MIN / b.GP - l.MPG, 2) AS DIFF
        FROM lebron l
        JOIN boxscore_player b ON l.SEASON = b.SEASON AND l.PLAYER_ID = b.PLAYER_ID
        WHERE ABS(b.MIN / b.GP - l.MPG) > 0.1
        ORDER BY ABS(b.MIN / b.GP - l.MPG) DESC
    """,

    "tracking vs boxscore_player: catch-and-shoot + pull-up FGA exceed total FGA": """
        WITH cs AS (SELECT SEASON, PLAYER_ID, CATCH_SHOOT_FGA FROM tracking
                    WHERE MEASURE_TYPE = 'CatchShoot'),
             pu AS (SELECT SEASON, PLAYER_ID, PULL_UP_FGA FROM tracking
                    WHERE MEASURE_TYPE = 'PullUpShot')
        SELECT b.SEASON, b.PLAYER_NAME, b.FGA,
            cs.CATCH_SHOOT_FGA, pu.PULL_UP_FGA,
            cs.CATCH_SHOOT_FGA + pu.PULL_UP_FGA AS SUBSET_FGA
        FROM boxscore_player b
        JOIN cs ON b.SEASON = cs.SEASON AND b.PLAYER_ID = cs.PLAYER_ID
        JOIN pu ON b.SEASON = pu.SEASON AND b.PLAYER_ID = pu.PLAYER_ID
        WHERE cs.CATCH_SHOOT_FGA + pu.PULL_UP_FGA > b.FGA
    """,
}


def drop_known_corrections(result: pd.DataFrame) -> pd.DataFrame:
    """Remove rows for players listed in KNOWN_CORRECTIONS."""
    if not {"SEASON", "PLAYER_ID"} <= set(result.columns):
        return result
    keys = list(zip(result["SEASON"], result["PLAYER_ID"].astype("int64")))
    keep = [k not in KNOWN_CORRECTIONS for k in keys]
    return result[keep]


def run_checks(con) -> int:
    """Run every check, print the report, and return the number of failures."""
    failed = 0
    for name, sql in CHECKS.items():
        result = drop_known_corrections(con.sql(sql).df())
        if result.empty:
            print(f"PASS  {name}")
        else:
            failed += 1
            print(f"FAIL  {name}  ({len(result)} rows)")
            print(result.head(10).to_string(index=False), "\n")

    print(f"\n{len(CHECKS) - failed}/{len(CHECKS)} checks passed")
    return failed


def main() -> int:
    con = get_connection()
    try:
        failed = run_checks(con)
    finally:
        con.close()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())