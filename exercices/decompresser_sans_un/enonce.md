# Compression abrégée, sans les 1

> Variante des exercices des 17/11 et 18/11 : le nombre de répétitions peut avoir plusieurs chiffres,
> et il est **omis quand il vaut 1**. La chaine `abbbc` s'écrit donc `ab3c`.

## Organisation

Un seul module, à la racine : `abrege.py`.

## Hypothèses

- Les caractères d'origine ne sont jamais des chiffres. Les chaines peuvent être vides.
- On considère que les chaines compressées sont correctement formatées. Un nombre écrit vaut toujours
  au moins 2.

## Tâche 1 – `decompresser(compresse)`

Cette fonction renvoie la chaine décompressée.

```
>>> decompresser('ab3c')
'abbbc'
>>> decompresser('x12')
'xxxxxxxxxxxx'
```

## Tâche 2 (opération inverse) – `compresser(chaine)`

Cette fonction renvoie la chaine compressée.

```
>>> compresser('abbbc')
'ab3c'
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Les modules `re` et `itertools` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
