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


print("Liste des UEX normalisée :", liste_uex)
def randomiser_liste(liste):
    """
    Randomise la liste donnée en paramètre.
    """
    return pd.Series(liste).sample(frac=1).tolist()

def get_liste_etud_uex():
    """
    Retourn une liste qui pour chaque UEX admet un liste des equipes qui lui sont associés.
    """
    liste_equipe_uex = []
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
    liste_etud_uex = get_liste_etud_uex()
    groupes_liste = []
    
    for i in range(nombre_groupes):
        groupe = Classes.Groupe(i + 1, [], None)
        groupes_liste.append(groupe)
    
    return groupes_liste


def table_contraintes():
    """
    Retourne une table des contraintes.
    
    """
    


if __name__ == "__main__":
    liste_etud_uex = get_liste_etud_uex()
    for uex, etudiants in liste_etud_uex:
        print(uex)
        print(etudiants)
    


