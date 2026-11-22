# Examen de janvier 2025 : Slam

> Partie pratique, 2 h. L'énoncé original, avec ses figures, est dans
> `sources/anciens_examens/AI_PRB_Janvier_2025.pdf`. La tâche de tests unitaires est retirée. Les
> messages que l'original laissait libres sont fixés ici.

On veut programmer une variante de la finale du jeu « Slam » : le joueur doit retrouver les mots
d'une grille de mots croisés. Chaque mot porte un numéro.

## Organisation

- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.
- Un package `slam` qui contient le module `grille_mots.py` et trois modules fournis :
  `colonnes_positions.py`, `fonctions.py` (interdits de modification) et `exemples.py` (des grilles).

Lisez la documentation de `colonnes_positions.py` avant de commencer.

## La grille

Une grille est une liste de lignes ; une ligne est une liste de caractères (des lettres ou des
espaces). Une position est un tuple `(ligne, colonne)`.

```
[[' ', ' ', ' '], [' ', 'A', 'B'], [' ', 'C', 'D']]
```

On considère que la grille a assez de place pour numéroter tous les mots et qu'elle en contient au
plus neuf. Inutile de le vérifier.

## Tâche 2.1 – `chercher_mots_ligne(ligne, numero, note)`, dans `grille_mots.py`

Une phase préparatoire est demandée : dessinez une ligne de plusieurs mots avec ses index, et
indiquez où l'on détecte un nouveau mot, où l'on peut l'ajouter au résultat et avec quelles
informations.

Cette fonction cherche tous les mots d'au moins deux lettres dans la ligne. Elle renvoie une liste
de dictionnaires :

- `'mot'` : la liste des caractères du mot ;
- `'debut'` : le tuple `(numero, index)`, où `index` est la position de la première lettre ;
- `'note'` : la note reçue.

```
>>> chercher_mots_ligne(['M', 'T', ' ', 'T', ' ', 'T', 'O', 'T'], 17, '###')
[{'mot': ['M', 'T'], 'debut': (17, 0), 'note': '###'}, {'mot': ['T', 'O', 'T'], 'debut': (17, 5), 'note': '###'}]
>>> chercher_mots_ligne([' ', ' ', ' '], 289, 'RAS')
[]
```

## Tâche 2.2 – `chercher_mots_grille(grille)`, dans `grille_mots.py`

Cette fonction renvoie la liste de tous les mots de la grille, dans le même format :

- d'abord les mots horizontaux, ligne par ligne, avec la note `'H'` et le début
  `(numero_ligne, index)` ;
- puis les mots verticaux, colonne par colonne, avec la note `'V'` et le début
  `(numero_colonne, index)`.

**Contrainte :** vous devez utiliser `chercher_mots_ligne` et `obtenir_colonne`.

```
>>> chercher_mots_grille([[' ', ' ', ' '], [' ', 'A', 'B'], [' ', 'C', 'D']])
[{'mot': ['A', 'B'], 'debut': (1, 1), 'note': 'H'}, {'mot': ['C', 'D'], 'debut': (2, 1), 'note': 'H'},
 {'mot': ['A', 'C'], 'debut': (1, 1), 'note': 'V'}, {'mot': ['B', 'D'], 'debut': (2, 1), 'note': 'V'}]
```

## Tâche 3.1 – `numeroter_grille(grille, liste_mots)`, dans `grille_mots.py`

Cette fonction **modifie** la grille. Pour chaque mot de la liste, elle écrit son numéro (sa place
dans la liste, à partir de 1, sous forme de chaine) dans la case à gauche de la première lettre s'il
est horizontal, au-dessus s'il est vertical. Les mots absents de la liste sont ignorés.

Après l'appel avec la grille ci-dessus et les mots `AB`, `CD` et `BD` de l'exemple précédent, la
grille vaut :

```
[[' ', ' ', '3'], ['1', 'A', 'B'], ['2', 'C', 'D']]
```

## Tâche 3.2 – `afficher_grille(grille, positions_trouvees)`, dans `grille_mots.py`

Cette fonction affiche la grille. Les lettres sont remplacées par `_`, sauf celles dont la position
est dans l'ensemble `positions_trouvees`. Les autres caractères sont affichés normalement.

**Contrainte :** utilisez la méthode des chaines qui reconnait une lettre (`isalpha`).

```
>>> afficher_grille([['1', 'A', 'B'], ['2', 'C', 'D']], {(0, 2), (1, 1), (0, 0)})
1_B
2C_
```

## Tâche 4 – Documentation

Les fonctions sont documentées avec des docstrings Sphinx complètes.

## Tâche 6 – Programme principal (version avancée)

Le programme joue une partie avec la grille `ENONCE` de `exemples.py` :

1. Il salue le joueur, annonce le nombre de mots et le nombre d'essais (nombre de mots + 3), puis
   affiche la grille numérotée.
2. Il demande une proposition de la forme `C MOT`, où `C` est un chiffre de 1 à 9 et `MOT` un mot
   d'au moins deux lettres majuscules, séparés par **une** espace. Le format est vérifié avec une
   expression régulière (module `re`). S'il est incorrect, la question est reposée sans consommer
   d'essai.
3. Une proposition correcte révèle le mot : la grille est affichée à nouveau. Utilisez
   `positions_mot`.
4. Une proposition incorrecte affiche `MOT : ce mot n'est pas correct.` C'est aussi le cas si le
   numéro ne correspond à aucun mot.
5. Un mot déjà trouvé affiche `MOT : ce mot a déjà été trouvé.` L'essai est consommé.
6. La partie s'arrête quand tous les mots sont trouvés ou qu'il n'y a plus d'essai.

Les lignes vides de l'affichage n'importent pas. Début d'une partie :

```
Bienvenue dans Slam sur France 3 !
Il y a 5 mots à trouver, vous avez 8 essais.
      5
      _
  4   _
1__2______
  _   _
 3_____
Entrez un numéro suivi d'un mot : 4 FOR
      5
      _
  4   _
1_F2______
  O   _
 3R____
Entrez un numéro suivi d'un mot : K 2000
Entrez un numéro suivi d'un mot : 5 GOTO
GOTO : ce mot n'est pas correct.
```

La dernière ligne est `Bravo, vous avez gagné !` ou `Dommage, vous avez perdu.`

## Contraintes de l'outil

- `break`, `continue` et `while True` sont interdits.
- Vous devez utiliser `chercher_mots_grille`, `numeroter_grille`, `afficher_grille` et
  `positions_mot`.
