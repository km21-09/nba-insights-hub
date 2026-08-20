import pandas as pd

# Read with low_memory=False to avoid dtype warnings
df = pd.read_csv("archive/PlayerStatistics.csv", low_memory=False)

# Build fullName column
df["fullName"] = df["firstName"].str.strip() + " " + df["lastName"].str.strip()

# Get unique player names
players = sorted(df["fullName"].dropna().unique())

with open("data/player_list.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(players))

print("player_list.txt regenerated with", len(players), "players")
