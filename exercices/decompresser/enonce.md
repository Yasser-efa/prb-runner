# Décompresser une chaine

> Exercice de début de séance du 17/11 : une chaine comme `a1b2c3d5` est la version compressée
> de `abbcccddddd`. Retrouvez la chaine de départ.

## Organisation

Un seul module, à la racine : `decompression.py`.

## Hypothèses

Une chaine compressée est une suite de couples formés d'un caractère, puis d'un **seul** chiffre
(de 0 à 9) qui donne son nombre de répétitions.

- Le caractère peut être n'importe lequel : lettre, espace, ponctuation… ou même un chiffre.
  Par exemple, `73` représente trois fois le caractère `7`.
- On considère que la chaine est correctement formatée. Elle peut être vide.

## Tâche 1 – `decompresser(compresse)`

Cette fonction prend en argument une chaine compressée et renvoie la chaine décompressée.

```
>>> decompresser('a1b2c3d5')
'abbcccddddd'
>>> decompresser('73')
'777'
```

## Tâche 2 – `taille_decompressee(compresse)`

Cette fonction prend en argument une chaine compressée et renvoie la longueur de la chaine
décompressée, **sans la construire**.

**Contrainte :** vous ne pouvez pas appeler `decompresser`.

```
>>> taille_decompressee('a1b2c3d5')
11
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Le module `re` est interdit.
- Chaque fonction est documentée (docstring Sphinx).
