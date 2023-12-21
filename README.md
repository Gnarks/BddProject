# Fonctionnement de l'application

## Pré-requis

Afin d'utiliser des bases de données, veuillez les placer dans le dossier DB.

Il est requis d'avoir les dépendances suivantes : sqlite3, os,itertools (normalement installées par défaut)
## Options de l'utilisateur

- Pour faire un choix dans l'invite de commande l'utilisateur doit taper : 
    - soit :
        'y' ou 'n' lorsque "(y/n) :" est demandé
    - soit :
        un des index affichés lorsqu'il est listé un choix du style :
        1) choix1
        2) choix2
        3) choix3

- De plus de manière générale lorsque vous tapez '0', l'utilisateur reviendra vers le menu principal (excepté lorsqu'il est demandé d'entrer le nom d'une DB)

## Fonctionnalités

### Affichage et modifications des DFs de FuncDep
- Lister les dépendances fonctionnelles

- Ajouter une dépendance fonctionnelle

- Supprimer une dépendance fonctionnelle

- Modifier une dépendance fonctionnelle

### Vérifications sur les Dfs de FuncDep

- Vérifier les dépendances fonctionnelles
    - Affiche les dépendances fonctionnelles non-repsectées par table.
    L'utilisateur peut supprimer ces dernière au choix (Voir Options de l'utilisateur)

- Vérifier les conséquences logiques
    -Affiche les conséquences logiques par table    
    L'utilisateur peut supprimer ces dernière au choix (Voir Options de l'utilisateur)


### Affichage des clefs

### Verification sur le type des tables des différentes DB

- Vérifier si chaque table est en BCNF
    - Si non, affiche les dépendances fonctionnelles qui ne respecte pas BCNF

- Vérifier si chaque table est en 3NF
    - Si non, affiche les dépendances fonctionnelles qui ne respecte pas 3NF
    et les éléments du right-hand size n'appartenant pas aux clefs 
