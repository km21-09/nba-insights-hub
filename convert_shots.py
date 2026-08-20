import pyarrow.parquet as pq
import csv
import os

PARQUET_PATH = r"C:\Users\kanav\Desktop\nba-insight-hub\archive\PlayByPlay.parquet"
OUTPUT_PATH = "data/shot_logs.csv"

os.makedirs("data", exist_ok=True)

COLUMNS = [
    "playerName",
    "x",
    "y",
    "shotResult",
    "shotDistance",
    "actionType",     # ⭐ ADD THIS BACK
    "isFieldGoal"
]

parquet_file = pq.ParquetFile(PARQUET_PATH)

with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(COLUMNS)

for batch in parquet_file.iter_batches(batch_size=50000, columns=COLUMNS):
    df = batch.to_pandas()

    df["isFieldGoal"] = df["isFieldGoal"].fillna(False)

    # Keep only real shots
    df = df[df["isFieldGoal"] == True]

    # Drop rows without coordinates
    df = df.dropna(subset=["x", "y", "playerName"])

    df.to_csv(OUTPUT_PATH, mode="a", header=False, index=False)

print("✅ Finished converting FULL parquet file with ALL SHOTS!")
