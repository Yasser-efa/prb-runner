# PRB Starters

Entrainement en ligne de commande aux exercices de début de séance du cours « Programmation de
base » (Python), dans les conditions de la partie pratique de l'examen.

## Installation

Il faut Windows et Python 3.14 ou plus récent. Dans le dossier du projet :

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Ouvre ensuite le dossier dans PyCharm et choisis l'interpréteur `.venv` du projet
(*Settings › Project › Python Interpreter*). Le terminal de PyCharm active alors `.venv` tout seul.

Conseil : désactive *Full Line Code Completion* pendant l'entrainement. À l'examen, il faudra
écrire chaque ligne soi-même.

## Utilisation

1. Lis l'énoncé `exercices/<id>/enonce.md` et fais d'abord la phase préparatoire sur papier.
2. Code ta solution dans `mes_solutions/<id>/`, en créant toi-même les fichiers demandés.
3. Lance la vérification :

```powershell
python -m prb verifier <id>
```

Sans `<id>`, la commande vérifie l'exercice en cours.

### Le verdict

1. **Recevabilité** (bloquant) : fichiers et packages demandés avec leurs noms exacts, syntaxe,
   noms non définis, imports inexistants, signatures.
2. **Contraintes** (bloquant) : constructions et fonctions interdites ou imposées.
3. **Tests** (tout ou rien) : les tests visibles sont détaillés, les tests cachés sont comptés.
4. **Qualité** (non bloquant) : PEP 8, nommage, docstrings Sphinx, imports, bonnes pratiques.

Ton code est exécuté sur une copie, dans un processus isolé, avec 2 secondes par test.

## Dossiers

| Dossier | Contenu |
|---|---|
| `exercices/` | énoncés, descriptions et tests visibles |
| `_prive/` | solutions, tests cachés et indices : exclu dans PyCharm, à ne pas ouvrir |
| `mes_solutions/` | ton code (ignoré par git) |
| `prb/` | l'outil |
| `tests/` | les tests de l'outil (`python -m pytest`) |

## Ajouter un exercice

Choisis un identifiant en minuscules (`ma_table`), puis ajoute-le dans `exercices/ordre.toml`.

### `exercices/<id>/exercice.toml`

```toml
titre = "Table de multiplication"
reference = "exemple"
sorte = "fonction"                 # ou "programme" (exige organisation.main)
duree_minutes = 40                 # facultatif
timeout_secondes = 2.0             # facultatif

[organisation]
fichiers = ["main.py", "tables/__init__.py", "tables/calculs.py"]
main = "main.py"                   # facultatif : exige main() et le garde __main__

[[fonctions]]
module = "tables.calculs"
signature = "table(nombre: int, taille: int = 10) -> list[int]"
preserve_arguments = true          # facultatif : ne pas modifier les arguments

[contraintes]                      # tout est facultatif
interdits = ["break", "continue", "try", "while True"]
imposes = ["while"]
fonctions_interdites = ["int", ".replace"]   # un point devant une méthode
modules_interdits = ["re"]
appels_imposes = ["table"]

[contraintes.fonctions.table]      # mêmes clés, pour une seule fonction
interdits = ["for"]
```

Constructions possibles dans `interdits` et `imposes` : `break`, `continue`, `try`, `while True`,
`while`, `for`, `if`, `match`, `with`, `lambda`, `global`, `ternaire`, `compréhension`, `tranche`,
`f-string`, `dictionnaire`, `ensemble`, `liste`.

### `exercices/<id>/tests_visibles.toml`

Les résultats attendus sont écrits à la main, sous forme de valeurs Python.

```toml
[[tests]]
appel = "table(3, taille=4)"
attendu = "[3, 6, 9, 12]"

[[tests]]                          # programme : saisies et affichage
entree = ["3"]
sortie = """
Nombre ? 3
3 6 9 12 15 18 21 24 27 30
"""
```

Une fonction qui affiche se teste avec `appel` et `sortie`. Les saisies apparaissent dans la
sortie, comme dans la console de PyCharm.

### `exercices/<id>/enonce.md`

L'énoncé, avec l'organisation des fichiers, les hypothèses, des exemples et les contraintes.

### `_prive/<id>/`

- `solution/` : la solution de référence, avec l'organisation imposée.
- `tests_caches.toml` : les résultats attendus sont calculés avec la solution.

```toml
[[groupes]]
theme = "valeurs limites"          # seuls le thème et le compte sont affichés
appels = ["table(0)", "table(-2, 1)"]
entrees = [["0"], ["-4"]]          # exécutions du programme
```

- `indices.toml` : `indices = ["premier indice", "deuxième", "troisième"]`.
