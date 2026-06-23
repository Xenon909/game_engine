def load_moves(filepath):
    moves = []
    L = {'UP', 'DOWN', 'LEFT', 'RIGHT', 'WAIT'}
    with open(filepath, 'r', encoding='utf-8') as f:
        for i in f:
            i = i.strip()
            if not i or i.startswith('#'):
                continue
            if i not in L:
                print(f"Erreur : action invalide '{i}'")
                exit(1)
            moves.append(i)
    return moves