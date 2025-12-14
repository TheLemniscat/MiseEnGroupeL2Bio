import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import configparser
import os 
import backend.LectureFichierEtudiants as lfe
import backend.LectureFichierEquipes as lft  
import backend.LectureFichierMariages as lfm
import backend.AnalyseDesFichiers as adf
import backend.MiseEnGroupe as meg
import backend.TraitementDesResultats as tdr



class InterfaceSelectionFichiers:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Système de Mise en Groupe - Sélection des Fichiers")
        # Afficher la fenêtre en plein écran par défaut
        self.root.attributes('-zoomed', True)
        
        # Variables pour stocker les chemins des fichiers
        self.fichier_etudiants = tk.StringVar()
        self.fichier_equipes = tk.StringVar()
        self.fichier_mariages = tk.StringVar()
        self.fichier_correction = tk.StringVar()
        
        # Variables pour stocker l'état de validation
        self.valid_etudiants = tk.BooleanVar(value=False)
        self.valid_equipes = tk.BooleanVar(value=False)
        self.valid_mariages = tk.BooleanVar(value=False)
        self.valid_correction = tk.BooleanVar(value=False)
        self.correction_generee = tk.BooleanVar(value=False)
        
        # Variables pour les paramètres de configuration
        self.nombre_groupes = tk.StringVar()
        self.taille_groupes = tk.StringVar()
        self.taille_max_groupes = tk.StringVar()
        self.liste_uex = tk.StringVar()
        
        # Variable pour mémoriser les messages d'erreur persistants
        self.message_erreur_persistant = None
        
        self.creer_interface()

    
    def creer_interface(self):
        """Crée l'interface utilisateur."""
        # Titre principal
        titre = tk.Label(
            self.root, 
            text="🎓 Système de Mise en Groupe L2 Bio", 
            font=("Arial", 16, "bold"),
            fg="#2E7D32"
        )
        titre.grid(row=0, column=0, columnspan=4, pady=20)
        
        # Section paramètres de configuration
        frame_config = tk.LabelFrame(
            self.root, 
            text="⚙️ Paramètres de Configuration", 
            font=("Arial", 12, "bold"),
            padx=10, pady=10
        )
        frame_config.grid(row=1, column=0, columnspan=4, padx=20, pady=10, sticky="ew")
        
        # Première ligne : Bouton pour charger un fichier INI (centré)
        btn_charger_ini = tk.Button(
            frame_config,
            text="📁 Charger fichier de configuration",
            command=self.charger_fichier_ini,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            padx=10, pady=5
        )
        btn_charger_ini.grid(row=0, column=0, columnspan=6, padx=5, pady=5)
        
        # Deuxième ligne : Tous les champs numériques sur la même ligne
        tk.Label(frame_config, text="Nombre de groupes:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_nb_groupes = tk.Entry(frame_config, textvariable=self.nombre_groupes, width=10, justify="center")
        self.entry_nb_groupes.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_config, text="Taille des groupes:", font=("Arial", 10, "bold")).grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.entry_taille_groupes = tk.Entry(frame_config, textvariable=self.taille_groupes, width=10, justify="center")
        self.entry_taille_groupes.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Label(frame_config, text="Taille max des groupes:", font=("Arial", 10, "bold")).grid(row=1, column=4, padx=5, pady=5, sticky="w")
        self.entry_taille_max = tk.Entry(frame_config, textvariable=self.taille_max_groupes, width=10, justify="center")
        self.entry_taille_max.grid(row=1, column=5, padx=5, pady=5)
        
        # Troisième ligne : Liste des UEX (sur toute la largeur)
        tk.Label(frame_config, text="Liste des UEX (séparées par des virgules):", font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.entry_liste_uex = tk.Entry(frame_config, textvariable=self.liste_uex, width=50)
        self.entry_liste_uex.grid(row=2, column=2, columnspan=4, padx=5, pady=5, sticky="ew")
        
        # Lier l'événement de modification pour convertir en majuscules
        self.entry_liste_uex.bind('<KeyRelease>', self.convertir_uex_majuscules)
        
        # Configuration de la grille pour redimensionnement
        frame_config.columnconfigure(2, weight=1)
        frame_config.columnconfigure(3, weight=1)
        frame_config.columnconfigure(4, weight=1)
        frame_config.columnconfigure(5, weight=1)
        
        # Section sélection de fichiers
        frame_fichiers = tk.LabelFrame(
            self.root, 
            text="📁 Sélection des Fichiers", 
            font=("Arial", 12, "bold"),
            padx=10, pady=10
        )
        frame_fichiers.grid(row=2, column=0, columnspan=4, padx=20, pady=10, sticky="ew")
        
        # Configuration des fichiers
        fichiers_config = [
            ("Liste des Étudiants", self.fichier_etudiants, self.valid_etudiants, self.valider_fichier_etudiants),
            ("Demandes pour les Équipes", self.fichier_equipes, self.valid_equipes, self.valider_fichier_equipes),
            ("Configuration Mariages", self.fichier_mariages, self.valid_mariages, self.valider_fichier_mariages)
        ]
        
        self.labels_status = []
        
        for i, (label_text, var_fichier, var_valid, fonction_validation) in enumerate(fichiers_config):
            # Label du fichier
            label = tk.Label(frame_fichiers, text=f"{label_text}:", font=("Arial", 10, "bold"))
            label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
            
            # Entry pour le chemin du fichier
            entry = tk.Entry(frame_fichiers, textvariable=var_fichier, width=50, state="readonly")
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            
            # Bouton parcourir
            btn_parcourir = tk.Button(
                frame_fichiers, 
                text="Parcourir...", 
                command=lambda var=var_fichier, valid=var_valid, func=fonction_validation: 
                    self.choisir_fichier(var, valid, func)
            )
            btn_parcourir.grid(row=i, column=2, padx=5, pady=5)
            
            # Indicateur de validation
            label_status = tk.Label(frame_fichiers, text="❌", font=("Arial", 12), fg="red")
            label_status.grid(row=i, column=3, padx=5, pady=5)
            self.labels_status.append((label_status, var_valid))
        
        # Configuration de la grille pour redimensionnement
        frame_fichiers.columnconfigure(1, weight=1)
        
        # Section informations
        frame_info = tk.LabelFrame(
            self.root, 
            text="ℹ️ Informations", 
            font=("Arial", 12, "bold"),
            padx=10, pady=10
        )
        frame_info.grid(row=5, column=0, columnspan=4, padx=20, pady=10, sticky="ew")
        
        self.label_info = tk.Label(
            frame_info, 
            text="Sélectionnez les trois fichiers requis pour continuer.",
            font=("Arial", 10),
            wraplength=1000,
            justify="left",
            anchor="nw"
        )
        self.label_info.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Section boutons d'action - Étape 1 : Génération du fichier de correction
        frame_actions1 = tk.Frame(self.root)
        frame_actions1.grid(row=4, column=0, columnspan=4, pady=10)
        
        # Bouton pour générer le fichier de correction
        self.btn_generer = tk.Button(
            frame_actions1,
            text="🔧 Générer Fichier de Correction",
            command=self.generer_fichier_correction,
            font=("Arial", 12, "bold"),
            bg="#FF9800",
            fg="white",
            padx=20, pady=10,
            state="disabled"
        )
        self.btn_generer.grid(row=0, column=0, padx=10)
        
        # Section sélection du fichier de correction (initialement cachée)
        self.frame_correction = tk.LabelFrame(
            self.root, 
            text="📝 Fichier de Correction Manuelle", 
            font=("Arial", 12, "bold"),
            padx=10, pady=10
        )
        # Ne pas afficher le frame initialement
        
        # Contenu du frame de correction
        correction_label = tk.Label(
            self.frame_correction, 
            text="Fichier de Correction :", 
            font=("Arial", 10, "bold")
        )
        correction_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.entry_correction = tk.Entry(
            self.frame_correction, 
            textvariable=self.fichier_correction, 
            width=50, 
            state="readonly"
        )
        self.entry_correction.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.btn_parcourir_correction = tk.Button(
            self.frame_correction, 
            text="Parcourir...", 
            command=self.choisir_fichier_correction
        )
        self.btn_parcourir_correction.grid(row=0, column=2, padx=5, pady=5)
        
        self.label_status_correction = tk.Label(
            self.frame_correction, 
            text="❌", 
            font=("Arial", 12), 
            fg="red"
        )
        self.label_status_correction.grid(row=0, column=3, padx=5, pady=5)
        
        # Configuration de la grille pour redimensionnement
        self.frame_correction.columnconfigure(1, weight=1)
        
        # Section boutons d'action - Étape 2 : Mise en groupe (initialement cachée)
        self.frame_actions2 = tk.Frame(self.root)
        # Ne pas afficher le frame initialement
        
        # Bouton pour lancer la mise en groupe
        self.btn_mise_en_groupe = tk.Button(
            self.frame_actions2,
            text="🚀 Lancer Mise en Groupe",
            command=self.on_mise_en_groupe_click,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            padx=20, pady=10,
            state="disabled"
        )
        self.btn_mise_en_groupe.grid(row=0, column=0, padx=10)
        
        # Vérifier périodiquement l'état des validations
        self.verifier_etat_boutons()
    
    def choisir_fichier(self, var_fichier, var_valid, fonction_validation):
        """Ouvre une boîte de dialogue pour choisir un fichier."""
        fichier = filedialog.askopenfilename(
            title="Sélectionner un fichier Excel",
            filetypes=[("Fichiers Excel", "*.xlsx *.xls"), ("Tous les fichiers", "*.*")]
        )
        
        if fichier:
            var_fichier.set(fichier)
            self.valider_fichier(fichier, var_valid, fonction_validation)
    
    def choisir_fichier_correction(self):
        """Ouvre une boîte de dialogue pour choisir le fichier de correction."""
        fichier = filedialog.askopenfilename(
            title="Sélectionner le fichier de correction manuelle",
            filetypes=[("Fichiers Excel", "*.xlsx *.xls"), ("Tous les fichiers", "*.*")],
            initialdir=os.getcwd(),
            initialfile="correction_manuelle_resultat.xlsx"
        )
        
        if fichier:
            self.fichier_correction.set(fichier)
            self.valider_fichier_correction(fichier)
    
    def charger_fichier_ini(self):
        """Charge un fichier INI et remplit les champs de configuration."""
        fichier = filedialog.askopenfilename(
            title="Sélectionner un fichier de configuration INI",
            filetypes=[("Fichiers INI", "*.ini"), ("Tous les fichiers", "*.*")]
        )
        
        if fichier:
            try:
                config = configparser.ConfigParser()
                config.read(fichier)
                
                # Vérifier que la section Configuration existe
                if 'Configuration' in config:
                    section = config['Configuration']
                    
                    # Charger les valeurs si elles existent
                    if 'nombre_groupes' in section:
                        self.nombre_groupes.set(section['nombre_groupes'])
                    
                    if 'taille_groupes' in section:
                        self.taille_groupes.set(section['taille_groupes'])
                    
                    if 'taille_max_groupes' in section:
                        self.taille_max_groupes.set(section['taille_max_groupes'])
                    
                    if 'liste_uex' in section:
                        # Convertir en majuscules et nettoyer les espaces
                        uex_list = section['liste_uex'].upper().replace(' ', '')
                        self.liste_uex.set(uex_list)
                    
                    messagebox.showinfo(
                        "Succès", 
                        f"✅ Configuration chargée depuis {os.path.basename(fichier)}"
                    )
                else:
                    messagebox.showerror(
                        "Erreur", 
                        "Le fichier INI ne contient pas de section [Configuration]"
                    )
                    
            except Exception as e:
                messagebox.showerror(
                    "Erreur", 
                    f"Erreur lors du chargement du fichier INI:\n{str(e)}"
                )
    
    def convertir_uex_majuscules(self, event):
        """Convertit automatiquement la saisie des UEX en majuscules."""
        current_value = self.liste_uex.get()
        cursor_position = self.entry_liste_uex.index(tk.INSERT)
        
        # Convertir en majuscules
        new_value = current_value.upper()
        
        # Mettre à jour la valeur si elle a changé
        if new_value != current_value:
            self.liste_uex.set(new_value)
            # Restaurer la position du curseur
            self.entry_liste_uex.icursor(cursor_position)
    
    def valider_fichier_correction(self, chemin_fichier):
        """Valide le fichier de correction."""
        try:
            if os.path.exists(chemin_fichier):
                self.valid_correction.set(True)
                self.label_status_correction.config(text="✅", fg="green")
                # Effacer le message d'erreur persistant si validation réussie
                self.message_erreur_persistant = None
                self.label_info.config(
                    text=f"✅ Fichier de correction sélectionné: {os.path.basename(chemin_fichier)}",
                    fg="green"
                )
                # Activer le bouton de mise en groupe
                self.btn_mise_en_groupe.config(state="normal")
            else:
                self.valid_correction.set(False)
                self.label_status_correction.config(text="❌", fg="red")
                # Sauvegarder le message d'erreur pour qu'il persiste
                error_msg = f"❌ Fichier de correction non trouvé: {os.path.basename(chemin_fichier)}"
                self.message_erreur_persistant = error_msg
                self.label_info.config(
                    text=error_msg,
                    fg="red"
                )
                self.btn_mise_en_groupe.config(state="disabled")
        except Exception as e:
            self.valid_correction.set(False)
            self.label_status_correction.config(text="❌", fg="red")
            # Sauvegarder le message d'erreur pour qu'il persiste
            error_msg = f"❌ Erreur lors de la validation du fichier de correction: {str(e)}"
            self.message_erreur_persistant = error_msg
            self.label_info.config(
                text=error_msg,
                fg="red"
            )
            self.btn_mise_en_groupe.config(state="disabled")
    
    def valider_fichier(self, chemin_fichier, var_valid, fonction_validation):
        """Valide un fichier avec la fonction appropriée."""
        try:
            if fonction_validation and chemin_fichier:
                resultat, message_erreur = fonction_validation(chemin_fichier)
                var_valid.set(resultat)
                
                if resultat:
                    # Effacer le message d'erreur persistant si validation réussie
                    self.message_erreur_persistant = None
                    self.label_info.config(
                        text=f"✅ Fichier validé: {os.path.basename(chemin_fichier)}",
                        fg="green"
                    )
                else:
                    # Sauvegarder le message d'erreur pour qu'il persiste
                    error_msg = f"❌ Erreur dans {os.path.basename(chemin_fichier)}: {message_erreur}"
                    self.message_erreur_persistant = error_msg
                    self.label_info.config(
                        text=error_msg,
                        fg="red"
                    )
            else:
                var_valid.set(False)
                
        except Exception as e:
            var_valid.set(False)
            # Sauvegarder le message d'erreur pour qu'il persiste
            error_msg = f"❌ Erreur lors de la validation: {str(e)}"
            self.message_erreur_persistant = error_msg
            self.label_info.config(
                text=error_msg,
                fg="red"
            )
            messagebox.showerror("Erreur de validation", f"Erreur lors de la validation du fichier: {str(e)}")
    
    def valider_parametres_configuration(self):
        """Valide les paramètres de configuration saisis."""
        try:
            # Vérifier que tous les champs sont remplis
            if not all([
                self.nombre_groupes.get().strip(),
                self.taille_groupes.get().strip(), 
                self.taille_max_groupes.get().strip(),
                self.liste_uex.get().strip()
            ]):
                return False, "Tous les champs de configuration doivent être remplis"
            
            # Vérifier que les nombres sont des entiers positifs
            try:
                nb_groupes = int(self.nombre_groupes.get())
                taille_groupes = int(self.taille_groupes.get())
                taille_max = int(self.taille_max_groupes.get())
                
                if nb_groupes <= 0 or taille_groupes <= 0 or taille_max <= 0:
                    return False, "Les nombres doivent être des entiers positifs"
                
                if taille_max < taille_groupes:
                    return False, "La taille maximale doit être supérieure ou égale à la taille des groupes"
                    
            except ValueError:
                return False, "Les valeurs numériques doivent être des entiers valides"
            
            # Vérifier la liste des UEX
            uex_list = [uex.strip() for uex in self.liste_uex.get().split(',') if uex.strip()]
            if len(uex_list) == 0:
                return False, "Au moins une UEX doit être spécifiée"
            
            # Vérifier le format des UEX (optionnel - on peut être plus flexible)
            for uex in uex_list:
                if not uex or len(uex) < 3:
                    return False, f"UEX invalide: '{uex}'. Les UEX doivent avoir au moins 3 caractères"
            
            return True, "Configuration valide"
            
        except Exception as e:
            return False, f"Erreur lors de la validation: {str(e)}"
    
    def get_parametres_configuration(self):
        """Récupère les paramètres de configuration depuis l'interface."""
        try:
            # Convertir les valeurs numériques
            nb_groupes = int(self.nombre_groupes.get())
            taille_groupes = int(self.taille_groupes.get())
            taille_max = int(self.taille_max_groupes.get())
            
            # Traiter la liste des UEX
            uex_list = [uex.strip() for uex in self.liste_uex.get().split(',') if uex.strip()]
            uex_list = [uex.lower() for uex in uex_list]  # Convertir en minuscules


            return {
                'nombre_groupes': nb_groupes,
                'taille_groupes': taille_groupes,
                'taille_max_groupes': taille_max,
                'liste_uex': uex_list
            }
        
        except ValueError as e:
            # Si la configuration n'a pas été rentrée du tout
            if "invalid literal for int()" in str(e):
                raise ValueError("Rentrez les paramètres de configuration puis réessayez.")
            
            # Sinon, erreur générique
            raise ValueError(f"Erreur dans les paramètres de configuration: {str(e)}")
    
    def valider_fichier_etudiants(self, chemin_fichier):
        """Valide le fichier des étudiants."""
        try:
            # Tester la lecture du fichier avec les fonctions existantes
            df = lfe.get_df_etudiants(chemin_fichier)
            # Utiliser les paramètres de configuration de l'interface
            config_params = self.get_parametres_configuration()
            liste_UEX = config_params['liste_uex']
            lfe.df_etudiants_clean(df, liste_UEX)
            return True, "Fichier des étudiants valide."
        except Exception as e:
            # Retourner une erreur spécifique basée sur le type d'exception
            error_msg = str(e)
            if "colonnes requises" in error_msg:
                return False, f"Colonnes manquantes. Requis: N°, NOM, PRENOM, UEX. Vérifiez que la première ligne contient ces en-têtes. Erreur : {error_msg}"
            elif "numéros d'étudiants" in error_msg:
                return False, f"Numéros d'étudiants invalides (doivent être des entiers). Vérifiez la colonne N°. Erreur : {error_msg}"
            elif "UEX" in error_msg or "liste_UEX" in error_msg:
                return False, f"Valeurs UEX invalides. Valeurs autorisées: BIO303, BIO304, BIO305 (ou leurs variantes VALIDÉ). Erreur : {error_msg}"
            elif "FileNotFoundError" in str(type(e)):
                return False, f"Fichier non trouvé. Vérifiez le chemin du fichier. Erreur : {error_msg}"
            elif "PermissionError" in str(type(e)):
                return False, f"Permission refusée. Fermez le fichier Excel s'il est ouvert. Erreur : {error_msg}"
            else:
                return False, f"Erreur technique: {error_msg}"
    
    def valider_fichier_equipes(self, chemin_fichier):
        """Valide le fichier des équipes."""
        try:
                
            # Tester la lecture et nettoyage du fichier équipes
            df = lft.get_df_equipes(chemin_fichier)
            lft.df_equipes_clean(df)
            return True, "Fichier des équipes valide."

        except Exception as e:
            # Retourner une erreur spécifique basée sur le type d'exception
            error_msg = str(e)
            return False, f"Erreur technique: {error_msg}"

    def valider_fichier_mariages(self, chemin_fichier):
        """Valide le fichier des mariages."""
        try:

            # Tester la lecture du fichier mariages
            df_uex, df_groupes = lfm.get_dfs_mariages(chemin_fichier)
            # Utiliser les paramètres de configuration de l'interface
            config_params = self.get_parametres_configuration()
            liste_uex = config_params['liste_uex']
            config_params['taille_max_groupes']
            lfm.df_mariages_UEX_clean(df_uex, liste_uex)
            lfm.df_mariages_groupes_clean(df_groupes, liste_uex)
            return True, "Fichier des mariages valide."

        except Exception as e:
            # Retourner une erreur spécifique basée sur le type d'exception
            error_msg = str(e)
            if "sheet_name" in error_msg or "feuille" in error_msg or "Worksheet" in error_msg:
                return False, error_msg
            elif "colonnes requises" in error_msg:
                return False, error_msg
            elif "UEX" in error_msg:
                return False, error_msg
            elif "FileNotFoundError" in str(type(e)):
                return False, "Fichier non trouvé. Vérifiez le chemin du fichier."
            elif "PermissionError" in str(type(e)):
                return False, "Permission refusée. Fermez le fichier Excel s'il est ouvert."
            else:
                return False, f"Erreur technique: {error_msg}"
    
    def verifier_etat_boutons(self):
        """Vérifie l'état des validations et active/désactive les boutons selon l'étape."""
        # Mettre à jour les indicateurs visuels des fichiers principaux
        for label_status, var_valid in self.labels_status:
            if var_valid.get():
                label_status.config(text="✅", fg="green")
            else:
                label_status.config(text="❌", fg="red")
        
        # Vérifier la configuration
        config_valide, message_config = self.valider_parametres_configuration()
        
        # ÉTAPE 1 : Vérifier si tous les fichiers initiaux sont valides ET la configuration
        tous_fichiers_valides = (self.valid_etudiants.get() and 
                                self.valid_equipes.get() and 
                                self.valid_mariages.get())
        
        if tous_fichiers_valides and config_valide:
            # Activer le bouton de génération de correction
            self.btn_generer.config(state="normal")
            if not self.correction_generee.get():
                # Ne pas écraser le message d'erreur persistant
                if not self.message_erreur_persistant:
                    self.label_info.config(
                        text="✅ Tous les fichiers et la configuration sont valides. Cliquez sur 'Générer Fichier de Correction' pour continuer.",
                        fg="green"
                    )
        else:
            # Désactiver le bouton de génération
            self.btn_generer.config(state="disabled")
            if not self.correction_generee.get():
                # Ne pas écraser le message d'erreur persistant, mais afficher un message par défaut si aucune erreur
                if not self.message_erreur_persistant:
                    if not config_valide:
                        self.label_info.config(
                            text=f"❌ Configuration invalide: {message_config}",
                            fg="red"
                        )
                    elif not tous_fichiers_valides:
                        self.label_info.config(
                            text="Sélectionnez les trois fichiers requis et configurez les paramètres pour continuer.",
                            fg="black"
                        )
        
        # ÉTAPE 2 : Affichage conditionnel des sections suivantes
        if self.correction_generee.get():
            # Afficher la section de sélection du fichier de correction
            self.frame_correction.grid(row=5, column=0, columnspan=4, padx=20, pady=10, sticky="ew")
            
            # Si un fichier de correction est sélectionné, afficher la section mise en groupe
            if self.valid_correction.get():
                self.frame_actions2.grid(row=6, column=0, columnspan=4, pady=10)
                self.btn_mise_en_groupe.config(state="normal")
            else:
                # Cacher la section mise en groupe si pas de fichier de correction
                self.frame_actions2.grid_forget()
                
        # Programmer la prochaine vérification
        self.root.after(500, self.verifier_etat_boutons)
    
    def generer_fichier_correction(self):
        """Génère le fichier de correction manuelle."""
        try:

            # Récupérer et vérifier les chemins des fichiers
            chemin_etudiants = str(self.fichier_etudiants.get())
            chemin_equipes = str(self.fichier_equipes.get())
            chemin_mariages = str(self.fichier_mariages.get())

            # Vérifier que les fichiers existent avant de les lire
            if not os.path.exists(chemin_etudiants):
                raise FileNotFoundError(f"Le fichier étudiants n'existe pas : {chemin_etudiants}")
            if not os.path.exists(chemin_equipes):
                raise FileNotFoundError(f"Le fichier équipes n'existe pas : {chemin_equipes}")

            if not os.path.exists(chemin_mariages):
                raise FileNotFoundError(f"Le fichier mariages n'existe pas : {chemin_mariages}")

            # Lire et nettoyer les fichiers étudiants et équipes
            df_etudiants = lfe.get_df_etudiants(chemin_etudiants)
            liste_uex = self.get_parametres_configuration()['liste_uex']
            df_etudiants_clean = lfe.df_etudiants_clean(df_etudiants, liste_uex)
            df_equipes = lft.get_df_equipes(chemin_equipes)
            df_equipes_clean = lft.df_equipes_clean(df_equipes)
            # Appeler la fonction correction_manuelle avec les DataFrames nettoyés et chemins complets
            liste_uex = self.get_parametres_configuration()['liste_uex']
            adf.correction_manuelle(df_etudiants_clean, df_equipes_clean, liste_uex)
            
            # Marquer que le fichier de correction a été généré
            self.correction_generee.set(True)
            
            # Proposer automatiquement le fichier de correction s'il existe
            fichier_correction_defaut = os.path.join(os.getcwd(), "correction_manuelle_resultat.xlsx")
            if os.path.exists(fichier_correction_defaut):
                self.fichier_correction.set(fichier_correction_defaut)
                self.valider_fichier_correction(fichier_correction_defaut)
            
            messagebox.showinfo(
                "Succès", 
                "✅ Fichier de correction généré avec succès!\n\n"
                "Le fichier 'correction_manuelle_resultat.xlsx' a été créé.\n"
                "Sélectionnez maintenant le fichier de correction pour continuer."
            )
            
            self.label_info.config(
                text="✅ Fichier de correction généré. Sélectionnez le fichier de correction pour continuer.",
                fg="green"
                )

        except FileNotFoundError as e:
            messagebox.showerror(
                "Fichier non trouvé", 
                f"Le fichier sélectionné n'existe plus :\n{str(e)}\n\n"
                "Veuillez sélectionner à nouveau le fichier."
            )
            self.label_info.config(
                text="❌ Fichier non trouvé. Veuillez resélectionner les fichiers.",
                fg="red"
            )
        except PermissionError as e:
            messagebox.showerror(
                "Permission refusée", 
                f"Impossible d'accéder au fichier :\n{str(e)}\n\n"
                "Vérifiez que le fichier n'est pas ouvert dans Excel."
            )
        except Exception as e:
            messagebox.showerror(
                "Erreur", 
                f"Erreur lors de la génération du fichier de correction :\n{str(e)}\n\n"
                "Répertoire de travail : {os.getcwd()}"
            )

    def lancer_mise_en_groupe(self, chemin_fichier_correction, chemin_fichier_configuration, df_mariages_groupe, df_mariages_uex):
        """Lance le processus de mise en groupe."""
        try:
            
            # Récupérer les paramètres de configuration depuis l'interface
            config_params = self.get_parametres_configuration()
            
            resultat = meg.fonction_main_avec_params(
                chemin_fichier_correction,
                df_mariages_groupe,
                df_mariages_uex,
                config_params['taille_groupes'],
                config_params['liste_uex'],
                config_params['taille_max_groupes']
            )

            if resultat and resultat[0] is not None:
                nb_etudiants, nb_places, nb_etudiants_place, liste_groupes, liste_mariages = resultat
                
                message = f"✅ Mise en groupe terminée avec succès!\n\n"
                message += f"📊 Résultats :\n"
                message += f"• Étudiants placés : {nb_etudiants_place}/{nb_etudiants}\n"
                message += f"• Taux de réussite : {(nb_etudiants_place/nb_etudiants)*100:.1f}%\n"
                message += f"• Solution parfaite : {'Oui' if nb_etudiants_place == nb_etudiants else 'Non'}\n\n"
                message += "Les résultats ont été générés."
                
                messagebox.showinfo("Résultats", message)
                
                if messagebox.askyesno("Export", "Voulez-vous exporter les résultats vers Excel ?"):
                    self.exporter_resultats(resultat)
                        
           
            else:
                messagebox.showerror("Erreur", "Module de mise en groupe non disponible.")
                
        except Exception as e:
            messagebox.showerror(
                "Erreur", 
                f"Erreur lors de la mise en groupe:\n{str(e)}"
            )
    
    def exporter_resultats(self, resultat):
        """Exporte les résultats vers un fichier Excel."""
        try:
            liste_uex = self.get_parametres_configuration()['liste_uex']
            tdr.exporter_resultats(resultat, liste_uex)
            messagebox.showinfo(
                "Export", 
                "✅ Résultats exportés vers 'resultats_mise_en_groupe.xlsx'"
            )


        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror(
                "Erreur", 
                f"Erreur lors de l'export:\n{str(e)}"
            )

    def on_mise_en_groupe_click(self):
        """Récupère les DataFrames nettoyés et lance la mise en groupe."""
        try:
         # Récupérer les chemins des fichiers
            chemin_mariages = str(self.fichier_mariages.get())
            chemin_fichier_correction = str(self.fichier_correction.get())


            df_uex, df_groupes = lfm.get_dfs_mariages(chemin_mariages)
            # Utiliser les paramètres de configuration de l'interface
            config_params = self.get_parametres_configuration()
            liste_uex = config_params['liste_uex']
            df_uex_clean = lfm.df_mariages_UEX_clean(df_uex,liste_uex) 
            df_groupe_clean = lfm.df_mariages_groupes_clean(df_groupes, liste_uex)

            # Appeler la fonction de mise en groupe
            self.lancer_mise_en_groupe(chemin_fichier_correction, chemin_mariages, df_groupe_clean, df_uex_clean)
        except Exception as e:
            messagebox.showerror(
                "Erreur",
                f"Erreur lors de la préparation des données pour la mise en groupe:\n{str(e)}"
            )

    def afficher(self):
        """Affiche l'interface."""
        self.root.mainloop()

def afficher_grille_selection_fichiers():
    """Fonction principale pour afficher l'interface de sélection de fichiers."""
    interface = InterfaceSelectionFichiers()
    interface.afficher()

