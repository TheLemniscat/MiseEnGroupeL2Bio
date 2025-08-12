import pandas as pd

from backend import Classes
from backend import MyTools as mytools


def get_dfs_mariages(file_path):
    """
    Lit le fichier des mariages et retourne un DataFrame.
    """
    try:
        df_mariages_groupes = pd.read_excel(file_path, sheet_name=0)
        df_mariages_UEX = pd.read_excel(file_path, sheet_name=1)
        return df_mariages_UEX, df_mariages_groupes
    except Exception as e:
        raise ValueError(f"Le fichier {file_path} ne peut pas être lu. Vérifiez qu'il contient 2 feuilles Excel.") from e


def df_mariages_groupes_clean(df_mariages_groupes, liste_uex):
    """
    Nettoie le DataFrame des groupes des mariages.
    """
    df_copie = df_mariages_groupes.copy()
    
    # Vérifier que la colonne 'Groupes' existe
    if 'Groupes' not in df_copie.columns:
        raise ValueError("La feuille des groupes doit contenir une colonne 'Groupes'")
    
    df_copie['Groupes'] = mytools.normaliser_colonne_texte(df_copie['Groupes'])

    def normaliser_UEX_groupe(df_UEX):
        try: 
            int(df_UEX)
            return int(df_UEX)
        except (ValueError, TypeError):
            return not pd.isna(df_UEX)

    liste_uex_majuscule = [uex.upper() for uex in liste_uex]

    for uex in liste_uex_majuscule:
        if uex in df_copie.columns:
            df_copie[uex] = df_copie[uex].apply(normaliser_UEX_groupe)

    return df_copie



def df_mariages_UEX_clean(df_mariages_UEX, liste_uex):
    """
    Nettoie le DataFrame des UEX des mariages.
    """
    df_copie = df_mariages_UEX.copy()

    liste_cardinal = ['PREMIER', 'DEUXIEME', 'TROISIEME']
    
    try:
        # Vérifier que les colonnes requises existent
        missing_cols = [col for col in liste_cardinal if col not in df_copie.columns]
        if missing_cols:
            raise ValueError(f"Colonnes manquantes dans la feuille UEX: {missing_cols}")
        
        for col in liste_cardinal:        
            df_copie[col] = mytools.normaliser_colonne_texte(df_copie[col])

        liste_uex_majuscule = [uex.upper() for uex in liste_uex]

        for uex in liste_uex_majuscule:
            if uex in df_copie.columns:
                df_copie[uex] = df_copie[uex].apply(lambda x: not pd.isna(x))
            
    except Exception as e:
        raise ValueError(f"Erreur lors du nettoyage de la feuille UEX: {str(e)}") from e

    return df_copie



def dfs_mariages_clean(df_mariages_UEX, df_mariages_groupes, liste_uex):
    """
    Nettoie les DataFrames des mariages.
    """
    df_mariages_UEX = df_mariages_UEX_clean(df_mariages_UEX, liste_uex)
    df_mariages_groupes = df_mariages_groupes_clean(df_mariages_groupes, liste_uex)

    return df_mariages_UEX, df_mariages_groupes


def get_nombre_groupes(df_mariages_groupes):
    """
    Retourne le nombre de groupes à créer.
    """
    # Exclure la ligne 'bioint' si elle existe
    if 'Groupes' in df_mariages_groupes.columns:
        groupes_sans_bioint = df_mariages_groupes[df_mariages_groupes['Groupes'] != 'bioint']
        return len(groupes_sans_bioint)
    else:
        # Si pas de colonne 'Groupes', compter toutes les lignes sauf la dernière (supposée être bioint)
        return len(df_mariages_groupes) - 1   




def creation_des_groupes(df_mariages_groupes, liste_uex, taille_max_groupe):
    """
    Crée les groupes à partir de la liste des étudiants et de la taille des groupes.
    """
    nombre_groupes = get_nombre_groupes(df_mariages_groupes)

    groupes_liste = []
    for i in range(nombre_groupes):
        liste_equipes = []

        numero_groupe = i + 1
        nom_groupe = f"groupe {numero_groupe}"
        
        # Obtenir les UEX pour ce groupe
        uex_groupe = []
        liste_uex_majuscule = [uex.upper() for uex in liste_uex]
        for uex in liste_uex_majuscule:
            if uex in df_mariages_groupes.columns:
                if i < len(df_mariages_groupes) and not pd.isna(df_mariages_groupes.iloc[i][uex]) and df_mariages_groupes.iloc[i][uex]:
                    uex_groupe.append(uex)

        # Création de l'objet Groupe
        groupe = Classes.Groupe(numero_groupe, nom_groupe, liste_equipes, uex_groupe, taille_max_groupe)
        
        groupes_liste.append(groupe)

    return groupes_liste


