import pandas as pd
import unicodedata

def normaliser_colonne_texte(serie):
    """
    Met en minuscule, enlève les accents et supprime les espaces superflus d'une colonne pandas de type texte.
    Ne modifie pas les valeurs NaN.
    """
    # On traite uniquement les valeurs non nulles
    mask_notna = serie.notna()
    serie_out = serie.copy()
    serie_out[mask_notna] = (
        serie_out[mask_notna].astype(str)
        .str.lower()
        .apply(lambda x: unicodedata.normalize('NFD', x))
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)
    )
    return serie_out