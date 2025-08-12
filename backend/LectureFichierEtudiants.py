import pandas as pd
from backend import MyTools as mytools

# Liste des colonnes à selectionner
df_etudiants_colonnes = ["N°", "NOM", "PRENOM","UEX"]

# Chargement du fichier Excel avec les colonnes spécifiées
# Utilisation de `header=0` pour indiquer que la première ligne contient les noms

def get_df_etudiants(file_path):
    try:
        return pd.read_excel(file_path, header=0, usecols=df_etudiants_colonnes)
    except ValueError:
        raise ValueError(f"Le fichier {file_path} ne contient pas les colonnes requises : {df_etudiants_colonnes}")

def df_etudiants_clean(df, liste_UEX):
    # Convertit les colonnes spécifiques en types appropriés, les nombres sont des entiers
    df_copie = df.copy()  # Crée une copie du DataFrame pour éviter de modifier l'original

    # Vérification des valeurs non convertibles pour la colonne 'N°'
    mask_num = ~df_copie['N°'].apply(lambda x: pd.api.types.is_integer(x) or (isinstance(x, float) and x.is_integer()))
    if mask_num.any():
        lignes_erreur = df_copie[mask_num]
        raise ValueError(f"Il y a un problème dans les numéros d'étudiants, du fichier des étudiants, lignes en erreur :\n{lignes_erreur}")

    df_copie['N°'] = df_copie['N°'].astype(int)  # Convertit en entier

    df_copie['UEX'] = mytools.normaliser_colonne_texte(df_copie['UEX'])  # Normalise la colonne UEX
    
    # VALIDE : True si la colonne UEX contient une des valeurs de liste_UEX, False sinon
    def is_valid_uex(x):
        if pd.isna(x):
            return False
        x = str(x).strip()
        return x not in liste_UEX

    df_copie['VALIDE'] = df_copie['UEX'].apply(is_valid_uex)
    return df_copie



def df_etudiants_add_column_index(df):
    df_copie = df.copy()
    df_copie['INDEX_ETUDIANT'] = range(1, len(df_copie) + 1)
    return df_copie


def df_etudiants_normalisation(df_etudiants, liste_UEX):
    df_etudiants = df_etudiants_clean(df_etudiants, liste_UEX)
    df_out = df_etudiants.copy()
    df_out['NOM'] = mytools.normaliser_colonne_texte(df_out['NOM'])
    df_out['PRENOM'] = mytools.normaliser_colonne_texte(df_out['PRENOM'])
    return df_out