def creation_groupe_bioint(liste_uex, taille_max_groupe):
    liste_uex_majuscule = [uex.upper() for uex in liste_uex]
    return Classes.Groupe(-1,'bioint', [], liste_uex_majuscule, taille_max_groupe)

def get_bioint_dict(df_mariages_groupes, liste_uex):
    """
    Retourne un dictionnaire des bioint. (les clés sont les UEX et les valeurs sont les nombres de bioint)
    """
    try:
        # Chercher la ligne avec 'bioint' (insensible à la casse)
        mask = df_mariages_groupes['Groupes'].str.lower().str.contains('bioint', na=False)
        
        if not mask.any():
            raise ValueError("Le groupe 'bioint' n'a pas été trouvé dans la configuration des mariages.")
        
        row = df_mariages_groupes.loc[mask].iloc[0]

    except (IndexError, KeyError) as e:
        raise ValueError("Le groupe 'bioint' n'a pas été trouvé dans la configuration des mariages.") from e
    
    bioint_liste = {}
    liste_uex_majuscule = [uex.upper() for uex in liste_uex]
    for uex in liste_uex_majuscule:
        if uex in row.index and not pd.isna(row[uex
]) and row[uex]:
            # Convertir en entier si c'est un nombre
            try:
                bioint_liste[uex] = int(row[uex])
            except (ValueError, TypeError):
                bioint_liste[uex] = row[uex]

    return bioint_liste


def creation_des_mariages(liste_groupes, df_mariages_UEX, liste_uex, taille_max_mariage):
    """ 
    Crée les mariages à partir de la liste des groupes et de la configuration des mariage.
    """

    nombre_mariages = df_mariages_UEX.shape[0]

    liste_cardinal = ['PREMIER', 'DEUXIEME', 'TROISIEME']
    
    for col in liste_cardinal:        
        df_mariages_UEX[col] = mytools.normaliser_colonne_texte(df_mariages_UEX[col])

    mariages_liste = []
    for i in range(nombre_mariages):
        row = df_mariages_UEX.iloc[i]
        
        membres = []
        
        for col in liste_cardinal:
            if pd.isna(row[col]):
                continue
            
            membre = row[col].strip()
            
            # On souhaite ajouter l'objet Groupe correspondant au membre
            #On le cherche dans la liste des groupes
            for groupe in liste_groupes:
                if membre == groupe.get_name():
                    membres.append(groupe)
                                    
        liste_uex_majuscule = [uex.upper() for uex in liste_uex]
        
        uex = [uex for uex in liste_uex_majuscule if row[uex]]
        uex = uex[0]
        
        mariages_liste.append(Classes.Mariage(i+1,uex,membres, taille_max_mariage))
        
    
    return mariages_liste 



def ajouter_bioint_mariage(mariages_liste, df_mariages_groupes, liste_uex):
    
    dict_bioint = get_bioint_dict(df_mariages_groupes, liste_uex)  # On récupère le dictionnaire des bioint
    
    try:
        # Chercher la ligne avec 'bioint' (insensible à la casse)
        mask = df_mariages_groupes['Groupes'].str.lower().str.contains('bioint', na=False)
        if not mask.any():
            raise ValueError("Le groupe 'bioint' n'a pas été trouvé dans la configuration des mariages.")
        
        row = df_mariages_groupes.loc[mask].iloc[0]
        

    except (IndexError, KeyError) as e:
        raise ValueError("Le groupe 'bioint' n'a pas été trouvé dans la configuration des mariages.") from e
    
    liste_uex_majuscule = [uex.upper() for uex in liste_uex]
    for i, uex in enumerate(liste_uex_majuscule):
        if uex not in row.index or pd.isna(row[uex]):
            continue
        
        if row[uex]:
            for mariage in mariages_liste:
                groupes_liste = mariage.get_groupes_liste()
                if 'bioint' in [grp.get_name() for grp in groupes_liste]:
                    if mariage.get_uex().upper() == uex:
                        mariage.set_bioint(dict_bioint[uex])

                        dict_bioint[uex] = 0  # On met à zéro pour éviter de le placer deux fois


