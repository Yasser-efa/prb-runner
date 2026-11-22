# Alice et Bob : créneaux de nuit

> Variante de l'exercice n° 6 : Alice travaille de 22 h à 2 h, Bob de 23 h à 6 h. Combien de temps
> travaillent-ils en même temps ?

## Organisation

Un package `horaires` qui contient les modules `decoupage.py` et `rencontre.py`.

## Hypothèses

- Une heure est un nombre entre 0 (compris) et 24 (non compris), éventuellement décimal.
- Alice et Bob ont chacun un créneau, **le même tous les jours**.
- Si l'heure de fin est plus petite que l'heure de début, le créneau passe minuit : il se termine
  le lendemain. Si les deux heures sont égales, le créneau est vide.

## Tâche 1 – `decouper(debut, fin)`, dans `decoupage.py`

Cette fonction découpe un créneau quotidien en morceaux qui ne passent pas minuit. Elle renvoie la
liste des morceaux `(debut, fin)` d'une journée, du plus tôt au plus tard. Minuit se note 0 au début
de la journée et 24 à la fin. Un morceau n'est jamais vide.

```
>>> decouper(14, 17)
[(14, 17)]
>>> decouper(22, 2)
[(0, 2), (22, 24)]
```

## Tâche 2 – `temps_ensemble(debut_alice, fin_alice, debut_bob, fin_bob)`, dans `rencontre.py`

Cette fonction renvoie le nombre d'heures par jour pendant lesquelles les deux créneaux ont lieu en
même temps.

**Contrainte :** vous devez utiliser la fonction `decouper`.

```
>>> temps_ensemble(22, 2, 23, 6)
3
>>> temps_ensemble(20, 8, 6, 22)
4
```

Dans le second exemple, ils se voient de 6 h à 8 h, puis de 20 h à 22 h.

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
