from pathlib import Path
import pandas as pd

raw_dir = Path("nba_sim/data/raw")
parquet_dir = Path("nba_sim/data/parquet")

problems = []

for csv_path in raw_dir.rglob("*.csv"):
    pq_path = (parquet_dir / csv_path.relative_to(raw_dir)).with_suffix(".parquet")

    if not pq_path.exists():
        problems.append(f"MISSING  {pq_path}")
        continue

    csv_df = pd.read_csv(csv_path, dtype={"GAME_ID": str})
    pq_df = pd.read_parquet(pq_path)

    try:
        pd.testing.assert_frame_equal(csv_df, pq_df)
    except AssertionError as e:
        problems.append(f"MISMATCH {pq_path}\n{e}")

print("All files match" if not problems else "\n\n".join(problems))