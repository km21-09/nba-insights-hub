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

# ---------------------- VACUUM (reclaim unused space) ----------------------
print("Running VACUUM to shrink the database ...")
conn.execute("VACUUM")
conn.close()

db_size = os.path.getsize(DB_PATH) / (1024 * 1024)
print(f"nba.db created: {db_size:.1f} MB")

# ---------------------- COMPRESS (gzip for faster download) ----------------------
import gzip
import shutil

GZ_PATH = DB_PATH + ".gz"
print("Compressing nba.db to nba.db.gz ...")

with open(DB_PATH, "rb") as f_in:
    with gzip.open(GZ_PATH, "wb", compresslevel=6) as f_out:
        shutil.copyfileobj(f_in, f_out)

gz_size = os.path.getsize(GZ_PATH) / (1024 * 1024)
print(f"\nDone.")
print(f"  {DB_PATH} ({db_size:.1f} MB)  <- keep locally for testing")
print(f"  {GZ_PATH} ({gz_size:.1f} MB)  <- upload THIS to GitHub Releases instead")
print(f"\nCompression saved {db_size - gz_size:.1f} MB ({(1 - gz_size/db_size) * 100:.0f}% smaller)")