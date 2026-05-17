#map.py
def load_map(filepath):
    grid = []
    N, M = None, None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if N is None:
                    parts = line.split(';')
                    if len(parts) != 2:
                        raise ValueError("Format invalide : attendu N;M")
                    N, M = int(parts[0]), int(parts[1])
                else:
                    cells = line.split(' ')
                    if len(cells) != M:
                        raise ValueError(f"Ligne invalide : {len(cells)} colonnes, {M} attendues")
                    grid.append(cells)
        if len(grid) != N:
            raise ValueError(f"{len(grid)} lignes lues, {N} attendues")
    except FileNotFoundError:
        print(f"Erreur : fichier '{filepath}' introuvable.")
        exit(1)
    except ValueError as e:
        print(f"Erreur de format : {e}")
        exit(1)
    return {"grid": grid, "N": N, "M": M}

def get_cell(grid, row, col):
    return grid[row][col]

def is_valid_position(grid, N, M, row, col):
    if 0 <= row < N and 0 <= col < M:
        return True
    return False