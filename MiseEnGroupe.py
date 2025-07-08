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




def creation_des_groupes():
    """
    Crée les groupes à partir de la liste des étudiants et de la taille des groupes.
    """
    contraintes_groupes = pd.read_excel(lc.get_name_mariage(), sheet_name=0, header=0)
    contraintes_groupes['Groupes'] = normaliser_colonne_texte(contraintes_groupes['Groupes'])

    for uex in liste_uex_majuscule:
        contraintes_groupes[uex] = contraintes_groupes[uex].apply(
            lambda x: not pd.isna(x)
        )


    groupe_liste = []
    for i in range(nombre_groupes):
        liste_equipes = []

        nom_groupe = f"Groupe {i+1}"
        uex_groupe = [uex for uex in liste_uex_majuscule if contraintes_groupes.loc[i, uex]]

        # Création de l'objet Groupe
        groupe = Classes.Groupe(i+1, liste_equipes, uex_groupe,[])
        
        groupe_liste.append(groupe)

    return groupe_liste



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
    

    mariage_liste = []
    for i in range(nombre_mariages):
        row = mariage.iloc[i]
        uex = [uex for uex in liste_uex_majuscule if row[uex]]
        
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
                                    

        
        
        mariage_liste.append(Classes.Mariage(uex,membres))
        
    
    return mariage_liste 





if __name__ == "__main__":
    liste_groupes = creation_des_groupes()
    liste_mariages = creation_des_mariages(liste_groupes)

    for i in range(len(liste_mariages)):
        print(f"Mariage {i+1} :", liste_mariages[i])


    liste_groupes_uex = [groupe.get_uex() for groupe in liste_groupes]
    
    #print(liste_groupes_uex)
    


