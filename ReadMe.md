# 🎓 Système de Mise en Groupe L2 Bio

## 📋 Description

Système automatisé de répartition des étudiants de L2 Biologie en groupes de travaux pratiques, en tenant compte des équipes pré-constituées et des contraintes d'UEX (Unités d'Enseignement optionnelles).

## 🚀 Installation

### Prérequis
- Python 3.11+
- Environnement virtuel (recommandé)

### Installation des dépendances
```bash
# Activer l'environnement virtuel
source mon_env/bin/activate  # Linux/Mac
# ou
mon_env\Scripts\activate     # Windows

# Les dépendances sont déjà installées dans mon_env :
# - pandas (lecture/écriture Excel)
# - numpy (calculs numériques)
# - openpyxl (manipulation fichiers Excel)
# - ortools (optimisation contraintes)
# - tkinter (interface graphique - inclus avec Python)
```

## 📁 Structure des fichiers d'entrée

### 1. Fichier Liste des Étudiants (`*_trame*.xlsx`)
**Colonnes requises (première ligne) :**
- `N°` : Numéro étudiant (8 chiffres, ex: 12345678)
- `NOM` : Nom de famille
- `PRENOM` : Prénom
- `UEX` : Unité d'enseignement optionnelle

**Valeurs UEX autorisées :**
- `BIO303` ou `BIO303 VALIDÉ`
- `BIO304` ou `BIO304 VALIDÉ` 
- `BIO305` ou `BIO305 VALIDÉ`

### 2. Fichier Liste des Équipes (`*_equipe*.xlsx`)
**Structure :**
- Colonnes pour chaque membre de l'équipe (numéros + noms/prénoms)
- Validation automatique des numéros étudiants (8 chiffres)
- Détection des doublons d'équipes

### 3. Fichier Configuration Mariages (`*mariage*.xlsx`)
**2 feuilles Excel requises :**
- **Feuille 1** : Configuration des mariages entre UEX
- **Feuille 2** : Configuration des groupes et contraintes

## 🎯 Utilisation

### Étape 1 : Lancement
```bash
./mon_env/bin/python3 frontend/Interfaces.py
```

### Étape 2 : Sélection des fichiers
1. **Liste des Étudiants** : Sélectionner le fichier `*_trame*.xlsx`
2. **Liste des Équipes** : Sélectionner le fichier `*_equipe*.xlsx`
3. **Configuration Mariages** : Sélectionner le fichier de configuration

✅ **Validation automatique** à chaque sélection avec messages d'erreur détaillés

### Étape 3 : Génération du fichier de correction
- Clic sur **"🔧 Générer Fichier de Correction"**
- Création automatique de `correction_manuelle_resultat.xlsx`
- Analyse des correspondances étudiants/équipes
- Suggestions pour les noms non concordants

### Étape 4 : Correction manuelle (optionnelle)
- Ouvrir `correction_manuelle_resultat.xlsx` dans Excel
- Corriger les correspondances suggérées si nécessaire
- Sauvegarder le fichier

### Étape 5 : Mise en groupe
- Sélectionner le fichier de correction (auto-détecté)
- Clic sur **"🚀 Lancer Mise en Groupe"**
- Algorithme d'optimisation avec contraintes
- Affichage des résultats (taux de réussite, statistiques)

### Étape 6 : Export des résultats
- Export automatique vers `resultats_mise_en_groupe.xlsx`
- Feuilles séparées : étudiants placés, mariages, groupes

## 📊 Fichiers de sortie

### `correction_manuelle_resultat.xlsx`
- **Étudiants trouvés** : Correspondances exactes
- **Étudiants non trouvés** : Avec suggestions de noms similaires
- **Noms non concordants** : Différences entre fichiers étudiants/équipes

### `resultats_mise_en_groupe.xlsx`
- **Feuille 1** : Liste complète des étudiants avec leurs groupes
- **Feuille 2** : Détail des mariages réalisés
- **Feuille 3** : Composition détaillée des groupes

## ⚙️ Configuration

### `Configuration.txt`
```txt
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