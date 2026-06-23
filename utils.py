def write_run_log(log_lines, result_line, filepath):
    """
    Writes the game journal to a text file
    Each line corresponds to one step of the simulation
    The last line contains the final result.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        # Write each step line followed by a newline
        for line in log_lines:
            f.write(line + '\n')
        # Write the final result line
        f.write(result_line + '\n')