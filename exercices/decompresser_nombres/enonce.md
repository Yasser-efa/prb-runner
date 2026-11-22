# Décompresser avec des nombres à plusieurs chiffres

> Version plus dure de l'exercice du 17/11 : un caractère peut être répété plus de 9 fois.
> La chaine `a12b3` est la version compressée de `aaaaaaaaaaaabbb`.

## Organisation

Un package `rle` qui contient les modules `decoupage.py` et `decompression.py`.

## Hypothèses

Une chaine compressée est une suite de couples formés d'un caractère, puis d'un nombre naturel
écrit avec **un ou plusieurs chiffres**.

- Le caractère peut être n'importe lequel (lettre, espace, ponctuation…), **sauf un chiffre**.
- On considère que la chaine est correctement formatée. Elle peut être vide.

## Tâche 1 – `obtenir_couples(compresse)`, dans `decoupage.py`

Cette fonction renvoie la liste des couples de la chaine, dans l'ordre. Chaque couple est un
tuple formé du caractère et du nombre, sous forme d'entier.

**Contrainte :** vous devez utiliser au moins une boucle `while`.

```
>>> obtenir_couples('a12b3c1')
[('a', 12), ('b', 3), ('c', 1)]
```

## Tâche 2 – `decompresser(compresse)`, dans `decompression.py`

Cette fonction renvoie la chaine décompressée.

**Contrainte :** vous devez utiliser la fonction `obtenir_couples`.

```
>>> decompresser('a12b3c1')
'aaaaaaaaaaaabbbc'
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Le module `re` est interdit.
- Chaque fonction est documentée (docstring Sphinx).
