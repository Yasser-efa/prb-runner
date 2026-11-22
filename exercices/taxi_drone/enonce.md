# Le taxi et le drone

> Exercice de début de séance du 10/11 (n° 17) : « Dans une ville en damier, un taxi va du carrefour
> (2, 3) au carrefour (7, 1). Quelle distance parcourt-il ? Et un drone ? »

## Organisation

Un package `distances` qui contient les modules `taxi.py` et `drone.py`.

## Hypothèses

- Un carrefour est un tuple de deux entiers, éventuellement négatifs.
- L'unité de distance est la longueur d'un côté de bloc de maisons.
- Le taxi suit les rues et prend un des plus courts chemins. Le drone vole en ligne droite.

## Tâche 1 – `distance_taxi(depart, arrivee)`, dans `taxi.py`

Cette fonction renvoie la distance parcourue par le taxi, sous forme d'entier.

```
>>> distance_taxi((2, 3), (7, 1))
7
```

## Tâche 2 – `distance_drone(depart, arrivee)`, dans `drone.py`

Cette fonction renvoie la distance parcourue par le drone.

```
>>> distance_drone((0, 0), (3, 4))
5.0
>>> distance_drone((2, 3), (7, 1))
5.385164807134504
```

## Tâche 3 – `gain_drone(depart, arrivee)`, dans `drone.py`

Cette fonction renvoie la distance que le drone économise par rapport au taxi.

**Contrainte :** vous devez utiliser les fonctions `distance_taxi` et `distance_drone`.

```
>>> gain_drone((0, 0), (3, 4))
2.0
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
