import re
import statistics
from collections import defaultdict

llm_stats = {
    "overall": defaultdict(list),
    "player_0": defaultdict(list),
    "player_1": defaultdict(list),
}

game_over_pattern = re.compile(r"Game over after (\d+) round\(s\)")
winner_pattern = re.compile(r"Player (\d+) \(LLM\) won")
llm_position_pattern = re.compile(r"Player (\d+) \(LLM\)")
net_worth_pattern = re.compile(r"Player \d+ \(LLM\).*?net worth of \$(\d+)", re.DOTALL)
rent_paid_pattern = re.compile(r"Rent paid: (\d+)")
rent_received_pattern = re.compile(r"Rent received: (\d+)")
properties_bought_pattern = re.compile(r"Properties bought: (\d+)")
houses_built_pattern = re.compile(r"Houses built: (\d+)")
mortgages_pattern = re.compile(r"Mortgages: (\d+)")
unmortgages_pattern = re.compile(r"Unmortgages: (\d+)")
actions_taken_pattern = re.compile(r"Actions taken: (\d+)")
duration_pattern = re.compile(r"Game duration: ([\d.]+) seconds")
invalid_json_pattern = re.compile(r"Invalid json: (\d+)")
invalid_move_pattern = re.compile(r"Invalid move: (\d+)")
defaulted_move_pattern = re.compile(r"Defaulted move: (\d+)")

with open("phi3_results.txt", "r") as file:
    content = file.read()

games = re.split(r"Game \d+ Results", content)

def update_stats(stats, category, value):
    stats[category].append(value)

for game in games[1:]:
    position_match = llm_position_pattern.search(game)
    if not position_match:
        continue
    llm_position = int(position_match.group(1))

    stats_to_update = ["overall"]
    if llm_position == 0:
        stats_to_update.append("player_0")
    elif llm_position == 1:
        stats_to_update.append("player_1")

    for stats in stats_to_update:
        llm_stats[stats]["games_played"].append(1)

    if winner_pattern.search(game):
        for stats in stats_to_update:
            llm_stats[stats]["games_won"].append(1)

    stat_patterns = {
        "net_worth": net_worth_pattern,
        "rent_paid": rent_paid_pattern,
        "rent_received": rent_received_pattern,
        "properties_bought": properties_bought_pattern,
        "houses_built": houses_built_pattern,
        "mortgages": mortgages_pattern,
        "unmortgages": unmortgages_pattern,
        "actions_taken": actions_taken_pattern,
        "game_duration": duration_pattern,
        "invalid_json": invalid_json_pattern,
        "invalid_move": invalid_move_pattern,
        "defaulted_move": defaulted_move_pattern,
    }
    for stat_name, pattern in stat_patterns.items():
        if match := pattern.search(game):
            value = float(match.group(1)) if "duration" in stat_name else int(match.group(1))
            for stats in stats_to_update:
                update_stats(llm_stats[stats], stat_name, value)

def calculate_averages_and_summary(stats):
    summary = {}
    summary["games_played"] = len(stats["games_played"])
    summary["games_won"] = len(stats["games_won"])
    summary["win_rate"] = (
        summary["games_won"] / summary["games_played"] * 100 if summary["games_played"] > 0 else 0
    )
    for key in stats:
        if key not in ["games_played", "games_won"]:
            summary[f"avg_{key}"] = statistics.mean(stats[key]) if stats[key] else 0
            # summary[f"total_{key}"] = sum(stats[key])

    if "game_duration" in stats and "actions_taken" in stats:
        total_actions = [
            actions + invalids + moves
            for actions, invalids, moves in zip(
                stats["actions_taken"], stats["invalid_json"], stats["invalid_move"]
            )
        ]
        inference_times = [
            duration / total if total > 0 else 0
            for duration, total in zip(stats["game_duration"], total_actions)
        ]
        summary["avg_inference_time"] = statistics.mean(inference_times) if inference_times else 0
    else:
        summary["avg_inference_time"] = 0

    return summary

summaries = {
    "overall": calculate_averages_and_summary(llm_stats["overall"]),
    "player_0": calculate_averages_and_summary(llm_stats["player_0"]),
    "player_1": calculate_averages_and_summary(llm_stats["player_1"]),
}


for role, stats in summaries.items():
    print(f"\n=== LLM Statistics ({role}) ===")
    print(f"Games Played: {stats['games_played']}")
    print(f"Games Won: {stats['games_won']} ({stats['win_rate']:.2f}%)")
    print(f"Average Game Duration: {stats.get('avg_game_duration', 0):.2f} seconds")
    print(f"Average Inference Time: {stats.get('avg_inference_time', 0):.4f} seconds per action")
    for key, value in stats.items():
        if key not in ["games_played", "games_won", "win_rate", "avg_game_duration", "avg_inference_time"]:
            print(f"{key.replace('_', ' ').capitalize()}: {value:.2f}")
