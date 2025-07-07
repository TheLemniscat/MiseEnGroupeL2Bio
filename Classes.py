# File: Classes.py

import LectureConfig as lc


class Etudiant:
    def __init__(self, nom, prenom, numero_etudiant,uex,redoublant):
        self.nom = nom
        self.prenom = prenom
        self.numero_etudiant = numero_etudiant
        self.uex = uex
        self.redoublant = redoublant


    def get_nom(self):
        return self.nom
    
    def get_prenom(self):
        return self.prenom
    
    def get_numero_etudiant(self):
        return self.numero_etudiant
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.numero_etudiant})"



class Equipe:
    def __init__(self, numero, membres, uex):
        self.numero = numero
        self.membres = membres
        self.uex = uex

    def get_numero(self):
        return self.numero
    
    def get_membres(self):
        return self.membres
    
    def get_uex(self):
        return self.uex
    
    def length(self):
        return len(self.membres)
    


class Groupe:
    taille_max = lc.get_taille_groupes()  # Taille maximale des groupes
    

    def __init__(self, numero, equipes, uex):
        self.numero = numero
        self.equipes = equipes
        self.uex = uex

    def get_numero(self):
        return self.numero
    
    def get_equipes(self):
        return self.equipes
    
    def length(self):
        return len(self.equipes)
    
    def get_uex(self):
        return self.uex
    
    def get_taille_max(self):
        return  self.taille_max
    
    def ajouter_equipe(self, equipe):
        self.equipes.append(equipe)
