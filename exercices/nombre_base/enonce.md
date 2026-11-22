# Nombre dans une base quelconque

> Variante de l'exercice n° 12 : le nombre n'est plus forcément écrit en base 16.

## Organisation

Un seul module, à la racine : `bases.py`.

## Hypothèses

- Une base est un entier entre 2 et 36.
- En base `b`, on utilise les `b` premiers chiffres parmi `0` à `9`, puis `A` (10) à `Z` (35), en
  majuscule ou en minuscule. La base 2 utilise `0` et `1`, la base 8 `0` à `7`.
- Dans un nombre, chaque chiffre vaut `b` fois plus que s'il était placé une position plus à droite.

## Tâche 1 – `est_valide(nombre, base=16)`

Cette fonction renvoie vrai si la chaine est un nombre correct dans cette base. Une chaine vide n'est
pas un nombre. Un nombre ne contient ni signe, ni espace.

```
>>> est_valide('1F')
True
>>> est_valide('128', 8)
False
```

## Tâche 2 – `valeur_nombre(nombre, base=16)`

Cette fonction renvoie la valeur du nombre, sous forme d'entier. Si le nombre n'est pas valide dans
cette base, elle renvoie -1.

```
>>> valeur_nombre('1011', 2)
11
>>> valeur_nombre('z', 36)
35
>>> valeur_nombre('128', 8)
-1
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Aucun `dictionnaire` ne peut être écrit dans le code.
- Les fonctions `int`, `ord`, `chr`, `eval`, `float` et `bytes` sont interdites.
- Chaque fonction est documentée (docstring Sphinx).
