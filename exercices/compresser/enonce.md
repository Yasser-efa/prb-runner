# Compresser une chaine

> Exercice de début de séance du 18/11 : faites l'opération inverse de la décompression.
> La chaine `aaabbcccc` devient `a3b2c4`.

## Organisation

- Un module `compresseur.py`, à la racine.
- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.

## Vocabulaire et hypothèses

- Une *série* est une suite de caractères identiques qui se touchent, la plus longue possible.
  Dans `abba`, il y a trois séries : `a`, `bb` et `a`.
- La chaine peut contenir n'importe quels caractères. Elle peut être vide.
- On considère qu'une série ne dépasse jamais 9 caractères.

## Tâche 1 – `obtenir_couples(chaine)`, dans `compresseur.py`

Cette fonction renvoie la liste des séries de la chaine, dans l'ordre. Chaque série est un tuple
formé du caractère et du nombre de fois qu'il apparait.

```
>>> obtenir_couples('aaabbcccc')
[('a', 3), ('b', 2), ('c', 4)]
>>> obtenir_couples('abba')
[('a', 1), ('b', 2), ('a', 1)]
```

## Tâche 2 – `compresser(chaine)`, dans `compresseur.py`

Cette fonction renvoie la chaine compressée : chaque série est remplacée par son caractère suivi
de son nombre de répétitions.

**Contrainte :** vous devez utiliser la fonction `obtenir_couples`.

```
>>> compresser('aaabbcccc')
'a3b2c4'
>>> compresser('abba')
'a1b2a1'
```

## Tâche 3 – Programme principal

Le programme demande une chaine, affiche sa version compressée, puis les deux longueurs. Vous
devez utiliser `compresser`.

```
Chaine ? aaabbcccc
Compressée : a3b2c4
Longueur : 9 -> 6
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Les modules `re` et `itertools` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
