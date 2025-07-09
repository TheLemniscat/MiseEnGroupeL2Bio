from ReconstructionPostVerif import get_dict_uex, df_etud_ref
import pandas as pd
import unicodedata

from AnalyseDesFichiers import normaliser_colonne_texte
import LectureConfig as lc
import Classes

taille_groupe = lc.get_taille_groupes()
nombre_groupes = lc.get_nombre_groupes()





dictionnaire_uex = get_dict_uex()


liste_uex = lc.get_liste_uex()
liste_uex_majuscule = [uex.upper() for uex in liste_uex]


def randomiser_liste(liste):
    """
    Randomise la liste donnée en paramètre.
    """
    return pd.Series(liste).sample(frac=1).tolist()

def get_liste_etud_uex():
    """
    Retourn une liste qui pour chaque UEX admet un liste des equipes qui lui sont associés.
    """
    liste_etud_uex = []
    tmp = []
    for uex in dictionnaire_uex.keys():
        if uex in liste_uex:
            liste_tmp = randomiser_liste(dictionnaire_uex[uex])
            liste_etud_uex.append((uex, liste_tmp))
        else:
            tmp.append(dictionnaire_uex[uex])
    liste_etud_uex.append(("Valide", randomiser_liste(tmp)))

    return liste_etud_uex



def liste_etud_to_classes_etud(liste_etud_uex):
    """
    Transforme la liste des étudiants par UEX en une liste d'objets Etudiant.
    """
    liste_equipes = []
    for uex, equipe in liste_etud_uex:
        equipe_tmp = []
        for INDEX in equipe:
            etudiant = df_etud_ref.loc[INDEX]
            nom = normaliser_colonne_texte(etudiant['NOM'])
            prenom = normaliser_colonne_texte(etudiant['PRENOM'])
            numero_etudiant = etudiant['N°']
            valide = etudiant['VALIDE']
            
            etud_obj = Classes.Etudiant(nom, prenom, numero_etudiant, uex, valide)
            equipe_tmp.append(etud_obj)

        liste_equipes.append(Classes.Equipe(uex, equipe_tmp, uex))
            
    
    return liste_equipes


def get_contraintes_groupes():
    """
    Retourne les contraintes de mariage des groupes.
    """
    contraintes_groupes = pd.read_excel(lc.get_name_mariage(), sheet_name=0, header=0)
    contraintes_groupes['Groupes'] = normaliser_colonne_texte(contraintes_groupes['Groupes'])


    def normaliser_contrainte_groupe(contrainte):
        try: 
            int(contrainte)
            return int(contrainte)
        except ValueError:
            return not pd.isna(contrainte)

    for uex in liste_uex_majuscule:
        contraintes_groupes[uex] = contraintes_groupes[uex].apply(normaliser_contrainte_groupe)

    return contraintes_groupes



def creation_des_groupes():
    """
    Crée les groupes à partir de la liste des étudiants et de la taille des groupes.
    """
    contraintes_groupes = get_contraintes_groupes()


    groupes_liste = []
    for i in range(nombre_groupes):
        liste_equipes = []

        nom_groupe = f"groupe {i+1}"
        uex_groupe = [uex for uex in liste_uex_majuscule if contraintes_groupes.loc[i, uex]]

        # Création de l'objet Groupe
        groupe = Classes.Groupe(nom_groupe, liste_equipes, uex_groupe)
        
        groupes_liste.append(groupe)

    groupe_bioint = Classes.Groupe('bioint', [], liste_uex_majuscule)
    groupes_liste.append(groupe_bioint)

    return groupes_liste





def creation_des_mariages(liste_groupes):
    """ 
    Crée les mariages à partir de la liste des étudiants et des contraintes de mariage.
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


def get_bioint(mariages_liste):
    contraintes_groupes = get_contraintes_groupes()

    try:
        row = contraintes_groupes.loc[contraintes_groupes['Groupes'] == 'bioint'].iloc[0]
    
    except IndexError:
        raise ValueError("Le groupe 'bioint' n'a pas été trouvé dans les contraintes de mariage.")


    for uex in liste_uex_majuscule:
        if pd.isna(row[uex]):
            continue
        
        if row[uex]:
            for mariage in mariages_liste:
                groupes_liste = mariage.get_groupes_liste()
                if 'bioint' in [grp.get_name() for grp in groupes_liste]:
                    if mariage.get_uex() == uex:
                        new_taille_max = mariage.get_taille_max() - row[uex]
                        mariage.modifier_taille_max(new_taille_max)

                            



if __name__ == "__main__":
    mariage_liste = creation_des_mariages(creation_des_groupes())
    get_bioint(mariage_liste)

    print("Liste des mariages :")
    for mariage in mariage_liste:
        print(mariage)
    
    #print(liste_groupes_uex)
    


