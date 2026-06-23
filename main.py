# main.py
from map import load_map
from rules import load_rules, validate_rules
from moves import load_moves
from engine import init_state, apply_action, is_terminal
from simulate import run_all_simulations, compute_stats
from explore import run_explore
from utils import write_run_log
import sys


def print_usage():
    print("Usage:")
    print("  python main.py play    <map.txt> <rules.txt> <moves.txt>")
    print("  python main.py simulate <map.txt> <rules.txt>")
    print("  python main.py explore  <map.txt> <rules.txt>")
    sys.exit(1)


# --- Entry point ---
if len(sys.argv) < 2:
    print_usage()

mode = sys.argv[1]
if mode == 'play':
    if len(sys.argv) != 5:
        print("Erreur : le mode 'play' requiert exactement 3 arguments (map, rules, moves).")
        print_usage()

    # Load and validate all required files
    grid_info = load_map(sys.argv[2])
    rules     = load_rules(sys.argv[3])
    validate_rules(rules)
    moves     = load_moves(sys.argv[4])

    # Initialize the player state at starting position
    state     = init_state(grid_info['start_pos'], rules)
    log_lines = []

    # Execute each action from moves.txt step by step
    for action in moves:
        if is_terminal(state, rules):
            break
        state, event = apply_action(state, action, grid_info['grid'], rules)
        line = (
            f"Step {state['steps']} | Action : {action} | "
            f"Pos : {state['pos']} | Score : {state['score']} | Event : {event}"
        )
        log_lines.append(line)
        print(line)

    # If moves are exhausted without reaching a terminal state, mark as LIMIT
    if state["status"] == "CONTINUE":
        state["status"] = "LIMIT"

    # Write final result line and flush to log file
    result_line = (
        f"RESULT : {state['status']} | Steps : {state['steps']} | "
        f"Final Score : {state['score']}"
    )
    write_run_log(log_lines, result_line, "run_log.txt")
    print(result_line)

elif mode == 'simulate':
    if len(sys.argv) != 4:
        print("Erreur : le mode 'simulate' requiert exactement 2 arguments (map, rules).")
        print_usage()

    grid_info = load_map(sys.argv[2])
    rules     = load_rules(sys.argv[3])
    validate_rules(rules)

    # Run all simulations and collect raw results
    results = run_all_simulations(grid_info, rules)

    # Compute statistical indicators
    stats = compute_stats(results)

    # Display the simulation report
    print(f"\n=== Rapport de simulation ({stats['total']} parties) ===")
    print(f"Taux de succes : {stats['taux_succes']:.2f} %")
    print(f"Score moyen    : {stats['score_moyen']:.2f}")
    print(f"Score max      : {stats['score_max']}")
    print(f"Score min      : {stats['score_min']}")
    print(f"Ecart-type     : {stats['ecart_type']:.2f}")
    print(f"Pas moyens     : {stats['pas_moyens']:.1f}")
    print(
        f"Distribution   : SUCCESS={stats['success']} | "
        f"FAILURE={stats['failure']} | LIMIT={stats['limit']}"
    )

elif mode == 'explore':
    if len(sys.argv) != 4:
        print("Erreur : le mode 'explore' requiert exactement 2 arguments (map, rules).")
        print_usage()

    grid_info = load_map(sys.argv[2])
    rules     = load_rules(sys.argv[3])
    validate_rules(rules)

    # Launch recursive exploration and display the best path found
    run_explore(grid_info, rules)
else:
    print(f"Erreur : mode inconnu '{mode}'. Modes valides : play, simulate, explore.")
    print_usage()
