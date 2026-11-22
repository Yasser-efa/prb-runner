# Le taxi : un trajet à étapes

> Variante de l'exercice du 10/11 : dans une ville en damier, un taxi passe par plusieurs carrefours,
> dans un ordre imposé.

## Organisation

- Un module `trajets.py`, à la racine.
- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.

## Hypothèses

Un carrefour est un tuple de deux entiers, éventuellement négatifs. Le taxi suit les rues et prend
toujours un des plus courts chemins. Les listes reçues ne doivent pas être modifiées.

## Tâche 1 – `distance_taxi(depart, arrivee)`, dans `trajets.py`

Cette fonction renvoie la distance entre deux carrefours.

```
>>> distance_taxi((2, 3), (7, 1))
7
```

## Tâche 2 – `lire_etapes(texte)`, dans `trajets.py`

Cette fonction prend en argument une chaine qui contient des carrefours de la forme `x,y`, séparés par
une ou plusieurs espaces. Elle renvoie la liste des carrefours. On considère que la chaine est
correctement formatée. Elle peut être vide.

```
>>> lire_etapes('2,3 7,1 -1,0')
[(2, 3), (7, 1), (-1, 0)]
```

## Tâche 3 – `distance_trajet(etapes)`, dans `trajets.py`

Cette fonction renvoie la distance totale d'un trajet qui passe par toutes les étapes, dans l'ordre.
S'il y a moins de deux étapes, la distance vaut 0.

**Contrainte :** vous devez utiliser la fonction `distance_taxi`.

```
>>> distance_trajet([(2, 3), (7, 1), (0, 0)])
15
```

## Tâche 4 – `taxi_le_plus_proche(client, taxis)`, dans `trajets.py`

Cette fonction renvoie l'indice, dans la liste `taxis`, du taxi le plus proche du client. En cas
d'égalité, c'est le premier de la liste. Si la liste est vide, elle renvoie -1.

**Contrainte :** vous devez utiliser la fonction `distance_taxi`.

```
>>> taxi_le_plus_proche((0, 0), [(5, 5), (1, 2), (3, 0)])
1
```

## Tâche 5 – Programme principal

Le programme demande les étapes et affiche la distance totale. Vous devez utiliser `lire_etapes` et
`distance_trajet`.

```
Étapes ? 2,3 7,1 0,0
Distance : 15
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
