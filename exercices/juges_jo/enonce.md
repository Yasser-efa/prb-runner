# La note des juges aux JO

> Exercice de début de séance du 09/11 : « Aux JO, cinq juges notent un plongeon. On retire la
> meilleure et la moins bonne note, puis on fait la moyenne des autres. Quelle est la note finale
> pour [7.5, 8, 6.5, 9, 8] ? »

## Organisation

Un seul module, à la racine : `plongeon.py`.

## Hypothèses

- Les notes sont des nombres, dans un ordre quelconque.
- En cas d'égalité, on ne retire qu'**une seule** meilleure note et **une seule** moins bonne note.
- Les listes reçues ne doivent pas être modifiées.

## Tâche 1 – `note_finale(notes)`

Cette fonction prend en argument les notes de cinq juges et renvoie la note finale du plongeon.

```
>>> note_finale([7.5, 8, 6.5, 9, 8])
7.833333333333333
>>> note_finale([8, 8, 8, 8, 8])
8.0
```

## Tâche 2 (généralisation) – `note_ajustee(notes, nb_retirees=1)`

Cette fonction prend en argument les notes d'un nombre quelconque de juges. Elle retire les
`nb_retirees` meilleures notes et les `nb_retirees` moins bonnes, puis renvoie la moyenne des
autres. On considère qu'il reste toujours au moins une note. `nb_retirees` peut valoir 0.

```
>>> note_ajustee([5, 9, 7, 6, 8, 1, 10], 2)
7.0
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Le module `statistics` est interdit.
- Chaque fonction est documentée (docstring Sphinx).
