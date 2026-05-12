/* -------------------- A* CHASE ANALYZER -------------------- */
async function analyze() {
    const target = document.getElementById("target").value;
    const current = document.getElementById("current").value;
    const balls = document.getElementById("balls").value;
    const wickets = document.getElementById("wickets").value;

    const response = await fetch("http://127.0.0.1:5000/analyze_chase", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target, current, balls, wickets })
    });

    const data = await response.json();

    document.getElementById("result").innerHTML = `
        <h3>${data.result}</h3>
        <p><b>Win Probability:</b> ${data.probability}%</p>
        <p><b>Suggested Run Pattern:</b> ${data.pattern.join(", ")}</p>
    `;
}

/* -------------------- MINIMAX STRATEGY -------------------- */
async function getMinimax() {
    const payload = {
        target: document.getElementById("target").value,
        current: document.getElementById("current").value,
        balls: document.getElementById("balls").value,
        wickets: document.getElementById("wickets").value
    };

    const res = await fetch("http://127.0.0.1:5000/minimax_strategy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    document.getElementById("strategyBox").innerHTML = `
        <h3>🧠 AI Strategy Advisor</h3>
        <p><b>Recommended Style:</b> ${data.strategy}</p>
        <p><b>Confidence:</b> ${data.confidence}%</p>
        <p>${data.reason}</p>
    `;
}

/* -------------------- LIVE MATCH ENGINE -------------------- */
let runChart, probChart, rrrChart;
let interval = null;

let ball = 0;
let runs = 0;
let targetScore = 0;
let totalBalls = 0;

let wicketsLeft = 0;
let totalWickets = 10;
let lastWicketBall = -1;

function initCharts() {

    runChart = new Chart(document.getElementById("runChart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Runs Scored",
                    data: [],
                    borderWidth: 2,
                    tension: 0.3
                },
                {
                    label: "Target",
                    data: [],
                    borderDash: [8, 6],
                    borderWidth: 2,
                    pointRadius: 0
                }
            ]
        },
        options: {
            scales: { y: { beginAtZero: true } }
        }
    });

    probChart = new Chart(document.getElementById("probChart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Win Probability %",
                data: [],
                borderWidth: 2,
                tension: 0.3
            }]
        },
        options: {
            scales: { y: { min: 0, max: 100 } }
        }
    });

    rrrChart = new Chart(document.getElementById("rrrChart"), {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Required Run Rate",
                data: [],
                borderWidth: 2,
                tension: 0.3
            }]
        },
        options: {
            scales: { y: { beginAtZero: true } }
        }
    });
}

function start() {
    ball = 0;
    lastWicketBall = -1;

    runs = parseInt(document.getElementById("current").value);
    targetScore = parseInt(document.getElementById("target").value);
    totalBalls = parseInt(document.getElementById("balls").value);
    wicketsLeft = parseInt(document.getElementById("wickets").value);

    initCharts();
    interval = setInterval(simulateBall, 1000);
}

function pause() {
    clearInterval(interval);
}

function resume() {
    interval = setInterval(simulateBall, 1000);
}

function simulateBall() {

    /* 🛑 STOP CONDITIONS */
    if (runs >= targetScore || ball >= totalBalls || wicketsLeft <= 0) {
        clearInterval(interval);
        interval = null;

        if (runs >= targetScore) {
            alert("🏆 Target Chased Successfully!");
        } else {
            alert("❌ Chase Failed!");
        }
        return;
    }

    ball++;

    /* 🎯 BALL OUTCOME */
    let wicketChance =
        wicketsLeft >= 7 ? 0.05 :
        wicketsLeft >= 4 ? 0.08 :
        0.12; // collapse pressure

    let wicketFell = Math.random() < wicketChance;
    let run = wicketFell ? 0 : Math.floor(Math.random() * 7);

    if (wicketFell) wicketsLeft--;
    runs += run;

    /* --- RUN CHART --- */
    runChart.data.labels.push("Ball " + ball);
    runChart.data.datasets[0].data.push(runs);
    runChart.data.datasets[1].data.push(targetScore);
    runChart.update();

    /* ------------------ SMART WIN PROBABILITY ------------------ */

    let ballsRemaining = totalBalls - ball;
    let runsNeeded = Math.max(0, targetScore - runs);

    /* Base progress */
    let progress = runs / targetScore;

    /* Required Run Rate pressure */
    let rrr = ballsRemaining > 0
        ? (runsNeeded / ballsRemaining) * 6
        : 99;

    let rrrPenalty =
        rrr <= 6 ? 1 :
        rrr <= 9 ? 0.75 :
        rrr <= 12 ? 0.5 :
        0.3;

    /* Wicket pressure */
    let wicketPenalty =
        wicketsLeft >= 7 ? 1 :
        wicketsLeft >= 4 ? 0.7 :
        0.4;

    /* Final probability */
    let probability =
        progress * 100 *
        rrrPenalty *
        wicketPenalty;

    /* Extra shock on wicket */
    if (wicketFell) {
        probability *= 0.65;
        alert(`⚠ WICKET FALLEN! ${wicketsLeft} wickets left`);
    }

    /* Random nerves factor */
    probability *= (0.9 + Math.random() * 0.2);

    probability = Math.max(0, Math.min(100, Math.round(probability)));

    /* --- PROBABILITY CHART --- */
    probChart.data.labels.push(
        wicketFell ? `Ball ${ball} ⚠` : `Ball ${ball}`
    );

    probChart.data.datasets[0].data.push(probability);
    probChart.update();

    /* --- REQUIRED RUN RATE CHART --- */
    rrrChart.data.labels.push("Ball " + ball);
    rrrChart.data.datasets[0].data.push(rrr.toFixed(2));
    rrrChart.update();
}

/* -------------------- INIT MATCH -------------------- */
async function startSimulation() {
    const payload = {
        target: document.getElementById("target").value,
        current: document.getElementById("current").value,
        balls: document.getElementById("balls").value,
        wickets: document.getElementById("wickets").value
    };

    const res = await fetch("http://127.0.0.1:5000/init_match", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    if (data.status) {
        alert("✅ Live match initialized. Use Start below.");
    }
}

/* -------------------- WHAT-IF SCENARIO (SEPARATE ENGINE) -------------------- */

async function simulate(type) {

    const payload = {
        target: parseInt(document.getElementById("target").value),
        current: parseInt(document.getElementById("current").value),
        balls: parseInt(document.getElementById("balls").value),
        wickets: parseInt(document.getElementById("wickets").value),
        scenario: type
    };

    const res = await fetch("http://127.0.0.1:5000/what_if", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    document.getElementById("simulation-result").innerHTML = `
        <h3>🧪 What-If Scenario Result</h3>
        <p><b>Scenario:</b> ${data.scenario}</p>
        <p><b>New Score:</b> ${data.new_score}</p>
        <p><b>Balls Left:</b> ${data.balls_left}</p>
        <p><b>Wickets Left:</b> ${data.wickets_left}</p>
        <p><b>Win Probability:</b> ${data.probability}%</p>
        <p><i>This analysis does not affect live simulation.</i></p>
    `;
}