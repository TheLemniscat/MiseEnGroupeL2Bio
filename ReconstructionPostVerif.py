import LectureConfig as lc
import pandas as pd

from AnalyseDesFichiers import normaliser_colonne_texte
from collections import deque




"""
Recounstruit les équipes après la vérification des étudiants.
"""

nom_fichier_verifie = lc.get_name_fichier_verifie()
nombre_groupes = lc.get_nombre_groupes()
taille_groupes = lc.get_taille_groupes()
nombre_uex = lc.get_nombre_uex()

try:
    df_etud_ref = pd.read_excel(nom_fichier_verifie, sheet_name='etudiants')
    df_etud_trouves = pd.read_excel(nom_fichier_verifie, sheet_name='trouves')
    df_etud_non_trouves = pd.read_excel(nom_fichier_verifie, sheet_name='non_trouves')
except FileNotFoundError:
    raise FileNotFoundError(f"Le fichier '{nom_fichier_verifie}' n'a pas été crée. Veuillez d'abord exécuter le script d'analyse des fichiers.")


def supprimer_lignes_sans_index(df):
    return df[df['INDEX_ETUDIANT'].notna()]

df_etud_non_trouves = supprimer_lignes_sans_index(df_etud_non_trouves)
df_etud_ref["UEX"] = normaliser_colonne_texte(df_etud_ref["UEX"])
df_etud_trouves["UEX"] = normaliser_colonne_texte(df_etud_trouves["UEX"])
df_etud_non_trouves["UEX"] = normaliser_colonne_texte(df_etud_non_trouves["UEX"])

def reconstruction_equipe_post_verif(df_etud_trouves, df_etud_non_trouve, df_etud_ref):
    # Combine les deux DataFrames
    df_combined = pd.concat([df_etud_trouves, df_etud_non_trouve], ignore_index=True)

    df_etud_ref['NOM_PRENOM'] = df_etud_ref['NOM'] + ' ' + df_etud_ref['PRENOM']

    # On fait un merge pour récupérer les valeurs corrigées depuis df_etud_ref
    # On garde toutes les colonnes de df_combined, mais on remplace les valeurs par celles de ref si INDEX_ETUDIANT existe
    df_ref = df_etud_ref.set_index('INDEX_ETUDIANT')
    df_combined = df_combined.copy()
    for idx, row in df_combined.iterrows():
        index_etudiant = row.get('INDEX_ETUDIANT')
        if pd.notna(index_etudiant) and index_etudiant in df_ref.index:
            # Remplace toutes les colonnes de référence (N°, NOM, PRENOM, etc.) par celles de df_etud_ref
            for col in ['N°', 'NOM_PRENOM']:
                if col in df_ref.columns and col in df_combined.columns:
                    df_combined.at[idx, col] = df_ref.at[index_etudiant, col]
    

    df_combined['INDEX_ETUDIANT'] = df_combined['INDEX_ETUDIANT'].astype(int)
    df_combined.drop(columns=['NOM', 'PRENOM'], inplace=True, errors='ignore')

    return df_combined




def verif_UEX(df_etud_ref, df_etud_reconstruits):
    # Vérifie que chaque étudiant dans df_etud_reconstruits a la même UEX que dans df_etud_ref
    df_ref = df_etud_ref.set_index('INDEX_ETUDIANT')
    erreurs = []
    for idx, row in df_etud_reconstruits.iterrows():
        index_etudiant = row.get('INDEX_ETUDIANT')
        is_valide = df_ref.at[index_etudiant, 'VALIDE']
        if not is_valide:
            # On ne vérifie que les étudiants qui n'ont pas validé
            if pd.notna(index_etudiant) and index_etudiant in df_ref.index:
                uex_ref = df_ref.at[index_etudiant, 'UEX']
                uex_reconstruit = row.get('UEX')
                if uex_ref != uex_reconstruit:
                    erreurs.append((index_etudiant, uex_ref, uex_reconstruit))
    if erreurs:
        index_erreur = [erreur[0] for erreur in erreurs]
        etudiant_erreur = df_etud_ref[df_etud_ref['INDEX_ETUDIANT'].isin(index_erreur)][['INDEX_ETUDIANT', 'NOM', 'PRENOM', 'UEX']]
        raise ValueError(f"Des incohérences d'UEX ont été trouvées : {etudiant_erreur}")
    


