import unicodedata

with open('Configuration.txt', 'r') as f:
    lignes = f.readlines()  # Retourne une liste


# Attention de ne pas changer les ligne des lignes

def get_name_fichier_etudiants():
    position = lignes[0].find(':')  # Trouve la position du caractère ':'
    if position == -1:
        raise ValueError("La première ligne du fichier Configuration.txt doit contenir un ':' pour séparer le nom du fichier étudiant")
    
    position += 1  # Pour ne pas inclure le caractère ':'
    txt = lignes[0][position:-1]  # Le nom du fichier étudiant
    
    # Vérifie les conditions du nom du fichier
    if ".xlsx" not in txt:
        raise NameError("La pemière ligne du fichier Configuration.txt doit contenir le nom du fichier étudiant")
    if txt.startswith(' '):
        txt = txt[1:]
    if txt.endswith(' '):
        txt = txt[:-1]
    return txt



def get_name_fichier_equipe():
    position = lignes[1].find(':')  # Trouve la position du caractère ':'
    if position == -1:
        raise ValueError("La deuxième ligne du fichier Configuration.txt doit contenir un ':' pour séparer le nom du fichier équipe")
    
    position += 1  # Pour ne pas inclure le caractère ':'
    txt = lignes[1][position:-1]  # Le nom du fichier équipe
    
    # Vérifie les conditions du nom du fichier
    if ".xlsx" not in txt:
        raise NameError("La deuxième ligne du fichier Configuration.txt doit contenir le nom du fichier équipe")
    if txt.startswith(' '):
        txt = txt[1:]
    if txt.endswith(' '):
        txt = txt[:-1]
    return txt



def get_nombre_groupes():
    position = lignes[2].find(':')  # Trouve la position du caractère ':'
    if position == -1:
        raise ValueError("La troisième ligne du fichier Configuration.txt doit contenir un ':' pour séparer le nombre de groupe")
    
    position += 1  # Pour ne pas inclure le caractère ':'
    nombre = lignes[2][position:-1]  # Le nombre de groupe

    # Vérifie les conditions du nombre de groupe
    if nombre.startswith(' '):
        nombre = nombre[1:]
    if nombre.endswith(' '):
        nombre = nombre[:-1]

    try:
        return int(nombre)
    except ValueError:
        raise ValueError("La troisième ligne du fichier Configuration.txt doit contenir un nombre entier pour le nombre de groupe") from None



def get_taille_groupes():
    position = lignes[3].find(':')  # Trouve la position du caractère ':'
    if position == -1:
        raise ValueError("La quatrième ligne du fichier Configuration.txt doit contenir un ':' pour séparer la taille des groupes")
    
    position += 1  # Pour ne pas inclure le caractère ':'
    taille = lignes[3][position:-1]  # La taille des groupes

    # Vérifie les conditions de la taille des groupes
    if taille.startswith(' '):
        taille = taille[1:]
    if taille.endswith(' '):
        taille = taille[:-1]

    try:
        return int(taille)
    except ValueError:
        raise ValueError("La quatrième ligne du fichier Configuration.txt doit contenir un nombre entier pour la taille des groupes") from None



def get_nombre_uex():
    position = lignes[4].find(':')  # Trouve la position du caractère ':'
    if position == -1:
        raise ValueError("La cinquième ligne du fichier Configuration.txt doit contenir un ':' pour séparer le nombre d'UEX")
    
    position += 1  # Pour ne pas inclure le caractère ':'
    nombre = lignes[4][position:-1]  # Le nombre d'UEX

    # Vérifie les conditions du nombre d'UEX
    if nombre.startswith(' '):
        nombre = nombre[1:]
    if nombre.endswith(' '):
        nombre = nombre[:-1]

    try:
        return int(nombre)
    except ValueError:
        raise ValueError("La cinquième ligne du fichier Configuration.txt doit contenir un nombre entier pour le nombre d'UEX") from None

def get_name_fichier_verifie():
    position = lignes[5].find(':')  # Trouve la position du caractère ':'
    if position == -1:
        raise ValueError("La sixième ligne du fichier Configuration.txt doit contenir un ':' pour séparer le nom du fichier étudiant")
    
    position += 1  # Pour ne pas inclure le caractère ':'
    txt = lignes[5][position:-1]  # Le nom du fichier étudiant

    # Vérifie les conditions du nom du fichier
    if ".xlsx" not in txt:
        raise NameError("La sixième ligne du fichier Configuration.txt doit contenir le nom du fichier après vérification")
    if txt.startswith(' '):
        txt = txt[1:]
    if txt.endswith(' '):
        txt = txt[:-1]
    return txt

def get_liste_uex():
    position = lignes[6].find(':')  # Trouve la position du caractère ':'
    if position == -1:
        raise ValueError("La septième ligne du fichier Configuration.txt doit contenir un ':' pour séparer la liste des UEX")
    
    position += 1  # Pour ne pas inclure le caractère ':'
    liste_uex = lignes[6][position:-1]  # La liste des UEX

    # Vérifie les conditions de la liste des UEX
    if liste_uex.startswith(' '):
        liste_uex = liste_uex[1:]
    if liste_uex.endswith(' '):
        liste_uex = liste_uex[:-1]

    liste_uex = [uex.strip() for uex in liste_uex.split(',')]

    liste_uex = [unicodedata
             .normalize('NFD', str(uex))
             .encode('ascii', errors='ignore')
             .decode('utf-8')
             .strip()
             .lower()
             .replace('  ', ' ') for uex in liste_uex]
    
    return liste_uex



def get_name_mariage():
    position = lignes[7].find(':')  # Trouve la position du caractère ':'
    if position == -1:
        raise ValueError("La huitième ligne du fichier Configuration.txt doit contenir un ':' pour séparer le nom du fichier mariage")
    
    position += 1  # Pour ne pas inclure le caractère ':'
    txt = lignes[7][position:-1]  # Le nom du fichier mariage

    # Vérifie les conditions du nom du fichier mariage
    if ".xlsx" not in txt:
        raise NameError("La huitième ligne du fichier Configuration.txt doit contenir le nom du fichier mariage")
    if txt.startswith(' '):
        txt = txt[1:]
    if txt.endswith(' '):
        txt = txt[:-1]
    return txt



if __name__ == "__main__":
    
    # Test des fonctions
    if True:
        print("Nom du fichier étudiant :", get_name_fichier_etudiants())
        print("Nom du fichier équipe :", get_name_fichier_equipe())
        print("Nombre de groupe :", get_nombre_groupes())
        print("Taille des groupes :", get_taille_groupes())
        print("Nombre d'UEX :", get_nombre_uex())
        print("Nom du fichier vérifié :", get_name_fichier_verifie())
        print("Liste des UEX :", get_liste_uex())