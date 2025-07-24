import unicodedata

with open('Configuration.txt', 'r') as f:
    lignes = f.readlines()  # Retourne une liste


def get_nombre_groupes():
    for i, ligne in enumerate(lignes):
        if "Nombre de groupes" in ligne:
            position = ligne.find(':')
            if position == -1:
                raise ValueError("La ligne contenant 'Nombre de groupes' doit contenir un ':' pour séparer la valeur")
            valeur = ligne[position+1:].strip()
            try:
                return int(valeur)
            except ValueError:
                raise ValueError("La valeur après ':' dans la ligne 'Nombre de groupes' doit être un entier") from None
    raise ValueError("Aucune ligne contenant 'Nombre de groupes' trouvée dans le fichier Configuration.txt")



def get_taille_groupes():
    for i, ligne in enumerate(lignes):
        if "Taille des groupes" in ligne:
            position = ligne.find(':')
            if position == -1:
                raise ValueError("La ligne 'Taille des groupes' doit contenir un ':' pour séparer la valeur")
            valeur = ligne[position+1:].strip()
            try:
                return int(valeur)
            except ValueError:
                raise ValueError("La valeur après ':' dans la ligne 'Taille des groupes' doit être un entier") from None
    raise ValueError("Aucune ligne contenant 'Taille des groupes' trouvée dans le fichier Configuration.txt")

def get_taille_max_groupes():
    for i, ligne in enumerate(lignes):
        if "Taille maximale des groupes" in ligne:
            position = ligne.find(':')
            if position == -1:
                raise ValueError("La ligne 'Taille maximale des groupes' doit contenir un ':' pour séparer la valeur")
            valeur = ligne[position+1:].strip()
            try:
                return int(valeur)
            except ValueError:
                raise ValueError("La valeur après ':' dans la ligne 'Taille maximale des groupes' doit être un entier") from None



def get_nombre_uex():
    for i, ligne in enumerate(lignes):
        if "Nombre d'UEX" in ligne:
            position = ligne.find(':')
            if position == -1:
                raise ValueError("La ligne 'Nombre d'UEX' doit contenir un ':' pour séparer la valeur")
            valeur = ligne[position+1:].strip()
            try:
                return int(valeur)
            except ValueError:
                raise ValueError("La valeur après ':' dans la ligne 'Nombre d'UEX' doit être un entier") from None
    raise ValueError("Aucune ligne contenant 'Nombre d'UEX' trouvée dans le fichier Configuration.txt")

def get_liste_uex():
    for i, ligne in enumerate(lignes):
        if "Liste des UEX" in ligne:
            position = ligne.find(':')
            if position == -1:
                raise ValueError("La ligne 'Liste des UEX' doit contenir un ':' pour séparer la valeur")
            valeur = ligne[position+1:].strip()
            if not valeur:
                raise ValueError("La valeur après ':' dans la ligne 'Liste des UEX' ne peut pas être vide")
            liste_uex = [uex.strip() for uex in valeur.split(',')]
            liste_uex = [unicodedata
             .normalize('NFD', str(uex))
             .encode('ascii', errors='ignore')
             .decode('utf-8')
             .strip()
             .lower()
             .replace('  ', ' ') for uex in liste_uex]
            return liste_uex
    
    raise ValueError("Aucune ligne contenant 'Liste des UEX' trouvée dans le fichier Configuration.txt")


if __name__ == "__main__":
    try:
        print("Nombre de groupes :", get_nombre_groupes())
        print("Taille des groupes :", get_taille_groupes())
        print("Nombre d'UEX :", get_nombre_uex())
        print("Liste des UEX :", get_liste_uex())
    except ValueError as e:
        print(f"Erreur : {e}")