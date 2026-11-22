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

Chaque matin, dans PyCharm : configuration **du_jour**, phase préparatoire sur papier, code dans
`mes_solutions/<id>/` (en créant toi-même les fichiers demandés), puis configuration **verifier**.
Les deux configurations sont dans `.run/` et apparaissent en haut à droite de PyCharm.

| Commande | Effet |
|---|---|
| `python -m prb du_jour` | affiche l'exercice du jour et lance le chrono |
| `python -m prb du_jour --suivant` | un exercice de plus, une fois celui du jour réussi |
| `python -m prb du_jour --nouveau` ou `--revision` | force le choix |
| `python -m prb verifier [<id>]` | vérifie ta solution et enregistre la tentative |
| `python -m prb indice [<id>]` | affiche l'indice suivant |
| `python -m prb solution [<id>]` | affiche la solution (confirmation si l'exercice n'est pas réussi) |
| `python -m prb progression` | tableau de tous les exercices |
| `python -m prb valider [<id>…]` | vérifie la banque elle-même |

Sans `<id>`, les commandes prennent l'exercice en cours.

### Le choix de l'exercice

1. L'exercice non réussi de la veille.
2. Un exercice réussi après avoir vu la solution : il revient le lendemain.
3. Sinon, une révision due pour deux nouveaux exercices, dans l'ordre de `exercices/ordre.toml`.

Un exercice réussi revient après 3 jours, puis 7, puis 21 ; ensuite il est acquis. Une révision qui
n'est pas réussie le jour même revient le lendemain et repart à 3 jours. Au début d'une révision,
l'ancien code est rangé dans `mes_solutions/_archives/`.

Le chrono additionne les séances d'un même exercice, plafonnées à 90 minutes chacune. Il compte
jusqu'à ta dernière commande.

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
| `mes_solutions/` | ton code (ignoré par git), anciens essais dans `_archives/` |
| `progression.sqlite3` | ton historique (ignoré par git) |
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

L'énoncé, avec l'organisation des fichiers, les hypothèses, des exemples (`>>> table(3, taille=4)`
puis le résultat) et les contraintes.

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

### Vérifier l'exercice

```powershell
python -m prb valider ma_table
```

La commande vérifie que la solution est recevable, respecte les contraintes, passe les tests
visibles, reste loin du timeout et n'a aucune remarque de qualité. Elle vérifie aussi qu'il y a
assez de tests cachés et d'indices, que les exemples `>>>` de l'énoncé sont justes et que l'énoncé
annonce tous les fichiers, fonctions et contraintes. Elle n'affiche ni test caché, ni indice.
