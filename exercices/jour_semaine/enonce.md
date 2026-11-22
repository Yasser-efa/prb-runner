# Le jour de la semaine

> Exercice de début de séance n° 5 : « Si nous sommes jeudi, quel jour serons-nous dans 17 jours ? »
> Bonus : donnez des valeurs limites aux paramètres.

## Organisation

- Un module `calendrier.py`, à la racine.
- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.

## Hypothèses

- Les jours sont les chaines `lundi`, `mardi`, `mercredi`, `jeudi`, `vendredi`, `samedi` et
  `dimanche`, en minuscules. On considère que les noms de jours donnés aux fonctions sont corrects.
- Le nombre de jours est un entier quelconque : il peut être nul, négatif (dans le passé) ou
  très grand.

## Tâche 1 – `jour_apres(jour, nb_jours)`, dans `calendrier.py`

Cette fonction renvoie le nom du jour qui vient `nb_jours` jours après `jour`.

```
>>> jour_apres('jeudi', 17)
'dimanche'
>>> jour_apres('lundi', -1)
'dimanche'
```

## Tâche 2 (opération inverse) – `jours_avant(jour, jour_voulu)`, dans `calendrier.py`

Nous sommes `jour`. Cette fonction renvoie le nombre de jours à attendre avant le **prochain**
`jour_voulu`. Il faut toujours attendre au moins un jour : si les deux jours sont identiques, la
fonction renvoie 7.

```
>>> jours_avant('jeudi', 'dimanche')
3
>>> jours_avant('dimanche', 'lundi')
1
>>> jours_avant('mardi', 'mardi')
7
```

## Tâche 3 – Programme principal

Le programme demande un jour et un nombre de jours, puis affiche le résultat. L'utilisateur peut
taper le jour avec des majuscules et des espaces autour. Vous devez utiliser `jour_apres`.

```
Jour de départ ? jeudi
Nombre de jours ? 17
Résultat : dimanche
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Les modules `datetime` et `calendar` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
