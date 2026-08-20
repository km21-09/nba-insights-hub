"""
Builds nba.db (SQLite) from the trimmed CSVs.

Run this ONCE locally (or whenever your source data changes):
    python build_db.py

Requires: pandas (pip install pandas)

Output:
    data/nba.db   <-- commit THIS to your repo instead of the big CSVs
"""

import pandas as pd
import sqlite3
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DATA_DIR, "nba.db")

# Remove old db if it exists, so this script can be re-run safely
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)

# ---------------------- SHOTS TABLE ----------------------
print("Loading shot_logs_trimmed.csv ...")
shot_df = pd.read_csv(os.path.join(DATA_DIR, "shot_logs_trimmed.csv"))

shot_df["playerName_lower"] = shot_df["PLAYER_NAME"].str.lower()
shot_df["SHOT_MADE"] = shot_df["SHOT_MADE"].astype(int)

shot_df.to_sql("shots", conn, if_exists="replace", index=False)
print(f"  -> wrote {len(shot_df)} rows to 'shots' table")

# ---------------------- GAME STATS TABLE ----------------------
print("Loading player_game_stats_trimmed.csv ...")
game_df = pd.read_csv(os.path.join(DATA_DIR, "player_game_stats_trimmed.csv"))

game_df["playerName_lower"] = game_df["fullName"].str.lower()

game_df.to_sql("game_stats", conn, if_exists="replace", index=False)
print(f"  -> wrote {len(game_df)} rows to 'game_stats' table")

# ---------------------- CAREER TOTALS TABLE ----------------------
career_path = os.path.join(DATA_DIR, "career_totals.csv")
if os.path.exists(career_path):
    print("Loading career_totals.csv ...")
    career_df = pd.read_csv(career_path)
    career_df["playerName_lower"] = career_df["fullName"].str.lower()
    career_df.to_sql("career_totals", conn, if_exists="replace", index=False)
    print(f"  -> wrote {len(career_df)} rows to 'career_totals' table")

# ---------------------- INDEXES (for fast lookups) ----------------------
print("Creating indexes ...")
cur = conn.cursor()
cur.execute("CREATE INDEX idx_shots_player ON shots(playerName_lower)")
cur.execute("CREATE INDEX idx_game_player ON game_stats(playerName_lower)")
conn.commit()
conn.close()

db_size = os.path.getsize(DB_PATH) / (1024 * 1024)
print(f"\nDone. Created {DB_PATH} ({db_size:.1f} MB)")
print("Commit this .db file to your repo instead of the large CSVs.")
