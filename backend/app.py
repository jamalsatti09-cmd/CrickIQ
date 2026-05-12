from flask import Flask, render_template, session, request, jsonify
from flask_cors import CORS
from team_csp import select_team
from minimax_strategy import get_strategy
import pandas as pd
import random

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)
app.secret_key = "crickiq_secret"

CORS(app)

matches = pd.read_csv("data/matches.csv")

# ===================== AI HELPER FUNCTIONS =====================

def calculate_win_probability(target, current, balls, wickets):
    runs_left = target - current

    if runs_left <= 0:
        return 100

    if balls <= 0 or wickets <= 0:
        return 0

    # Required Run Rate
    rrr = (runs_left * 6) / balls

    # ---- Base progress ----
    progress = current / target

    # ---- RRR pressure (non-linear) ----
    if rrr <= 6:
        rrr_factor = 1
    elif rrr <= 9:
        rrr_factor = 0.75
    elif rrr <= 12:
        rrr_factor = 0.5
    else:
        rrr_factor = 0.25

    # ---- Wicket pressure ----
    if wickets >= 7:
        wicket_factor = 1
    elif wickets >= 4:
        wicket_factor = 0.65
    else:
        wicket_factor = 0.35

    probability = progress * 100
    probability *= rrr_factor
    probability *= wicket_factor

    # ---- Nerves randomness ----
    probability *= random.uniform(0.9, 1.1)

    return round(max(0, min(100, probability)), 2)

# ===================== ROUTES =====================

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chase")
def chase():
    return render_template("chase.html")

