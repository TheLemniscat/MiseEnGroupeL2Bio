import AnalyseDesFichiers as AF
import LectureConfig as lc
import MiseEnGroupe as MEG
import sys
import time

def lancer_mise_en_groupe():
    """Lance la mise en groupe automatique."""
    try:
        # Lancement de la fonction principale
        resultat = MEG.fonction_main()
        
        if resultat and resultat[0] is not None:  # Succès
            nb_etudiants, nb_places, nb_etudiants_place, liste_groupes, liste_mariages = resultat
            
            return {
                'success': True,
                'nb_etudiants': nb_etudiants,
                'nb_places': nb_places,
                'nb_etudiants_place': nb_etudiants_place,
                'taux_reussite': (nb_etudiants_place/nb_etudiants)*100 if nb_etudiants > 0 else 0,
                'solution_parfaite': nb_etudiants_place == nb_etudiants,
                'groupes': liste_groupes,
                'mariages': liste_mariages
            }
        else:
            return {
                'success': False,
                'nb_etudiants': 0,
                'nb_places': 0,
                'nb_etudiants_place': 0,
                'taux_reussite': 0,
                'solution_parfaite': False,
                'groupes': [],
                'mariages': []
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'nb_etudiants': 0,
            'nb_places': 0,
            'nb_etudiants_place': 0,
            'taux_reussite': 0,
            'solution_parfaite': False,
            'groupes': [],
            'mariages': []
        }



if __name__ == "__main__":
    dict = lancer_mise_en_groupe()
    success = dict['success']
    nb_etudiants = dict['nb_etudiants']
    nb_places = dict['nb_places']
    nb_etudiants_place = dict['nb_etudiants_place']
    taux_reussite = dict['taux_reussite']
    solution_parfaite = dict['solution_parfaite']
    groupes = dict['groupes']
    mariages = dict['mariages']

    print('success:', success)

    for groupe in groupes:
        remplissage = groupe.length() / groupe.get_taille_max() * 100 if groupe.get_taille_max() > 0 else 0
        print(f"{groupe.get_name()} : {groupe.length()}/{groupe.get_taille_max()} ({remplissage:.1f}%)")
    
    print()
    for i,mariage in enumerate(mariages):
        print(f"Mariage {i} : {mariage.length() + mariage.get_bioint()}/{mariage.get_taille_max() + mariage.get_bioint()}")
