from ReconstructionPostVerif import get_dict_uex
import pandas as pd
import unicodedata

from AnalyseDesFichiers import normaliser_colonne_texte
import LectureConfig as lc

taille_groupe = lc.get_taille_groupes()
nombre_groupes = lc.get_nombre_groupes()


dictionnaire_uex = get_dict_uex()


liste_uex = lc.get_liste_uex()
liste_uex = [unicodedata
             .normalize('NFD', str(uex))
             .encode('ascii', errors='ignore')
             .decode('utf-8')
             .strip()
             .lower()
             .replace('  ', ' ') for uex in liste_uex]

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


def table_contraintes():
    """
    Retourne une table des contraintes.
    
    """
    


if __name__ == "__main__":
    liste_etud_uex = get_liste_etud_uex()
    for uex, etudiants in liste_etud_uex:
        print(uex)
        print(etudiants)
    


