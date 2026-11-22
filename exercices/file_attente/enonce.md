# La file d'attente qui double

> Exercice de début de séance n° 8 : « Une file d'attente double à chaque minute. Après 8 minutes,
> elle compte 1536 personnes. Combien y en avait-il au départ ? »

## Organisation

- Un module `attente.py`, à la racine.
- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.

## Hypothèses

- Un effectif est un nombre **entier** de personnes, positif ou nul. Il peut être très grand.
- Le nombre de minutes est un entier positif ou nul.
- À chaque minute, l'effectif est multiplié par `facteur` (un entier strictement positif).

## Tâche 1 – `effectif_depart(effectif_final, minutes, facteur=2)`, dans `attente.py`

Cette fonction renvoie l'effectif de départ, sous forme d'entier. Si aucun effectif entier ne
convient, elle renvoie -1.

```
>>> effectif_depart(1536, 8)
6
>>> effectif_depart(10, 2)
-1
```

## Tâche 2 (généralisation) – `evolution(depart, minutes, facteur=2)`, dans `attente.py`

Cette fonction renvoie la liste des effectifs successifs : au départ, après 1 minute, après
2 minutes… jusqu'à `minutes` minutes comprises.

**Contrainte :** vous devez utiliser une expression en compréhension.

```
>>> evolution(6, 3)
[6, 12, 24, 48]
```

## Tâche 3 – Programme principal

Le programme demande l'effectif final et le nombre de minutes, puis affiche l'effectif de départ.
Vous devez utiliser `effectif_depart`. On considère que l'utilisateur tape des entiers corrects.

```
Effectif final ? 1536
Nombre de minutes ? 8
Effectif de départ : 6
```

```
Effectif final ? 10
Nombre de minutes ? 2
Situation impossible.
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
