# Examen d'aout 2025 : Poker d'As

> Partie pratique, 2 h 30. L'énoncé original, avec ses figures, est dans
> `sources/anciens_examens/Enonce_aout_2025.pdf`. La tâche de tests unitaires est retirée. Les messages
> que l'original laissait libres sont fixés ici.

Le joueur affronte l'ordinateur au Poker d'As : il lance cinq dés, peut en conserver certains et
relancer les autres. La meilleure combinaison gagne.

## Organisation

- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.
- Un package `poker` qui contient le module `poker_as.py` et le module fourni `des.py` (interdit de
  modification).

Lisez la documentation de `des.py` : vous devez utiliser ses fonctions quand c'est possible.

## Vocabulaire

- Les dés valent 1 à 6 : neuf, dix, valet, dame, roi, as, de la plus faible figure à la plus forte.
- La **combinaison** d'un tirage est le plus grand nombre de dés identiques : main vide (1), paire
  (2), brelan (3), carré (4), poker (5). S'il y en a plusieurs de même taille, seule la plus forte
  figure compte : il n'y a pas de double paire, ni de main pleine, ni de suite.
- Un tirage en bat un autre si sa combinaison compte plus de dés identiques ou, à égalité, si sa
  figure est plus forte.
- Un **tirage** est une liste de dés, par exemple `[1, 4, 5, 2, 1]`.
- Un **comptage** associe à chaque valeur son nombre de dés, par exemple `{1: 2, 4: 1, 5: 1, 2: 1}`.
- Un **détail de tirage** est la liste triée des dés, avec un 0 entre les valeurs différentes, par
  exemple `[1, 1, 0, 2, 0, 4, 0, 5]`.

## Tâche 2.1 – `analyser_comptage(comptage)`, dans `poker_as.py`

Cette fonction prend un comptage non vide et renvoie un tuple `(combinaison, figure)` : le nombre de
dés de la combinaison la plus forte et la valeur de ses dés.

```
>>> analyser_comptage({1: 1, 4: 1, 5: 1, 2: 2})
(2, 2)
>>> analyser_comptage({4: 2, 6: 1, 2: 2})
(2, 4)
```

## Tâche 2.2 – `comparer_tirages(tirage1, tirage2)`, dans `poker_as.py`

Cette fonction compare deux tirages non vides. Elle renvoie un entier strictement positif si le premier
est le meilleur, strictement négatif si c'est le second, et 0 s'ils ont la même force. Les tirages
n'ont pas forcément cinq dés.

## Tâche 2.3 – `detailler_tirage_des(comptage)`, dans `poker_as.py`

Cette fonction renvoie le détail du tirage correspondant à un comptage non vide.

```
>>> detailler_tirage_des({2: 3, 1: 1, 5: 1})
[1, 0, 2, 2, 2, 0, 5]
```

## Tâche 3.1 – `afficher_tirage(des)`, dans `main.py`

Cette fonction affiche, sur une ligne, l'initiale de chaque dé. Le 0 est affiché comme une espace.

**Contrainte :** vous devez utiliser la fonction `initiale`.

```
>>> afficher_tirage([2, 3, 1, 1, 5, 1])
XV99R9
>>> afficher_tirage([1, 0, 2, 0, 3])
9 X V
```

## Tâche 3.2 – `selectionner_des(detail_des)`, dans `main.py`

Cette fonction affiche un détail de tirage et demande à l'utilisateur de souligner d'un `-` les dés
qu'il veut conserver. Elle renvoie le comptage des dés soulignés. Les tirets placés sous les espaces
n'importent pas ; la ligne tapée peut être plus courte ou plus longue que l'affichage. La présentation
est libre.

```
Veuillez choisir vos dés à l'aide du symbole '-' :
 9 XXX D R
>  ---   -
```

Avec cette saisie, la fonction renvoie `{2: 3, 5: 1}`.

## Tâche 4 – Documentation

Les fonctions sont documentées avec des docstrings Sphinx complètes.

## Tâche 6 – Programme principal

Une phase préparatoire est demandée : elle concerne le tirage de la main du joueur. Dessinez comment
évoluent les dés conservés, et listez les étapes.

1. La main de l'ordinateur est le meilleur de `DIFFICULTE` tirages de cinq dés. `DIFFICULTE` est une
   constante qui vaut 3.
2. Le joueur lance cinq dés, puis peut en conserver jusqu'à trois fois. Les dés conservés ne sont plus
   relancés ; les autres le sont. Le jeu s'arrête dès que les cinq dés sont conservés. Après les trois
   choix, les dés restants sont relancés une dernière fois et font partie de la main.
3. Les deux mains sont comparées.

Pour que les tests soient reproductibles, l'ordinateur joue **avant** le joueur et chaque lancer passe
par un seul appel à `effectuer_tirage` avec le nombre de dés à lancer. Vous devez utiliser
`comparer_tirages`, `detailler_tirage_des` et `selectionner_des`.

Le programme affiche `Tirage ordinateur : ` suivi de la combinaison. À la fin, il affiche
`Tirage joueur : ` suivi du détail de la main, puis la combinaison du joueur et le résultat :
`Vous gagnez la partie.`, `Vous perdez la partie.` ou `Égalité.` Le reste de la présentation est libre.

```
-- Jeu du Poker d'As --
Tirage ordinateur : BRELAN de DAME
Veuillez choisir vos dés à l'aide du symbole '-' :
 VVV D R
>---
Veuillez choisir vos dés à l'aide du symbole '-' :
 AA
>
Veuillez choisir vos dés à l'aide du symbole '-' :
 X D
>
Tirage joueur : 9 VVV A
BRELAN de VALET
Vous perdez la partie.
```

## Contraintes de l'outil

`break`, `continue` et `while True` sont interdits.
