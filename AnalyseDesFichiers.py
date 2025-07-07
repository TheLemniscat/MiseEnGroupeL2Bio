import pandas as pd
import LectureConfig as lc
import unicodedata



liste_UEX = lc.get_liste_uex()


def normaliser_colonne_texte(serie):
    """
    Met en minuscule, enlève les accents et supprime les espaces superflus d'une colonne pandas de type texte.
    """
    serie = (
        serie.astype(str)
        .str.lower()
        .apply(lambda x: unicodedata.normalize('NFD', x))
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)  # remplace les espaces multiples par un seul
    )
    return serie
        




"""

Analyse des fichiers pour la gestion des étudiants

"""
# Lecture de la configuration
nom_fichier_etudiants = lc.get_name_fichier_etudiants()

# Liste des colonnes à selectionner
df_etudiants_colonnes = ["N°", "NOM", "PRENOM","UEX"]

# Chargement du fichier Excel avec les colonnes spécifiées
# Utilisation de `header=0` pour indiquer que la première ligne contient les noms

def get_df_etudiants():
    try:
        return pd.read_excel(nom_fichier_etudiants, header=0, usecols=df_etudiants_colonnes)
    except ValueError:
        raise ValueError(f"Le fichier {nom_fichier_etudiants} ne contient pas les colonnes requises : {df_etudiants_colonnes}")

def df_etudiants_clean_types(df):
    # Convertit les colonnes spécifiques en types appropriés, les nombres sont des entiers
    df_copie = df.copy()  # Crée une copie du DataFrame pour éviter de modifier l'original

    # Vérification des valeurs non convertibles pour la colonne 'N°'
    mask_num = ~df_copie['N°'].apply(lambda x: pd.api.types.is_integer(x) or (isinstance(x, float) and x.is_integer()))
    if mask_num.any():
        lignes_erreur = df_copie[mask_num]
        raise ValueError(f"Il y a un problème dans les numéros d'étudiants, du fichier {nom_fichier_etudiants}, lignes en erreur :\n{lignes_erreur}")

    df_copie['N°'] = df_copie['N°'].astype(int)  # Convertit en entier

    df_copie['UEX'] = normaliser_colonne_texte(df_copie['UEX'])  # Normalise la colonne UEX
    
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








"""

Analyse des fichiers pour la gestion des équipes

"""
# Lecture de la configuration
nom_fichier_equipe = lc.get_name_fichier_equipe()

# Liste des colonnes à selectionner
df_equipe_colonnes = ["1. UE optionnelle du S3 commune",
            	"3. Numéro d'étudiant (1)",	"4. _Nom et prénom (1)",
                "5. Numéro d'étudiant (2)",	"6. _Nom et prénom (2)",	
                "7. Numéro d'étudiant (3)",	"8. _Nom et prénom (3)",
                "9. Numéro d'étudiant (4)",	"10. _Nom et prénom (4)"
]

def get_df_equipe():    
    try:
        return pd.read_excel(nom_fichier_equipe, header=0, usecols=df_equipe_colonnes)
    except ValueError as e:
        # Vérifie quelles colonnes manquent
        try:
            cols_in_file = pd.read_excel(nom_fichier_equipe, header=0, nrows=0).columns.tolist()
        except Exception:
            raise ValueError(f"Impossible de lire les colonnes du fichier {nom_fichier_equipe}. Erreur d'origine : {e}")
        missing = [col for col in df_equipe_colonnes if col not in cols_in_file]
        if missing:
            raise ValueError(f"Le fichier {nom_fichier_equipe} ne contient pas les colonnes requises : {missing}")
        else:
            raise



