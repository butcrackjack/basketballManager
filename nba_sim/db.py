# nba_sim/db.py
import duckdb
from nba_sim.config.settings import DB_PATH, PARQUET_DIR

P = PARQUET_DIR.as_posix()
VIEWS = {
    "boxscore_player": f"read_parquet('{P}/*/boxscore_player.parquet', union_by_name=true)",
    "boxscore_team": f"read_parquet('{P}/*/boxscore_team.parquet', union_by_name=true)",
    "hustle": f"read_parquet('{P}/*/hustle.parquet', union_by_name=true)",
    "play_by_play": f"read_parquet('{P}/*/playbyplays.parquet', union_by_name=true)",
    "combine": f"read_parquet('{P}/2025-26/combine_info.parquet', union_by_name=true)",
    "teamdef": f"read_parquet('{P}/*/PTDefense.parquet', union_by_name=true)",
    "lebron": f"read_parquet('{P}/*/lebron_data.parquet', union_by_name=true)",
    "shotlocations": f"read_parquet('{P}/*/shotLocations.parquet', union_by_name=true)",
}
# "tracking" is built separately by tracking_view_sql(), so it can carry a MEASURE_TYPE column.

# Tracking measure types, as named by the NBA tracking endpoint
TRACKING_MEASURES = [
    "SpeedDistance", "Rebounding", "Possessions", "CatchShoot", "PullUpShot",
    "Defense", "Drives", "Passing", "ElbowTouch", "PostTouch", "PaintTouch",
    "Efficiency",
]


def _measure_type(file_stem: str) -> str:
    """Work out which tracking measure a file holds from its name."""
    matches = [m for m in TRACKING_MEASURES if m.lower() in file_stem.lower()]
    if not matches:
        raise ValueError(
            f"Tracking file '{file_stem}' doesn't name a known measure type. "
            f"Expected one of: {TRACKING_MEASURES}"
        )
    return max(matches, key=len)   # most specific name if more than one matches


def tracking_view_sql() -> str:
    """
    One query over every tracking file, adding a MEASURE_TYPE column
    (e.g. 'CatchShoot') that says which measure each row came from.
    """
    files = sorted(PARQUET_DIR.glob("*/player_tracking/*.parquet"))
    if not files:
        raise FileNotFoundError(f"No tracking files found in {P}/*/player_tracking/")

    by_measure: dict[str, list[str]] = {}
    for f in files:
        by_measure.setdefault(_measure_type(f.stem), []).append(f.as_posix())

    parts = []
    for measure, paths in sorted(by_measure.items()):
        path_list = ", ".join(f"'{p}'" for p in paths)
        parts.append(
            f"SELECT *, '{measure}' AS MEASURE_TYPE "
            f"FROM read_parquet([{path_list}], union_by_name=true)"
        )
    return "\nUNION ALL BY NAME\n".join(parts)


def get_connection():
    con = duckdb.connect(str(DB_PATH))
    for name, source in VIEWS.items():
        con.execute(f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM {source}")
    con.execute(f"CREATE OR REPLACE VIEW tracking AS {tracking_view_sql()}")

    print("Connected to DB.")

    return con