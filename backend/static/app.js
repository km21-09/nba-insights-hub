// ---------------------- TAB SWITCHING ----------------------
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
  });
});

// ---------------------- PLAYER SEARCH ----------------------
async function searchPlayers(query, dropdownId) {
  const res = await fetch(`/api/player-search?q=${encodeURIComponent(query.toLowerCase())}`);
  const data = await res.json();
  const dropdown = document.getElementById(dropdownId);
  dropdown.innerHTML = "";
  data.forEach(p => {
    const option = document.createElement("option");
    option.value = p;
    option.textContent = p;
    dropdown.appendChild(option);
  });
}

// Autofill dropdown → input
["playerDropdown","shotPlayerDropdown","compareDropdown1","compareDropdown2"].forEach((id, idx) => {
  document.getElementById(id).addEventListener("change", () => {
    const val = document.getElementById(id).value;
    const inputMap = ["player-input","shotPlayer","compareInput1","compareInput2"];
    document.getElementById(inputMap[idx]).value = val;
  });
});

// ---------------------- STATS TAB ----------------------
document.getElementById("player-input").addEventListener("input", e => {
  searchPlayers(e.target.value, "playerDropdown");
});

document.getElementById("search-button").addEventListener("click", () => {
  const player = document.getElementById("playerDropdown").value || document.getElementById("player-input").value;
  if (player) loadStats(player);
});

async function loadStats(player) {
  const res = await fetch(`/api/player-stats?player=${encodeURIComponent(player.toLowerCase())}`);
  const data = await res.json();

  if (data.error) {
    document.getElementById("player-name").textContent = data.error;
    return;
  }

  document.getElementById("player-name").textContent = player;
  document.getElementById("points").textContent = data.points;
  document.getElementById("assists").textContent = data.assists;
  document.getElementById("blocks").textContent = data.blocks;
  document.getElementById("steals").textContent = data.steals;

  document.getElementById("fg").textContent = data.fg_pct + "%";
  document.getElementById("fgMadeTaken").textContent = `${data.fgm}/${data.fga}`;

  document.getElementById("threePct").textContent = data.three_pct + "%";
  document.getElementById("threeMadeTaken").textContent = `${data.threes_made}/${data.threes_attempted}`;

  document.getElementById("ftPct").textContent = data.ft_pct + "%";
  document.getElementById("ftMadeTaken").textContent = `${data.ftm}/${data.fta}`;
}

// ---------------------- PLAYER COMPARISON ----------------------
document.getElementById("compareInput1").addEventListener("input", e => {
  searchPlayers(e.target.value, "compareDropdown1");
});

document.getElementById("compareInput2").addEventListener("input", e => {
  searchPlayers(e.target.value, "compareDropdown2");
});

document.getElementById("compareButton").addEventListener("click", async () => {
  const p1 = document.getElementById("compareDropdown1").value || document.getElementById("compareInput1").value;
  const p2 = document.getElementById("compareDropdown2").value || document.getElementById("compareInput2").value;

  const res = await fetch(`/api/compare?p1=${encodeURIComponent(p1.toLowerCase())}&p2=${encodeURIComponent(p2.toLowerCase())}`);
  const data = await res.json();

  if (data.error) {
    document.getElementById("compareResult").innerHTML = `<p>${data.error}</p>`;
    return;
  }

  const p1Stats = data.p1;
  const p2Stats = data.p2;

  document.getElementById("compareResult").innerHTML = `
    <table>
      <tr><th>Stat</th><th>${p1}</th><th>${p2}</th></tr>
      <tr><td>Points</td><td>${p1Stats.points}</td><td>${p2Stats.points}</td></tr>
      <tr><td>Assists</td><td>${p1Stats.assists}</td><td>${p2Stats.assists}</td></tr>
      <tr><td>Rebounds</td><td>${p1Stats.rebounds}</td><td>${p2Stats.rebounds}</td></tr>
      <tr><td>Blocks</td><td>${p1Stats.blocks}</td><td>${p2Stats.blocks}</td></tr>
      <tr><td>FG%</td><td>${p1Stats.fg_pct}%</td><td>${p2Stats.fg_pct}%</td></tr>
      <tr><td>3PT%</td><td>${p1Stats.three_pct}%</td><td>${p2Stats.three_pct}%</td></tr>
      <tr><td>FT%</td><td>${p1Stats.ft_pct}%</td><td>${p2Stats.ft_pct}%</td></tr>
      <tr><td>Games Played</td><td>${p1Stats.games}</td><td>${p2Stats.games}</td></tr>
    </table>
  `;
});