def df_equipe_clean(df):
    df_copie = df.copy()
    df_copie.columns = [
        "UEX", "N°1", "NOM et prénom 1",
        "N°2", "NOM et prénom 2", "N°3", "NOM et prénom 3",
        "N°4", "NOM et prénom 4"
    ]  

    def clean_type(df):
        for i in range(1, 5):
            col_num = f'N°{i}'
            def is_valid_num(x):
                if pd.isna(x):
                    return True
                try:
                    # Vérifie que c'est un entier
                    if float(x).is_integer():
                        # Vérifie que l'entier a 8 chiffres (pour être un numéro d'étudiant valide), en ignorant les -1 utilisés pour NaN
                        if int(float(x)) == -1:
                            return True
                        return len(str(int(float(x)))) == 8
                    return False
                except Exception:
                    return False

            mask_invalid = ~df_copie[col_num].apply(is_valid_num)
            if mask_invalid.any():
                lignes_erreur = df_copie[mask_invalid]
                raise ValueError(
                    f"[PROBLÈME] Dans la colonne {col_num} du fichier {nom_fichier_equipe}, "
                    f"les numéros doivent être des entiers à 8 chiffres. Lignes en erreur :\n{lignes_erreur}\n"
                )
            df_copie[col_num] = df_copie[col_num].apply(lambda x: int(float(x)) if not pd.isna(x) else -1)
        
        return df_copie
        

    
    def supprimer_doublons(df):
        """
        Supprime les doublons dans le DataFrame en considérant les équipes comme des ensembles de numéros d'étudiants.
        """
        # On crée une colonne temporaire qui contient, pour chaque ligne, le set trié des numéros d'étudiants de l'équipe
        def equipe_key(row):
            nums = []
            for i in range(1, 5):
                n = row[f'N°{i}']
                if not pd.isna(n) and int(n) != -1:
                    nums.append(int(n))
            return tuple(sorted(nums))
        
        df_copie = df.copy()
        df_copie['EQUIPE_KEY'] = df_copie.apply(equipe_key, axis=1)
        # Les doublons sont ceux qui ont un EQUIPE_KEY déjà vu (duplicated retourne True pour tous sauf la première occurrence)
        mask_duplicated = df_copie.duplicated(subset='EQUIPE_KEY', keep='first')
        doublons = df_copie[mask_duplicated].copy()
        # On retire la colonne temporaire avant de retourner
        df_sans_doublons = df_copie.drop_duplicates(subset='EQUIPE_KEY', keep='first').reset_index(drop=True)
        df_sans_doublons = df_sans_doublons.drop(columns=['EQUIPE_KEY'])
        
        # Pour le débogage, la fonction peut retourner les doublons
        doublons = doublons.drop(columns=['EQUIPE_KEY'])
        return df_sans_doublons

    def supprimer_sousensembles(df):
        """
        Supprime les sous-ensembles stricts d'équipes dans le DataFrame.
        """
        # On crée une clé d'équipe sous forme d'ensemble pour chaque ligne
        def equipe_set(row):
            nums = set()
            for i in range(1, 5):
                n = row[f'N°{i}']
                if not pd.isna(n) and int(n) != -1:
                    nums.add(int(n))
            return nums

        df_copie = df.copy()
        df_copie['EQUIPE_SET'] = df_copie.apply(equipe_set, axis=1)

        # On marque les sous-ensembles stricts
        to_remove = set()
        equipes = df_copie['EQUIPE_SET'].tolist()
        for i, eq1 in enumerate(equipes):
            for j, eq2 in enumerate(equipes):
                if i != j and eq1 and eq1 < eq2:  # eq1 est un sous-ensemble strict de eq2
                    to_remove.add(i)

        sous_ensembles = df_copie.iloc[list(to_remove)].reset_index(drop=True)
        df_sans_sous_ensembles = df_copie.drop(df_copie.index[list(to_remove)]).reset_index(drop=True)

        # On retire la colonne temporaire avant de retourner
        df_sans_sous_ensembles = df_sans_sous_ensembles.drop(columns=['EQUIPE_SET'])
        
        # Pour le débogage, la fonction peut retourner les sous-ensembles
        sous_ensembles = sous_ensembles.drop(columns=['EQUIPE_SET'])
        return df_sans_sous_ensembles


    def verif_NOM_PRENOM(df):
        """
        Vérifie que les colonnes NOM et PRENOM sont bien formatées.
        """
        for i in range(1, 5):
            col_nom_prenom = f'NOM et prénom {i}'
            # Verifie qu'il n'y a pas de numéros dans les noms/prénoms
            mask_invalid = df[col_nom_prenom].str.contains(r'\d', na=False)
            if mask_invalid.any():
                lignes_erreur = df[mask_invalid]
                raise ValueError(
                    f"[PROBLÈME] Dans la colonne {col_nom_prenom} du fichier {nom_fichier_equipe}, "
                    f"les noms et prénoms ne doivent pas contenir de chiffres. Lignes en erreur :\n{lignes_erreur}\n"
                )

    verif_NOM_PRENOM(df_copie)  # Vérification des noms et prénoms

    df_copie = clean_type(df_copie)  # Nettoyage des types de données
    df_copie = supprimer_doublons(df_copie)
    df_copie = supprimer_sousensembles(df_copie)
    

    df_copie = df_copie.drop_duplicates(keep='first').reset_index(drop=True)



    return df_copie



