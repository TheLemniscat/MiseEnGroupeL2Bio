from ReconstructionPostVerif import get_liste_equipes, df_etud_ref
import pandas as pd
import unicodedata

from AnalyseDesFichiers import normaliser_colonne_texte
import LectureConfig as lc
import Classes

taille_groupe = lc.get_taille_groupes()
nombre_groupes = lc.get_nombre_groupes()





liste_equipes = get_liste_equipes()


liste_uex = lc.get_liste_uex()
liste_uex_majuscule = [uex.upper() for uex in liste_uex]


def randomiser_liste(liste):
    """
    Randomise la liste donnée en paramètre.
    """
    return pd.Series(liste).sample(frac=1).tolist()



def get_UEX_groupes():
    """
    Retourne un df qui contient les UEX des groupes.
    """
    df_UEX_groupes = pd.read_excel(lc.get_name_mariage(), sheet_name=0, header=0)
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

        nom_groupe = f"groupe {i+1}"
        uex_groupe = [uex for uex in liste_uex_majuscule if df_UEX_groupes.loc[i, uex]]

        # Création de l'objet Groupe
        groupe = Classes.Groupe(nom_groupe, liste_equipes, uex_groupe)
        
        groupes_liste.append(groupe)

    groupe_bioint = Classes.Groupe('bioint', [], liste_uex_majuscule)
    groupes_liste.append(groupe_bioint)

    return groupes_liste





def creation_des_mariages(liste_groupes):
    """ 
    Crée les mariages à partir de la liste des groupes et de la configuration des mariage.
    """
    mariage = pd.read_excel(lc.get_name_mariage(), sheet_name=1, header=0)
    
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
        
        mariages_liste.append(Classes.Mariage(uex,membres))
        
    
    return mariages_liste 


def modification_mariage_bioint(mariages_liste):
    UEX_groupes = get_UEX_groupes()

    try:
        row = UEX_groupes.loc[UEX_groupes['Groupes'] == 'bioint'].iloc[0]
    
    except IndexError:
        raise ValueError("Le groupe 'bioint' n'a pas été trouvé dans la configuration des mariage.")


    for uex in liste_uex_majuscule:
        if pd.isna(row[uex]):
            continue
        
        if row[uex]:
            for mariage in mariages_liste:
                groupes_liste = mariage.get_groupes_liste()
                if 'bioint' in [grp.get_name() for grp in groupes_liste]:
                    if mariage.get_uex().upper() == uex:
                        new_taille_max = mariage.get_taille_max() - row[uex]
                        mariage.modifier_taille_max(new_taille_max)

def score_groupe(groupe):
    """
    Calcule le score d'un groupe. 
    Le score est le pourcentage de remplissage du groupe.
    """
    return groupe.length() / groupe.get_taille_max()

def score_mariage(mariage):
    """
    Calcule le score d'un mariage.
    Le score est le pourcentage de remplissage du mariage.
    """

    return mariage.length() / mariage.get_taille_max()
                            




if __name__ == "__main__":
    liste_groupes = creation_des_groupes()
    liste_mariages = creation_des_mariages(liste_groupes)
    modification_mariage_bioint(liste_mariages)
    liste_equipes = get_liste_equipes()
    
    groupe = liste_groupes[2]
    equipe = liste_equipes[0]
    mariage = liste_mariages[3]
    groupe.ajouter_equipe(equipe)
    
    score_du_mariage = score_mariage(liste_mariages[4])
    
    print(mariage.get_taille_max())
    print(f"{mariage.get_uex()} : {', '.join(grp.get_name() for grp in mariage.get_groupes_liste())} : {score_mariage(mariage)}")
    print(equipe)
    print(f'{groupe.get_name()} : {score_groupe(groupe)}')

    if False:
        print(liste_equipes[0])
        for groupe in liste_groupes:
            print(f'{groupe.get_name()} : {score_groupe(groupe)}')
        
        for mariage in liste_mariages:
            pass




