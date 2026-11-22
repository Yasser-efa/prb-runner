# Les sièges du cinéma

> Exercice de début de séance n° 4 : « Les sièges d'un cinéma sont numérotés de 1 à 240, avec 20
> sièges par rangée. Dans quelle rangée et à quelle position se trouve le siège 147 ? »
> Bonus : proposez l'opération inverse.

## Organisation

- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.
- Un package `salle` qui contient le module `sieges.py`.

## Hypothèses

- Les rangées et les positions dans une rangée sont numérotées à partir de 1.
- Les sièges 1 à 20 forment la rangée 1, les sièges 21 à 40 la rangée 2, etc.
- On considère que les arguments des fonctions sont des entiers strictement positifs et que la
  position existe dans la rangée.

## Tâche 1 – `position_siege(siege, sieges_par_rangee=20)`, dans `sieges.py`

Cette fonction renvoie un tuple `(rangee, position)`.

```
>>> position_siege(147)
(8, 7)
>>> position_siege(5, 4)
(2, 1)
```

## Tâche 2 (opération inverse) – `numero_siege(rangee, position, sieges_par_rangee=20)`, dans `sieges.py`

Cette fonction renvoie le numéro du siège.

```
>>> numero_siege(8, 7)
147
```

## Tâche 3 – Programme principal

Le programme demande un numéro de siège et affiche sa place. La salle compte 240 sièges : si le
numéro n'existe pas, il l'indique. Vous devez utiliser `position_siege`. On considère que
l'utilisateur tape un entier.

```
Numéro du siège ? 147
Rangée 8, position 7
```

```
Numéro du siège ? 241
Ce siège n'existe pas.
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Les boucles `while` et `for` sont interdites.
- Chaque fonction est documentée (docstring Sphinx).
