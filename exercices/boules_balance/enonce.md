# Les boules et la balance

> Exercice de début de séance n° 2 : « J'ai 9 boules identiques. L'une d'elles est plus lourde que
> les autres. Je dispose d'une balance à plateaux. En combien de pesées (min) puis-je trouver la
> boule la plus lourde ? »

## Organisation

Un seul module, à la racine : `balance.py`.

## Hypothèses

- Il y a au moins une boule, et exactement une boule plus lourde que les autres.
- Une pesée compare deux groupes de boules. On cherche le plus petit nombre de pesées qui suffit
  **à coup sûr**, même dans le cas le moins favorable.

## Tâche 1 – `nombre_pesees(nb_boules)`

Cette fonction renvoie le nombre de pesées nécessaires pour trouver la boule la plus lourde parmi
`nb_boules` boules.

**Contrainte :** vous devez utiliser une boucle `while`.

```
>>> nombre_pesees(9)
2
>>> nombre_pesees(1)
0
```

## Tâche 2 (opération inverse) – `boules_maximum(nb_pesees)`

Cette fonction renvoie le plus grand nombre de boules parmi lesquelles on peut trouver la plus
lourde en `nb_pesees` pesées (un entier positif ou nul).

```
>>> boules_maximum(2)
9
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Le module `math` est interdit.
- Chaque fonction est documentée (docstring Sphinx).
