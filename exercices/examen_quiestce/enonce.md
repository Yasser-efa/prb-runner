# Examen d'entrainement : Qui est-ce ?

> Partie pratique, 2 h. L'énoncé original, avec ses figures, est dans
> `sources/anciens_examens/AI-PRB-Examen_entrainement.pdf`. La tâche de tests unitaires est retirée. Les
> messages que l'original laissait libres sont fixés ici.

Le joueur doit deviner un personnage mystère en posant des questions sur ses caractéristiques. Après
chaque question, les personnages qui ne correspondent pas sont éliminés.

## Organisation

- Un module `main.py`, à la racine, qui contient la fonction principale `main()`.
- Un package `quiestce` qui contient les modules `personnages.py` et `questions.py`.
- Un dossier `donnees` fourni, qui contient le fichier `prenoms.txt`.

## Tâche 2.1 – `lire_lignes_fichier(chemin_fichier=...)`, dans `personnages.py`

Cette fonction renvoie la liste des lignes d'un fichier, sans les retours à la ligne. Le paramètre est
optionnel : sa valeur par défaut est le fichier `prenoms.txt` du dossier `donnees`. Si une `OSError`
survient, elle renvoie une liste vide.

**Contrainte :** vous devez utiliser un `try` et une expression en compréhension.

```
>>> lire_lignes_fichier('inconnu.txt')
[]
```

## Tâche 2.2 – `creer_personnages(prenoms, attributs)`, dans `personnages.py`

Une phase préparatoire est demandée : dessinez le tableau des combinaisons pour trois attributs, avec
le numéro binaire de chaque ligne, et justifiez vos boucles.

Cette fonction crée autant de personnages qu'il y a de combinaisons de `'oui'` et de `'non'` pour les
attributs. Un personnage est un dictionnaire : `'prenom'`, puis une clé par attribut. Les prénoms sont
choisis **au hasard** dans la liste, sans homonymes. On considère que la liste est assez grande.

Les personnages sont rangés dans l'ordre du tableau : tous les attributs à `'non'` d'abord, et le
dernier attribut change le plus vite.

```
[{'prenom': 'A', 'lunettes': 'non', 'chapeau': 'non'},
 {'prenom': 'B', 'lunettes': 'non', 'chapeau': 'oui'},
 {'prenom': 'D', 'lunettes': 'oui', 'chapeau': 'non'},
 {'prenom': 'C', 'lunettes': 'oui', 'chapeau': 'oui'}]
```

C'est un résultat possible de `creer_personnages(['A', 'B', 'C', 'D'], ('lunettes', 'chapeau'))`. Sans
attribut, la liste est vide.

## Tâche 3.1 – `is_question_valide(question, attributs)`, dans `questions.py`

Cette fonction renvoie une valeur vraie si la question est de la forme `attribut = valeur`, où
l'attribut est dans la collection et la valeur est `oui` ou `non`. Les espaces autour du `=` sont
facultatives ; il peut y en avoir plusieurs. Utilisez une expression régulière.

## Tâche 3.2 – `lire_question_utilisateur(invite, attributs)`, dans `questions.py`

Cette fonction affiche l'invite et lit une question. Si son format est incorrect, elle affiche
`Format invalide. Utilisez 'attribut=valeur'.` et recommence. Elle renvoie le tuple
`(attribut, valeur)`, en minuscules et sans espaces autour. L'utilisateur peut taper des majuscules.

**Contrainte :** vous devez utiliser `is_question_valide`.

## Tâche 4 – `filtrer_personnages(personnages, attribut, valeur, conserver)`, dans `personnages.py`

Cette fonction renvoie une **nouvelle** liste, dans le même ordre. Si `conserver` est vrai, elle garde
les personnages dont l'attribut a cette valeur ; sinon, elle garde les autres. Si les personnages
n'ont pas cet attribut, la liste est simplement copiée. La liste reçue ne doit pas être modifiée.

```
>>> filtrer_personnages([{'prenom': 'A', 'chapeau': 'non'}, {'prenom': 'B', 'chapeau': 'oui'}], 'chapeau', 'oui', True)
[{'prenom': 'B', 'chapeau': 'oui'}]
```

## Tâche 4 bis – `decrire_personnage(personnage)`, dans `personnages.py`

Cette fonction n'est pas dans l'énoncé original : elle permet de tester l'affichage. Elle renvoie le
prénom du personnage, suivi de ses attributs qui valent `oui`, dans l'ordre du dictionnaire, et d'un
point.

```
>>> decrire_personnage({'prenom': 'Sacha', 'lunettes': 'non', 'chapeau': 'oui', 'écharpe': 'oui'})
'Sacha : chapeau, écharpe.'
>>> decrire_personnage({'prenom': 'David', 'lunettes': 'non'})
'David.'
```

## Tâche 5 – Documentation

Les fonctions sont documentées avec des docstrings Sphinx complètes.

## Tâche 7 – Programme principal (version avancée)

Définissez dans `main.py` la constante `ATTRIBUTS`, qui contient `lunettes`, `chapeau`, `yeux clairs`,
`cheveux foncés`, `pilosité faciale` et `écharpe`, dans cet ordre, et la constante `NB_QUESTIONS`, qui
vaut 6.

1. Créez les personnages à partir du fichier et gardez-en 36 au hasard. Choisissez parmi eux, au
   hasard, le personnage mystère.
2. Avant chaque question, affichez le nombre de personnages restants, puis chaque personnage sur une
   ligne, avec `decrire_personnage`.
3. Après chaque question, gardez les personnages qui ont la même valeur que le personnage mystère pour
   l'attribut demandé.
4. S'il ne reste qu'un personnage, le joueur a gagné. S'il a posé `NB_QUESTIONS` questions et qu'il en
   reste plusieurs, il a perdu.

Vous devez utiliser `lire_lignes_fichier`, `creer_personnages`, `filtrer_personnages`,
`decrire_personnage` et `lire_question_utilisateur`. Les lignes vides n'importent pas.

```
Bienvenue dans Qui-est-ce ? Essayez de deviner le personnage que j'ai choisi !
Voici les caractéristiques possibles :
lunettes, chapeau, yeux clairs, cheveux foncés, pilosité faciale, écharpe
Il reste 36 personnage(s) :
Jules : chapeau, yeux clairs, cheveux foncés.
David.
```

Les 34 autres personnages suivent, puis :

```
Posez une question (exemple : lunettes = oui) : lunetes=oui
Format invalide. Utilisez 'attribut=valeur'.
Posez une question (exemple : lunettes = oui) : lunettes = oui
Il reste 20 personnage(s) :
```

La dernière ligne est `Bravo ! Le personnage est Jules.` ou `Perdu ! Le personnage était Jules.`

Les tests jouent de vraies parties et vérifient qu'elles sont cohérentes, quels que soient les choix
aléatoires de votre programme.

## Contraintes de l'outil

`break`, `continue` et `while True` sont interdits.
