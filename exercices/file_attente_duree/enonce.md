# La file d'attente : combien de temps ?

> Variante de l'exercice n° 8 : une file d'attente de 6 personnes double à chaque minute. Après
> combien de minutes compte-t-elle au moins 1000 personnes ?

## Organisation

- Un module `attente.py`, à la racine.
- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.

## Hypothèses

On considère que l'effectif de départ vaut au moins 1 et que le facteur vaut au moins 2.

## Tâche 1 – `minutes_necessaires(depart, voulu, facteur=2)`, dans `attente.py`

Cette fonction renvoie le plus petit nombre de minutes au bout duquel la file compte au moins
`voulu` personnes. À chaque minute, l'effectif est multiplié par `facteur`.

**Contrainte :** vous devez utiliser une boucle `while`.

```
>>> minutes_necessaires(6, 1000)
8
>>> minutes_necessaires(6, 6)
0
```

## Tâche 2 – `premier_depassement(effectifs, capacite)`, dans `attente.py`

Cette fonction prend en argument la liste des effectifs relevés minute par minute (à partir de la
minute 0). Elle renvoie la première minute à laquelle l'effectif **dépasse strictement** la
capacité, ou -1 si cela n'arrive jamais. La liste reçue ne doit pas être modifiée.

**Contrainte :** vous devez utiliser une boucle `while`. Les boucles `for` sont interdites dans cette
fonction.

```
>>> premier_depassement([6, 12, 24, 20], 15)
2
>>> premier_depassement([6, 12], 12)
-1
```

## Tâche 3 – Programme principal

Le programme demande l'effectif de départ et l'effectif voulu, puis affiche la durée. Vous devez
utiliser `minutes_necessaires`.

```
Effectif de départ ? 6
Effectif voulu ? 1000
Durée : 8 min
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Le module `math` est interdit.
- Chaque fonction est documentée (docstring Sphinx).
