"""
Trims shot_logs.csv and player_game_stats.csv down to only the columns
actually used by app.py, and saves smaller versions.

Run this from your project root (same level as the 'data' folder):
    python trim_datasets.py

Requires: pandas (pip install pandas)
"""

import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------- SHOT LOGS ----------------------
shot_cols = [
    "PLAYER_NAME",
    "SHOT_MADE",
    "LOC_X",
    "LOC_Y",
    "SHOT_DISTANCE",
    "SHOT_TYPE",
    "QUARTER",
    "MINS_LEFT",
    "SECS_LEFT",
    "GAME_DATE"
]

shot_in = os.path.join(DATA_DIR, "shot_logs.csv")
shot_out = os.path.join(DATA_DIR, "shot_logs_trimmed.csv")

print(f"Reading {shot_in} ...")
shot_df = pd.read_csv(shot_in, usecols=shot_cols)
shot_df.to_csv(shot_out, index=False)

before = os.path.getsize(shot_in) / (1024 * 1024)
after = os.path.getsize(shot_out) / (1024 * 1024)
print(f"shot_logs.csv: {before:.1f} MB -> {after:.1f} MB (trimmed)\n")

# ---------------------- PLAYER GAME STATS ----------------------
game_cols = [
    "fullName",
    "points",
    "assists",
    "blocks",
    "steals",
    "fieldGoalsMade",
    "fieldGoalsAttempted",
    "threePointersMade",
    "threePointersAttempted",
    "freeThrowsMade",
    "freeThrowsAttempted",
    "reboundsTotal",
    "gameDate"
]

game_in = os.path.join(DATA_DIR, "player_game_stats.csv")
game_out = os.path.join(DATA_DIR, "player_game_stats_trimmed.csv")

print(f"Reading {game_in} ...")
game_df = pd.read_csv(game_in, usecols=game_cols)
game_df.to_csv(game_out, index=False)

before = os.path.getsize(game_in) / (1024 * 1024)
after = os.path.getsize(game_out) / (1024 * 1024)
print(f"player_game_stats.csv: {before:.1f} MB -> {after:.1f} MB (trimmed)\n")

print("Done. Trimmed files saved as:")
print(f"  {shot_out}")
print(f"  {game_out}")
print("\nIf these look good, rename them to replace the originals")
print("(or update app.py to point to the _trimmed versions).")
