# Vitesse moyenne

> Exercice de début de séance n° 1 : « Je roule pour aller de Ath à Bernissart à 90 km/h. Je roule
> ensuite par la même route de Bernissart à Ath à 60 km/h. Quelle est ma vitesse moyenne ? »
> Bonus : généraliser.

## Organisation

- Un module `trajets.py`, à la racine.
- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.

## Hypothèses

- Une distance est exprimée en kilomètres, une vitesse en kilomètres par heure.
- On considère que les distances et les vitesses sont strictement positives.
- La vitesse moyenne est la distance totale divisée par la durée totale.

## Tâche 1 – `vitesse_aller_retour(vitesse_aller, vitesse_retour)`, dans `trajets.py`

Cette fonction renvoie la vitesse moyenne d'un aller-retour par la même route.

```
>>> vitesse_aller_retour(90, 60)
72.0
```

## Tâche 2 (généralisation) – `vitesse_moyenne(troncons)`, dans `trajets.py`

Cette fonction prend en argument une liste non vide de tronçons. Chaque tronçon est un tuple
`(distance, vitesse)`. Elle renvoie la vitesse moyenne sur tout le trajet. La liste reçue ne doit
pas être modifiée.

**Contrainte :** vous devez utiliser au moins une expression en compréhension.

```
>>> vitesse_moyenne([(30, 90), (30, 60)])
72.0
>>> vitesse_moyenne([(100, 50), (100, 100), (30, 30)])
57.5
```

## Tâche 3 – Programme principal

Le programme demande les deux vitesses d'un aller-retour et affiche la vitesse moyenne avec une
décimale. Vous devez utiliser `vitesse_aller_retour`. Les vitesses tapées peuvent être décimales.

```
Vitesse à l'aller (km/h) ? 90
Vitesse au retour (km/h) ? 60
Vitesse moyenne : 72.0 km/h
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Le module `statistics` est interdit.
- Chaque fonction est documentée (docstring Sphinx).
