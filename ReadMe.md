# 🎓 Système de Mise en Groupe L2 Bio

## 📋 Description

Système automatisé de répartition des étudiants de L2 Biologie en groupes, en tenant compte des dmandes d'équipes effectuées par les étudiants et des contraintes d'UEX (Unités d'Enseignement optionnelles).

## 🚀 Installation
A faire

## 📁 Structure des fichiers d'entrée

Trois fichier excels (.xlsx) sont requis. Il faut que sur la première ligne, les entêtes des colonnes correspondent à celles demandées. Si rien est précisé les données doivent être dans la première feuille.

### 1. Fichier Liste des Étudiants

**Colonnes requises :**
- `N°` : Numéro étudiant (8 chiffres)
- `NOM` : Nom de famille
- `PRENOM` : Prénom
- `REDOUBLANT` : Redoublant (`x` si oui, rien sinon)
- `UEX` : Unité d'enseignement optionnelle (valeurs possibles : `BIO303`, `BIO304`, `BIO305`, `BIO303 VALIDÉ`, `BIO304 VALIDÉ`, `BIO305 VALIDÉ`)


### 2. Fichier Liste des Équipes

**Colonnes requises :**

["N°Obs","1. UE optionnelle du S3 commune",
            	"3. Numéro d'étudiant (1)",	"4. _Nom et prénom (1)",
                "5. Numéro d'étudiant (2)",	"6. _Nom et prénom (2)",	
                "7. Numéro d'étudiant (3)",	"8. _Nom et prénom (3)",
                "9. Numéro d'étudiant (4)",	"10. _Nom et prénom (4)"


- `N°Obs` : Numéro d'observation ou identifiant d'équipe
- `UE optionnelle du S3 commune` : UE optionnelle commune à l'équipe (S3)
- `Numéro d'étudiant (1)` : Numéro étudiant du membre 1
- `Nom et prénom (1)` : Nom et prénom du membre 1
- `Numéro d'étudiant (2)` : Numéro étudiant du membre 2
- `Nom et prénom (2)` : Nom et prénom du membre 2
- `Numéro d'étudiant (3)` : Numéro étudiant du membre 3
- `Nom et prénom (3)` : Nom et prénom du membre 3
- `Numéro d'étudiant (4)` : Numéro étudiant du membre 4
- `Nom et prénom (4)` : Nom et prénom du membre 4

### 3. Fichier configuration (`*mariage*.xlsx`)
Ici, trois feuilles sont requises

**Colonnes requises (feuille 1)** :
- `Groupes` : Numéro du groupe
- `BIO303` : Indique si le groupe i accepte des étudiants qui ont BIO303 (`x` si oui, laisser vide sinon)
- `BIO304` : Indique si le groupe i accepte des étudiants qui ont cette BIO304 (`x` si oui, laisser vide sinon)
- `BIO305` : Indique si le groupe i accepte des étudiants qui ont cette BIO305 (`x` si oui, laisser vide sinon)

**Colonnes requises (feuille 2)** :
- `PREMIER` : Numéro du premier groupe concerné par le mariage
- `DEUXIEME` : Numéro du deuxième groupe concerné par le mariage
- `TROISIEME` : Numéro du troisième groupe concerné par le mariage (laisser vide si mariage à deux)
- `BIO303` : Indique si ce mariage concerne l'UEX BIO303 (`x` si oui, laisser vide sinon)
- `BIO304` : Indique si ce mariage concerne l'UEX BIO304 (`x` si oui, laisser vide sinon)
- `BIO305` : Indique si ce mariage concerne l'UEX BIO305 (`x` si oui, laisser vide sinon)

### 3. Feuille Configuration Générale

Cette feuille doit contenir les informations suivantes (une valeur par cellule, sur la même ligne ou colonne) :

- **Nombre de groupes** : Nombre total de groupes à créer
- **Taille des groupes** : Taille cible de chaque groupe
- **Taille maximale des groupes** : Taille maximale autorisée pour un groupe
- **Nombre d'UEX** : Nombre d'Unités d'Enseignement optionnelles
- **Liste des UEX** : Liste des UEX concernées (ex : `BIO303, BIO304, BIO305`)

> Exemple de structure pour le S3:

| Nombre de groupes | Taille des groupes | Taille maximale des groupes | Nombre d'UEX | Liste des UEX           |
|-------------------|-------------------|----------------------------|--------------|-------------------------|
| 8                 | 32                | 34                         | 3            | BIO303, BIO304, BIO305  |




## 🎯 Utilisation

### Étape 1 : Lancement


### Étape 2 : Sélection des fichiers
1. **Liste des Étudiants** : Sélectionner le fichier *liste des étudiant*
2. **Liste des Équipes** : Sélectionner le fichier *liste des équipes*
3. **Configuration Mariages** : Sélectionner le fichier *Configuration mariage

✅ **Validation automatique** à chaque sélection avec messages d'erreur détaillés

### Étape 4 : Génération du fichier de `correction_manuelle_resultat.xlsx`:
 - Cliquer sur "🔧 Générer Fichier de Correction"

### Étape 3 : Correction manuelle :
 Le fichier `correction_manuelle_resultat.xlsx` contient 4 feuilles:
- **Première feuille** : Liste tous les étudiants du fichier *liste étudiant*, avec un index ajouté pour chaque étudiant.
- **Deuxième feuille** : Liste les étudiants du fichier *liste équipe* qui ont été retrouvés dans la *liste étudiant*.
- **Troisième feuille** : Liste les étudiants du fichier *liste équipe* qui n'ont pas été retrouvés dans la *liste étudiant*.  
    👉 **Action requise** : Pour chaque étudiant non trouvé, renseigner l’index correspondant de la *liste étudiant* s'il n'existe pas, il faut soit supprimer l'étudiatn soit le rajouter au fichier *liste étudiant*.  
    À noter : Certains étudiants ont déjà un index renseigné. Cela signifie que leur numéro d’étudiant ne correspond à aucun de la *liste étudiant*, mais que leur nom et prénom ont été retrouvés.
- **Quatrième feuille** : Liste les étudiants dont le numéro d’étudiant a été trouvé, mais dont le nom et le prénom ne correspondent pas exactement. (Cette feuille sert de contrôle.)


### Étape 5 : Mise en groupe
- Sélectionner le fichier de correction (auto-détecté)
- Cliquer sur **"🚀 Lancer Mise en Groupe"**
- Algorithme d'optimisation avec contraintes
- Affichage des résultats (taux de réussite, statistiques)

### Étape 6 : Export des résultats
- Export automatique vers `resultats_mise_en_groupe.xlsx`
- Feuilles séparées : étudiants placés, mariages, groupes

## 📊 Fichiers de sortie

### `resultats_mise_en_groupe.xlsx`
- **Feuille 1** : Liste complète des étudiants avec leurs groupes
- **Feuille 2** : Détail des mariages réalisés
- **Feuille 3** : Composition détaillée des groupes

## ⚙️ Configuration

### `Configuration.txt`
```
Nom du fichier liste étudiant : BIOS32024_trame_modif.xlsx
Nom du fichier équipe : BIOS32024_equipe_modif.xlsx
Nombre de groupe : 8
Taille des groupe : 32
Nombre d'UEX : 3
Nom du fichier après validation : correction_manuelle_resultat.xlsx
Liste UEX : BIO303, BIO304, BIO305
Mariage : MariageMiseEnGroupe.xlsx
```
