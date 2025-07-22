import ReconstructionPostVerif as rpv
import pandas as pd
from math import inf
from ortools.sat.python import cp_model

from Tools import normaliser_colonne_texte
import LectureConfig as lc
import Classes

import LectureFichierMariages as lfm


taille_groupe = lc.get_taille_groupes()
nombre_groupes = lc.get_nombre_groupes()




liste_uex = lc.get_liste_uex()
liste_uex_majuscule = [uex.upper() for uex in liste_uex]


def randomiser_liste(liste):
    """
    Randomise la liste donnée en paramètre.
    """
    return pd.Series(liste).sample(frac=1).tolist()

def liste_etudiants_to_liste_equipes(liste_etudiants):
    """
    Transforme une liste d'étudiants en une liste d'équipes.
    Chaque équipe contient un seul étudiant.
    """
    return [Classes.Equipe(-etudiant.get_index_etud(), [etudiant], etudiant.get_uex(), etudiant.get_valide()) for etudiant in liste_etudiants]

def liste_equipes_pop_valide(liste_equipes):
    """
    Sépare les équipes qui ont validée des autres.
    """
    liste_non_valide = [equipe for equipe in liste_equipes if not equipe.get_valide()]
    liste_valide = [equipe for equipe in liste_equipes if equipe.get_valide()]

    return liste_non_valide, liste_valide




def score_groupe(groupe):
    """
    Calcule le score d'un groupe. 
    Le score est le pourcentage de remplissage du groupe.
    """
    return groupe.length() / groupe.get_taille_max()

def score_mariage(mariage):
    """
    Calcule le score d'un mariage.
    Le score est le pourcentage de remplissage du mariage.
    """
    return mariage.length() / mariage.get_taille_max()
                            

def mise_en_groupe_determinee(liste_groupe, liste_equipes):
    """
    Cherche les UEX qui ne sont que dans un seul groupe et ajoute les équpie et étudiant correspondants
    """

    for uex in liste_uex_majuscule:
        count = 0
        groupe_teste = None
        for i, groupe in enumerate(liste_groupe):
            if uex in groupe.get_uex_liste():
                count += 1
                groupe_teste = liste_groupe[i]

        
        if count == 1 and groupe_teste is not None:
            groupe = groupe_teste
            for equipe in liste_equipes:
                if uex.lower() in equipe.get_uex():
                    groupe.ajouter_equipe(equipe)
                    liste_equipes.remove(equipe)


def find_mariage_by_groupe(liste_mariages, groupe, uex):
    """
    Trouve le mariage auquel appartient le groupe.
    """
    for mariage in liste_mariages:
        if groupe in mariage.get_groupes_liste():
            if mariage.get_uex() == uex:
                return mariage
    return None

def score_si_ajout_groupe(groupe, equipe):
    """
    Calcule le score d'un groupe si l'équipe est ajoutée.
    """
    new_lenght = groupe.length() + equipe.length()
    if new_lenght > groupe.get_taille_max():
        return inf
    return new_lenght / groupe.get_taille_max()


def score_si_ajout_mariage(liste_mariages, groupe, equipe):
    """
    Calcule le score d'un mariage si l'équipe est ajoutée.
    """
    mariage = find_mariage_by_groupe(liste_mariages, groupe, equipe.get_uex())
    if mariage is None:
        return 0
    new_lenght = mariage.length() + equipe.length()
    if new_lenght > mariage.get_taille_max():
        return inf
    return new_lenght / mariage.get_taille_max()




