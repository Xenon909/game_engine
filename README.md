# Simulation de Jeu et Analyse Stratégique
**Rapport de projet** **Travail réalisé par :** Yasser Bakkali & Mansour Bengoumi

---

## 1. Architecture et choix de conception

### 1.1 Structure des fichiers
Le projet est organisé en modules Python indépendants, chacun ayant une responsabilité unique et clairement définie. Cette séparation favorise la lisibilité, la testabilité et la maintenabilité du code.

* **`main.py`** : Point d'entrée principal, dispatche vers les trois modes d'exécution (`play`, `simulate`, `explore`).
* **`map.py`** : Lecture, validation et représentation de la grille.
* **`rules.py`** : Lecture, validation et vérification des paramètres de jeu.
* **`moves.py`** : Lecture et validation de la séquence de mouvements.
* **`engine.py`** : Moteur de jeu contenant les fonctions `init_state`, `apply_action` et `is_terminal`.
* **`simulate.py`** : Simulations aléatoires et calcul des statistiques.
* **`explore.py`** : Exploration récursive de l'arbre des mouvements avec mémoïsation.
* **`utils.py`** : Fonctions utilitaires partagées, notamment l'écriture du fichier `run_log.txt`.

### 1.2 Représentation de l'état du jeu
L'état du jeu à un instant donné est représenté par un dictionnaire Python structuré ainsi :

```python
state = {
    "pos": (ligne, colonne),      # Position courante du joueur
    "score": 0,                   # Score courant
    "steps": 0,                   # Nombre de pas effectués
    "collected": set(),           # Coordonnées des bonus déjà collectés
    "hp": HP,                     # Points de vie (uniquement en mode health)
    "status": "CONTINUE"          # CONTINUE | SUCCESS | FAILURE | LIMIT
}

```

> **Note de conception :** Ce choix permet de passer l'état facilement entre fonctions, de le copier rapidement avec `copy.deepcopy()` lors de l'exploration récursive, et de l'inspecter simplement lors du débogage.

### 1.3 Choix de conception clés

* **Immuabilité de l'état :** La fonction `apply_action()` effectue toujours un `copy.deepcopy()` avant toute modification. Cela garantit l'absence d'effets de bord entre les branches de l'arbre récursif et entre les simulations indépendantes.
* **Gestion des obstacles :** Une tentative de mouvement vers une case `X` ou hors grille est comptabilisée comme un pas (coût `MOVE_COST` déduit) mais la position du joueur reste inchangée.
* **Bonus à usage unique :** L'ensemble `collected` mémorise les coordonnées des cases `B` déjà visitées. Un second passage sur la même case ne rapporte aucun point supplémentaire.
* **Validation stricte des entrées :** Chaque fichier est intégralement validé avant toute exécution (symboles autorisés, dimensions cohérentes, paramètres obligatoires présents).

---

## 2. Modes d'exécution

### 2.1 Mode `play`

Ce mode rejoue de façon déterministe la séquence d'actions contenue dans le fichier `moves.txt`. Chaque action est appliquée via `apply_action()` et une ligne de journal est produite et affichée. L'exécution s'arrête dès qu'un état terminal est atteint (`SUCCESS`, `FAILURE` ou `LIMIT`).

**Commande :**

```bash
python main.py play map.txt rules.txt moves.txt

```

**Exemple de sortie (Carte de test 1) :**

```text
Step 1 | Action: RIGHT | Pos: (4, 1) | Score: -1 | Event: NONE
Step 2 | Action: RIGHT | Pos: (4, 2) | Score: -2 | Event: NONE
Step 3 | Action: UP    | Pos: (3, 2) | Score: -3 | Event: NONE
Step 4 | Action: UP    | Pos: (2, 2) | Score:  6 | Event: BONUS (+10)
RESULT: LIMIT | Steps: 7 | Final Score: 3

```

### 2.2 Mode `simulate`

Ce mode effectue `SIMU_COUNT` simulations indépendantes avec des actions tirées aléatoirement parmi les cinq actions valides. La graine `RANDOM_SEED` garantit la reproductibilité des résultats. À l'issue des simulations, un rapport statistique complet est affiché.

**Commande :**

```bash
python main.py simulate map.txt rules.txt

```

### 2.3 Mode `explore`

Ce mode explore récursivement l'arbre de tous les chemins possibles jusqu'à la profondeur `DEPTH_EXPLORATION`. Il retourne la séquence d'actions menant au score maximal ainsi que le nombre total de feuilles explorées après élagage.

**Commande :**

```bash
python main.py explore map.txt rules.txt

```

---

## 3. Algorithme d'exploration récursive

### 3.1 Principe général

L'exploration récursive construit implicitement un arbre dont chaque nœud représente un état du jeu et chaque arc une action. La racine est l'état initial (position `P` avec un score égal à 0). À chaque niveau, les 5 actions possibles sont testées. Sans optimisation, la complexité théorique est en $O(5^d)$ où $d$ est la profondeur maximale.

### 3.2 Pseudo-algorithme

```text
fonction explore(etat, profondeur, chemin, meilleur_ref, memo):
    SI profondeur == 0 OU etat terminal:
        mettre a jour meilleur_ref si etat.score > meilleur
        RETOURNER 1

    empreinte = (pos, collected_frozen, steps)
    SI empreinte dans memo ET memo[empreinte] >= etat.score:
        RETOURNER 0 (branche élaguée)

    memo[empreinte] = etat.score
    total = 0
    POUR chaque action DANS [UP, DOWN, LEFT, RIGHT, WAIT]:
        prochain = apply_action(etat, action)
        total += explore(prochain, profondeur - 1, ...)
    RETOURNER total

```

