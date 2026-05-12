import csv
import random

MAX_CREDITS = 100
MAX_OVERSEAS = 4

ROLE_LIMITS = {
    "Batsman": (3, 5),
    "Bowler": (3, 5),
    "AllRounder": (1, 3),
    "WicketKeeper": (1, 2)
}

# ---------- LOAD & FILTER PLAYERS ----------
def load_players():
    players = []
    with open("data/players.csv", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["credits"] = int(row["credits"])
            players.append(row)

    # 🔥 DOMAIN REDUCTION (CRITICAL FOR 200+ PLAYERS)
    filtered = []
    for role in ROLE_LIMITS.keys():
        role_players = [p for p in players if p["role"] == role]
        random.shuffle(role_players)
        filtered.extend(role_players[:30])  # take max 30 per role

    random.shuffle(filtered)
    return filtered


# ---------- PARTIAL CHECK ----------
def valid_team(team):
    if len(team) > 11:
        return False

    if sum(p["credits"] for p in team) > MAX_CREDITS:
        return False

    if sum(1 for p in team if p["country"] == "Overseas") > MAX_OVERSEAS:
        return False

    role_count = {}
    for p in team:
        role_count[p["role"]] = role_count.get(p["role"], 0) + 1

    for role, (_, max_r) in ROLE_LIMITS.items():
        if role_count.get(role, 0) > max_r:
            return False

    return True


# ---------- FINAL CHECK ----------
def final_check(team):
    if len(team) != 11:
        return False

    role_count = {}
    for p in team:
        role_count[p["role"]] = role_count.get(p["role"], 0) + 1

    for role, (min_r, max_r) in ROLE_LIMITS.items():
        if not (min_r <= role_count.get(role, 0) <= max_r):
            return False

    return True


# ---------- BACKTRACKING CSP ----------
def backtrack(team, players, index):
    if len(team) == 11:
        return team if final_check(team) else None

    if index >= len(players):
        return None

    player = players[index]

    # Try including
    team.append(player)
    if valid_team(team):
        result = backtrack(team, players, index + 1)
        if result:
            return result
    team.pop()

    # Try excluding
    return backtrack(team, players, index + 1)


# ---------- MAIN FUNCTION ----------
def select_team():
    players = load_players()
    print("Players loaded:", len(players))

    team = []

    # Step 1: Ensure minimum required per role
    for role, (min_r, max_r) in ROLE_LIMITS.items():
        role_players = [p for p in players if p["role"] == role]
        team.extend(role_players[:min_r])

    # Step 2: Fill remaining slots up to 11
    remaining_slots = 11 - len(team)
    remaining_players = [p for p in players if p not in team]
    random.shuffle(remaining_players)

    for p in remaining_players:
        if len(team) >= 11:
            break
        # Check credits & overseas
        if sum(pl["credits"] for pl in team) + p["credits"] > MAX_CREDITS:
            continue
        if sum(1 for pl in team if pl["country"] == "Overseas") + (1 if p["country"]=="Overseas" else 0) > MAX_OVERSEAS:
            continue
        team.append(p)

    # Final validation
    if len(team) != 11:
        print("Could not form valid team")
        return None

    random.shuffle(team)
    return team
