# La guirlande lumineuse

> Exercice de début de séance n° 9 : « Une guirlande lumineuse est composée de 5 lampes qui
> s'allument ou s'éteignent chacune à des fréquences différentes : toutes les 2, 3, 5, 7, 11
> minutes. Quand on allume la guirlande, au bout de combien de temps les 5 lampes sont à nouveau
> toutes allumées ? »

## Organisation

Un package `lumieres` qui contient le module `guirlande.py`.

## Interprétation

- On allume la guirlande à la minute 0 : toutes les lampes s'allument un bref instant.
- Ensuite, chaque lampe s'allume un bref instant, à intervalles réguliers. Une lampe de période 3
  s'allume donc aux minutes 0, 3, 6, 9…
- Une période est un entier strictement positif. On considère que la liste des périodes n'est pas
  vide. Plusieurs lampes peuvent avoir la même période.

(La variante `guirlande_bascule` propose l'autre lecture de l'énoncé.)

## Tâche 1 – `duree_rallumage(periodes)`

Cette fonction renvoie la première minute, après la minute 0, à laquelle toutes les lampes
s'allument en même temps. La liste reçue ne doit pas être modifiée.

**Contrainte :** vous devez utiliser une boucle `while`.

```
>>> duree_rallumage([2, 3, 5, 7, 11])
2310
>>> duree_rallumage([2, 4])
4
```

## Tâche 2 (généralisation) – `instants_communs(periodes, limite)`

Cette fonction renvoie la liste de toutes les minutes, de 1 à `limite` comprise, auxquelles toutes
les lampes s'allument en même temps. La liste reçue ne doit pas être modifiée.

```
>>> instants_communs([2, 3], 20)
[6, 12, 18]
>>> instants_communs([2, 3], 5)
[]
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Le module `math` est interdit.
- Chaque fonction est documentée (docstring Sphinx).
