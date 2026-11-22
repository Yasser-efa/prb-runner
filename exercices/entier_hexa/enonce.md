# D'un entier vers l'hexadécimal

> Opération inverse de l'exercice n° 12 : traduire un entier en nombre hexadécimal, sans les fonctions
> de conversion de Python.

## Organisation

- Un module `conversion.py`, à la racine.
- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.

## Hypothèses

- Les chiffres sont `0` à `9`, puis `A` (10), `B` (11)… jusqu'à `Z` (35). Une base est un entier
  entre 2 et 36.
- L'entier à traduire est positif ou nul. Il peut être très grand.
- Le résultat est écrit en majuscules, sans zéro inutile devant. Zéro s'écrit `0`.

## Tâche 1 – `entier_vers_base(valeur, base=16)`, dans `conversion.py`

Cette fonction renvoie l'écriture de l'entier dans la base donnée.

**Contrainte :** vous devez utiliser une boucle `while`. Les `f-string` sont interdites dans cette
fonction et dans la suivante.

```
>>> entier_vers_base(31)
'1F'
>>> entier_vers_base(11, 2)
'1011'
```

## Tâche 2 – `entier_vers_hexa(valeur)`, dans `conversion.py`

Cette fonction renvoie l'écriture hexadécimale de l'entier.

```
>>> entier_vers_hexa(675)
'2A3'
```

## Tâche 3 – Programme principal

Le programme demande un entier et affiche son écriture hexadécimale. Vous devez utiliser
`entier_vers_hexa`.

```
Nombre entier ? 31
En hexadécimal : 1F
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Les fonctions `hex`, `bin`, `oct`, `format` et `chr` sont interdites, ainsi que la méthode
  `.format`.
- Chaque fonction est documentée (docstring Sphinx).
