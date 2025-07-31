import pandas as pd
import LectureConfig as lc
import unicodedata

import LectureFichierEtudiants as lfe
import LectureFichierEquipes as lft

from Tools import normaliser_colonne_texte


"""

Comparaison des DataFrames etudiants et équipes pour trouver les étudiants mal renseignés

"""

def df_verification_existance(df_etudiants, df_equipe):
    # On ne normalise plus les noms/prénoms, on compare uniquement sur N°
    df_etud = df_etudiants.copy()
    df_equip = df_equipe.copy()

    # On ignore les numéros d'étudiant à -1 (issus de NaN)
    df_equip = df_equip[df_equip['N°'] != -1]

    merged = df_equip.merge(
        df_etud[['N°', 'INDEX_ETUDIANT']],
        on=['N°'],
        how='left',
        indicator=True
    )

    trouves = merged[merged['_merge'] == 'both'].copy()
    non_trouves = merged[merged['_merge'] == 'left_only'].copy()

    cols = list(df_equipe.columns) + ['INDEX_ETUDIANT']
    trouves = trouves[cols]
    non_trouves = non_trouves[cols]

    return trouves, non_trouves
    




def noms_non_concordants(df_etudiants, df_equipe):
    # Crée une colonne NOM_PRENOM dans df_etudiants pour la comparaison
    df_etud = df_etudiants.copy()
    df_equip = df_equipe.copy().drop('UEX', axis=1, errors='ignore')

    df_equip['NOM_PRENOM_EQUIPE'] = normaliser_colonne_texte(df_equip['NOM_PRENOM'])
    df_etud['NOM_PRENOM_ETUD'] = normaliser_colonne_texte(df_etud['NOM'] + ' ' + df_etud['PRENOM'])
    df_etud['PRENOM_NOM_ETUD'] = normaliser_colonne_texte(df_etud['PRENOM'] + ' ' + df_etud['NOM'])

    merged = df_equip.merge(
        df_etud[['N°', 'NOM_PRENOM_ETUD', 'PRENOM_NOM_ETUD', 'INDEX_ETUDIANT']],
        on='N°',
        how='left',
        indicator=True
    )

    # On sélectionne les cas où le numéro existe mais le nom/prénom ne correspond à aucun ordre
    noms_non_concord = merged[
        (merged['_merge'] == 'both') &
        (~(
            (merged['NOM_PRENOM_EQUIPE'] == merged['NOM_PRENOM_ETUD']) |
            (merged['NOM_PRENOM_EQUIPE'] == merged['PRENOM_NOM_ETUD'])
        ))
    ].copy()

    return noms_non_concord[['N°', 'NOM_PRENOM_EQUIPE', 'NOM_PRENOM_ETUD', 'NUMERO EQUIPE', 'INDEX_ETUDIANT']]
    

def suggere_etudiant_par_nom(non_trouves, df_etud_norm):
    # On prépare une colonne NOM_PRENOM normalisée dans les deux DataFrames
    non_trouves = non_trouves.copy()
    df_etud_norm = df_etud_norm.copy()
    non_trouves['NOM_PRENOM'] = normaliser_colonne_texte(non_trouves['NOM_PRENOM'])
    df_etud_norm['NOM_PRENOM'] = normaliser_colonne_texte(df_etud_norm['NOM'] + ' ' + df_etud_norm['PRENOM'])
    df_etud_norm['PRENOM_NOM'] = normaliser_colonne_texte(df_etud_norm['PRENOM'] + ' ' + df_etud_norm['NOM'])

    suggestions = []
    for nom_prenom in non_trouves['NOM_PRENOM']:
        # Cherche d'abord NOM PRENOM
        matches = df_etud_norm[df_etud_norm['NOM_PRENOM'] == nom_prenom]
        # Sinon cherche PRENOM NOM
        if matches.empty:
            matches = df_etud_norm[df_etud_norm['PRENOM_NOM'] == nom_prenom]
        if not matches.empty:
            suggestions.append(matches.iloc[0]['INDEX_ETUDIANT'])
        else:
            suggestions.append(None)
    non_trouves['INDEX_ETUDIANT'] = suggestions
    return non_trouves


def correction_manuelle(df_etudiants, df_equipes, liste_UEX):
    """
    Génère le fichier de correction manuelle en utilisant les DataFrames fournis.
    Args:
        df_etudiants: DataFrame des étudiants déjà nettoyé
        df_equipes: DataFrame des équipes déjà nettoyé
    """
    df_etudiants = lfe.df_etudiants_add_column_index(df_etudiants)

    # Utiliser le DataFrame fourni au lieu de relire le fichier
    # df_equipes = lft.get_df_equipes(lc.get_name_fichier_equipe())  # ← Ligne problématique commentée
    
    df_etud_norm = lfe.df_etudiants_normalisation(df_etudiants, liste_UEX)
    df_equipe_norm = lft.df_equipes_normalisation(df_equipes)

    trouves, non_trouves = df_verification_existance(df_etud_norm, df_equipe_norm)
    non_trouves = suggere_etudiant_par_nom(non_trouves, df_etud_norm)
    noms_non_concord = noms_non_concordants(df_etud_norm, df_equipe_norm)

    # Écriture dans un fichier Excel avec quatre feuilles
    with pd.ExcelWriter("correction_manuelle_resultat.xlsx") as writer:
        df_etud_norm.to_excel(writer, sheet_name="etudiants", index=False)
        trouves.to_excel(writer, sheet_name="trouves", index=False)
        non_trouves.to_excel(writer, sheet_name="à modifier", index=False)
        noms_non_concord.to_excel(writer, sheet_name="noms_non_concordants", index=False)
    

