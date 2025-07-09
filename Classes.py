# File: Classes.py

import LectureConfig as lc


class Etudiant:
    def __init__(self, nom:str, prenom:str, numero_etudiant:int,uex:str,valide:bool, index_etud:int):
        self.nom = nom
        self.prenom = prenom
        self.numero_etudiant = numero_etudiant
        self.uex = uex
        self.valide = valide
        self.index_etud = index_etud

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.numero_etudiant})"

    def get_nom(self):
        return self.nom
    
    def get_prenom(self):
        return self.prenom
    
    def get_numero_etudiant(self):
        return self.numero_etudiant
    
    def get_valide(self):
        return self.valide
    
    def get_index_etud(self):
        return self.index_etud




class Equipe:
    def __init__(self, numero_equipe:int, membres:list[Etudiant], uex:str, valide:bool = False):
        self.numero_equipe = numero_equipe
        self.membres = membres
        self.uex = uex
        self.valide = valide

    def __str__(self):
        return f"Équipe {self.numero_equipe} (UEX: {self.uex}, VALIDE: {self.valide}): {', '.join(str(membre) for membre in self.membres)} "

    def get_numero(self):
        return self.numero_equipe
    
    def get_membres(self):
        return self.membres
    
    def get_uex(self):
        return self.uex
    
    def get_valide(self):
        return self.valide
    
    def length(self):
        return len(self.membres)
    


class Groupe:
    taille_max = lc.get_taille_groupes()  # Taille maximale des groupes
    

    def __init__(self, nom_groupe:str, equipes_liste:list[Equipe], uex_liste:list[str]):
        self.nom_groupe = nom_groupe
        self.equipes_liste = equipes_liste
        self.uex_liste = uex_liste
        
    def get_name(self):
        return self.nom_groupe
    
    def get_equipes(self):
        return self.equipes_liste
    
    def length(self):
        taille = 0
        for equipe in self.equipes_liste:
            taille += equipe.length()
        
        return taille
    
    def get_taille_max(self):
        return  self.taille_max
    
    def modfifier_taille_max(self, taille_max:int):
        if taille_max > 0:
            self.taille_max = taille_max
        else:
            raise ValueError("La taille maximale doit être un entier positif.")

    
    def get_uex_liste(self):
        return self.uex_liste


    def ajouter_equipe(self, equipe):
        self.equipes_liste.append(equipe)

    def enlever_equipe(self, equipe):
        if equipe in self.equipes_liste:
            self.equipes_liste.remove(equipe)
        else:
            raise ValueError("L'équipe n'est pas dans le groupe.")







class Mariage:
    taille_max = lc.get_taille_groupes() # Taille maximale des mariages
    
    def __init__(self, uex:str, groupes_liste:list[Groupe]):
        self.uex = self.init_uex(uex)
        self.groupes_liste = groupes_liste

    def __str__(self):
        return f"{', '.join(groupe.get_name() for groupe in self.groupes_liste)} : {self.uex}, taille max: {self.taille_max}"
    
    def init_uex(self,uex:str):
        """
        Normalise l'UEX du mariage.
        """
        return uex.lower().strip()

    def get_uex(self):
        return self.uex
    
    def get_groupes_liste(self):
        return self.groupes_liste
    
    def get_taille_max(self):
        return self.taille_max
    
    def length(self):
        taille = 0
        for groupe in self.groupes_liste:
            for equipe in groupe.get_equipes():
                if equipe.get_uex() == self.uex:
                    taille += equipe.length()
        
        return taille

    def modifier_taille_max(self, taille_max:int):
        if taille_max > 0:
            self.taille_max = taille_max
        else:
            raise ValueError("La taille maximale doit être un entier positif.")