import csv
import random
from collections import defaultdict

# ------------------------------
# STEP 1: COLLECT PLAYER STATS
# ------------------------------

players = defaultdict(lambda: {
    "runs": 0,
    "balls": 0,
    "wickets": 0
})

with open("data/deliveries.csv", newline='', encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        batsman = row["batsman"]
        bowler = row["bowler"]

        runs = int(row["batsman_runs"])
        players[batsman]["runs"] += runs
        players[batsman]["balls"] += 1

        # Count wicket for bowler
        if row["player_dismissed"] != "":
            players[bowler]["wickets"] += 1


# ------------------------------
# STEP 2: ASSIGN ROLES & CREDITS
# ------------------------------

final_players = []

for name, stats in players.items():
    runs = stats["runs"]
    balls = stats["balls"]
    wickets = stats["wickets"]

    if balls == 0:
        continue

    strike_rate = (runs / balls) * 100

    # ROLE DECISION (Simple & Explainable)
    if runs > 1200 and wickets > 40:
        role = "AllRounder"
        credits = 9
    elif wickets > 70:
        role = "Bowler"
        credits = 8
    elif runs > 1000:
        role = "Batsman"
        credits = 8
    else:
        continue  # discard low-impact players

    # RANDOM COUNTRY ASSIGNMENT (25% Overseas)
    country = "Overseas" if random.random() < 0.25 else "India"

    final_players.append({
        "name": name,
        "role": role,
        "country": country,
        "credits": credits
    })


# ------------------------------
# STEP 3: WRITE PLAYERS.CSV
# ------------------------------

with open("data/players.csv", "w", newline='', encoding="utf-8") as file:
    fieldnames = ["name", "role", "country", "credits"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_players)

print(f"✅ players.csv generated successfully with {len(final_players)} players!")
