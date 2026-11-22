# Les maisons d'une rue

> Exercice de début de séance n° 3 : « Le nombre de maisons situées entre les numéros 17 et 25
> d'une rue (s'il n'y a pas de numéro doublé). » Bonus : envisagez plusieurs cas.

## Organisation

Un package `rue` qui contient le module `numeros.py`.

## Vocabulaire et hypothèses

- Le long d'un **quai**, il n'y a des maisons que d'un côté : les numéros se suivent (1, 2, 3…).
- Dans une **rue**, les numéros impairs sont d'un côté et les pairs de l'autre. D'une maison à la
  suivante du même côté, on avance donc de 2 en 2.
- Tous les numéros existent, sans numéro doublé (comme 17 bis).
- Les deux numéros peuvent être donnés dans n'importe quel ordre. Ils peuvent être égaux.
- `bornes_comprises` indique si les deux maisons données sont comptées elles-mêmes.

## Tâche 1 – `maisons_quai(premier, dernier, bornes_comprises=True)`

Cette fonction renvoie le nombre de maisons situées entre les deux numéros d'un quai.

```
>>> maisons_quai(17, 25)
9
>>> maisons_quai(17, 25, False)
7
```

## Tâche 2 – `maisons_rue(premier, dernier, bornes_comprises=True)`

Cette fonction renvoie le nombre de maisons situées entre les deux numéros, **du même côté** d'une
rue. Si les deux numéros ne sont pas du même côté de la rue, elle renvoie -1.

```
>>> maisons_rue(17, 25)
5
>>> maisons_rue(17, 25, False)
3
>>> maisons_rue(17, 24)
-1
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
