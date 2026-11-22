# Examen de juin 2025 : Les Damoiselles

> Partie pratique, 2 h 30. L'énoncé original, avec ses figures, est dans
> `sources/anciens_examens/AI_PRB_Juin_2025.pdf` (damiers vierges dans `Sources-20261122/damier.pdf`).
> La tâche de tests unitaires est retirée. Les messages que l'original laissait libres sont fixés ici.

On veut aider un joueur de « damoiselles » (des dames sans dames) à trouver sa meilleure prise.

## Organisation

- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.
- Un package `damoiselles` qui contient le module `damier.py` et le module fourni `pions.py`
  (interdit de modification).

Les pions se manipulent avec les constantes et les fonctions de `pions.py` : lisez sa documentation.

## Le damier

- Il compte 10 lignes et 10 colonnes. Seules les cases **blanches** sont utilisées ; la case en haut à
  gauche est noire.
- Les cases blanches sont numérotées de 0 à 49, de gauche à droite et de haut en bas.
- La « position des pions » est un dictionnaire : les clés sont des numéros de cases, les valeurs des
  pions.

Définissez dans `damier.py` les constantes suivantes :

```
HAUTEUR, LARGEUR = 10, 10
CASE_NOIRE = "█"*3
```

## Tâche 2.1 – `dessiner_damier(positions_pions)`, dans `damier.py`

Une phase préparatoire est demandée : sur un dessin du damier, déterminez comment savoir qu'une case
est blanche, le lien entre le numéro d'une case et ses ligne et colonne, et quelles cases sont au bord.

Cette fonction dessine le damier. Une case noire s'affiche avec `CASE_NOIRE`, une case blanche avec
son pion ou, si elle est vide, avec son numéro aligné à droite sur trois caractères.

```
>>> dessiner_damier({27: ' ● ', 13: ' ○ ', 18: ' ○ ', 22: ' ○ '})
███  0███  1███  2███  3███  4
  5███  6███  7███  8███  9███
███ 10███ 11███ 12███ ○ ███ 14
 15███ 16███ 17███ ○ ███ 19███
███ 20███ 21███ ○ ███ 23███ 24
 25███ 26███ ● ███ 28███ 29███
███ 30███ 31███ 32███ 33███ 34
 35███ 36███ 37███ 38███ 39███
███ 40███ 41███ 42███ 43███ 44
 45███ 46███ 47███ 48███ 49███
```

## Tâche 2.2 – `position_depart()`, dans `damier.py`

Cette fonction renvoie la position des pions en début de partie : des pions noirs sur les 20 premières
cases et des pions blancs sur les 20 dernières.

## Tâche 3.1 – `voisines(numero_case)`, dans `damier.py`

Cette fonction renvoie l'ensemble des numéros des cases atteignables en diagonale, d'une seule case.

```
>>> voisines(0)
{5, 6}
>>> voisines(21)
{16, 17, 26, 27}
>>> voisines(38)
{32, 33, 42, 43}
```

## Tâche 3.2 – `arrivee_capture(depart, prise)`, dans `damier.py`

Un pion placé sur la case `depart` prend le pion de la case `prise` en sautant par-dessus, en
diagonale. Cette fonction renvoie la case d'arrivée, ou -1 si la prise est impossible (les cases ne
sont pas voisines ou l'arrivée est hors du damier). On ne s'occupe pas ici des pions présents.

**Contrainte :** vous devez utiliser `voisines`. L'énoncé original conseille une opération sur des
ensembles.

```
>>> arrivee_capture(27, 22)
18
>>> arrivee_capture(27, 18)
-1
>>> arrivee_capture(6, 0)
-1
```

## Tâche 3.3 – `captures_possibles(positions_pions, depart)`, dans `damier.py`

Cette fonction renvoie l'ensemble des prises possibles, simples et multiples, à partir d'une case.
Une prise s'écrit avec ses étapes séparées par `x`. Si la case de départ est vide, l'ensemble est
vide. La position des pions ne doit pas être modifiée. Voici l'algorithme à suivre :

- `prises_a_explorer` est une liste de listes d'étapes, qui vaut `[[depart]]` au départ.
- Tant qu'elle n'est pas vide, retirez sa dernière liste d'étapes. Pour chaque voisine `v` de la
  dernière étape, calculez l'arrivée d'une prise de `v`.
- Si l'arrivée existe, n'est pas déjà une étape, est une case vide, et que les pions de `v` et de
  `depart` sont de couleurs différentes : créez une nouvelle liste d'étapes qui se termine par
  l'arrivée, et décrivez-la (`27x18x7`).
- Si cette description est nouvelle, ajoutez-la au résultat et ajoutez la nouvelle liste à la fin de
  `prises_a_explorer`.

**Contrainte :** vous devez utiliser `voisines`, `arrivee_capture`, et les fonctions
`sont_couleurs_differentes` et `est_case_vide` de `pions.py`.

```
>>> captures_possibles({27: ' ○ ', 21: ' ● ', 22: ' ● ', 31: ' ● ', 32: ' ● ', 12: ' ● '}, 27)
{'27x36', '27x18x7', '27x16', '27x38', '27x18'}
```

## Tâche 4 – Documentation

Les fonctions sont documentées avec des docstrings Sphinx complètes.

## Tâche 6 – Programme principal (version avancée)

Le programme affiche le damier de départ, puis un menu. Après chaque opération, il demande la
suivante ; le menu n'est réaffiché que si le choix est incorrect. Vous devez utiliser
`position_depart`, `dessiner_damier` et `captures_possibles`.

1. Vider le damier.
2. Ajouter des pions : les numéros des cases sont séparés par des espaces (il peut n'y en avoir
   aucun). Le damier est ensuite affiché.
3. Calculer la meilleure prise à partir d'une case, c'est-à-dire la plus longue. S'il n'y en a pas,
   le programme affiche `Pas de capture possible !` Si la saisie n'est pas un entier, il affiche
   `Entrez un entier.`
4. Quitter.

Les lignes vides de l'affichage n'importent pas. Après l'affichage du damier de départ :

```
1. Vider le damier
2. Ajouter des pions
3. Calculer la meilleure prise
4. Quitter
Votre choix ? 1
Damier vidé
Votre choix ? 2
Pions noirs ? 12 22 32
Pions blancs ? 27
```

Le damier s'affiche, puis :

```
Votre choix ? 3
Case départ ? 27
Meilleure capture : 27x18x7
Votre choix ? 3
Case départ ? blanc
Entrez un entier.
Votre choix ? 4
Au revoir
```

Le programme commence par `Bonjour !`

## Contraintes de l'outil

`break`, `continue` et `while True` sont interdits.
