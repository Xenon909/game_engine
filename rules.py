#rules.py
import sys

def load_rules(filepath):
    rules = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip blank lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Split line into parameter name and raw value
                if '=' not in line:
                    raise ValueError(f"Ligne de configuration malformée ( '=' manquant) : '{line}'")
                    
                parts = line.split('=', 1)  # Max split of 1 to handle safely
                param_name = parts[0].strip()
                raw_value = parts[1].strip()
                
                # Convert types: ENEMY_MODE stays a string, others become ints
                if param_name == "ENEMY_MODE":
                    rules[param_name] = raw_value
                else:
                    rules[param_name] = int(raw_value)
                    
    except FileNotFoundError:
        print(f"Erreur : Le fichier des règles '{filepath}' est introuvable.")
        sys.exit(1)
    except ValueError as e:
        print(f"Erreur de format dans le fichier des règles : {e}")
        sys.exit(1)
        
    return rules

def validate_rules(rules):
    mandatory_params = {
        "MAX_MOVES", 
        "MOVE_COST", 
        "BONUS_POINTS", 
        "TARGET_BONUS", 
        "ENEMY_PENALTY", 
        "ENEMY_MODE", 
        "SIMU_COUNT", 
        "DEPTH_EXPLORATION"
    }
    
    for param in mandatory_params:
        if param not in rules:
            print(f"Erreur de validation : Le paramètre obligatoire '{param}' est manquant.")
            sys.exit(1)
            
    allowed_modes = {"death", "health"}
    if rules["ENEMY_MODE"] not in allowed_modes:
        print(f"Erreur de validation : ENEMY_MODE doit être 'death' ou 'health' (trouvé: '{rules['ENEMY_MODE']}').")
        sys.exit(1)
        
    # NB: if ENEMY_MODE is set to "health", the additional parameter HP becomes mandatory 
    if rules["ENEMY_MODE"] == "health":
        if "HP" not in rules:
            print("Erreur de validation : Le paramètre 'HP' est obligatoire lorsque ENEMY_MODE='health'.")
            sys.exit(1)
        if rules["HP"] <= 0:
            print(f"Erreur de validation : 'HP' doit être un entier strictement positif (trouvé: {rules['HP']}).")
            sys.exit(1)

    if rules["MAX_MOVES"] < 0:
        print(f"Erreur de validation : MAX_MOVES ne peut pas être négatif (trouvé: {rules['MAX_MOVES']}).")
        sys.exit(1)
        
    if rules["DEPTH_EXPLORATION"] < 0:
        print(f"Erreur de validation : DEPTH_EXPLORATION ne peut pas être négatif (trouvé: {rules['DEPTH_EXPLORATION']}).")
        sys.exit(1)

    if rules["SIMU_COUNT"] <= 0:
        print(f"Erreur de validation : SIMU_COUNT doit être au moins de 1 (trouvé: {rules['SIMU_COUNT']}).")
        sys.exit(1)

    return True

if __name__ == "__main__":
    # 1. Load the rules dictionary
    game_rules = load_rules("data/rules.txt")
    print("--- 1. Rules Parsed From File ---")
    print(game_rules)
    
    # 2. Run them through the validator
    print("\n--- 2. Running Validator Module ---")
    if validate_rules(game_rules):
        print("Success: All configuration parameters are valid and structurally sound!")

