import pandas as pd
import LectureConfig as lc
from Tools import normaliser_colonne_texte

# Lecture de la configuration
nom_fichier_equipe = lc.get_name_fichier_equipe()

# Liste des colonnes à selectionner
df_equipe_colonnes = ["N°Obs","1. UE optionnelle du S3 commune",
            	"3. Numéro d'étudiant (1)",	"4. _Nom et prénom (1)",
                "5. Numéro d'étudiant (2)",	"6. _Nom et prénom (2)",	
                "7. Numéro d'étudiant (3)",	"8. _Nom et prénom (3)",
                "9. Numéro d'étudiant (4)",	"10. _Nom et prénom (4)"
]

def get_df_equipe(file_path):    
    nom_fichier_equipe = file_path
    try:
        return pd.read_excel(nom_fichier_equipe, header=0, usecols=df_equipe_colonnes)
    except ValueError as e:
        # Vérifie quelles colonnes manquent
        try:
            cols_in_file = pd.read_excel(nom_fichier_equipe, header=0, nrows=0).columns.tolist()
        except Exception:
            raise ValueError(f"Impossible de lire les colonnes du fichier {nom_fichier_equipe}. Erreur d'origine : {e}")
        missing = [col for col in df_equipe_colonnes if col not in cols_in_file]
        if missing:
            raise ValueError(f"Le fichier {nom_fichier_equipe} ne contient pas les colonnes requises : {missing}")
        else:
            raise ValueError(f"Le fichier {nom_fichier_equipe} ne contient pas les colonnes requises : {df_equipe_colonnes}") from e



def df_equipe_clean(df):
    df_copie = df.copy()
    df_copie.columns = [
        "NUMERO EQUIPE",
        "UEX", "N°1", "NOM et prénom 1",
        "N°2", "NOM et prénom 2", "N°3", "NOM et prénom 3",
        "N°4", "NOM et prénom 4"
    ]  


    def clean_type(df):
        for i in range(1, 5):
            col_num = f'N°{i}'
            def is_valid_num(x):
                if pd.isna(x):
                    return True
                try:
                    # Vérifie que c'est un entier
                    if float(x).is_integer():
                        # Vérifie que l'entier a 8 chiffres (pour être un numéro d'étudiant valide), en ignorant les -1 utilisés pour NaN
                        if int(float(x)) == -1:
                            return True
                        return len(str(int(float(x)))) == 8
                    return False
                except Exception:
                    return False

            mask_invalid = ~df_copie[col_num].apply(is_valid_num)
            if mask_invalid.any():
                lignes_erreur = df_copie[mask_invalid]
                raise ValueError(
                    f"[PROBLÈME] Dans la colonne {col_num} du fichier {nom_fichier_equipe}, "
                    f"les numéros doivent être des entiers à 8 chiffres. Lignes en erreur :\n{lignes_erreur}\n"
                )
            df_copie[col_num] = df_copie[col_num].apply(lambda x: int(float(x)) if not pd.isna(x) else -1)
        
        return df_copie
        

    
    def supprimer_doublons(df):
        """
        Supprime les doublons dans le DataFrame en considérant les équipes comme des ensembles de numéros d'étudiants.
        """
        # On crée une colonne temporaire qui contient, pour chaque ligne, le set trié des numéros d'étudiants de l'équipe
        def equipe_key(row):
            nums = []
            for i in range(1, 5):
                n = row[f'N°{i}']
                if not pd.isna(n) and int(n) != -1:
                    nums.append(int(n))
            return tuple(sorted(nums))
        
        df_copie = df.copy()
        df_copie['EQUIPE_KEY'] = df_copie.apply(equipe_key, axis=1)
        # Les doublons sont ceux qui ont un EQUIPE_KEY déjà vu (duplicated retourne True pour tous sauf la première occurrence)
        mask_duplicated = df_copie.duplicated(subset='EQUIPE_KEY', keep='first')
        doublons = df_copie[mask_duplicated].copy()
        # On retire la colonne temporaire avant de retourner
        df_sans_doublons = df_copie.drop_duplicates(subset='EQUIPE_KEY', keep='first').reset_index(drop=True)
        df_sans_doublons = df_sans_doublons.drop(columns=['EQUIPE_KEY'])
        
        # Pour le débogage, la fonction peut retourner les doublons
        doublons = doublons.drop(columns=['EQUIPE_KEY'])
        return df_sans_doublons

    def supprimer_sousensembles(df):
        """
        Supprime les sous-ensembles stricts d'équipes dans le DataFrame.
        """
        # On crée une clé d'équipe sous forme d'ensemble pour chaque ligne
        def equipe_set(row):
            nums = set()
            for i in range(1, 5):
                n = row[f'N°{i}']
                if not pd.isna(n) and int(n) != -1:
                    nums.add(int(n))
            return nums

        df_copie = df.copy()
        df_copie['EQUIPE_SET'] = df_copie.apply(equipe_set, axis=1)

        # On marque les sous-ensembles stricts
        to_remove = set()
        equipes = df_copie['EQUIPE_SET'].tolist()
        for i, eq1 in enumerate(equipes):
            for j, eq2 in enumerate(equipes):
                if i != j and eq1 and eq1 < eq2:  # eq1 est un sous-ensemble strict de eq2
                    to_remove.add(i)

        sous_ensembles = df_copie.iloc[list(to_remove)].reset_index(drop=True)
        df_sans_sous_ensembles = df_copie.drop(df_copie.index[list(to_remove)]).reset_index(drop=True)

        # On retire la colonne temporaire avant de retourner
        df_sans_sous_ensembles = df_sans_sous_ensembles.drop(columns=['EQUIPE_SET'])
        
        # Pour le débogage, la fonction peut retourner les sous-ensembles
        sous_ensembles = sous_ensembles.drop(columns=['EQUIPE_SET'])
        return df_sans_sous_ensembles


    def verif_NOM_PRENOM(df):
        """
        Vérifie que les colonnes NOM et PRENOM sont bien formatées.
        """
        for i in range(1, 5):
            col_nom_prenom = f'NOM et prénom {i}'
            # Convertit d'abord en string et ignore les valeurs NaN
            df_temp = df[col_nom_prenom].astype(str)
            # Vérifie qu'il n'y a pas de numéros dans les noms/prénoms (ignore 'nan' qui vient des NaN)
            mask_invalid = df_temp.str.contains(r'\d', na=False) & (df_temp != 'nan')
            if mask_invalid.any():
                lignes_erreur = df[mask_invalid]
                raise ValueError(
                    f"[PROBLÈME] Dans la colonne {col_nom_prenom} du fichier {nom_fichier_equipe}, "
                    f"les noms et prénoms ne doivent pas contenir de chiffres. Lignes en erreur :\n{lignes_erreur}\n"
                )

    verif_NOM_PRENOM(df_copie)  # Vérification des noms et prénoms

    df_copie = clean_type(df_copie)  # Nettoyage des types de données
    df_copie = supprimer_doublons(df_copie)
    df_copie = supprimer_sousensembles(df_copie)
    

    df_copie = df_copie.drop_duplicates(keep='first').reset_index(drop=True)



    return df_copie