def df_to_liste_equipes(df):
    """
    Regroupe les étudiants par numéro d'équipe.
    Retourne une liste de listes d'INDEX_ETUDIANT, chaque sous-liste représentant une équipe.
    """
    equipes_liste = []
    if 'NUMERO EQUIPE' not in df.columns:
        raise ValueError("La colonne 'NUMERO EQUIPE' est absente du DataFrame.")
    groupes = df.groupby('NUMERO EQUIPE')
    for _, groupe in groupes:
        membres = groupe['INDEX_ETUDIANT'].dropna().astype(int).tolist()
        if membres:
            equipes_liste.append(membres)
    
    return equipes_liste


"""
Gère les étudiants qui on fait des chaines d'équipe.
"""
def get_chaines_equipes(equipes_liste):
    """
    Détecte les chaînes d'équipes : si deux équipes partagent au moins un membre, elles sont fusionnées.
    Retourne une liste de listes, chaque sous-liste étant une chaîne d'équipes fusionnées.
    """

    # Convertit chaque équipe en set pour faciliter les opérations d'union/intersection
    equipes_sets = [set(equipe) for equipe in equipes_liste]
    chaines = []

    while equipes_sets:
        current = equipes_sets.pop(0)
        merged = True
        est_une_chaine = False
        while merged:
            merged = False
            for i, other in enumerate(equipes_sets):
                if current & other:  # Intersection non vide
                    current = current | other
                    equipes_sets.pop(i)
                    merged = True
                    est_une_chaine = True
                    break
        if est_une_chaine:
            chaines.append(sorted(list(current)))
    return chaines
    

def decouper_equipes(equipes_liste):
    """
    Découpe les équipes en sous-équipes de taille maximale.
    Chaque sous-équipe contient au maximum 5 étudiants.
    """
    taille_max = 5 # Taille maximale des équipes
    equipes_decoupees = []
    for equipe in equipes_liste:
        if len(equipe) <= taille_max:
            equipes_decoupees.append(equipe)
        else:
            # Découpe l'équipe en sous-équipes de taille maximale
            for i in range(0, len(equipe), taille_max):
                equipes_decoupees.append(equipe[i:i + taille_max])
    return equipes_decoupees


def correction_equpie_liste(equipes_liste):
    """
    Corrige les équipes en supprimant les doublons et en normalisant les numéros d'équipe.
    Retourne une liste de listes d'INDEX_ETUDIANT, chaque sous-liste représentant une équipe.
    """
    equipes_set = set(tuple(sorted(equipe)) for equipe in equipes_liste)
    equipes_liste_corrigee = [list(equipe) for equipe in equipes_set]
    chaines_equipes = get_chaines_equipes(equipes_liste_corrigee)

    # Fusionne les chaines d'équipes dans la liste principale
    for chaine in chaines_equipes:
        # Supprime toutes les équipes qui ont des membres dans la chaine
        equipes_liste_corrigee = [equipe for equipe in equipes_liste_corrigee if not set(equipe) & set(chaine)]
        # Ajoute la chaine fusionnée comme une nouvelle équipe
        equipes_liste_corrigee.append(sorted(chaine))
    
    # Supprime les équipes vides ou avec un seul membre
    equipes_liste_corrigee = [equipe for equipe in equipes_liste_corrigee if len(equipe) > 1]

    return equipes_liste_corrigee


