import pandas as pd
from pathlib import Path

SEASONS = ['2023-24','2024-25','2025-26']


# convert lebron data season attribute to be correct
def convert_season_lebron():

    lebron_seasons = [2024,2025,2026]

    season = 0

    while season < 3:
        
        path = f"nba_sim/data/parquet/{SEASONS[season]}/lebron_data.parquet"
        df = pd.read_parquet(path)
        df["SEASON"] = df["SEASON"].replace({lebron_seasons[season]:SEASONS[season]})

        df.to_parquet(path, index=False)

        counts = df['SEASON'].value_counts()
        print(counts)
        season += 1


# convert madeglaf to be boolean
def convert_made_flag_pbp():
    for season in SEASONS:

        path = f"nba_sim/data/parquet/{season}/playbyplays.parquet"

        df = pd.read_parquet(path)
        df["SHOT_MADE_FLAG"] = df["SHOT_MADE_FLAG"] == "Made"
        df.to_parquet(path, index=False)

        print(f"Updated nba_sim/data/parquet/{season}/playbyplays.parquet")

        counts = df['SHOT_MADE_FLAG'].value_counts()
        print(counts)


# convert shot made flag and shot value to be correct for free throws
def convert_made_flag_and_ft():
    RAW = Path("nba_sim/data/raw")
    PARQUET = Path("nba_sim/data/parquet")

    for season in SEASONS:
        df = pd.read_csv(RAW / season / "playbyplays.csv", dtype={"GAME_ID": str})

        # Field goals: raw text -> boolean
        df["SHOT_MADE_FLAG"] = df["SHOT_MADE_FLAG"] == "Made"

        # Free throws: no flag in the raw data, so derive it from the description
        is_ft = df["ACTION_TYPE"] == "Free Throw"
        is_miss = df["DESCRIPTION"].str.startswith("MISS", na=False)
        df.loc[is_ft, "SHOT_VALUE"] = 1
        df.loc[is_ft, "SHOT_MADE_FLAG"] = ~is_miss[is_ft]

        out = PARQUET / season / "playbyplays.parquet"
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out, index=False)

        fg_made = (df["SHOT_MADE_FLAG"] & (df["IS_FIELD_GOAL"] == 1)).sum()
        ft_made = (df["SHOT_MADE_FLAG"] & is_ft).sum()
        print(f"{season}: {fg_made} made FGs, {ft_made} made FTs")

# convert EVENT_TYPE in shotLocations to bool
def convert_event_type_shotLoc():
    for season in SEASONS:

        path = f"nba_sim/data/parquet/{season}/shotLocations.parquet"

        df = pd.read_parquet(path)
        df["EVENT_TYPE"] = df["EVENT_TYPE"] == "Made Shot"
        df.to_parquet(path, index=False)

        print(f"Updated nba_sim/data/parquet/{season}/shotLocations.parquet")

        counts = df['EVENT_TYPE'].value_counts()
        print(counts)