def df_equipe_split_names(df):
    # Sépare les noms et prénoms en deux colonnes distinctes, est utilisé après que les colonnes soient renommées
    df_copie = df.copy()  # Crée une copie du DataFrame pour éviter de modifier l'original
    for i in range(1, 5):
        df_copie[[f'NOM {i}', f'PRENOM {i}']] = df_copie[f'NOM et prénom {i}'].str.split(' ', n=1, expand=True)
        df_copie.drop(columns=[f'NOM et prénom {i}'], inplace=True)
    
    df_copie = df_copie.drop_duplicates(keep='first').reset_index(drop=True)  # Supprime les doublons
    
    return df_copie


def df_equipe_add_column_index(df):
    df_copie = df.copy()  # Crée une copie du DataFrame pour éviter de modifier l'original
    # Ajoute une colonne 'NUMERO EQUIPE' qui est un index de 1 à n
    df_copie['NUMERO EQUIPE'] = range(1, len(df_copie) + 1)
    return df_copie




"""

Comparaison des DataFrames etudiants et équipes pour trouver les étudiants mal renseignés

"""


def df_equipe_normalisation(df):
    df_copie = df.copy()
    df_copie = df_equipe_clean(df_copie)
    df_copie = df_equipe_add_column_index(df_copie)

    liste_etudiants = []
    for i in range(1, 5):
        cols = [f'N°{i}', f'NOM et prénom {i}', 'NUMERO EQUIPE', 'UEX']
        df_temp = df_copie[cols].dropna(subset=[f'N°{i}'])
        df_temp = df_temp.rename(columns={
            f'N°{i}': 'N°',
            f'NOM et prénom {i}': 'NOM_PRENOM'
        })
        liste_etudiants.append(df_temp[['N°', 'NOM_PRENOM', 'NUMERO EQUIPE', 'UEX']])

    df_out = pd.concat(liste_etudiants, ignore_index=True)
    df_out['NOM_PRENOM'] = normaliser_colonne_texte(df_out['NOM_PRENOM'])
    
    return df_out[['N°', 'NOM_PRENOM', 'NUMERO EQUIPE', 'UEX']]


def df_etudiants_normalisation(df_etudiants):
    df_etudiants = df_etudiants_clean_types(df_etudiants)
    df_out = df_etudiants.copy()
    df_out['NOM'] = normaliser_colonne_texte(df_out['NOM'])
    df_out['PRENOM'] = normaliser_colonne_texte(df_out['PRENOM'])
    return df_out


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


def correction_manuelle():
    df_etudiants = get_df_etudiants()
    df_etudiants = df_etudiants_add_column_index(df_etudiants)

    df_equipe = get_df_equipe()
    
    df_etud_norm = df_etudiants_normalisation(df_etudiants)
    df_equipe_norm = df_equipe_normalisation(df_equipe)

    trouves, non_trouves = df_verification_existance(df_etud_norm, df_equipe_norm)
    non_trouves = suggere_etudiant_par_nom(non_trouves, df_etud_norm)
    noms_non_concord = noms_non_concordants(df_etud_norm, df_equipe_norm)

    # Écriture dans un fichier Excel avec quatre feuilles
    with pd.ExcelWriter("correction_manuelle_resultat.xlsx") as writer:
        df_etud_norm.to_excel(writer, sheet_name="etudiants", index=False)
        trouves.to_excel(writer, sheet_name="trouves", index=False)
        non_trouves.to_excel(writer, sheet_name="non_trouves", index=False)
        noms_non_concord.to_excel(writer, sheet_name="noms_non_concordants", index=False)
    


    


if __name__ == "__main__":
    correction_manuelle()
    print("Analyse terminée, les résultats sont dans le fichier 'correction_manuelle_resultat.xlsx'.")
