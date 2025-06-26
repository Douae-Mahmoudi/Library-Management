import os
import csv
from datetime import datetime
from src.exceptions import LivreInexistantError, LivreIndisponibleError, MembreInexistantError, QuotaEmpruntDepasseError
# Classe principale de la bibliothèque

class Bibliotheque:
    # Classe interne représentant un livre

    class Livre:
        def __init__(self, isbn, titre, auteur, annee, genre, statut="disponible"):
            self.isbn = isbn
            self.titre = titre
            self.auteur = auteur
            self.annee = annee
            self.genre = genre
            self.statut = statut

        def __str__(self):
            return f"{self.titre} ({self.auteur}) - {self.statut}"
     # Classe interne représentant un membre


    class Membre:
        def __init__(self, id_membre, nom):
            self.id_membre = id_membre
            self.nom = nom
            self.livres_empruntes = []

        def __str__(self):
            return f"{self.nom} ({len(self.livres_empruntes)} livre(s) emprunté(s))"

    def __init__(self):
        self.livres = {}      # isbn -> Livre
        self.membres = {}     # id_membre -> Membre
        self.historique = []  # (date, isbn, id_membre, action)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(base_dir, "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)

        self.livres_fichier = os.path.join(self.data_dir, "livres.txt")
        self.membres_fichier = os.path.join(self.data_dir, "membres.txt")
        self.historique_fichier = os.path.join(self.data_dir, "historique.csv")
    # Ajouter un nouveau livre à la bibliothèque

    def ajouter_livre(self, livre):
        if livre.isbn in self.livres:
            raise ValueError("Livre déjà existant.")
        self.livres[livre.isbn] = livre
        self.sauvegarder()
    # Supprimer un livre (seulement s’il n’est pas emprunté)

    def supprimer_livre(self, isbn):
        if isbn not in self.livres:
            raise LivreInexistantError("Livre inexistant.")
        if self.livres[isbn].statut == "emprunte":
            raise LivreIndisponibleError("Le livre est actuellement emprunté.")
        del self.livres[isbn]
        self.sauvegarder()
    # Enregistrer un nouveau membre

    def enregistrer_membre(self, membre):
        if membre.id_membre in self.membres:
            raise ValueError("Membre déjà existant.")
        self.membres[membre.id_membre] = membre
        self.sauvegarder()
    # Supprimer un membre (seulement s’il n’a pas de livres empruntés)

    def supprimer_membre(self, id_membre):
        if id_membre not in self.membres:
            raise MembreInexistantError("Membre inexistant.")
        if self.membres[id_membre].livres_empruntes:
            raise ValueError("Le membre a encore des livres empruntés.")
        del self.membres[id_membre]
        self.sauvegarder()
    # Emprunter un livre pour un membre donné

    def emprunter_livre(self, isbn, id_membre):
        if id_membre not in self.membres:
            raise MembreInexistantError("Membre inexistant.")
        if isbn not in self.livres:
            raise LivreInexistantError("Livre inexistant.")
        if self.livres[isbn].statut != "disponible":
            raise LivreIndisponibleError("Livre déjà emprunté.")
        if len(self.membres[id_membre].livres_empruntes) >= 3:
            raise QuotaEmpruntDepasseError("Ce membre a atteint le quota maximal de 3 emprunts.")

        self.livres[isbn].statut = "emprunte"
        self.membres[id_membre].livres_empruntes.append(isbn)
        self._log_action("emprunt", isbn, id_membre)
        self.sauvegarder()
    # Retourner un livre emprunté

    def retourner_livre(self, isbn, id_membre):
        if id_membre not in self.membres:
            raise MembreInexistantError("Membre inexistant.")
        if isbn not in self.livres:
            raise LivreInexistantError("Livre inexistant.")
        if isbn not in self.membres[id_membre].livres_empruntes:
            raise ValueError("Ce livre n'a pas été emprunté par ce membre.")

        self.membres[id_membre].livres_empruntes.remove(isbn)
        self.livres[isbn].statut = "disponible"
        self._log_action("retour", isbn, id_membre)
        self.sauvegarder()
# Enregistrer une action dans l’historique

    def _log_action(self, action, isbn, id_membre):
        date = datetime.now().strftime("%Y-%m-%d")
        self.historique.append((date, isbn, id_membre, action))
        with open(self.historique_fichier, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([date, isbn, id_membre, action])
    # Sauvegarder les données (livres et membres)

    def sauvegarder(self):
        with open(self.livres_fichier, "w", encoding="utf-8") as f:
            for livre in self.livres.values():
                ligne = ";".join([livre.isbn, livre.titre, livre.auteur, livre.annee, livre.genre, livre.statut])
                f.write(ligne + "\n")

        with open(self.membres_fichier, "w", encoding="utf-8") as f:
            for membre in self.membres.values():
                emprunts = ",".join(membre.livres_empruntes)
                ligne = f"{membre.id_membre};{membre.nom};{emprunts}"
                f.write(ligne + "\n")

    def charger(self):
        # Charger livres
        try:
            with open(self.livres_fichier, "r", encoding="utf-8") as f:
                for ligne in f:
                    parts = ligne.strip().split(";")
                    if len(parts) == 6:
                        isbn, titre, auteur, annee, genre, statut = parts
                        self.livres[isbn] = self.Livre(isbn, titre, auteur, annee, genre, statut)
        except FileNotFoundError:
            pass

        # Charger membres
        try:
            with open(self.membres_fichier, "r", encoding="utf-8") as f:
                for ligne in f:
                    parts = ligne.strip().split(";")
                    if len(parts) >= 2:
                        id_m, nom = parts[0], parts[1]
                        emprunts = parts[2].split(",") if len(parts) > 2 and parts[2] else []
                        membre = self.Membre(id_m, nom)
                        membre.livres_empruntes = emprunts
                        self.membres[id_m] = membre
        except FileNotFoundError:
            pass

        # Charger historique
        try:
            with open(self.historique_fichier, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.historique = [tuple(row) for row in reader if len(row) == 4]
        except FileNotFoundError:
            pass
