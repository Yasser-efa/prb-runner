# Les arrêts du bus

> Exercice de début de séance n° 7 : « Après son premier arrêt, un bus s'arrête tous les 9 km. Si le
> premier arrêt est au kilomètre 3, à quelle distance sera le 15e arrêt ? »
> Bonus : donnez des valeurs limites aux paramètres.

## Organisation

Un seul module, à la racine : `ligne.py`.

## Hypothèses

- Les arrêts sont numérotés à partir de 1. La ligne est infinie.
- `premier` est la position du premier arrêt, en kilomètres (un entier positif ou nul).
- `ecart` est la distance entre deux arrêts, en kilomètres (un entier strictement positif).

## Tâche 1 – `position_arret(numero, premier=3, ecart=9)`

Cette fonction renvoie la position de l'arrêt demandé, en kilomètres.

**Contrainte :** les boucles `for` et `while` sont interdites.

```
>>> position_arret(15)
129
>>> position_arret(2, 10, 5)
15
```

## Tâche 2 (opération inverse) – `numero_arret(position, premier=3, ecart=9)`

Cette fonction renvoie le numéro de l'arrêt situé à cette position (un entier positif ou nul). S'il
n'y a pas d'arrêt à cet endroit, elle renvoie -1.

**Contrainte :** les boucles `for` et `while` sont interdites.

```
>>> numero_arret(129)
15
>>> numero_arret(130)
-1
```

## Tâche 3 (généralisation) – `arrets_entre(debut, fin, premier=3, ecart=9)`

Cette fonction renvoie la liste des positions des arrêts situés entre les kilomètres `debut` et
`fin`, bornes comprises, de la plus petite à la plus grande.

```
>>> arrets_entre(10, 40)
[12, 21, 30, 39]
>>> arrets_entre(4, 11)
[]
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
