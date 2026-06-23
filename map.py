#map.py
import sys

def load_map(filepath):
    grid = []
    N, M = None, None  # N: rows, M: columns
    
    #trackers to validate map constraints
    p_count = 0
    t_count = 0
    start_pos = None
    allowed_symbols = {'.', 'X', 'B', 'E', 'T', 'P'}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                #parse dimensions line
                if N is None:
                    parts = line.split(';')
                    if len(parts) != 2:
                        raise ValueError("Format invalide : attendu N;M")
                    N, M = int(parts[0]), int(parts[1])
                
                #parse map rows
                else:
                    cells = line.split()  # Fixes the trailing/double space issue
                    if len(cells) != M:
                        raise ValueError(f"Ligne invalide : {len(cells)} colonnes, {M} attendues")
                    grid.append(cells)
                    
        #check if the total rows read matches N
        if len(grid) != N:
            raise ValueError(f"{len(grid)} lignes lues, {N} attendues")
            
        #validate symbols and find player start position
        for r in range(N):
            for c in range(M):
                symbol = grid[r][c]
                
                if symbol not in allowed_symbols:
                    raise ValueError(f"Symbole interdit '{symbol}' détecté à la position ({r}, {c})")
                
                if symbol == 'P':
                    p_count += 1
                    start_pos = (r, c)
                elif symbol == 'T':
                    t_count += 1

        #checks for contraints
        if p_count != 1:
            raise ValueError(f"La carte doit contenir exactement un point de départ P (trouvé: {p_count})")
        if t_count < 1:
            raise ValueError(f"La carte doit contenir au moins une cible T (trouvé: {t_count})")

    except FileNotFoundError:
        print(f"Erreur : fichier '{filepath}' introuvable.")
        sys.exit(1)
    except ValueError as e:
        print(f"Erreur de format de la carte : {e}")
        sys.exit(1)
        
    
    return {"grid": grid, "N": N, "M": M, "start_pos": start_pos}


def get_cell(grid, row, col):
    return grid[row][col]


def is_valid_position(grid, N, M, row, col):
    return 0 <= row < N and 0 <= col < M




    
    
    
    