// ---------------------- SHOT CHART ----------------------
document.getElementById("shotPlayer").addEventListener("input", e => {
  searchPlayers(e.target.value, "shotPlayerDropdown");
});

let globalShots = [];

document.getElementById("loadShots").addEventListener("click", () => {
  const player = document.getElementById("shotPlayerDropdown").value || document.getElementById("shotPlayer").value;
  if (player) loadShotChart(player);
});

async function loadShotChart(player) {
  const res = await fetch(`/api/shots?player=${encodeURIComponent(player.toLowerCase())}`);
  globalShots = await res.json();
  drawRawShots();
}

// ---------------------- COURT DRAWING (NBA.com style, basket at TOP) ----------------------
function drawCourt(ctx) {

    const W = ctx.canvas.width;
    const H = ctx.canvas.height;

    ctx.clearRect(0, 0, W, H);

    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);

    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 2;

    function sx(ft) {
        return (ft / 94) * W;
    }

    function sy(ft) {
        return ((25 - ft) / 50) * H;
    }

    // Outer boundary
    ctx.strokeRect(0, 0, W, H);

    // Half court
    ctx.beginPath();
    ctx.moveTo(sx(47), 0);
    ctx.lineTo(sx(47), H);
    ctx.stroke();

    // Center circle
    ctx.beginPath();
    ctx.arc(
        sx(47),
        sy(0),
        sx(6),
        0,
        Math.PI * 2
    );
    ctx.stroke();

    drawBasket(ctx, sx, sy, true);
    drawBasket(ctx, sx, sy, false);
}
function drawBasket(ctx, sx, sy, leftSide) {

    const hoopX = leftSide ? 5.25 : 94 - 5.25;
    const hoopY = 0;

    // Paint
    const paintX = leftSide ? 0 : 94 - 19;

    ctx.strokeRect(
        sx(paintX),
        sy(8),
        sx(19),
        sy(-8) - sy(8)
    );

    // Free throw circle
    ctx.beginPath();
    ctx.arc(
        sx(leftSide ? 19 : 75),
        sy(0),
        sx(6),
        0,
        Math.PI * 2
    );
    ctx.stroke();

    // Rim
    ctx.beginPath();
    ctx.arc(
        sx(hoopX),
        sy(0),
        sx(0.75),
        0,
        Math.PI * 2
    );
    ctx.stroke();

    // Backboard
    ctx.beginPath();

    if (leftSide) {
        ctx.moveTo(sx(4), sy(-3));
        ctx.lineTo(sx(4), sy(3));
    } else {
        ctx.moveTo(sx(90), sy(-3));
        ctx.lineTo(sx(90), sy(3));
    }

    ctx.stroke();

    // Restricted area
    ctx.beginPath();

    if (leftSide) {

        ctx.arc(
            sx(hoopX),
            sy(0),
            sx(4),
            -Math.PI / 2,
            Math.PI / 2
        );

    } else {

        ctx.arc(
            sx(hoopX),
            sy(0),
            sx(4),
            Math.PI / 2,
            -Math.PI / 2
        );
    }

    ctx.stroke();

    // Corner 3s
    if (leftSide) {

        ctx.beginPath();
        ctx.moveTo(sx(0), sy(22));
        ctx.lineTo(sx(14), sy(22));
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(sx(0), sy(-22));
        ctx.lineTo(sx(14), sy(-22));
        ctx.stroke();

    } else {

        ctx.beginPath();
        ctx.moveTo(sx(80), sy(22));
        ctx.lineTo(sx(94), sy(22));
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(sx(80), sy(-22));
        ctx.lineTo(sx(94), sy(-22));
        ctx.stroke();
    }

    // 3-point arc
    ctx.beginPath();

    const radius = sx(23.75);

    if (leftSide) {

        ctx.arc(
            sx(hoopX),
            sy(0),
            radius,
            -1.15,
            1.15
        );

    } else {

        ctx.arc(
            sx(hoopX),
            sy(0),
            radius,
            Math.PI - 1.15,
            Math.PI + 1.15
        );
    }

    ctx.stroke();
}
// ---------------------- DOT COORDINATE FIX (scaled + flipped) ----------------------
function convertCoords(s) {

    const W = 940;
    const H = 500;

    let x = s.x;
    let y = s.y;

    // Mirror shots from opposite half
    if (y > 47) {
        y = 94 - y;
        x = -x;
    }

    return {
        x: (y / 94) * W,
        y: ((25 - x) / 50) * H
    };
}