def repartition_UEX(equipes_liste):
    """
    Répartit les équipes par UEX.
    Pour chaque équipe, si au moins un membre n'a pas 'valide' dans son UEX,
    alors l'équipe est associée à la clé UEX sans 'valide'.
    Retourne un dictionnaire où la clé est l'UEX (corrigée) et la valeur est une liste d'équipes.
    """
    uex_dict = {}
    for equipe in equipes_liste:
        if not equipe:
            continue  # Ignore les équipes vides
        # Récupère les UEX des membres de l'équipe
        uex_membres = df_etud_ref.loc[df_etud_ref['INDEX_ETUDIANT'].isin(equipe), 'UEX']
        # Si au moins un membre n'a pas 'valide', on retire 'valide' de la clé UEX
        au_moins_un_non_valide = any('valide' not in str(uex).lower() for uex in uex_membres)
        # On prend l'UEX du premier membre comme référence
        index_etudiant = equipe[0]
        uex_selection = df_etud_ref.loc[df_etud_ref['INDEX_ETUDIANT'] == index_etudiant, 'UEX']
        if isinstance(uex_selection, pd.Series) and not uex_selection.empty:
            uex = uex_selection.iloc[0]
        else:
            uex = None
        # Corrige la clé si besoin
        if au_moins_un_non_valide and uex is not None:
            uex_corrigee = str(uex).replace('valide', '').strip()
        else:
            uex_corrigee = uex
        if uex_corrigee not in uex_dict:
            uex_dict[uex_corrigee] = []
        uex_dict[uex_corrigee].append(equipe)
    return uex_dict  # Retourne le dictionnaire des équipes par UEX



def get_dict_uex():
    """
    Retourne un dictionnaire des UEX et des étudiant associés.
    Chaque clé est une UEX et la valeur est une liste d'équipes.
    Les étudiants seuls sont des équipes à un seul membre.
    """

    verif_UEX(df_etud_ref, df_etud_trouves)


    df_reconstruction = reconstruction_equipe_post_verif(df_etud_trouves, df_etud_non_trouves, df_etud_ref) # Reconstruit le tableau des équipes après vérification
    equipes_liste = df_to_liste_equipes(df_reconstruction) # Convertit le DataFrame en liste d'équipes

    equipes_corrigees = correction_equpie_liste(equipes_liste) # Corrige les équipes en supprimant les doublons et en normalisant les numéros d'équipe
    equipes_decoupees = decouper_equipes(equipes_corrigees) # Découpe les équipes en sous-équipes de taille maximale
    dictionnaire_uex = repartition_UEX(equipes_decoupees) # Répartit les équipes par UEX

    # Ajoute les étudiants seuls (ceux qui n'ont pas d'équipe) dans le dictionnaire
    for index, row in df_etud_ref.iterrows():
        index_etudiant = row['INDEX_ETUDIANT']
        if index_etudiant not in df_reconstruction['INDEX_ETUDIANT'].values:
            uex = row['UEX']
            if uex not in dictionnaire_uex:
                dictionnaire_uex[uex] = []
            dictionnaire_uex[uex].append([index_etudiant])
    
    return dictionnaire_uex


def verification_dictionnaire_uex(dictionnaire_uex):
    """
    Vérifie que le dictionnaire des UEX est cohérent.
    Chaque UEX doit avoir au moins une équipe. 
    Tous les étudiants doivent être présents une et une seule fois dans le dictionnaire. (on vérifie que tous les numéros jusqu'au maximum sont présents)
    """
    if not isinstance(dictionnaire_uex, dict):
        raise ValueError("Le dictionnaire des UEX n'est pas un dictionnaire valide.")
    
    # Vérifie que chaque UEX a au moins une équipe
    for uex, equipes in dictionnaire_uex.items():
        if not equipes:
            raise ValueError(f"L'UEX '{uex}' n'a pas d'équipes associées.")
    
    # Vérifie que tous les étudiants sont présents une et une seule fois dans le dictionnaire
    index_etudiants = set()
    for equipes in dictionnaire_uex.values():
        for equipe in equipes:
            for index_etudiant in equipe:
                if index_etudiant in index_etudiants:
                    raise ValueError(f"L'étudiant avec l'index {index_etudiant} est présent plusieurs fois dans le dictionnaire.")
                index_etudiants.add(index_etudiant)

    

if __name__ == "__main__":
    try:
        print(get_dict_uex())
    except ValueError as e:
        print(f"Erreur de vérification des UEX : {e}")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
    else:
        print("Reconstruction des équipes réussie.")