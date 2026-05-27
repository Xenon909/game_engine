def write_run_log(log_lines, result_line, filepath):
    with open(filepath, 'r' , encoding='utf8') as f:
        for i in log_lines:
            f.write(i+'\n')
        f.write(result_line+'\n')