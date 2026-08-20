import pandas as pd

df = pd.read_csv("archive/PlayerStatistics.csv", low_memory=False)
df["fullName"] = df["firstName"].str.strip() + " " + df["lastName"].str.strip()

required_cols = [
    "fullName", "gameId", "gameDate",
    "points", "assists", "reboundsTotal",
    "fieldGoalsAttempted", "fieldGoalsMade", "fieldGoalsPercentage",
    "threePointersAttempted", "threePointersMade", "threePointersPercentage",
    "freeThrowsAttempted", "freeThrowsMade", "freeThrowsPercentage",
    "numMinutes", "steals", "blocks", "turnovers"
]

# Convert numeric columns safely
numeric_cols = [
    "points", "assists", "reboundsTotal",
    "fieldGoalsAttempted", "fieldGoalsMade", "fieldGoalsPercentage",
    "threePointersAttempted", "threePointersMade", "threePointersPercentage",
    "freeThrowsAttempted", "freeThrowsMade", "freeThrowsPercentage",
    "numMinutes", "steals", "blocks", "turnovers"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

filtered = df[required_cols]
filtered.to_csv("data/player_game_stats.csv", index=False)

print("player_game_stats.csv regenerated with", len(filtered), "rows")
