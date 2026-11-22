# Les pages du livre, à l'envers

> Opération inverse de l'exercice n° 13 : il a fallu imprimer 660 chiffres pour numéroter les pages
> d'un livre. Combien de pages compte-t-il ?

## Organisation

- Un module `numerotation.py`, à la racine.
- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.

## Hypothèses

- Les pages sont numérotées à partir de 1, sans zéro devant. Un livre peut être vide (0 page).
- Le nombre de chiffres est un entier entre 0 et 500 000.

## Tâche 1 – `nombre_pages(nb_chiffres)`, dans `numerotation.py`

Cette fonction renvoie le nombre de pages d'un livre dont la numérotation utilise exactement
`nb_chiffres` chiffres. Si aucun livre ne convient, elle renvoie -1.

**Contrainte :** vous devez utiliser une boucle `while`.

```
>>> nombre_pages(660)
256
>>> nombre_pages(10)
-1
```

Avec 9 pages, on imprime 9 chiffres ; avec 10 pages, on en imprime 11.

## Tâche 2 – `page_du_chiffre(rang)`, dans `numerotation.py`

On imprime les chiffres les uns après les autres : `1234567891011…`. Cette fonction renvoie le
numéro de la page sur laquelle se trouve le chiffre imprimé au rang donné (à partir de 1).

```
>>> page_du_chiffre(9)
9
>>> page_du_chiffre(11)
10
```

## Tâche 3 – Programme principal

Le programme demande un nombre de chiffres et affiche le nombre de pages. Vous devez utiliser
`nombre_pages`.

```
Nombre de chiffres ? 660
Nombre de pages : 256
```

```
Nombre de chiffres ? 10
Aucun livre ne convient.
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
