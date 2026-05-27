from map import load_map
from rules import load_rules
from moves import load_moves
from engine import init_state, apply_action, is_terminal
from utils import write_run_log
import sys
mode = sys.argv[1]
if mode == 'play':
    grid_info = load_map(sys.argv[2])
    rules = load_rules(sys.argv[3])
    moves = load_moves(sys.argv[4])
    state = init_state(grid_info['start_pos'], rules)
    log_lines = []
    for i in moves:
        if is_terminal(state, rules):
            break
        state, event = apply_action(state, i, grid_info['grid'], rules)      
        line = f"Step {state['steps']} | Action : {i} | Pos : {state['pos']} | Score : {state['score']} | Event : {event}"
        log_lines.append(line)
        print(line)
    if state["status"] == "CONTINUE":
        state["status"] = "LIMIT"
    result_line = f"RESULT : {state['status']} | Steps : {state['steps']} | Final Score : {state['score']}"
    write_run_log(log_lines, result_line, "run_log.txt")
    print(result_line)
elif mode == 'simulate':
    pass
elif mode == 'explore':
    pass