import pandas as pd
import LectureConfig as lc

import Classes
from Tools import normaliser_colonne_texte


liste_uex = lc.get_liste_uex()
liste_uex_majuscule = [uex.upper() for uex in liste_uex]


nom_fichier_mariages = lc.get_name_mariages()
nombre_groupes = lc.get_nombre_groupes()


def get_nombre_groupes():
    """
    Retourne le nombre de groupes à créer.
    """
    
    df_UEX_groupes = pd.read_excel(nom_fichier_mariages, sheet_name=0, header=0)
    print(len(df_UEX_groupes[0])-1) # Pour ne pas compter les bioint   


print(f"Nombre de groupes : {get_nombre_groupes()}")


def get_UEX_groupes():
    """
    Retourne un df qui contient les UEX des groupes.
    """
    df_UEX_groupes = pd.read_excel(nom_fichier_mariages, sheet_name=0, header=0)
    df_UEX_groupes['Groupes'] = normaliser_colonne_texte(df_UEX_groupes['Groupes'])


    def normaliser_UEX_groupe(df_UEX):
        try: 
            int(df_UEX)
            return int(df_UEX)
        except ValueError:
            return not pd.isna(df_UEX)

    for uex in liste_uex_majuscule:
        df_UEX_groupes[uex] = df_UEX_groupes[uex].apply(normaliser_UEX_groupe)

    return df_UEX_groupes


def creation_des_groupes():
    """
    Crée les groupes à partir de la liste des étudiants et de la taille des groupes.
    """
    df_UEX_groupes = get_UEX_groupes()


    groupes_liste = []
    for i in range(nombre_groupes):
        liste_equipes = []

        numero_groupe = i + 1
        nom_groupe = f"groupe {numero_groupe}"
        uex_groupe = [uex for uex in liste_uex_majuscule if df_UEX_groupes.loc[i, uex]]

        # Création de l'objet Groupe
        groupe = Classes.Groupe(numero_groupe,nom_groupe, liste_equipes, uex_groupe)
        
        groupes_liste.append(groupe)


    return groupes_liste


def creation_groupe_bioint():
    return Classes.Groupe(-1,'bioint', [], liste_uex_majuscule)

def get_bioint_liste():
    """
    Retourne la liste des UEX bioint.
    """
    df_UEX_groupes = get_UEX_groupes()
    
    try:
        row = df_UEX_groupes.loc[df_UEX_groupes['Groupes'] == 'bioint'].iloc[0]
    
    except IndexError:
        raise ValueError("Le groupe 'bioint' n'a pas été trouvé dans la configuration des mariage.")
    
    bioint_liste = []
    for uex in liste_uex_majuscule:
        if pd.isna(row[uex]):
            continue
        
        if row[uex]:
            bioint_liste.append(uex)
    
    return bioint_liste


def creation_des_mariages(liste_groupes):
    """ 
    Crée les mariages à partir de la liste des groupes et de la configuration des mariage.
    """
    mariage = pd.read_excel(lc.get_name_mariages(), sheet_name=1, header=0)
    
    nombre_mariages = mariage.shape[0]

    liste_cardinal = ['PREMIER', 'DEUXIEME', 'TROISIEME']
    
    for col in liste_cardinal:        
        mariage[col] = normaliser_colonne_texte(mariage[col])
    
    for uex in liste_uex_majuscule:
        mariage[uex] = mariage[uex].apply(
            lambda x: not pd.isna(x)
        )
    

    mariages_liste = []
    for i in range(nombre_mariages):
        row = mariage.iloc[i]
        
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
                                    

        uex = [uex for uex in liste_uex_majuscule if row[uex]]
        uex = uex[0]
        
        mariages_liste.append(Classes.Mariage(i+1,uex,membres))
        
    
    return mariages_liste 


def enlever_bioint_mariage(mariages_liste):
    UEX_groupes = get_UEX_groupes()

    try:
        row = UEX_groupes.loc[UEX_groupes['Groupes'] == 'bioint'].iloc[0]
    
    except IndexError:
        raise ValueError("Le groupe 'bioint' n'a pas été trouvé dans la configuration des mariage.")

    for i,uex in enumerate(liste_uex_majuscule):
        if pd.isna(row[uex]):
            continue
        
        if row[uex]:
            for mariage in mariages_liste:
                groupes_liste = mariage.get_groupes_liste()
                if 'bioint' in [grp.get_name() for grp in groupes_liste]:
                    if mariage.get_uex().upper() == uex:
                        mariage.set_bioint(row[uex])


def ajouter_bioint_mariage(mariages_liste):
    UEX_groupes = get_UEX_groupes()

    try:
        row = UEX_groupes.loc[UEX_groupes['Groupes'] == 'bioint'].iloc[0]
    
    except IndexError:
        raise ValueError("Le groupe 'bioint' n'a pas été trouvé dans la configuration des mariage.")

    for i,uex in enumerate(liste_uex_majuscule):
        if pd.isna(row[uex]):
            continue
        
        if row[uex]:
            for mariage in mariages_liste:
                groupes_liste = mariage.get_groupes_liste()
                if 'bioint' in [grp.get_name() for grp in groupes_liste]:
                    if mariage.get_uex().upper() == uex:
                        new_taille_max = mariage.get_taille_max() - row[uex]
                        mariage.set_taille_max(new_taille_max)