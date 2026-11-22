# La suite de Conway

> Exercice de début de séance du 03/11 : chaque terme de la suite de Conway décrit le précédent.
> Le terme `1211` se lit « un 1, un 2, deux 1 » : le terme suivant est donc `111221`.

## Organisation

- Un module `suite_de_conway.py`, à la racine.
- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.

## Règle

Pour obtenir le terme suivant, on lit le terme de gauche à droite. Chaque série de caractères
identiques qui se touchent est remplacée par sa longueur, suivie du caractère. Le premier terme de
la suite est `1`. Les suivants sont `11`, `21`, `1211`, `111221`…

On considère que les termes donnés ne sont pas vides. Une série ne dépasse jamais 9 caractères.

## Tâche 1 – `conway(terme)`, dans `suite_de_conway.py`

Cette fonction renvoie le terme qui suit celui donné en argument. Le terme donné ne fait pas
forcément partie de la suite qui commence par `1`.

```
>>> conway('1211')
'111221'
>>> conway('333')
'33'
```

## Tâche 2 (généralisation) – `serie(nb_termes)`, dans `suite_de_conway.py`

Cette fonction renvoie la liste des `nb_termes` premiers termes de la suite qui commence par `1`.
Si `nb_termes` est inférieur à 1, elle renvoie une liste vide.

**Contrainte :** vous devez utiliser la fonction `conway`.

```
>>> serie(4)
['1', '11', '21', '1211']
```

## Tâche 3 – Programme principal

Le programme demande un nombre de termes et les affiche, un par ligne. Vous devez utiliser `serie`.
On considère que l'utilisateur tape un entier.

```
Nombre de termes ? 5
1
11
21
1211
111221
```

## Contraintes

- `break`, `continue`, `try` et `while True` sont interdits.
- Les modules `re` et `itertools` sont interdits.
- Chaque fonction est documentée (docstring Sphinx).
