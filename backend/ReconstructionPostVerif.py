import LectureConfig as lc
import pandas as pd

from Tools import normaliser_colonne_texte
from collections import deque

import Classes



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
    Retourne une liste d'objets Equipe, chaque équipe contenant des objets Etudiant.
    """
    equipes_liste = []
    if 'NUMERO EQUIPE' not in df.columns:
        raise ValueError("La colonne 'NUMERO EQUIPE' est absente du DataFrame.")
    groupes = df.groupby('NUMERO EQUIPE')
    for _, groupe in groupes:
        index_etudiants = groupe['INDEX_ETUDIANT'].dropna().astype(int).tolist()
        if index_etudiants:
            numero_equipe = groupe['NUMERO EQUIPE'].iloc[0]
            try:
                uex = groupe['UEX'].iloc[0]
            except KeyError:
                raise KeyError("La colonne 'UEX' est absente du DataFrame.")
            
            # Créer les objets Etudiant pour cette équipe
            membres = []
            for index_etudiant in index_etudiants:
                etudiant_row = df_etud_ref[df_etud_ref['INDEX_ETUDIANT'] == index_etudiant]
                if not etudiant_row.empty:
                    etudiant_data = etudiant_row.iloc[0]
                    nom = str(etudiant_data['NOM']).strip()
                    prenom = str(etudiant_data['PRENOM']).strip()
                    numero = etudiant_data['N°']
                    valide = etudiant_data['VALIDE']
                    etudiant = Classes.Etudiant(nom, prenom, numero, uex, valide, index_etudiant)
                    membres.append(etudiant)
            
            if membres:  # Seulement si on a trouvé des étudiants
                equipe = Classes.Equipe(numero_equipe, membres, uex)
                equipes_liste.append(equipe)
    
    return equipes_liste


"""
Gère les étudiants qui on fait des chaines d'équipe.
"""
def get_chaines_equipes(equipes_liste):
    """
    Détecte les chaînes d'équipes : si deux équipes partagent au moins un membre, elles sont fusionnées.
    Retourne une liste d'objets Equipe fusionnés.
    """
    # Convertit chaque équipe en set d'INDEX_ETUDIANT pour faciliter les opérations d'union/intersection
    equipes_sets = []
    equipes_originales = []
    
    for equipe in equipes_liste:
        # Récupère les INDEX_ETUDIANT des membres de l'équipe
        index_etudiants = set()
        for etudiant in equipe.get_membres():
            index_etudiants.add(etudiant.get_index_etud()) 
        
        equipes_sets.append(index_etudiants)
        equipes_originales.append(equipe)
    
    chaines = []
    equipes_utilisees = set()

    for i, current_set in enumerate(equipes_sets):
        if i in equipes_utilisees:
            continue
            
        equipes_fusionnees = [equipes_originales[i]]
        equipes_utilisees.add(i)
        current_union = current_set.copy()
        
        merged = True
        while merged:
            merged = False
            for j, other_set in enumerate(equipes_sets):
                if j in equipes_utilisees:
                    continue
                if current_union & other_set:  # Intersection non vide
                    current_union = current_union | other_set
                    equipes_fusionnees.append(equipes_originales[j])
                    equipes_utilisees.add(j)
                    merged = True
        
        if len(equipes_fusionnees) > 1:
            # Fusionner toutes les équipes en une seule
            tous_membres = []
            uex_equipe = equipes_fusionnees[0].get_uex()  # Prend l'UEX de la première équipe
            numero_equipe = equipes_fusionnees[0].get_numero()  # Prend le numéro de la première équipe
            
            for equipe in equipes_fusionnees:
                tous_membres.extend(equipe.get_membres())
            
            # Supprime les doublons basés sur le numéro d'étudiant
            membres_uniques = []
            numeros_vus = set()
            for membre in tous_membres:
                if membre.get_numero_etudiant() not in numeros_vus:
                    membres_uniques.append(membre)
                    numeros_vus.add(membre.get_numero_etudiant())
            
            equipe_fusionnee = Classes.Equipe(numero_equipe, membres_uniques, uex_equipe)

            chaines.append(equipe_fusionnee)
    
    return chaines
    

def decouper_equipes(equipes_liste):
    """
    Découpe les équipes en sous-équipes de taille maximale.
    Chaque sous-équipe contient au maximum 5 étudiants.
    """
    taille_max = 5 # Taille maximale des équipes
    equipes_decoupees = []
    
    for equipe in equipes_liste:
        membres = equipe.get_membres()
        if equipe.length() <= taille_max:
            equipes_decoupees.append(equipe)
        else:
            # Découpe l'équipe en sous-équipes de taille aussi équilibrée que possible
            n = equipe.length()
            # Calcule le nombre de sous-équipes nécessaires
            nb_equipes = (n + taille_max - 1) // taille_max
            # Calcule la taille de chaque sous-équipe (équilibrée)
            base_size = n // nb_equipes
            reste = n % nb_equipes
            start = 0
            
            for i in range(nb_equipes):
                size = base_size + (1 if i < reste else 0)
                sous_membres = membres[start:start+size]
                # Crée une nouvelle équipe avec un numéro unique (on utilise un hash pour avoir un int)
                nouveau_numero = int(f"{equipe.get_numero()}00{i+1}")
                sous_equipe = Classes.Equipe(nouveau_numero, sous_membres, equipe.get_uex())
                equipes_decoupees.append(sous_equipe)
                start += size
            
    return equipes_decoupees

def correction_equpie_liste(equipes_liste):
    """
    Corrige les équipes en supprimant les doublons et en normalisant les numéros d'équipe.
    Retourne une liste d'objets Equipe corrigés.
    """
    # Supprime les équipes en double basées sur les numéros d'étudiants
    equipes_uniques = []
    equipes_vues = set()
    
    for equipe in equipes_liste:
        # Crée une signature de l'équipe basée sur les numéros d'étudiants
        numeros_etudiants = tuple(sorted(etudiant.get_numero_etudiant() for etudiant in equipe.get_membres()))
        if numeros_etudiants not in equipes_vues:
            equipes_vues.add(numeros_etudiants)
            equipes_uniques.append(equipe)
    
    # Détecte et fusionne les chaînes d'équipes
    chaines_equipes = get_chaines_equipes(equipes_uniques)
    
    # Supprime les équipes qui ont été fusionnées dans les chaînes
    equipes_finales = []
    equipes_dans_chaines = set()
    
    # Marque les équipes qui sont dans des chaînes
    for chaine in chaines_equipes:
        for membre in chaine.get_membres():
            equipes_dans_chaines.add(membre.get_numero_etudiant())
    
    # Ajoute les équipes qui ne sont pas dans des chaînes
    for equipe in equipes_uniques:
        equipe_dans_chaine = any(etudiant.get_numero_etudiant() in equipes_dans_chaines 
                                for etudiant in equipe.get_membres())
        if not equipe_dans_chaine:
            equipes_finales.append(equipe)
    
    # Ajoute les chaînes fusionnées
    equipes_finales.extend(chaines_equipes)
    
    # Supprime les équipes vides ou avec un seul membre
    equipes_finales = [equipe for equipe in equipes_finales if equipe.length() > 1]

    return equipes_finales


def correction_equipe_liste_UEX(equipes_liste):
    """
    Si tous les membres d'une équipe ont 'valide' dans leur UEX, on met valide à True.
    """
    equipes_corrigees = []
    for equipe in equipes_liste:
        membres = equipe.get_membres()
        uex = equipe.get_uex()
        
        # Vérifie si tous les membres sont valides
        if all(membre.get_valide() for membre in membres):
            valide = True
        else:
            valide = False
        
        equipe_corrigee = Classes.Equipe(equipe.get_numero(), membres, uex, valide)
        equipes_corrigees.append(equipe_corrigee)
    
    return equipes_corrigees



def get_liste_equipes():
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
    equipes_corrigees_uex = correction_equipe_liste_UEX(equipes_decoupees) # Corrige les équipes en fonction de la validité des membres

    return equipes_corrigees_uex

def get_etudiant_not_in_equipes(equipes_liste):
    """
    Retourne une liste d'objets Etudiant qui ne sont pas dans les équipes.
    """


    index_etudiants_dans_equipes = set()
    for equipe in equipes_liste:
        for membre in equipe.get_membres():
            index_etudiants_dans_equipes.add(membre.get_index_etud())
    
    etudiants_non_dans_equipes_df = df_etud_ref[~df_etud_ref['INDEX_ETUDIANT'].isin(index_etudiants_dans_equipes)]
    
    etudiants_non_dans_equipes = []
    for _, row in etudiants_non_dans_equipes_df.iterrows():
        nom = str(row['NOM']).strip()
        prenom = str(row['PRENOM']).strip()
        numero = row['N°']
        uex = row['UEX']
        valide = row['VALIDE']
        index_etudiant = row['INDEX_ETUDIANT']
        etudiant = Classes.Etudiant(nom, prenom, numero, uex, valide, index_etudiant)
        etudiants_non_dans_equipes.append(etudiant)
    
    return etudiants_non_dans_equipes
    

if __name__ == "__main__":
    
    try:
        get_liste_equipes()

    except ValueError as e:
        print(f"Erreur de vérification des UEX : {e}")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
    else:
        print("Reconstruction des équipes réussie.")