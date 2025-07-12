
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def afficher_grille_selection_fichiers():
    root = tk.Tk()
    root.title("Sélection de fichiers")

    fichier_names = ["Liste des étudiants", "Liste des équipes", "Liste des groupes/mariages"]

    for i in range(3):
        label = tk.Label(root, text=fichier_names[i])
        label.grid(row=i, column=0, padx=10, pady=5, sticky="e")

        entry = tk.Entry(root, width=40)
        entry.grid(row=i, column=1, padx=10, pady=5)

        def choisir_fichier(e=entry):
            fichier = filedialog.askopenfilename()
            if fichier:
                e.delete(0, tk.END)
                if fichier.lower().endswith(('.xls', '.xlsx')):
                    e.insert(0, fichier)
                else:
                    messagebox.showerror("Erreur", "Veuillez sélectionner un fichier Excel (.xls ou .xlsx).")

        bouton = tk.Button(root, text="Parcourir", command=choisir_fichier)
        bouton.grid(row=i, column=2, padx=10, pady=5)

    root.mainloop()



if __name__ == "__main__":
    afficher_grille_selection_fichiers()