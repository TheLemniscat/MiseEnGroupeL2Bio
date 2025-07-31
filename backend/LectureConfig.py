import unicodedata
import pandas as pd

def get_df_config(file_path):
    """
    Lit le fichier de configuration des mariages et retourne un DataFrame.
    """
    try:
        df_config = pd.read_excel(file_path, sheet_name=2)
        # Enleve les espaces en début et fin de chaîne dans toutes les colonnes et les entètes
        for col in df_config.columns:
            if df_config[col].dtype == 'object':
                df_config[col] = df_config[col].str.strip()
        df_config.columns = df_config.columns.str.strip()
        return df_config
    except Exception as e:
        raise ValueError(f"Le fichier {file_path} ne peut pas être lu. Erreur : {e}") from e


def charger_config_dataframe(df):
    """
    Charge la configuration à partir d'un DataFrame.
    Les colonnes attendues sont :
    - 'Nombre de groupes'
    - 'Taille des groupes'
    - 'Taille maximale des groupes' (optionnelle)
    - 'Nombre d\'UEX'
    - 'Liste des UEX'
    
    Le DataFrame doit contenir exactement une ligne de données.
    """
    if df.shape[0] != 1:
        raise ValueError("Le DataFrame de configuration doit contenir exactement une ligne")
    config = df.iloc[0].to_dict()
    return config

def get_nombre_groupes(file_path):
    """
    Récupère le nombre de groupes depuis le fichier de configuration.
    
    Args:
        file_path (str): Chemin vers le fichier de configuration

    Returns:
        int: Le nombre de groupes
    """
    config_df = get_df_config(file_path)
    config = charger_config_dataframe(config_df)
    
    try:
        return int(config["Nombre de groupes"])
    except Exception:
        raise ValueError("La valeur de 'Nombre de groupes' doit être un entier")

def get_taille_groupes(file_path):
    """
    Récupère la taille des groupes depuis le fichier de configuration.

    Args:
        file_path (str): Chemin vers le fichier de configuration

    Returns:
        int: La taille des groupes
    """
    config_df = get_df_config(file_path)
    config = charger_config_dataframe(config_df)
    try:
        return int(config["Taille des groupes"])
    except Exception:
        raise ValueError("La valeur de 'Taille des groupes' doit être un entier")

def get_taille_max_groupes(file_path):
    """
    Récupère la taille maximale des groupes depuis le fichier de configuration.

    Args:
        file_path (str): Chemin vers le fichier de configuration

    Returns:
        int or None: La taille maximale des groupes, ou None si non définie
    """
    config_df = get_df_config(file_path)
    config = charger_config_dataframe(config_df)
    try:
        return int(config["Taille maximale des groupes"])
    except KeyError:
        return None
    except Exception:
        raise ValueError("La valeur de 'Taille maximale des groupes' doit être un entier")


def get_nombre_uex(file_path):
    """
    Récupère le nombre d'UEX depuis le fichier de configuration.

    Args:
        file_path (str): Chemin vers le fichier de configuration

    Returns:
        int: Le nombre d'UEX
    """
    config_df = get_df_config(file_path)
    config = charger_config_dataframe(config_df)
    try:
        return int(config["Nombre d'UEX"])
    except Exception:
        raise ValueError("La valeur de 'Nombre d'UEX' doit être un entier")


def get_liste_uex(file_path):
    """
    Récupère la liste des UEX depuis le fichier de configuration.
    
    Args:
        file_path (str): Chemin vers le fichier de configuration

    Returns:
        list: Liste des UEX normalisées (en minuscules, sans accents)
    """
    config_df = get_df_config(file_path)
    config = charger_config_dataframe(config_df)
    valeur = config["Liste des UEX"]
    if not valeur:
        raise ValueError("La valeur de 'Liste des UEX' ne peut pas être vide")
    if isinstance(valeur, str):
        liste_uex = [uex.strip() for uex in valeur.split(',')]
    elif isinstance(valeur, list):
        liste_uex = valeur
    else:
        raise ValueError("Le format de 'Liste des UEX' n'est pas reconnu")
    liste_uex = [unicodedata
            .normalize('NFD', str(uex))
            .encode('ascii', errors='ignore')
            .decode('utf-8')
            .strip()
            .lower()
            .replace('  ', ' ') for uex in liste_uex]
    return liste_uex


if __name__ == "__main__":
    try:
        # Exemple de DataFrame de configuration pour les tests
        import pandas as pd

        file_path = '/home/thelemniscat/Documents/Projets/MiseEnGroupeL2Bio/data/MariageMiseEnGroupe.xlsx'

        
        print("=== Test avec DataFrame de configuration ===")
        print("Nombre de groupes :", get_nombre_groupes(file_path))
        print("Taille des groupes :", get_taille_groupes(file_path))
        print("Taille maximale des groupes :", get_taille_max_groupes(file_path))
        print("Nombre d'UEX :", get_nombre_uex(file_path))
        print("Liste des UEX :", get_liste_uex(file_path))
    except ValueError as e:
        print(f"Erreur : {e}")