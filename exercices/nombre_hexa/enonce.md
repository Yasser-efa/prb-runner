# Nombre hexadécimal

> Exercice de début de séance n° 12 : « On voudrait traduire un nombre hexadécimal sous forme de
> chaine en entier, mais sans la fonction build-in int() et en utilisant uniquement des chaines de
> caractères. Comment pourrait-on procéder ? »

## Organisation

- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.
- Un package `hexa` qui contient les modules `chiffres.py` et `nombres.py`.

## Hypothèses

- Les chiffres hexadécimaux sont `0` à `9`, puis `A` (10) à `F` (15), en majuscule ou en minuscule.
- Un nombre hexadécimal s'écrit en base 16 : chaque chiffre vaut 16 fois plus que s'il était placé
  une position plus à droite. Par exemple, `1F` vaut 1 × 16 + 15.
- On considère que les nombres donnés sont corrects et non vides. Ils peuvent commencer par des
  zéros et être très longs.

## Tâche 1 – `valeur_chiffre(chiffre)`, dans `chiffres.py`

Cette fonction renvoie la valeur d'un chiffre hexadécimal.

```
>>> valeur_chiffre('F')
15
```

## Tâche 2 – `valeur_nombre(nombre)`, dans `nombres.py`

Cette fonction renvoie la valeur d'un nombre hexadécimal, sous forme d'entier.

**Contrainte :** vous devez utiliser la fonction `valeur_chiffre`.

```
>>> valeur_nombre('1F')
31
>>> valeur_nombre('2a3')
675
```

## Tâche 3 – Programme principal

Le programme demande un nombre hexadécimal et affiche sa valeur. L'utilisateur peut taper des
espaces autour du nombre. Vous devez utiliser `valeur_nombre`.

```
Nombre hexadécimal ? 1F
Valeur : 31
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Aucun `dictionnaire` ne peut être écrit dans le code.
- Les fonctions `int`, `ord`, `hex`, `eval`, `float` et `bytes` sont interdites, ainsi que la
  méthode `.fromhex`.
- Chaque fonction est documentée (docstring Sphinx).
