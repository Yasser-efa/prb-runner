# Alice et Bob : temps passé ensemble

> Exercice de début de séance n° 6 : « Alice est disponible de 14 h à 17 h, Bob de 15 h à 19 h.
> Combien de temps peuvent-ils passer ensemble ? »
> Bonus : donnez des valeurs limites aux paramètres.

## Organisation

Un seul module, à la racine : `rencontre.py`.

## Hypothèses

- Une heure est un nombre entre 0 et 24, éventuellement décimal : `14.5` représente 14 h 30.
- Un créneau commence et se termine le même jour. On considère que son début ne dépasse jamais
  sa fin.
- Les durées sont exprimées en heures.

## Tâche 1 – `temps_ensemble(debut_alice, fin_alice, debut_bob, fin_bob)`

Cette fonction prend en argument les heures de début et de fin du créneau d'Alice, puis de
celui de Bob. Elle renvoie le temps qu'ils peuvent passer ensemble. S'ils ne peuvent pas se
voir, elle renvoie 0.

```
>>> temps_ensemble(14, 17, 15, 19)
2
>>> temps_ensemble(9, 12, 14, 18)
0
>>> temps_ensemble(10, 18, 12.5, 13.5)
1.0
```

## Tâche 2 (généralisation) – `temps_groupe(creneaux)`

Cette fonction prend en argument une liste de créneaux, un par personne. Chaque créneau est un
tuple `(debut, fin)`. Elle renvoie le temps que **toutes** les personnes peuvent passer ensemble.
Si la liste est vide, elle renvoie 0. La liste reçue ne doit pas être modifiée.

```
>>> temps_groupe([(14, 17), (15, 19), (13, 16.5)])
1.5
>>> temps_groupe([(14, 17)])
3
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
