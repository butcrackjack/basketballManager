import duckdb
from nba_sim.config.settings import DB_PATH, STAGING_DIR

con = duckdb.connect(str(DB_PATH))          # creates the file if it doesn't exist
for path in sorted(STAGING_DIR.glob("*.parquet")):
    con.execute(f"CREATE OR REPLACE VIEW {path.stem} AS SELECT * FROM '{path.as_posix()}'")
    print("view:", path.stem)
con.close()