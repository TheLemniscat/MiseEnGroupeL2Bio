from ReconstructionPostVerif import get_liste_equipes, get_etudiant_not_in_equipes
import pandas as pd
import unicodedata

from AnalyseDesFichiers import normaliser_colonne_texte
import LectureConfig as lc
import Classes

taille_groupe = lc.get_taille_groupes()
nombre_groupes = lc.get_nombre_groupes()




liste_uex = lc.get_liste_uex()
liste_uex_majuscule = [uex.upper() for uex in liste_uex]


def randomiser_liste(liste):
    """
    Randomise la liste donnée en paramètre.
    """
    return pd.Series(liste).sample(frac=1).tolist()

def liste_etudiants_to_liste_equipes(liste_etudiants):
    """
    Transforme une liste d'étudiants en une liste d'équipes.
    Chaque équipe contient un seul étudiant.
    """
    return [Classes.Equipe(-etudiant.get_index_etud(), [etudiant], etudiant.get_uex(), True) for etudiant in liste_etudiants]



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


    return groupes_liste


def creation_groupe_bioint():
    return Classes.Groupe('bioint', [], liste_uex_majuscule)

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
                            

def mise_en_groupe_determinee(liste_groupe, liste_equipes):
    """
    Cherche les UEX qui ne sont que dans un seul groupe et ajoute les équpie et étudiant correspondants
    """
    for uex in liste_uex_majuscule:
        count = 0
        groupe_teste = None
        for i, groupe in enumerate(liste_groupe):
            if uex in groupe.get_uex_liste():
                count += 1
                groupe_teste = liste_groupe[i]

        
        if count == 1 and groupe_teste is not None:
            groupe = groupe_teste
            for equipe in liste_equipes:
                if uex.lower() in equipe.get_uex():
                    groupe.ajouter_equipe(equipe)
                    liste_equipes.remove(equipe)
        
    



if __name__ == "__main__":
    liste_groupes = creation_des_groupes()
    goupe_bioint = creation_groupe_bioint()
    liste_groupes_avec_bioint = liste_groupes + [goupe_bioint]
    
    
    liste_mariages = creation_des_mariages(liste_groupes_avec_bioint)
    modification_mariage_bioint(liste_mariages)
    
    liste_equipes = get_liste_equipes()
    liste_equipes = randomiser_liste(liste_equipes)

    liste_etudiants = get_etudiant_not_in_equipes(liste_equipes)
    liste_etudiants = randomiser_liste(liste_etudiants)

    liste_etudiants = liste_etudiants_to_liste_equipes(liste_etudiants)

    liste_equipes_complete = liste_equipes + liste_etudiants


    mise_en_groupe_determinee(liste_groupes, liste_equipes_complete)
    
    if True:
        for groupe in liste_groupes:
            print(f"{groupe.get_name()} : {groupe.length()}/{groupe.get_taille_max()} ({score_groupe(groupe) * 100:.2f}%)")
            for equipe in groupe.get_equipes():
                print(f"-{equipe}")