def resoudre_affectation(equipes, groupes, mariages):
    """
    Résout le problème d'affectation d'équipes dans des groupes sous contraintes
    en utilisant Google OR-Tools.
    
    Args:
        equipes: Liste d'objets Equipe
        groupes: Liste d'objets Groupe  
        mariages: Liste d'objets Mariage
        
    Returns:
        tuple: (dict, int) - ({equipe_id: groupe_id}, nb_etudiants_places) ou (None, 0)
    """
    
    # 1. CRÉATION DU MODÈLE
    model = cp_model.CpModel()
    
    # 2. DÉFINITION DES VARIABLES
    # Variables binaires x[e][g] = 1 si équipe e affectée au groupe g, 0 sinon
    x = {}
    for equipe in equipes:
        for groupe in groupes:
            x[(equipe.get_numero(), groupe.get_name())] = model.NewBoolVar(
                f'x_{equipe.get_numero()}_{groupe.get_name()}'
            )
    
    # 3. CONTRAINTES
    
    # Contrainte 1: Chaque équipe doit être affectée à exactement un groupe
    for equipe in equipes:
        model.Add(
            sum(x[(equipe.get_numero(), groupe.get_name())] for groupe in groupes) == 1
        )
    
    # Contrainte 2: Compatibilité UEX (équipes non validées)
    for equipe in equipes:
        if not equipe.get_valide():  # Si l'équipe n'est pas validée
            uex_equipe = equipe.get_uex().upper()
            for groupe in groupes:
                # L'équipe ne peut être affectée que si le groupe accepte son UEX
                uex_groupe = [uex.upper() for uex in groupe.get_uex_liste()]
                if uex_equipe not in uex_groupe:
                    model.Add(x[(equipe.get_numero(), groupe.get_name())] == 0)
    
    # Contrainte 3: Capacité des groupes
    for groupe in groupes:
        # La somme des tailles des équipes affectées ne doit pas dépasser la capacité
        model.Add(
            sum(x[(equipe.get_numero(), groupe.get_name())] * equipe.length() 
                for equipe in equipes) <= groupe.get_taille_max()
        )
    
    # Contrainte 4: Contraintes de mariage
    for mariage in mariages:
        uex_mariage = mariage.get_uex().upper()
        groupes_maries = mariage.get_groupes_liste()
        
        # Filtrer les équipes non validées ayant la même UEX que le mariage
        equipes_concernees = [
            equipe for equipe in equipes 
            if not equipe.get_valide() and equipe.get_uex().upper() == uex_mariage
        ]
        
        if equipes_concernees and len(groupes_maries) > 0:
            # Vérifier que toutes les combinaisons équipe-groupe existent avant de les utiliser
            termes_mariage = []
            for equipe in equipes_concernees:
                for groupe in groupes_maries:
                    cle = (equipe.get_numero(), groupe.get_name())
                    if cle in x:  # Vérification de l'existence de la variable
                        termes_mariage.append(x[cle] * equipe.length())
            
            if termes_mariage:  # Ajouter la contrainte seulement s'il y a des termes valides
                model.Add(sum(termes_mariage) <= mariage.get_taille_max())
    
    # 4. FONCTION OBJECTIF (équilibrage des groupes)
    nb_etudiants_par_groupe = []
    for groupe in groupes:
        if groupe.get_taille_max() > 0:
            nb_etudiants = model.NewIntVar(0, groupe.get_taille_max(), f'nb_etudiants_{groupe.get_name()}')
            model.Add(nb_etudiants == sum(x[(equipe.get_numero(), groupe.get_name())] * equipe.length() 
                                         for equipe in equipes))
            nb_etudiants_par_groupe.append(nb_etudiants)
    

    
    # Minimiser l'écart entre le groupe le plus rempli et le moins rempli
    if len(nb_etudiants_par_groupe) > 1:
        max_etudiants = model.NewIntVar(0, max(g.get_taille_max() for g in groupes), 'max_etudiants')
        min_etudiants = model.NewIntVar(0, max(g.get_taille_max() for g in groupes), 'min_etudiants')
        
        for nb in nb_etudiants_par_groupe:
            model.AddMaxEquality(max_etudiants, [nb, max_etudiants])
            model.AddMinEquality(min_etudiants, [nb, min_etudiants])
        
        ecart_groupes = model.NewIntVar(0, max(g.get_taille_max() for g in groupes), 'ecart_groupes')
        model.Add(ecart_groupes == max_etudiants - min_etudiants)
    else:
        ecart_groupes = model.NewIntVar(0, 0, 'ecart_groupes')
        model.Add(ecart_groupes == 0)

    # Minimiser aussi l'écart entre le mariage le plus rempli et le moins rempli
    nb_etudiants_par_mariage = []
    for mariage in mariages:
        if mariage.get_taille_max() > 0:
            nb_etudiants_m = model.NewIntVar(0, mariage.get_taille_max(), f'nb_etudiants_mariage_{mariage.get_uex()}_{mariage.get_numero()}')
            groupes_maries = mariage.get_groupes_liste()
            equipes_concernees = [
                equipe for equipe in equipes
                if not equipe.get_valide() and equipe.get_uex().upper() == mariage.get_uex().upper()
            ]
            termes = []
            for equipe in equipes_concernees:
                for groupe in groupes_maries:
                    cle = (equipe.get_numero(), groupe.get_name())
                    if cle in x:
                        termes.append(x[cle] * equipe.length())
            if termes:
                model.Add(nb_etudiants_m == sum(termes))
            else:
                model.Add(nb_etudiants_m == 0)
            nb_etudiants_par_mariage.append(nb_etudiants_m)

    if len(nb_etudiants_par_mariage) > 1:
        max_mariage = model.NewIntVar(0, max(m.get_taille_max() for m in mariages), 'max_mariage')
        min_mariage = model.NewIntVar(0, max(m.get_taille_max() for m in mariages), 'min_mariage')
        for nb in nb_etudiants_par_mariage:
            model.AddMaxEquality(max_mariage, [nb, max_mariage])
            model.AddMinEquality(min_mariage, [nb, min_mariage])
        ecart_mariages = model.NewIntVar(0, max(m.get_taille_max() for m in mariages), 'ecart_mariages')
        model.Add(ecart_mariages == max_mariage - min_mariage)
    else:
        ecart_mariages = model.NewIntVar(0, 0, 'ecart_mariages')
        model.Add(ecart_mariages == 0)

    # Fonction objectif combinée : minimiser la somme des deux écarts
    model.Minimize(ecart_groupes + ecart_mariages)


    model.Minimize(ecart_groupes)

    # 5. RÉSOLUTION
    solver = cp_model.CpSolver()
    
    # Configuration du solveur pour de meilleures performances
    solver.parameters.max_time_in_seconds = 300.0  # 5 minutes max
    solver.parameters.log_search_progress = False  # Réduire la verbosité
    
    status = solver.Solve(model)
    
    # 6. TRAITEMENT DES RÉSULTATS
    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        return None, 0
    
    # 7. EXTRACTION DE LA SOLUTION
    affectation = {}
    for equipe in equipes:
        for groupe in groupes:
            if solver.Value(x[(equipe.get_numero(), groupe.get_name())]) == 1:
                affectation[equipe.get_numero()] = groupe.get_name()
                break
    
    # Calculer le nombre total d'étudiants placés
    nb_etudiants_places = sum(equipe.length() for equipe in equipes if equipe.get_numero() in affectation)
    
    return affectation, nb_etudiants_places

