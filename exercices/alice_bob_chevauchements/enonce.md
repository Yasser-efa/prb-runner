# Alice et Bob : créneaux qui se chevauchent

> Variante de `alice_bob_listes` : les créneaux d'une même personne peuvent se chevaucher, se toucher
> ou être répétés. Il ne faut pas compter deux fois le même moment.

## Organisation

Deux modules, à la racine : `fusion.py` et `rencontre.py`.

## Hypothèses

- Une heure est un entier entre 0 et 24.
- Un créneau est un tuple `(debut, fin)` avec `debut < fin`.
- Les créneaux d'une même personne sont donnés dans un ordre quelconque.

## Tâche 1 – `fusionner(creneaux)`, dans `fusion.py`

Cette fonction renvoie les mêmes disponibilités sous la forme de créneaux qui ne se chevauchent pas
et ne se touchent pas, du plus tôt au plus tard. La liste reçue ne doit pas être modifiée.

```
>>> fusionner([(9, 12), (11, 14), (16, 18)])
[(9, 14), (16, 18)]
>>> fusionner([(14, 17), (9, 14)])
[(9, 17)]
```

## Tâche 2 – `temps_ensemble(dispos_alice, dispos_bob)`, dans `rencontre.py`

Cette fonction renvoie le temps total pendant lequel Alice et Bob sont disponibles tous les deux, en
heures. Les listes reçues ne doivent pas être modifiées.

**Contrainte :** vous devez utiliser la fonction `fusionner`.

```
>>> temps_ensemble([(9, 12), (11, 14)], [(10, 13), (10, 13)])
3
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
