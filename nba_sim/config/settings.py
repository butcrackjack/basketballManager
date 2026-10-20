"""
Shared settings for the whole project. Import from here instead of
hard-coding paths or seasons in individual scripts.
"""

from pathlib import Path

# settings.py -> config/ -> nba_sim/
NBA_SIM_DIR = Path(__file__).resolve().parents[1]

# Data locations
DATA_DIR = NBA_SIM_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
STAGING_DIR = DATA_DIR / "staging"
DB_PATH = DATA_DIR / "warehouse.duckdb"   # yet to specify name
PARQUET_DIR = DATA_DIR / "parquet"

# Seasons in the dataset, oldest first
SEASONS = ["2023-24", "2024-25", "2025-26"]
CURRENT_SEASON = SEASONS[-1]