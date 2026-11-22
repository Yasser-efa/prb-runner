# Le classement des plongeurs

> Variante de l'exercice du 09/11 : plusieurs plongeurs ont été notés par les juges. Il faut les
> classer.

## Organisation

Un package `jo` qui contient les modules `notes.py` et `classement.py`.

## Structure de données

Les résultats sont un dictionnaire : les clés sont les noms des plongeurs, les valeurs sont les
listes des notes de leurs juges. On considère que chaque plongeur a au moins trois notes. Le
dictionnaire peut être vide. Aucun argument ne doit être modifié.

## Tâche 1 – `note_finale(notes)`, dans `notes.py`

Cette fonction retire une meilleure note et une moins bonne note, puis renvoie la moyenne des autres.

```
>>> note_finale([7, 8, 6, 9, 8.5])
7.833333333333333
```

## Tâche 2 – `classer(resultats)`, dans `classement.py`

Cette fonction renvoie la liste des tuples `(nom, note_finale)`, de la meilleure note à la moins
bonne. En cas d'égalité, les noms sont dans l'ordre alphabétique.

**Contrainte :** vous devez utiliser la fonction `note_finale`.

```
>>> classer({'Zoé': [8, 9, 7], 'Tom': [9, 9, 9], 'Ana': [5, 8, 10]})
[('Tom', 9.0), ('Ana', 8.0), ('Zoé', 8.0)]
```

## Tâche 3 – `podium(resultats)`, dans `classement.py`

Cette fonction renvoie les noms des trois premiers plongeurs du classement, ou de tous s'ils sont
moins de trois.

**Contrainte :** vous devez utiliser la fonction `classer`.

```
>>> podium({'Zoé': [8, 9, 7], 'Tom': [9, 9, 9]})
['Tom', 'Zoé']
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Le module `statistics` est interdit.
- Chaque fonction est documentée (docstring Sphinx).