function drawRawShots() {
  const canvas = document.getElementById("court");
  const ctx = canvas.getContext("2d");

  canvas.width = 940;
  canvas.height = 500;

  drawCourt(ctx);

  const showMade = document.getElementById("toggleMade").checked;
  const showMissed = document.getElementById("toggleMissed").checked;

  globalShots.forEach(s => {
    if (s.shotResult === "Made" && !showMade) return;
    if (s.shotResult !== "Made" && !showMissed) return;

    const { x, y } = convertCoords(s);

    ctx.beginPath();
    ctx.arc(x, y, 4, 0, 2 * Math.PI);
    ctx.fillStyle = s.shotResult === "Made" ? "#7cff6b" : "#ff5533";
    ctx.fill();
  });

  document.getElementById("heatmapCanvas").style.display = "none";
}

// ---------------------- HEATMAP ----------------------
function drawHeatmap() {
  const canvas = document.getElementById("heatmapCanvas");
  const ctx = canvas.getContext("2d");

  canvas.width = 940;
  canvas.height = 500;

  const density = Array.from({ length: 940 }, () => Array(500).fill(0));

  globalShots.forEach(s => {
    const { x, y } = convertCoords(s);
    const xi = Math.floor(x);
    const yi = Math.floor(y);
    if (xi >= 0 && xi < 940 && yi >= 0 && yi < 500) {
      for (let dx = -8; dx <= 8; dx++) {
  for (let dy = -8; dy <= 8; dy++) {

    const nx = xi + dx;
    const ny = yi + dy;

    if (
      nx >= 0 &&
      nx < 940 &&
      ny >= 0 &&
      ny < 500
    ) {
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist <= 8) {
        density[nx][ny] += (8 - dist);
      }
    }
  }
}
    }
  });

  const imgData = ctx.createImageData(940, 500);

  for (let x = 0; x < 940; x++) {
    for (let y = 0; y < 500; y++) {
      const value = density[x][y];
      let r = 0;
let g = 0;
let b = 0;

if (value > 0) {

    const intensity = Math.min(value * 8, 255);

    r = intensity;

    if (intensity > 128) {
        g = 255 - (intensity - 128) * 2;
    } else {
        g = intensity * 2;
    }

    g = Math.max(0, Math.min(255, g));
}

      const idx = (y * 940 + x) * 4;
      imgData.data[idx] = r;
      imgData.data[idx + 1] = g;
      imgData.data[idx + 2] = b;
      imgData.data[idx + 3] =
    value > 0
        ? Math.min(value * 3, 180)
        : 0;
    }
  }

  ctx.putImageData(imgData, 0, 0);
  canvas.style.display = "block";
}

document.getElementById("showHeatmap").addEventListener("click", drawHeatmap);
document.getElementById("showRawShots").addEventListener("click", drawRawShots);

document.getElementById("toggleMade").addEventListener("change", drawRawShots);
document.getElementById("toggleMissed").addEventListener("change", drawRawShots);

// ---------------------- LEADERBOARD TOGGLE ----------------------
const seasonBtn = document.getElementById("showSeasonLeaderboard");
const singleBtn = document.getElementById("showSingleGame");

