# Compresser de longues séries

> Variante de l'exercice du 18/11 : une série peut dépasser 9 caractères, mais chaque nombre de
> répétitions doit rester un **seul** chiffre. Douze `a` s'écrivent donc `a9a3`.

## Organisation

Un package `rle` qui contient les modules `couples.py` et `compression.py`.

## Hypothèses

La chaine peut contenir n'importe quels caractères. Elle peut être vide.

## Tâche 1 – `obtenir_couples(chaine, maximum=9)`, dans `couples.py`

Cette fonction renvoie la liste des couples `(caractere, nombre)` qui décrivent la chaine, dans
l'ordre. Un nombre ne dépasse jamais `maximum` (un entier strictement positif) : une série trop
longue donne plusieurs couples, tous complets sauf peut-être le dernier.

```
>>> obtenir_couples('aaaaaaaaaaaabb')
[('a', 9), ('a', 3), ('b', 2)]
>>> obtenir_couples('aaaaa', 2)
[('a', 2), ('a', 2), ('a', 1)]
```

## Tâche 2 – `compresser(chaine)`, dans `compression.py`

Cette fonction renvoie la chaine compressée, avec un seul chiffre par caractère.

**Contrainte :** vous devez utiliser la fonction `obtenir_couples`.

```
>>> compresser('aaaaaaaaaaaabb')
'a9a3b2'
```

## Tâche 3 – `meilleure_forme(chaine)`, dans `compression.py`

Cette fonction renvoie la version compressée si elle est **strictement plus courte** que la chaine,
et la chaine elle-même sinon.

**Contrainte :** vous devez utiliser la fonction `compresser`.

```
>>> meilleure_forme('aaab')
'aaab'
>>> meilleure_forme('aaaab')
'a4b1'
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Les modules `re` et `itertools` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
