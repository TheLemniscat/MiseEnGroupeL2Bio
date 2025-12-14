from backend import Classes
import pandas as pd


def liste_groupes_to_liste_EtudiantEnPlace(liste_groupes):
    liste_etudiants_en_place = []
    for groupe in liste_groupes:
        for equipe in groupe.get_liste_equipes():
            for etudiant in equipe.get_membres():
                etudiant_en_place = Classes.EtudiantEnPlace(
                    etudiant.get_nom(),
                    etudiant.get_prenom(),
                    etudiant.get_numero_etudiant(),
                    etudiant.get_uex(),
                    etudiant.get_valide(),
                    etudiant.get_index_etud(),
                    groupe.get_numero(),
                    equipe.get_numero()
                )
                liste_etudiants_en_place.append(etudiant_en_place)
   
    return liste_etudiants_en_place

def trie_liste_EtudiantEnPlace(liste_etudiants_en_place):
    return sorted(liste_etudiants_en_place, key= lambda etudiant: etudiant.get_index_etud())


def liste_EtudiantEnPlace_to_df(liste_etudiants_en_place, liste_mariages):
    data = {
        'Index': [etudiant.get_index_etud() for etudiant in liste_etudiants_en_place],
        'Numéro étudiant': [etudiant.get_numero_etudiant() for etudiant in liste_etudiants_en_place],
        'Nom': [etudiant.get_nom() for etudiant in liste_etudiants_en_place],
        'Prénom': [etudiant.get_prenom() for etudiant in liste_etudiants_en_place],
        'UEX': [etudiant.get_uex() for etudiant in liste_etudiants_en_place],
        'Valide': [etudiant.get_valide() for etudiant in liste_etudiants_en_place],
        'Groupe': [etudiant.get_groupe() for etudiant in liste_etudiants_en_place],
        'Équipe': [etudiant.get_equipe() if etudiant.get_equipe() > 0 else pd.NA for etudiant in liste_etudiants_en_place],
        'Mariage': [determiner_mariage_etudiant(etudiant,liste_mariages) for etudiant in liste_etudiants_en_place]
    }
    return pd.DataFrame(data)




def liste_mariages_to_df(liste_mariages):
    premier = [mariage.get_groupes_liste()[0].get_numero() for mariage in liste_mariages]
    second = [mariage.get_groupes_liste()[1].get_numero() if len(mariage.get_groupes_liste()) > 1 else pd.NA for mariage in liste_mariages]
    troisieme = [mariage.get_groupes_liste()[2].get_numero() if len(mariage.get_groupes_liste()) > 2 else pd.NA for mariage in liste_mariages]



    for marie in [premier, second, troisieme]:
        for i,numero in enumerate(marie):
            if numero is not pd.NA:
                if numero < 0:
                    numero = 'BioInt'
                else:
                    numero = str(numero)
                
                marie[i] = numero


    data = {
        'Index': [i+1 for i in range(len(liste_mariages))],
        'Groupe 1': premier,
        'Groupe 2': second,
        'Groupe 3': troisieme,        
        'UEX': [mariage.get_uex() for mariage in liste_mariages],
        # Utilise une formule Excel pour compter les étudiants de chaque mariage
        'Taille sans bioint': [f'=COUNTIF(Etudiants!I:I,A{i+2})' for i in range(len(liste_mariages))],
        'Taille avec bioint': [f'=COUNTIF(Etudiants!I:I,A{i+2}) + {mariage.get_bioint()}' for i, mariage in enumerate(liste_mariages)],
    }
    return pd.DataFrame(data)


def liste_groupes_to_df(liste_groupes, liste_uex):
    data = {
        'Numéro': [groupe.get_numero() for groupe in liste_groupes],
        'Nom': [groupe.get_name() for groupe in liste_groupes],
        # Utilise une formule Excel pour compter les occurrences du numéro de groupe dans la colonne G de la feuille Etudiants
        'Taille actuelle': [f'=COUNTIF(Etudiants!G:G,A{i+2})' for i in range(len(liste_groupes))],
    }

    liste_uex_majuscule = [uex.upper() for uex in liste_uex]

    for uex in liste_uex_majuscule:
        data[uex] = ['x' if uex in groupe.get_uex_liste() else pd.NA for groupe in liste_groupes]

    return pd.DataFrame(data)


def ecrire_resultats_excel(df_etudiants_en_place, df_mariages, df_groupes):
    with pd.ExcelWriter('resultats_mise_en_groupe.xlsx') as writer:
        df_etudiants_en_place.to_excel(writer, sheet_name='Etudiants', index=False)
        df_mariages.to_excel(writer, sheet_name='Mariages', index=False)
        df_groupes.to_excel(writer, sheet_name='Groupes', index=False)
        # Ajouter d'autres feuilles si nécessaire



def determiner_mariage_etudiant(etudiant, liste_mariages):
    """
    Détermine quel mariage correspond à un étudiant en fonction de son UEX et de son groupe.
    """
    if not liste_mariages:
        return pd.NA
    
    uex_etudiant = etudiant.get_uex().upper()
    groupe_etudiant = etudiant.get_groupe()
    
    for i, mariage in enumerate(liste_mariages):
        # Vérifier si l'UEX correspond
        if mariage.get_uex().upper() == uex_etudiant:
            # Vérifier si le groupe de l'étudiant fait partie du mariage
            for groupe in mariage.get_groupes_liste():
                if groupe.get_numero() == groupe_etudiant:
                    return i+1 
    
    return pd.NA

def exporter_resultats(resultat, liste_uex):
    nb_etudiants, nb_places, nb_etudiants_place, liste_groupes, liste_mariages = resultat

    df_mariages = liste_mariages_to_df(liste_mariages)
    df_groupes = liste_groupes_to_df(liste_groupes, liste_uex)

   
    try:
        nb_etudiants, nb_places, nb_etudiants_place, liste_groupes, liste_mariages = resultat

        if resultat and resultat[0] is not None:  # Succès
            liste_etudiants_en_place = liste_groupes_to_liste_EtudiantEnPlace(liste_groupes)
            liste_etudiants_en_place = trie_liste_EtudiantEnPlace(liste_etudiants_en_place)
            df_etudiants_en_place = liste_EtudiantEnPlace_to_df(liste_etudiants_en_place, liste_mariages)
            
            df_mariages = liste_mariages_to_df(liste_mariages)
            df_groupes = liste_groupes_to_df(liste_groupes, liste_uex)


            try:
                ecrire_resultats_excel(df_etudiants_en_place, df_mariages, df_groupes)

            except Exception as e:
                print(f"Erreur lors de l'écriture du fichier Excel : {str(e)}")


    except Exception as e:
        print(f"Erreur lors de l'écriture des résultats : {str(e)}")