def df_equipe_split_names(df):
    # Sépare les noms et prénoms en deux colonnes distinctes, est utilisé après que les colonnes soient renommées
    df_copie = df.copy()  # Crée une copie du DataFrame pour éviter de modifier l'original
    for i in range(1, 5):
        df_copie[[f'NOM {i}', f'PRENOM {i}']] = df_copie[f'NOM et prénom {i}'].str.split(' ', n=1, expand=True)
        df_copie.drop(columns=[f'NOM et prénom {i}'], inplace=True)
    
    df_copie = df_copie.drop_duplicates(keep='first').reset_index(drop=True)  # Supprime les doublons
    
    return df_copie





def df_equipe_normalisation(df):
    df_copie = df.copy()
    df_copie = df_equipe_clean(df_copie)


    liste_etudiants = []
    for i in range(1, 5):
        cols = [f'N°{i}', f'NOM et prénom {i}', 'NUMERO EQUIPE', 'UEX']
        df_temp = df_copie[cols].dropna(subset=[f'N°{i}'])
        df_temp = df_temp.rename(columns={
            f'N°{i}': 'N°',
            f'NOM et prénom {i}': 'NOM_PRENOM'
        })
        liste_etudiants.append(df_temp[['N°', 'NOM_PRENOM', 'NUMERO EQUIPE', 'UEX']])

    df_out = pd.concat(liste_etudiants, ignore_index=True)
    df_out['NOM_PRENOM'] = normaliser_colonne_texte(df_out['NOM_PRENOM'])
    
    return df_out[['N°', 'NOM_PRENOM', 'NUMERO EQUIPE', 'UEX']]



def netoyage_fichier_equipe(file_path):
    """
    Nettoie le fichier d'équipe en supprimant les lignes vides et les doublons.
    """
    try:
        df_equipe = get_df_equipe(file_path)
        df_equipe = df_equipe_clean(df_equipe)
        df_equipe = df_equipe_normalisation(df_equipe)
        df_equipe = df_equipe_split_names(df_equipe)
    
        return df_equipe.reset_index(drop=True)
    
    except ValueError as e:
        raise ValueError(f"Erreur lors du nettoyage du fichier d'équipe : {e}")