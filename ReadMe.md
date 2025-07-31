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

## 🔧 Architecture technique

### Frontend (`frontend/`)
- `Interfaces.py` : Interface graphique Tkinter avec processus guidé

### Backend (`backend/`)
- `LectureFichierEtudiants.py` : Validation et nettoyage fichier étudiants
- `LectureFichierEquipes.py` : Validation et nettoyage fichier équipes  
- `LectureFichierMariages.py` : Lecture configuration mariages
- `AnalyseDesFichiers.py` : Analyse croisée et génération corrections
- `MiseEnGroupe.py` : Algorithme d'optimisation principal
- `TraitementDesResultats.py` : Export et formatage des résultats
- `Classes.py` : Modèles de données (Étudiant, Équipe, Groupe)

### Données (`data/`)
- Fichiers Excel d'entrée et de sortie
- Fichiers de configuration

## 🐛 Résolution des problèmes

### Erreurs courantes

**"Fichier non valide"**
- Vérifier les noms des colonnes (première ligne)
- Contrôler le format des numéros étudiants (8 chiffres)
- Valider les valeurs UEX autorisées

**"[Errno 2] No such file or directory"**
- Fermer les fichiers Excel ouverts
- Vérifier les chemins de fichiers
- Relancer l'interface si nécessaire

**"Colonnes manquantes"**
- Format de fichier incorrect
- Vérifier la structure attendue selon le type de fichier

### Debug
```bash
# Test des modules backend
./mon_env/bin/python3 -c "
import sys; sys.path.insert(0, 'backend')
import LectureFichierEtudiants as lfe
print('✅ Modules OK')
"

# Vérification des fichiers
./mon_env/bin/python3 debug_chemins.py  # (si créé)
```

## 📈 Performances

- **Étudiants supportés** : 500+ étudiants
- **Équipes** : 100+ équipes pré-constituées
- **Temps de traitement** : < 30 secondes pour 300 étudiants
- **Taux de placement** : Généralement > 95%


### Structure de développement
```
MiseEnGroupeL2Bio/
├── frontend/          # Interface utilisateur
├── backend/           # Logique métier
├── data/             # Fichiers de données
├── mon_env/          # Environnement Python
├── Configuration.txt # Configuration système
└── ReadMe.md        # Documentation
```


---
*Système développé pour la gestion automatisée des groupes de TP en L2 Biologie* 