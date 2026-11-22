# Alice et Bob : plusieurs créneaux

> Version plus dure de l'exercice de début de séance n° 6 : Alice et Bob ont chacun plusieurs
> créneaux libres dans la journée. Quand peuvent-ils se voir, et pendant combien de temps ?

## Organisation

- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.
- Un package `agenda` qui contient les modules `saisie.py` et `creneaux.py`.

## Hypothèses

- Une heure est un nombre entier entre 0 et 24.
- Un créneau est un tuple `(debut, fin)` avec `debut < fin`.
- Les disponibilités d'une personne sont une liste de créneaux. On considère que les créneaux
  d'une même personne ne se chevauchent pas et ne se touchent pas. En revanche, ils peuvent
  être donnés dans **n'importe quel ordre**.

## Tâche 1 – `lire_creneaux(texte)`, dans `saisie.py`

Cette fonction prend en argument une chaine qui contient des créneaux de la forme `debut-fin`,
séparés par une ou plusieurs espaces. Elle renvoie la liste des créneaux, dans le même ordre.
On considère que la chaine est correctement formatée. Elle peut être vide.

```
>>> lire_creneaux('9-12 14-17')
[(9, 12), (14, 17)]
>>> lire_creneaux('')
[]
```

## Tâche 2 – `creneaux_communs(dispos_alice, dispos_bob)`, dans `creneaux.py`

Cette fonction renvoie la liste des créneaux pendant lesquels Alice **et** Bob sont disponibles,
du plus tôt au plus tard. Un créneau commun a une durée d'au moins une heure. Les listes reçues
ne doivent pas être modifiées.

```
>>> creneaux_communs([(9, 12), (14, 17)], [(11, 15)])
[(11, 12), (14, 15)]
>>> creneaux_communs([(9, 12)], [(12, 14)])
[]
```

## Tâche 3 – `temps_ensemble(dispos_alice, dispos_bob)`, dans `creneaux.py`

Cette fonction renvoie le temps total qu'Alice et Bob peuvent passer ensemble, en heures.

**Contrainte :** vous devez utiliser la fonction `creneaux_communs`.

```
>>> temps_ensemble([(9, 12), (14, 17)], [(11, 15)])
2
```

## Tâche 4 – Programme principal

Le programme demande les créneaux d'Alice puis ceux de Bob. Il affiche leurs créneaux communs,
puis leur temps total. Vous devez utiliser les fonctions définies précédemment.

```
Créneaux d'Alice ? 9-12 14-17
Créneaux de Bob ? 11-15
Créneaux communs : 11-12 14-15
Temps ensemble : 2 h
```

S'il n'y a aucun créneau commun :

```
Créneaux d'Alice ? 9-12
Créneaux de Bob ? 14-18
Créneaux communs : aucun
Temps ensemble : 0 h
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
