# Les pages du livre

> Exercice de début de séance n° 13 : « Combien de chiffres faut-il imprimer pour numéroter les
> pages d'un livre de 256 pages ? »

## Organisation

Un seul module, à la racine : `numerotation.py`.

## Hypothèses

- Les pages sont numérotées à partir de 1, sans zéro devant. Le numéro 12 demande deux chiffres.
- Un livre compte au plus 100 000 pages. Il peut être vide (0 page).

## Tâche 1 – `nombre_chiffres(nb_pages)`

Cette fonction renvoie le nombre de chiffres à imprimer pour numéroter toutes les pages.

```
>>> nombre_chiffres(256)
660
>>> nombre_chiffres(10)
11
```

## Tâche 2 (généralisation) – `chiffres_entre(premiere, derniere)`

Cette fonction renvoie le nombre de chiffres à imprimer pour numéroter les pages de `premiere` à
`derniere`, bornes comprises. On considère que `1 <= premiere <= derniere`.

```
>>> chiffres_entre(8, 11)
6
```

## Tâche 3 (généralisation) – `occurrences(chiffre, nb_pages)`

Cette fonction renvoie le nombre de fois que le chiffre donné (entre 0 et 9) est imprimé pour
numéroter les pages d'un livre de `nb_pages` pages.

```
>>> occurrences(1, 12)
5
```

Pour les pages 1 à 12, le chiffre 1 est imprimé sur les pages 1, 10, 11 (deux fois) et 12.

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