def recherche_solution_parfaite_adaptative(equipes, groupes, mariages, max_iterations=100):
    """
    Recherche une solution parfaite en augmentant progressivement la taille des groupes.
    
    Args:
        equipes: Liste des équipes à placer
        groupes: Liste des groupes
        mariages: Liste des mariages
        max_iterations: Nombre maximum d'iterations (augmentations de taille)
    
    Returns:
        tuple: (affectation_dict, success)
    """
    
    nb_etudiants_total = sum(equipe.length() for equipe in equipes)
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        
        # Tenter de résoudre avec la taille actuelle
        affectation, nb_places_utilisees = resoudre_affectation(equipes, groupes, mariages)
        
        if affectation and nb_places_utilisees == nb_etudiants_total:            
            return affectation, True
        
        # Augmenter la taille des groupes pour la prochaine tentative
        if iteration < max_iterations:
            if groupes[0].get_taille_max() < 34:  # Limite arbitraire pour éviter des tailles trop grandes
                for groupe in groupes:
                    if groupe.get_name() != 'bioint':  # Ne pas modifier bioint
                        nouvelle_taille = groupe.get_taille_max() + 1
                        groupe.set_taille_max(nouvelle_taille)
            else:
                for mariage in mariages:
                   taille_actuelle = mariage.get_taille_max_bioint()
                   mariage.set_taille_max(taille_actuelle + 1)
        
        

    
    return None, False