seasonBtn.addEventListener("click", () => {
  seasonBtn.classList.add("active");
  singleBtn.classList.remove("active");

  document.getElementById("seasonLeaderboardSection").style.display = "block";
  document.getElementById("singleGameSection").style.display = "none";
});

singleBtn.addEventListener("click", () => {
  singleBtn.classList.add("active");
  seasonBtn.classList.remove("active");

  document.getElementById("seasonLeaderboardSection").style.display = "none";
  document.getElementById("singleGameSection").style.display = "block";
});

// ---------------------- LEADERBOARDS ----------------------
async function loadLeaderboard(stat, elementId) {
  const res = await fetch(`/api/leaderboard?stat=${stat}&top=5`);
  const data = await res.json();

  const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]);

  let html = `
    <h4>${stat} Leaderboard</h4>
    <table>
      <tr><th>#</th><th>Player</th><th>${stat}</th></tr>
  `;

  sorted.forEach(([player, val], index) => {
    html += `
      <tr>
        <td>${index + 1}</td>
        <td>${player}</td>
        <td>${val}</td>
      </tr>
    `;
  });

  html += "</table>";
  document.getElementById(elementId).innerHTML = html;
}

// ---------------------- SINGLE-GAME RECORDS ----------------------
async function loadSingleGameRecord(stat, elementId) {
  let data;

  if (stat === "PTS") {
    data = [
      { player: "Wilt Chamberlain", points: 100, rebounds: 25, assists: 2, blocks: 0, date: "1962-03-02" },
      { player: "Kobe Bryant", points: 81, rebounds: 6, assists: 2, blocks: 1, date: "2006-01-22" },
      { player: "David Thompson", points: 73, rebounds: 7, assists: 2, blocks: 0, date: "1978-04-09" },
      { player: "Wilt Chamberlain", points: 73, rebounds: 14, assists: 2, blocks: 0, date: "1962-01-13" },
      { player: "Wilt Chamberlain", points: 73, rebounds: 18, assists: 2, blocks: 0, date: "1962-01-21" }
    ];
  } else if (stat === "REB") {
    data = [
      { player: "Wilt Chamberlain", points: 32, rebounds: 55, assists: 2, blocks: 0, date: "1960-11-24" },
      { player: "Bill Russell", points: 23, rebounds: 51, assists: 5, blocks: 0, date: "1960-02-05" },
      { player: "Wilt Chamberlain", points: 34, rebounds: 43, assists: 2, blocks: 0, date: "1963-01-02" },
      { player: "Wilt Chamberlain", points: 29, rebounds: 43, assists: 2, blocks: 0, date: "1962-03-11" },
      { player: "Wilt Chamberlain", points: 26, rebounds: 42, assists: 2, blocks: 0, date: "1961-01-19" }
    ];
  } else {
    const res = await fetch(`/api/single-game-records?stat=${stat}`);
    data = await res.json();
  }

  let html = `
    <h4>${stat} Single-Game Records (Top 5)</h4>
    <table>
      <tr>
        <th>#</th>
        <th>Player</th>
        <th>PTS</th>
        <th>REB</th>
        <th>AST</th>
        <th>BLK</th>
        <th>Date</th>
      </tr>
  `;

  data.forEach((row, index) => {
    html += `
      <tr>
        <td>${index + 1}</td>
        <td>${row.player}</td>
        <td>${row.points}</td>
        <td>${row.rebounds}</td>
        <td>${row.assists}</td>
        <td>${row.blocks}</td>
        <td>${row.date}</td>
      </tr>
    `;
  });

  html += "</table>";
  document.getElementById(elementId).innerHTML = html;
}

// Load all leaderboards
loadLeaderboard("PTS", "leaderboardPTS");
loadLeaderboard("REB", "leaderboardREB");
loadLeaderboard("AST", "leaderboardAST");
loadLeaderboard("BLK", "leaderboardBLK");

// Load all single-game records
loadSingleGameRecord("PTS", "recordPTS");
loadSingleGameRecord("REB", "recordREB");
loadSingleGameRecord("AST", "recordAST");
loadSingleGameRecord("BLK", "recordBLK");