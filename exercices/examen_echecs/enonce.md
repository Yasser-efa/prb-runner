# Examen de janvier 2026 : Échec

> Partie pratique, 2 h 30. L'énoncé original, avec ses figures, est dans
> `sources/anciens_examens/Énoncé et sources-20261122/IA_Janvier26_énoncé.pdf`, avec la feuille de
> phase préparatoire. La tâche de tests unitaires est retirée.

Le programme charge un échiquier depuis un fichier et détermine si le roi blanc est en échec, puis
s'il est échec et mat.

## Organisation

- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.
- Un package `echecs` qui contient le module `analyse.py` et trois modules fournis :
  `deplacements.py`, `pieces.py` (interdits de modification) et `echiquiers.py` (des exemples).
- Un dossier `fichiers` fourni, avec des échiquiers.

Lisez la documentation des modules fournis avant de commencer.

## Les règles

- Le fou se déplace en diagonale, la tour sur une ligne ou une colonne, la dame des deux façons,
  d'autant de cases qu'ils veulent jusqu'à un obstacle. Le roi va sur une des huit cases voisines.
- Une pièce peut capturer une pièce de l'autre couleur si elle peut atteindre sa case. Elle ne peut ni
  passer par-dessus une pièce, ni continuer après une capture.
- Le roi est en échec si une pièce adverse peut le capturer. Il est échec **et mat** s'il est en
  échec et que, sur chacune des cases où il peut aller, il serait encore en échec. (Pas d'autre
  défense dans cet examen.)

## Les données

- Une position est un tuple `(ligne, colonne)`, de `(0, 0)` en haut à gauche à `(7, 7)` en bas à
  droite.
- Dans un fichier, chaque ligne contient `PIECE Couleur Ligne Colonne`. La pièce est `TOUR`, `FOU`,
  `DAME` ou `ROI` ; la couleur est `Blanc` ou `Noir`. On considère que les fichiers qui existent sont
  corrects.
- Un échiquier est un dictionnaire. Les clés sont les positions occupées, les valeurs des
  dictionnaires `{'piece': ..., 'couleur': ...}`.

```
TOUR Noir 0 0
ROI Blanc 7 0
```

Ce fichier donne `{(0, 0): {'piece': 'TOUR', 'couleur': 'Noir'}, (7, 0): {'piece': 'ROI', 'couleur': 'Blanc'}}`.

## Tâche 2.1 – `charger_depuis(chemin)`, dans `analyse.py`

Cette fonction charge un échiquier depuis un fichier. Elle renvoie un dictionnaire vide si le fichier
ne peut pas être ouvert ou lu.

## Tâche 2.2 – `dessiner(echiquier)`, dans `analyse.py`

Cette fonction affiche l'échiquier, 8 lignes de 8 cases. Chaque case est affichée avec la fonction
`afficher` de `pieces.py` ; une case vide utilise la pièce `'CASE_VIDE'`. La case `(0, 0)` est blanche
et les couleurs alternent comme sur un damier.

**Contrainte :** vous devez utiliser `afficher`.

Dans le verdict, l'outil remplace chaque case par deux caractères : une lettre (`T`, `F`, `D` ou `R`,
en minuscule pour une pièce noire, une espace si la case est vide), puis `.` pour une case blanche ou
`:` pour une case noire. La première ligne d'un échiquier vide devient ` . : . : . : . :`.

## Tâche 3.1 – `cases_attaquees(echiquier, position)`, dans `analyse.py`

Une phase préparatoire est demandée : dessinez une pièce gênée par une pièce de chaque couleur, les
résultats des appels à `calculer_en_theorie` et les cases attaquées. Justifiez vos boucles et exprimez
en français la condition d'arrêt des `while`.

Cette fonction renvoie l'ensemble des cases attaquées par la pièce placée à cette position : celles où
elle peut se déplacer librement et celles où elle peut capturer une pièce.

**Contrainte :** vous devez utiliser `calculer_en_theorie`, avec les constantes de `deplacements.py`.
Attention, elle donne parfois des cases hors de l'échiquier.

```
>>> cases_attaquees({(0, 0): {'piece': 'TOUR', 'couleur': 'Noir'}, (0, 2): {'piece': 'ROI', 'couleur': 'Noir'}, (3, 0): {'piece': 'FOU', 'couleur': 'Blanc'}}, (0, 0))
{(0, 1), (1, 0), (2, 0), (3, 0)}
```

## Tâche 3.2 – `roi_blanc_en_echec(echiquier)`, dans `analyse.py`

Cette fonction renvoie vrai si le roi blanc est en échec. S'il n'y a pas de roi blanc, elle renvoie
faux.

**Contrainte :** vous devez utiliser `cases_attaquees`.

```
>>> roi_blanc_en_echec({})
False
```

## Tâche 4 – Documentation

Les fonctions sont documentées avec des docstrings Sphinx complètes.

## Tâche 6 – Programme principal (avec l'échec et mat)

Le programme demande un chemin, affiche l'échiquier et son analyse : `Pas d'échec.`, `Échec !` si le
roi blanc est en échec sans être mat, et les deux lignes suivantes s'il est mat. Vous devez utiliser
`charger_depuis`, `dessiner` et `roi_blanc_en_echec`. Les lignes vides n'importent pas.

```
-- Analyse d'échiquier --
Chemin du fichier ? fichiers/harry_potter.txt
(l'échiquier)
Échec
 ... et Mat !
```

N'oubliez pas que la disposition de l'échiquier change quand une pièce se déplace.

## Contraintes de l'outil

`break`, `continue` et `while True` sont interdits.
