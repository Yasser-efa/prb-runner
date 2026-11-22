# La guirlande qui bascule

> Autre lecture de l'exercice n° 9 : chaque lampe **change d'état** à intervalles réguliers. Elle
> reste allumée pendant toute une période, puis éteinte pendant toute la suivante, etc.

## Organisation

Un seul module, à la racine : `bascule.py`.

## Interprétation

- On allume la guirlande à la minute 0 : toutes les lampes sont allumées.
- Une lampe de période 3 est allumée aux minutes 0, 1 et 2, éteinte aux minutes 3, 4 et 5, allumée
  aux minutes 6, 7 et 8, etc.
- On n'observe la guirlande qu'aux minutes entières.
- Une période est un entier strictement positif. On considère que la liste des périodes n'est pas
  vide.

## Tâche 1 – `lampe_allumee(periode, minute)`

Cette fonction renvoie vrai si une lampe de cette période est allumée à cette minute.

**Contrainte :** les boucles `for` et `while` sont interdites.

```
>>> lampe_allumee(3, 2)
True
>>> lampe_allumee(3, 5)
False
```

## Tâche 2 – `duree_rallumage(periodes)`

Cette fonction renvoie la première minute à laquelle toutes les lampes sont **à nouveau** allumées,
c'est-à-dire après qu'au moins une lampe s'est éteinte. La liste reçue ne doit pas être modifiée.

**Contrainte :** vous devez utiliser une boucle `while`.

```
>>> duree_rallumage([2])
4
>>> duree_rallumage([2, 3])
8
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Le module `math` est interdit.
- Chaque fonction est documentée (docstring Sphinx).
