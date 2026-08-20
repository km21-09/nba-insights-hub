from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
import urllib.request
from flask_cors import CORS

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
DB_PATH = os.path.join(DATA_DIR, "nba.db")

# TODO: replace with your real GitHub Release download URL once uploaded
NBA_DB_URL = "https://github.com/km21-09/nba-insights-hub/releases/download/v1.0-data/nba.db"


def ensure_db_exists():
    """Download nba.db from GitHub Releases if it's not already present locally.
    Runs once per fresh deploy/container, so subsequent restarts skip this."""
    if os.path.exists(DB_PATH):
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"nba.db not found locally, downloading from {NBA_DB_URL} ...")

    tmp_path = DB_PATH + ".tmp"
    urllib.request.urlretrieve(NBA_DB_URL, tmp_path)
    os.rename(tmp_path, DB_PATH)  # atomic swap, avoids partial-file issues

    print("Download complete.")


ensure_db_exists()


def get_db():
    """Open a fresh connection per request (SQLite + Flask best practice)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def root():
    return send_from_directory(app.static_folder, "index.html")


# ---------------------- PLAYER SEARCH ----------------------
@app.route("/api/player-search")
def player_search():
    q = request.args.get("q", "").lower()
    if not q:
        return jsonify([])

    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT fullName FROM game_stats WHERE playerName_lower LIKE ? LIMIT 5",
        (f"%{q}%",)
    ).fetchall()
    conn.close()

    return jsonify([row["fullName"] for row in rows])


# ---------------------- PLAYER TOTAL STATS ----------------------
@app.route("/api/player-stats")
def player_stats():
    player = request.args.get("player", "").lower()

    conn = get_db()
    row = conn.execute(
        """
        SELECT
            SUM(points) as points,
            SUM(assists) as assists,
            SUM(blocks) as blocks,
            SUM(steals) as steals,
            SUM(fieldGoalsMade) as fgm,
            SUM(fieldGoalsAttempted) as fga,
            SUM(threePointersMade) as threes_made,
            SUM(threePointersAttempted) as threes_attempted,
            SUM(freeThrowsMade) as ftm,
            SUM(freeThrowsAttempted) as fta
        FROM game_stats
        WHERE playerName_lower LIKE ?
        """,
        (f"%{player}%",)
    ).fetchone()
    conn.close()

    if row is None or row["points"] is None:
        return jsonify({"error": "Player not found"}), 404

    totals = dict(row)
    totals["fg_pct"] = round((totals["fgm"] / totals["fga"]) * 100, 1) if totals["fga"] else 0
    totals["three_pct"] = round((totals["threes_made"] / totals["threes_attempted"]) * 100, 1) if totals["threes_attempted"] else 0
    totals["ft_pct"] = round((totals["ftm"] / totals["fta"]) * 100, 1) if totals["fta"] else 0

    return jsonify(totals)


# ---------------------- SHOT CHART ----------------------
@app.route("/api/shots")
def shots():
    player = request.args.get("player", "").lower()

    conn = get_db()
    rows = conn.execute(
        """
        SELECT LOC_X, LOC_Y, SHOT_MADE, SHOT_DISTANCE, SHOT_TYPE,
               QUARTER, MINS_LEFT, SECS_LEFT, GAME_DATE
        FROM shots
        WHERE playerName_lower LIKE ?
        """,
        (f"%{player}%",)
    ).fetchall()
    conn.close()

    shots_list = []
    for row in rows:
        shot_result = "Made" if row["SHOT_MADE"] == 1 else "Missed"
        shots_list.append({
            "x": float(row["LOC_X"]),
            "y": float(row["LOC_Y"]),
            "shotResult": shot_result,
            "shotDistance": float(row["SHOT_DISTANCE"]),
            "actionType": row["SHOT_TYPE"],
            "quarter": int(row["QUARTER"]),
            "timeLeft": f"{row['MINS_LEFT']}:{row['SECS_LEFT']}",
            "gameDate": row["GAME_DATE"]
        })

    return jsonify(shots_list)


# ---------------------- TOTAL LEADERBOARD ----------------------
@app.route("/api/leaderboard")
def leaderboard():
    stat = request.args.get("stat", "PTS").upper()
    top = int(request.args.get("top", 5))

    stat_map = {
        "PTS": "points",
        "REB": "reboundsTotal",
        "AST": "assists",
        "BLK": "blocks"
    }

    col = stat_map.get(stat)
    if col is None:
        return jsonify({"error": "Invalid stat"}), 400

    conn = get_db()
    rows = conn.execute(
        f"""
        SELECT fullName, SUM({col}) as total
        FROM game_stats
        GROUP BY fullName
        ORDER BY total DESC
        LIMIT ?
        """,
        (top,)
    ).fetchall()
    conn.close()

    return jsonify({row["fullName"]: row["total"] for row in rows})


# ---------------------- SINGLE-GAME RECORDS ----------------------
@app.route("/api/single-game-records")
def single_game_records():
    stat = request.args.get("stat", "").upper()

    # Hardcoded Google-verified historical records for PTS & REB
    if stat == "PTS":
        return jsonify([
            {"player": "Wilt Chamberlain", "points": 100, "rebounds": 25, "assists": 2, "blocks": 0, "date": "1962-03-02"},
            {"player": "Kobe Bryant", "points": 81, "rebounds": 6, "assists": 2, "blocks": 1, "date": "2006-01-22"},
            {"player": "David Thompson", "points": 73, "rebounds": 7, "assists": 2, "blocks": 0, "date": "1978-04-09"},
            {"player": "Wilt Chamberlain", "points": 73, "rebounds": 14, "assists": 2, "blocks": 0, "date": "1962-01-13"},
            {"player": "Wilt Chamberlain", "points": 73, "rebounds": 18, "assists": 2, "blocks": 0, "date": "1962-01-21"}
        ])

    if stat == "REB":
        return jsonify([
            {"player": "Wilt Chamberlain", "points": 32, "rebounds": 55, "assists": 2, "blocks": 0, "date": "1960-11-24"},
            {"player": "Bill Russell", "points": 23, "rebounds": 51, "assists": 5, "blocks": 0, "date": "1960-02-05"},
            {"player": "Wilt Chamberlain", "points": 34, "rebounds": 43, "assists": 2, "blocks": 0, "date": "1963-01-02"},
            {"player": "Wilt Chamberlain", "points": 29, "rebounds": 43, "assists": 2, "blocks": 0, "date": "1962-03-11"},
            {"player": "Wilt Chamberlain", "points": 26, "rebounds": 42, "assists": 2, "blocks": 0, "date": "1961-01-19"}
        ])

    # AST & BLK from dataset
    stat_map = {
        "AST": "assists",
        "BLK": "blocks"
    }

    col = stat_map.get(stat)
    if col is None:
        return jsonify([])

    conn = get_db()
    rows = conn.execute(
        f"""
        SELECT fullName, points, reboundsTotal, assists, blocks, gameDate
        FROM game_stats
        ORDER BY {col} DESC
        LIMIT 5
        """
    ).fetchall()
    conn.close()

    records = []
    for row in rows:
        records.append({
            "player": row["fullName"],
            "points": int(row["points"]),
            "rebounds": int(row["reboundsTotal"]),
            "assists": int(row["assists"]),
            "blocks": int(row["blocks"]),
            "date": row["gameDate"] if row["gameDate"] is not None else "N/A"
        })

    return jsonify(records)


# ---------------------- PLAYER COMPARISON ----------------------
@app.route("/api/compare")
def compare_players():
    p1 = request.args.get("p1", "").lower()
    p2 = request.args.get("p2", "").lower()

    def get_stats(conn, player):
        row = conn.execute(
            """
            SELECT
                SUM(points) as points,
                SUM(assists) as assists,
                SUM(reboundsTotal) as rebounds,
                SUM(blocks) as blocks,
                SUM(fieldGoalsMade) as fgm,
                SUM(fieldGoalsAttempted) as fga,
                SUM(threePointersMade) as threes_made,
                SUM(threePointersAttempted) as threes_attempted,
                SUM(freeThrowsMade) as ftm,
                SUM(freeThrowsAttempted) as fta,
                COUNT(*) as games
            FROM game_stats
            WHERE playerName_lower LIKE ?
            """,
            (f"%{player}%",)
        ).fetchone()

        if row is None or row["points"] is None:
            return None

        return {
            "points": row["points"],
            "assists": row["assists"],
            "rebounds": row["rebounds"],
            "blocks": row["blocks"],
            "fg_pct": round((row["fgm"] / row["fga"]) * 100, 1) if row["fga"] else 0,
            "three_pct": round((row["threes_made"] / row["threes_attempted"]) * 100, 1) if row["threes_attempted"] else 0,
            "ft_pct": round((row["ftm"] / row["fta"]) * 100, 1) if row["fta"] else 0,
            "games": row["games"]
        }

    conn = get_db()
    stats1 = get_stats(conn, p1)
    stats2 = get_stats(conn, p2)
    conn.close()

    if not stats1 or not stats2:
        return jsonify({"error": "One or both players not found"}), 404

    return jsonify({"p1": stats1, "p2": stats2})


if __name__ == "__main__":
    app.run(debug=True)