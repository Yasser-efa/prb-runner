# Chiffre hexadécimal

> Exercice de début de séance n° 11 : « On voudrait traduire un chiffre hexadécimal sous forme de
> chaine en entier, mais sans la fonction build-in int() et en utilisant uniquement des chaines de
> caractères. Comment pourrait-on procéder ? »

## Organisation

Un seul module, à la racine : `chiffres.py`.

## Hypothèses

Les chiffres hexadécimaux sont `0` à `9`, puis `A` (10), `B` (11), `C` (12), `D` (13), `E` (14) et
`F` (15). On considère que les arguments des fonctions sont corrects.

## Tâche 1 – `valeur_chiffre(chiffre)`

Cette fonction prend en argument un chiffre hexadécimal, en majuscule **ou en minuscule**, et
renvoie sa valeur sous forme d'entier.

```
>>> valeur_chiffre('7')
7
>>> valeur_chiffre('b')
11
```

## Tâche 2 (opération inverse) – `chiffre_hexa(valeur)`

Cette fonction prend en argument un entier entre 0 et 15 et renvoie le chiffre hexadécimal
correspondant, en majuscule.

```
>>> chiffre_hexa(11)
'B'
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Vous ne pouvez utiliser que des chaines de caractères : pas de `dictionnaire`, de `liste` ni
  d'`ensemble` écrit dans le code, et pas de `f-string`.
- Les fonctions `int`, `ord`, `chr`, `hex`, `eval`, `float`, `bytes` et `format` sont interdites,
  ainsi que les méthodes `.format` et `.fromhex`.
- Chaque fonction est documentée (docstring Sphinx).
