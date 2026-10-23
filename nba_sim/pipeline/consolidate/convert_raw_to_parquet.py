from pathlib import Path
import pandas as pd
import os

raw_dir = Path("nba_sim/data/raw")
parquet_dir = Path("nba_sim/data/parquet")

SEASONS = ['2023-24', '2024-25', '2025-26']

def convert_to_parquet(file: str | Path | None = None):
    if file is None:
        csv_paths = list(raw_dir.rglob("*.csv"))
    else:
        path = Path(file)
        if not path.exists():
            path = raw_dir / path          # allow paths relative to raw_dir
        if not path.exists():
            raise FileNotFoundError(f"No such CSV: {file}")
        csv_paths = [path]

    for csv_path in csv_paths:
        relative = csv_path.resolve().relative_to(raw_dir.resolve())
        out_path = (parquet_dir / relative).with_suffix(".parquet")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(csv_path, dtype={"GAME_ID": str})
        df.to_parquet(out_path, index=False)

        print(f"{csv_path} -> {out_path}")

"""
for season in SEASONS:
    convert_to_parquet(f"nba_sim/data/raw/{season}/boxscore_player.csv")
    convert_to_parquet(f"nba_sim/data/raw/{season}/boxscore_team.csv")
    convert_to_parquet(f"nba_sim/data/raw/{season}/hustle.csv")
    convert_to_parquet(f"nba_sim/data/raw/{season}/lebron.csv")
    convert_to_parquet(f"nba_sim/data/raw/{season}/lineups.csv")
    convert_to_parquet(f"nba_sim/data/raw/{season}/matchups.csv")
    convert_to_parquet(f"nba_sim/data/raw/{season}/playbyplays.csv")
    convert_to_parquet(f"nba_sim/data/raw/{season}/playtypes.csv")
    convert_to_parquet(f"nba_sim/data/raw/{season}/PTDefense.csv")
    convert_to_parquet(f"nba_sim/data/raw/{season}/shotLocations.csv")
    convert_to_parquet(f"nba_sim/data/raw/{season}/teamDef.csv")
"""

p = r"nba_sim/data/raw"

for root, dirs, files in os.walk(p):
    for n in files:
        if(n == "count_rows.py" or n == ".DS_Store"):
            #print("GAHHAGHAGHG")
            continue
        print(f"{root}/{n}")
        convert_to_parquet(f"{root}/{n}")