@app.route("/team")
def team():
    return render_template("team.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ===================== CHASE ANALYZER =====================

@app.route('/analyze_chase', methods=['POST'])
def analyze_chase():
    data = request.json

    target = int(data['target'])
    current = int(data['current'])
    balls_left = int(data['balls'])
    wickets_left = int(data['wickets'])

    required_runs = target - current

    if required_runs <= 0:
        return jsonify({
            "result": "Already Won ✅",
            "probability": 100,
            "pattern": []
        })

    rrr = required_runs / (balls_left / 6)

    if wickets_left >= 7:
        max_run = 6
    elif wickets_left >= 4:
        max_run = 4
    else:
        max_run = 2

    probability = calculate_win_probability(
        target, current, balls_left, wickets_left
    )

    runs = required_runs
    balls = balls_left
    pattern = []

    while runs > 0 and balls > 0:
        run = random.choice([0, 1, 1, 2, 2, 3, 4])
        run = min(run, max_run)
        pattern.append(run)
        runs -= run
        balls -= 1

    result = "Chase Possible ✅" if runs <= 0 else "Chase Might Be Difficult ⚠️"

    return jsonify({
        "result": result,
        "probability": probability,
        "pattern": pattern[:12]
    })

# ===================== TEAM SELECTION (CSP) =====================

@app.route("/select_team")
def select_team_api():
    try:
        team = select_team()
        return jsonify({
            "team": team,
            "total_credits": sum(p["credits"] for p in team)
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# ===================== MINIMAX STRATEGY =====================

@app.route("/minimax_strategy", methods=["POST"])
def minimax_api():
    data = request.json
    target = int(data["target"])
    current = int(data["current"])
    balls = int(data["balls"])
    wickets = int(data["wickets"])

    runs_left = target - current
    strategy, score = get_strategy(runs_left, balls, wickets)

    explanation = {
        "Aggressive": "AI suggests attacking shots to maximize scoring despite risk.",
        "Balanced": "AI suggests controlled aggression balancing risk and reward.",
        "Defensive": "AI suggests protecting wickets and rotating strike."
    }

    return jsonify({
        "strategy": strategy,
        "confidence": round(min(95, max(40, score)), 2),
        "reason": explanation[strategy]
    })

# ===================== 🎯 WHAT-IF SCENARIO SIMULATOR =====================

@app.route("/what_if", methods=["POST"])
def what_if():

    data = request.json

    target = data["target"]
    current = data["current"]
    balls = data["balls"]
    wickets = data["wickets"]
    scenario = data["scenario"]

    # Copy state (DO NOT mutate live state)
    new_score = current
    balls_left = balls
    wickets_left = wickets

    # Apply scenario
    if scenario == "over_15":
        new_score += 15
        balls_left = max(0, balls_left - 6)

    elif scenario == "wicket":
        wickets_left = max(0, wickets_left - 1)

    elif scenario == "two_dots":
        balls_left = max(0, balls_left - 2)

    # Simple probability heuristic
    runs_needed = max(0, target - new_score)

    if balls_left == 0 or wickets_left == 0:
        probability = 0
    else:
        rr_required = (runs_needed / balls_left) * 6
        probability = max(0, min(100, 100 - rr_required * 5))

    return jsonify({
        "scenario": scenario.replace("_", " ").title(),
        "new_score": new_score,
        "balls_left": balls_left,
        "wickets_left": wickets_left,
        "probability": round(probability, 2)
    })

@app.route("/init_match", methods=["POST"])
def init_match():
    data = request.json

    session["match"] = {
        "target": int(data["target"]),
        "score": int(data["current"]),
        "balls": int(data["balls"]),
        "wickets": int(data["wickets"]),
        "timeline": [],
        "probability": [],
        "rrr": [],
        "wicket_balls": []
    }

    return jsonify({"status": "initialized"})

@app.route("/simulate_ball", methods=["POST"])
def simulate_ball():
    if "match" not in session:
        return jsonify({"error": "Match not initialized"}), 400

    m = session["match"]

    if m["balls"] <= 0 or m["wickets"] <= 0:
        return jsonify({"match_over": True})

    wicket_weight = 5 if m["wickets"] > 6 else 10 if m["wickets"] > 3 else 18

    outcome = random.choices(
        [0,1,2,3,4,6,"W"],
        weights=[18,22,20,6,14,10,wicket_weight]
    )[0]

    m["balls"] -= 1

    if outcome == "W":
        m["wickets"] -= 1
        m["wicket_balls"].append(len(m["timeline"]))
    else:
        m["score"] += outcome

    win_prob = calculate_win_probability(
        m["target"], m["score"], m["balls"], m["wickets"]
    )

    runs_left = m["target"] - m["score"]
    rrr = round(runs_left / (m["balls"] / 6), 2) if m["balls"] > 0 else 0

    m["timeline"].append(m["score"])
    m["probability"].append(win_prob)
    m["rrr"].append(rrr)

    session["match"] = m

    return jsonify({
        "score": m["score"],
        "balls": m["balls"],
        "wickets": m["wickets"],
        "timeline": m["timeline"],
        "probability": m["probability"],
        "rrr": m["rrr"],
        "wickets_fallen": m["wicket_balls"],
        "target": m["target"]
    })

@app.route("/venue")
def venue():
    return render_template("venue.html")

@app.route("/venue_chase_stats")
def venue_chase_stats():
    venue_stats = {}

    for _, row in matches.iterrows():
        venue = row.get("venue")
        winner = row.get("winner")
        team2 = row.get("team2")
        result = row.get("result")

        # Skip invalid or abandoned matches
        if (
            pd.isna(venue)
            or pd.isna(winner)
            or pd.isna(team2)
            or result == "no result"
        ):
            continue

        if venue not in venue_stats:
            venue_stats[venue] = {
                "matches": 0,
                "chase_wins": 0
            }

        venue_stats[venue]["matches"] += 1

        # Team batting second wins = successful chase
        if winner == team2:
            venue_stats[venue]["chase_wins"] += 1

    result_data = []

    for venue, stats in venue_stats.items():
        if stats["matches"] == 0:
            continue

        success_rate = round(
            (stats["chase_wins"] / stats["matches"]) * 100, 2
        )

        if success_rate > 55:
            difficulty = "Easy"
        elif success_rate > 40:
            difficulty = "Medium"
        else:
            difficulty = "Hard"

        result_data.append({
            "venue": venue,
            "matches": stats["matches"],
            "chase_success": success_rate,
            "difficulty": difficulty
        })

    # Sort venues by difficulty (Hard → Easy)
    result_data.sort(key=lambda x: x["chase_success"])

    return jsonify(result_data)

# ===================== MAIN =====================

if __name__ == "__main__":
    app.run(debug=True)
