"""
Build feat_shooting_counts: makes and attempts per player, season and
shooting attribute, in the standard long shape used by estimation.

Grain:   player_id, season, attribute
Columns: player_id, season, attribute, successes, trials

Run from the project root:
    python nba_sim/pipeline/transform/features/shooting_counts.py
"""

import sys
from dataclasses import dataclass
from pathlib import Path

import duckdb

# shooting_counts.py -> features/ -> transform/ -> pipeline/ -> nba_sim/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT))

from nba_sim.config.settings import DB_PATH

OUTPUT_TABLE = "feat_shooting_counts"


@dataclass(frozen=True)
class CountSource:
    """Where one attribute's makes and attempts come from."""
    attribute: str      # value written to the attribute column
    table: str          # staged table to read from
    successes: str      # SQL expression for makes
    trials: str         # SQL expression for attempts
    enabled: bool = True


COUNT_SOURCES = [
    CountSource("free_throw", "boxscore_player", "ftm", "fta"),

    # Enable once the CatchShoot and PullUpShot tracking pulls (Totals) are staged.
    # Check the table and column names match your staging first.
    CountSource("three_cs", "tracking_catch_shoot",
                "catch_shoot_fg3m", "catch_shoot_fg3a", enabled=False),
    CountSource("three_pu", "tracking_pull_up",
                "pull_up_fg3m", "pull_up_fg3a", enabled=False),
]


def source_query(src: CountSource) -> str:
    """SELECT that turns one source into the standard long shape."""
    return f"""
        SELECT
            CAST(player_id AS BIGINT) AS player_id,
            CAST(season AS VARCHAR)   AS season,
            '{src.attribute}'         AS attribute,
            {src.successes}           AS successes,
            {src.trials}              AS trials
        FROM {src.table}
    """


def check_sources_exist(con, sources: list[CountSource]) -> None:
    """Fail with a clear message if a source table or view is missing."""
    existing = {row[0] for row in con.execute(
        "SELECT table_name FROM information_schema.tables").fetchall()}
    missing = sorted({s.table for s in sources if s.table not in existing})
    if missing:
        raise RuntimeError(f"Source tables not found in the warehouse: {missing}")


def check_counts(con, view: str) -> None:
    """Counts must be present and whole numbers. Decimals mean a per-game pull."""
    nulls = con.execute(f"""
        SELECT attribute, COUNT(*) FROM {view}
        WHERE successes IS NULL OR trials IS NULL
        GROUP BY attribute
    """).fetchall()
    if nulls:
        raise ValueError(f"Null makes or attempts (attribute, rows): {nulls}")

    non_whole = con.execute(f"""
        SELECT attribute, COUNT(*) FROM {view}
        WHERE successes != FLOOR(successes) OR trials != FLOOR(trials)
        GROUP BY attribute
    """).fetchall()
    if non_whole:
        raise ValueError(
            f"Non-whole makes or attempts (attribute, rows): {non_whole}. "
            "The source is probably a per-game pull; re-pull it as Totals."
        )


def check_row_counts(con, sources: list[CountSource]) -> None:
    """Each attribute should have exactly one row per source row, per season."""
    for src in sources:
        mismatches = con.execute(f"""
            WITH src AS (
                SELECT CAST(season AS VARCHAR) AS season, COUNT(*) AS n
                FROM {src.table} GROUP BY 1
            ),
            out AS (
                SELECT season, COUNT(*) AS n
                FROM {OUTPUT_TABLE} WHERE attribute = '{src.attribute}' GROUP BY 1
            )
            SELECT COALESCE(src.season, out.season), src.n, out.n
            FROM src FULL OUTER JOIN out ON src.season = out.season
            WHERE src.n IS DISTINCT FROM out.n
        """).fetchall()
        if mismatches:
            raise RuntimeError(
                f"Row counts differ for {src.attribute} "
                f"(season, source rows, output rows): {mismatches}"
            )


def build_shooting_counts(con) -> None:
    """Stack every enabled source into OUTPUT_TABLE."""
    sources = [s for s in COUNT_SOURCES if s.enabled]
    check_sources_exist(con, sources)

    union_sql = "\nUNION ALL\n".join(source_query(s) for s in sources)
    con.execute(f"CREATE OR REPLACE TEMP VIEW shooting_counts_raw AS {union_sql}")
    check_counts(con, "shooting_counts_raw")

    con.execute(f"""
        CREATE OR REPLACE TABLE {OUTPUT_TABLE} AS
        SELECT player_id, season, attribute,
               CAST(successes AS INTEGER) AS successes,
               CAST(trials AS INTEGER)    AS trials
        FROM shooting_counts_raw
        ORDER BY attribute, season, player_id
    """)
    check_row_counts(con, sources)


def print_summary(con) -> None:
    """Players, totals and league rate per attribute and season."""
    summary = con.execute(f"""
        SELECT attribute, season,
               COUNT(*)        AS players,
               SUM(successes)::BIGINT AS makes,
               SUM(trials)::BIGINT    AS attempts,
               ROUND(SUM(successes)::DOUBLE / NULLIF(SUM(trials), 0), 3) AS league_rate
        FROM {OUTPUT_TABLE}
        GROUP BY attribute, season
        ORDER BY attribute, season
    """).df()
    print(summary.to_string(index=False))


def main() -> int:
    con = duckdb.connect(DB_PATH)
    con.execute("SHOW TABLES").fetchall()
    con.execute("SELECT table_name FROM duckdb_tables;").fetchall()
    try:
        build_shooting_counts(con)
        print(f"Built {OUTPUT_TABLE}\n")
        print_summary(con)
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())