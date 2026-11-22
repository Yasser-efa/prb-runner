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
| `python -m prb du_jour <id>` | l'exercice de ton choix, par exemple un ancien examen |
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

`du_jour <id>` passe outre cet ordre. Les anciens examens ne sortent que de cette façon : sans `<id>`,
`du_jour` ne les propose, ne les reprend et ne les révise jamais. Les autres exercices en cours sont
rappelés sous l'énoncé.

Un exercice réussi revient après 3 jours, puis 7, puis 21 ; ensuite il est acquis. Une révision qui
n'est pas réussie le jour même revient le lendemain et repart à 3 jours. Au début d'une révision,
l'ancien code est rangé dans `mes_solutions/_archives/`.

Le chrono additionne les séances d'un même exercice, plafonnées à 90 minutes chacune (30 minutes
de plus que la durée prévue pour les examens). Il compte jusqu'à ta dernière commande, sans le temps
passé sur un autre exercice.

### Les anciens examens

Cinq anciens examens (`examen_...`) se lancent à la demande, par exemple avec
`python -m prb du_jour examen_slam` ; relance la même commande pour les reprendre. `du_jour` copie
les fichiers fournis par le prof depuis `sources/anciens_examens/` ; comme à l'examen, les modifier
rend le dépôt non recevable. Les tâches de tests unitaires sont retirées.

### Le verdict

1. **Recevabilité** (bloquant) : fichiers et packages demandés avec leurs noms exacts (un fichier
   peut être vide), et aucune erreur que PyCharm montre en rouge : syntaxe, noms non définis, imports
   inexistants, expressions régulières incorrectes, liste dans un ensemble ou comme clé… Les
   avertissements (⚠) ne bloquent pas.
2. **Contraintes** (bloquant) : constructions, fonctions et modules interdits ou imposés. Les tests
   sont exécutés quand même.
3. **Tests** (tout ou rien) : les tests visibles sont détaillés, les tests cachés sont comptés. Une
   fonction absente, ou dont la signature diffère de l'énoncé, rate ses tests ; les autres sont
   exécutés.
4. **Qualité** (non bloquant) : PEP 8, nommage, docstrings Sphinx, modularité, bonnes pratiques.

Ton code est exécuté sur une copie, dans un processus isolé, avec 2 secondes par test.

L'étape 1 applique les consignes d'examen : fichiers, organisation, icône rouge de PyCharm. La
dernière condition, une phase préparatoire sur papier à ton nom, dépend de toi. L'outil approche
l'icône rouge sans la remplacer : en cas de doute, regarde celle de l'éditeur.

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

Choisis un identifiant en minuscules (`ma_table`), puis ajoute-le dans `exercices/ordre.toml` : dans
`ordre` pour `du_jour`, ou dans `examens` pour un exercice lancé seulement à la demande.

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

modifiables = ["tables/exemples.py"]   # facultatif : fichiers fournis que l'on peut modifier

[organisation.fournis]             # facultatif : copiés par du_jour, à laisser intacts
"tables/outils.py" = "sources/outils.py"
"tables/exemples.py" = "sources/archive.zip::exemples.py"

[[fonctions]]
module = "tables.calculs"
signature = "table(nombre: int, taille: int = 10) -> list[int]"   # « = ... » : valeur libre
preserve_arguments = true          # facultatif : ne pas modifier les arguments

[contraintes]                      # tout est facultatif
interdits = ["break", "continue", "try", "while True"]
imposes = ["while"]
fonctions_interdites = ["int", ".replace"]   # un point devant une méthode
modules_interdits = ["re"]
modules_imposes = ["random"]
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
sortie, comme dans la console de PyCharm. Autres clés possibles :

- `libelle` : le texte affiché à la place de l'appel ;
- `apres` : le nom d'un paramètre, dont on compare la valeur après l'appel ;
- `graine` : la graine de `random` ;
- `controle` : une fonction qui extrait ce qu'il faut comparer. `booleen`, `signe` et
  `sans_lignes_vides` existent ; un exercice peut définir les siennes dans
  `_prive/<id>/controles.py`, sous la forme `def nom(outcome, case)`.

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
tests = [{ appel = "lire('? ')", entree = ["3"] }]   # appel avec des saisies
ignorer_sortie = true              # ne compare que la valeur renvoyée
```

`apres`, `graine` et `controle` s'appliquent à tout un groupe.

- `fichiers/` (facultatif) : des fichiers ajoutés au projet pendant les tests seulement.
- `indices.toml` : `indices = ["premier indice", "deuxième", "troisième"]`.

### Vérifier l'exercice

```powershell
python -m prb valider ma_table
```

La commande vérifie que la solution est recevable, respecte les contraintes, passe les tests
visibles, reste loin du timeout et n'a aucune remarque de qualité. Elle vérifie aussi qu'il y a
assez de tests cachés et d'indices, que les exemples `>>>` de l'énoncé sont justes et que l'énoncé
annonce tous les fichiers, fonctions et contraintes. Elle n'affiche ni test caché, ni indice.