### 3.3 Optimisations mises en œuvre

Sans optimisation, une profondeur de 12 génère environ 244 millions de nœuds, ce qui est inexploitable. Deux stratégies d'élagage ont été mises en œuvre :

1. **Arrêt anticipé sur état terminal :** Dès qu'un état `SUCCESS` ou `FAILURE` est atteint, la récursion s'arrête immédiatement.
2. **Mémoïsation :** Un dictionnaire `memo` associe chaque empreinte d'état (position, bonus collectés, nombre de pas) au meilleur score depuis lequel cet état a été atteint. Si une branche arrive dans un état déjà visité avec un score inférieur ou égal, elle est abandonnée.

| Profondeur | Feuilles Théoriques | Feuilles Explorées (Élaguées) | Facteur de Gain |
| --- | --- | --- | --- |
| **6** | 15 625 | 105 | $\approx$ 149x |
| **10** | 9 765 625 | 289 | $\approx$ 33 800x |
| **12** | 244 000 000 | 315 | $\approx$ 775 000x |

### 3.4 Résultat sur la carte de test 1

```text
=== Exploration recursive (profondeur max: 12) ===
Meilleur score trouve: 51
Sequence optimale: UP UP RIGHT RIGHT RIGHT RIGHT RIGHT DOWN RIGHT
Feuilles explorees: 315

```

> Le score de 51 correspond à la collecte du bonus B (+10) puis à l'atteinte de la cible T (+50), diminué de 9 coups ayant chacun un coût de 1 ($50 + 10 - 9 = 51$).

---

## 4. Analyse des résultats de simulation

### 4.1 Configuration utilisée

* **Carte :** Grille de 5 lignes $\times$ 7 colonnes (carte de test 1)
* **Paramètres :** `MAX_MOVES = 50`, `MOVE_COST = 1`, `BONUS_POINTS = 10`, `TARGET_BONUS = 50`, `ENEMY_MODE = death`, `SIMU_COUNT = 200`, `RANDOM_SEED = 0`.

### 4.2 Rapport obtenu

```text
=== Rapport de simulation (200 parties) ===
Taux de succes : 15.00%
Score moyen    : -33.72
Score max      : 47
Score min      : -50
Ecart-type     : 23.59
Pas moyens     : 47.8
Distribution   : SUCCESS=30 | FAILURE=0 | LIMIT=170

```

### 4.3 Interprétation

* **Taux de succès faible (15%) :** Un joueur aléatoire a peu de chances d'atteindre la cible dans une grille parsemée d'obstacles, d'autant plus que la cible `T` se situe dans un coin de la grille, difficile d'accès sans stratégie dirigée.
* **Score moyen négatif (-33.72) :** La majorité des parties (170/200) atteignent la limite de pas sans succès. Chaque pas coûtant 1 point, une partie de 50 pas sans bonus rapporte -50, tirant la moyenne vers le bas.
* **Score maximal égal à 47 :** Ce score correspond à un succès (+50) avec collecte du bonus (+10) en 13 pas (-13). Certaines simulations trouvent le chemin optimal par pure chance.
* **Écart-type élevé (23.59) :** La dispersion des scores reflète la grande variabilité du comportement aléatoire (succès rapides vs errance jusqu'à la limite).
* **FAILURE égal à zéro :** La carte de test 1 ne contient pas d'ennemis malgré le mode `death`, donc aucune partie ne se termine par une mort.

---

## 5. Difficultés rencontrées et solutions adoptées

* **Explosion combinatoire :** Résolue par la mémoïsation réduisant l'exploration à une profondeur de 12 de 244M de nœuds à seulement 315 feuilles.
* **Effets de bord dans la récursion :** Les premières versions modifiaient l'état en place. Solutionné par un appel systématique à `copy.deepcopy()` dans `apply_action()`.
* **Gestion des bonus uniques :** Résolue via l'utilisation d'un ensemble (`set()`) nommé `collected` qui enregistre les coordonnées `(r, c)` des bonus consommés.
* **Cohérence des collisions :** S'assurer qu'un mouvement bloqué consomme un pas et applique le coût sans déplacer le joueur. Validé par des blocs de tests dédiés.
* **Validation des fichiers d'entrée :** Gestion des espaces multiples et commentaires via `line.split()` et vérification systématique des paramètres par rapport à une liste blanche autorisée dès le chargement.

---

## 6. Améliorations et extensions envisagées

* **Visualisation de la grille :** Intégrer un affichage textuel dynamique de la grille (position joueur, bonus restants, ennemis) mis à jour à chaque étape du mode `play`.
* **Interface interactive :** Ajouter un mode temps réel permettant de contrôler le joueur directement au clavier.
* **Tests unitaires formalisés :** Transposer les blocs de tests actuels en suites de tests `pytest` robustes (incluant les cas limites : grilles 1x1, `MAX_MOVES = 0`, etc.).
* **Exploration heuristique :** Remplacer la recherche exhaustive par un algorithme $A^*$ utilisant la distance de Manhattan à la cible `T` pour les grilles à grande échelle.

