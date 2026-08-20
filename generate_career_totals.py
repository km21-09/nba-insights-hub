import pandas as pd

df = pd.read_csv("archive/PlayerStatistics.csv", low_memory=False)

# Build fullName column
df["fullName"] = df["firstName"].str.strip() + " " + df["lastName"].str.strip()

# List of columns we expect to be numeric
numeric_cols = [
    "points", "assists", "blocks", "steals",
    "fieldGoalsAttempted", "fieldGoalsMade", "fieldGoalsPercentage",
    "threePointersAttempted", "threePointersMade", "threePointersPercentage",
    "freeThrowsAttempted", "freeThrowsMade", "freeThrowsPercentage",
    "reboundsDefensive", "reboundsOffensive", "reboundsTotal",
    "foulsPersonal", "turnovers", "plusMinusPoints", "numMinutes"
]

# Convert to numeric, forcing errors to NaN
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Now aggregate safely
career_totals = df.groupby("fullName").agg(
    games_played=("gameId", "nunique"),
    total_points=("points", "sum"),
    avg_points=("points", "mean"),
    total_rebounds=("reboundsTotal", "sum"),
    avg_rebounds=("reboundsTotal", "mean"),
    total_assists=("assists", "sum"),
    avg_assists=("assists", "mean"),
    avg_fg_percentage=("fieldGoalsPercentage", "mean"),
    avg_three_pt_percentage=("threePointersPercentage", "mean"),
    avg_ft_percentage=("freeThrowsPercentage", "mean"),
    avg_minutes=("numMinutes", "mean"),
    total_steals=("steals", "sum"),
    total_blocks=("blocks", "sum"),
    total_turnovers=("turnovers", "sum")
).reset_index()

career_totals.to_csv("data/career_totals.csv", index=False)

print("career_totals.csv regenerated with", len(career_totals), "players")