def appliquer_affectation(equipes, groupes, affectation):
    """
    Applique l'affectation trouvée par OR-Tools aux objets groupes.
    """
    
    if affectation is None:
        return False
    
    # Vider tous les groupes d'abord
    for groupe in groupes:
        groupe.set_liste_equipes([])
    
    # Appliquer l'affectation
    equipes_non_placees = []
    
    for equipe in equipes:
        equipe_id = equipe.get_numero()
        if equipe_id in affectation:
            nom_groupe = affectation[equipe_id]
            
            # Trouver le groupe correspondant
            groupe_trouve = None
            for groupe in groupes:
                if groupe.get_name() == nom_groupe:
                    groupe_trouve = groupe
                    break
            
            if groupe_trouve:
                groupe_trouve.ajouter_equipe(equipe)
            else:
                equipes_non_placees.append(equipe)
        else:
            equipes_non_placees.append(equipe)
    
    return len(equipes_non_placees) == 0






def fonction_main(chemin_fichier_correction, df_mariages_groupes, df_mariages_UEX):
    """Fonction principale pour la mise en groupe des étudiants avec OR-Tools."""

    df_etud_ref, df_etud_trouves, df_etud_non_trouves = rpv.recuperer_correction_manuelle(chemin_fichier_correction)


    # Création des structures de données
    liste_groupes = lfm.creation_des_groupes(df_mariages_groupes)
    groupe_bioint = lfm.creation_groupe_bioint()
    liste_groupes_avec_bioint = liste_groupes + [groupe_bioint]

    liste_mariages = lfm.creation_des_mariages(liste_groupes_avec_bioint, df_mariages_UEX)
    lfm.enlever_bioint_mariage(liste_mariages, df_mariages_groupes)
    
    liste_equipes = rpv.get_liste_equipes(df_etud_ref, df_etud_trouves, df_etud_non_trouves)
    liste_etudiants = rpv.get_etudiant_not_in_equipes(liste_equipes, df_etud_ref)
    liste_etudiants = liste_etudiants_to_liste_equipes(liste_etudiants)

    liste_equipes_complete = liste_etudiants + liste_equipes
    # liste_equipes_complete, liste_equipes_valide = liste_equipes_pop_valide(liste_equipes_complete)
    
    # Recherche de solution parfaite avec augmentation adaptative
    affectation, success = recherche_solution_parfaite_adaptative(
        liste_equipes_complete, liste_groupes, liste_mariages, max_iterations=10
    )

    succes_application = appliquer_affectation(liste_equipes_complete, liste_groupes, affectation)
    
    if succes_application:
        # Calcul des statistiques finales
        nb_etudiants = sum(equipe.length() for equipe in liste_equipes_complete)
        nb_places = sum(groupe.get_taille_max() for groupe in liste_groupes)
        nb_etudiants_place = sum(groupe.length() for groupe in liste_groupes)
        
        return nb_etudiants, nb_places, nb_etudiants_place, liste_groupes, liste_mariages
    else:
        return None, None, None, None, None