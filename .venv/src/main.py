import tkinter as tk
from tkinter import messagebox, ttk
from src.bibliotheque import Bibliotheque
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime, timedelta
import os
import sys
from PIL import Image, ImageTk
#  Initialisation de l’objet bibliothèque

biblio = Bibliotheque()
biblio.charger()
# Création de la fenêtre principale Tkinter
fenetre = tk.Tk()
fenetre.title("\U0001F4DA Gestion de Bibliothèque ENSAO")
fenetre.geometry("1200x750")
fenetre.configure(bg="white")

#  Chargement images
def charger_image(nom_fichier, largeur=None, hauteur=None):
    # Obtenir le répertoire du script actuellement en cours d'exécution ( C:\python\Projet-Python\.venv\src)
    dossier_script = os.path.dirname(os.path.abspath(sys.argv[0]))

    dossier_venv = os.path.dirname(dossier_script)

    dossier_racine_projet = os.path.dirname(dossier_venv)

    dossier_img = os.path.join(dossier_racine_projet, "img")

    chemin = os.path.join(dossier_img, nom_fichier)
    print(f"DEBUG: Attempting to load image from: {chemin}") # Debug print

    if not os.path.exists(chemin):
        print(f"ERROR: Image file NOT FOUND at: {chemin}")
        return None

    try:
        img = Image.open(chemin)
        if largeur and hauteur:
            img = img.resize((largeur, hauteur), Image.Resampling.LANCZOS)

        photo_image = ImageTk.PhotoImage(img)
        print(f"DEBUG: Successfully loaded {nom_fichier}")
        return photo_image
    except Exception as e:
        print(f"ERROR: Erreur chargement image {nom_fichier}: {e}")
        return None
# Dictionnaire contenant les icônes utilisées dans l'application

icones = {
    "livres_tab": charger_image("book.png", 24, 24),
    "membres_tab": charger_image("group.png", 24, 24),
    "stats_tab": charger_image("analytics.png", 24, 24),
    "pie_chart": charger_image("pie-chart.png", 20, 20),
    "bar_chart": charger_image("analysis.png", 20, 20),
    "line_graph": charger_image("graph.png", 20, 20),
    "member_list_icon": charger_image("membre.png", 20, 20),
    "book2_icon": charger_image("book2.png", 20, 20),
    "open_book_icon": charger_image("open-book.png", 20, 20) # NEW: Add the open-book.png icon
}
# TOP FRAME contenant uniquement onglets
top_frame = tk.Frame(fenetre, bg="white")
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

# Création notebook
notebook = ttk.Notebook(top_frame)
notebook.pack(fill="x", expand=True)

# On force notebook à prendre tout l’espace horizontal possible
top_frame.columnconfigure(0, weight=1)
# Fonction pour quitter l’application proprement

def quitter():
    biblio.sauvegarder()# Sauvegarde avant de fermer
    fenetre.destroy()

style_label = {"font": ("Arial", 10), "bg": "white", "fg": "#003366"}

style = ttk.Style(fenetre)
style.theme_use("clam")

style.configure("TNotebook", background="#d0e7ff")
style.map("TNotebook.Tab",
          background=[("selected", "white"),
                      ("!selected", "#d0e7ff")],
          foreground=[("selected", "#003366"),
                      ("!selected", "#003366")])

style.configure("Treeview",
                background="white",
                foreground="black",
                rowheight=25,
                fieldbackground="white",
                font=("Arial", 10))
style.map("Treeview",
          background=[("selected", "#cce6ff")],
          foreground=[("selected", "black")])
style.configure("Treeview.Heading",
                background="#003366",
                foreground="white",
                font=("Arial", 11, "bold"))
style.configure("oddrow", background="#f2f9ff")
style.configure("evenrow", background="white")


global_message_area = tk.Text(fenetre, height=5, bg="white", fg="#333333", font=("Arial", 10))


# === Onglet Livres
cadre_livre = tk.Frame(notebook, bg="white")
if icones["livres_tab"]:
    notebook.add(cadre_livre, text=" Livres", image=icones["livres_tab"], compound="left")
else:
    print("WARNING: Image 'book.png' failed to load, falling back to emoji.")
    notebook.add(cadre_livre, text="\U0001F4D8 Livres")

cadre_livre.grid_columnconfigure(0, weight=0) # Left column (form) - fixed size
cadre_livre.grid_columnconfigure(1, weight=1) # Right column (messages/table) - expands
cadre_livre.grid_rowconfigure(0, weight=1)    # Row to allow right pane to expand vertically

form_frame_livre = tk.Frame(cadre_livre, bg="white")
form_frame_livre.grid(row=0, column=0, padx=10, pady=10, sticky="ns") # Stick to north/south

fields_livre = {}
for i, champ in enumerate(["ISBN", "Titre", "Auteur", "Annee", "Genre"]):
    tk.Label(form_frame_livre, text=champ, **style_label).pack(anchor="w", pady=2)
    entry = tk.Entry(form_frame_livre, width=40)
    entry.pack(pady=2)
    fields_livre[champ.lower()] = entry

# Right Display Frame for Livres tab
right_pane_livre = tk.Frame(cadre_livre, bg="white")
right_pane_livre.grid(row=0, column=1, padx=10, pady=10, sticky="nsew") # Stick to all directions
right_pane_livre.grid_rowconfigure(0, weight=0) # For message area (fixed height)
right_pane_livre.grid_rowconfigure(1, weight=1) # For table area (expands vertically)
right_pane_livre.grid_columnconfigure(0, weight=1) # Column for message/table (expands horizontally

# Message display for Livres tab (specific to this tab's right pane)
affichage_livres = tk.Text(right_pane_livre, height=5, bg="white", fg="#333333", font=("Arial", 10))
affichage_livres.grid(row=0, column=0, sticky="ew", pady=5) # Use grid for positioning

# Re-route afficher_message to use the correct text widget based on context
def afficher_message_livres_tab(texte):
    affichage_livres.insert(tk.END, texte + "\n")
    affichage_livres.see(tk.END)

def ajouter_livre():
    try:
        livre = biblio.Livre(
            fields_livre["isbn"].get().strip(),
            fields_livre["titre"].get().strip(),
            fields_livre["auteur"].get().strip(),
            fields_livre["annee"].get().strip(),
            fields_livre["genre"].get().strip(),
            "disponible"
        )
        biblio.ajouter_livre(livre)
        afficher_message_livres_tab(" Livre ajouté avec statut 'disponible'.")
        maj_tout()
        # --- Modifications ici pour vider les champs après ajout ---
        for entry_field in fields_livre.values():
            entry_field.delete(0, tk.END)
        #  Fin des modifications
    except Exception as e:
        afficher_message_livres_tab(f" Erreur : {e}")

def supprimer_livre_by_form():
    try:
        biblio.supprimer_livre(fields_livre["isbn"].get().strip())
        afficher_message_livres_tab("🗑 Livre supprimé.")
        maj_tout()
        # --- Vider uniquement le champ ISBN après suppression par formulaire ---
        fields_livre["isbn"].delete(0, tk.END)
        # --- Fin des modifications ---
    except Exception as e:
        afficher_message_livres_tab(f" Erreur : {e}")

btn_frame_livre = tk.Frame(form_frame_livre, bg="white")
btn_frame_livre.pack(pady=5, anchor="w")

tk.Button(btn_frame_livre, text="Ajouter Livre", bg="#0066cc", fg="white",
          font=("Arial", 10, "bold"), command=ajouter_livre).pack(side="left", padx=5)

tk.Button(btn_frame_livre, text="Supprimer Livre", bg="#cc0000", fg="white",
          font=("Arial", 10, "bold"), command=supprimer_livre_by_form).pack(side="left", padx=5)

# === Création de la zone qui contiendra le tableau des livres dans l’onglet Livres ===
# Cette frame contiendra le titre ("Tous les Livres") et le widget Treeview (tableau)
tableau_livres_for_livres_tab_frame = tk.Frame(right_pane_livre, bg="white")
# Placement de la frame dans la grille, ligne 1, colonne 0, et elle s'étend dans toutes les directions
tableau_livres_for_livres_tab_frame.grid(row=1, column=0, sticky="nsew", pady=5)
# Permet à la frame de s’étendre verticalement
tableau_livres_for_livres_tab_frame.grid_rowconfigure(0, weight=1)
# Permet à la frame de s’étendre horizontalement

tableau_livres_for_livres_tab_frame.grid_columnconfigure(0, weight=1)

if icones["book2_icon"]:
    tk.Label(tableau_livres_for_livres_tab_frame, text=" Tous les Livres", image=icones["book2_icon"], compound="left", font=("Arial", 12, "bold"), bg="white", fg="#003366").pack(fill="x")
else:
    print("WARNING: Image 'book2.png' failed to load, falling back to emoji for Tous les Livres.")
    tk.Label(tableau_livres_for_livres_tab_frame, text="Tous les Livres", font=("Arial", 12, "bold"), bg="white", fg="#003366").pack(fill="x")
# FIN DE LA MODIFICATION

colonnes_livres = ("ISBN", "Titre", "Auteur", "Année", "Genre", "Statut", "ID Membre", "Nom Membre")
tableau_livres_for_livres_tab = ttk.Treeview(tableau_livres_for_livres_tab_frame, columns=colonnes_livres, show="headings", height=15) # Shorter height than global
# Fonction appelée lorsqu'un livre est sélectionné dans le tableau
# Elle remplit automatiquement les champs du formulaire avec les données du livre sélectionné
def remplir_champs_livre_depuis_selection(event):
    # Récupération de la sélection dans le tableau
    selection = tableau_livres_for_livres_tab.selection()
    # Si aucune ligne n’est sélectionnée, on vide tous les champs du formulaire
    if not selection:
        for entry_field in fields_livre.values():
            entry_field.delete(0, tk.END)
        return
        # Récupère les données (valeurs) de la ligne sélectionnée

    item = tableau_livres_for_livres_tab.item(selection[0])
    valeurs = item['values']
    # Remplit les champs du formulaire avec les données récupérées

    fields_livre["isbn"].delete(0, tk.END)
    fields_livre["isbn"].insert(0, valeurs[0])
    fields_livre["titre"].delete(0, tk.END)
    fields_livre["titre"].insert(0, valeurs[1])
    fields_livre["auteur"].delete(0, tk.END)
    fields_livre["auteur"].insert(0, valeurs[2])
    fields_livre["annee"].delete(0, tk.END)
    fields_livre["annee"].insert(0, valeurs[3])
    fields_livre["genre"].delete(0, tk.END)
    fields_livre["genre"].insert(0, valeurs[4])
# Lier l'événement de sélection dans le tableau à la fonction ci-dessus
tableau_livres_for_livres_tab.bind("<<TreeviewSelect>>", remplir_champs_livre_depuis_selection)

for col in colonnes_livres:
    tableau_livres_for_livres_tab.heading(col, text=col)
    tableau_livres_for_livres_tab.column(col, width=50 if col in ("Année", "Statut") else 100, anchor="center" if col in ("Année", "Statut", "ID Membre") else "w")
# Personnalisation spécifique de la largeur et de l'alignement de chaque colonne

tableau_livres_for_livres_tab.column("ISBN", width=80, anchor="w")
tableau_livres_for_livres_tab.column("Titre", width=150, anchor="w")
tableau_livres_for_livres_tab.column("Auteur", width=100, anchor="w")
tableau_livres_for_livres_tab.column("Année", width=60, anchor="center")
tableau_livres_for_livres_tab.column("Genre", width=80, anchor="w")
tableau_livres_for_livres_tab.column("Statut", width=80, anchor="center")
tableau_livres_for_livres_tab.column("ID Membre", width=80, anchor="center")
tableau_livres_for_livres_tab.column("Nom Membre", width=120, anchor="w")

tableau_livres_for_livres_tab.pack(fill="both", expand=True, padx=5, pady=5)
#Fonction pour rafraîchir (réinitialiser et recharger) le tableau des livres dans l'onglet Livres
def rafraichir_tableau_livres_livres_tab():
    # Suppression de toutes les lignes existantes dans le tableau
    tableau_livres_for_livres_tab.delete(*tableau_livres_for_livres_tab.get_children())
    # Parcours de tous les livres présents dans la bibliothèque
    for i, livre in enumerate(biblio.livres.values()):
        if livre.statut == "disponible":
            id_membre = ""
            nom_membre = ""
        else:
            emprunteur = next(((m.id_membre, m.nom) for m in biblio.membres.values() if livre.isbn in m.livres_empruntes), ("?", "?"))
            id_membre, nom_membre = emprunteur
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tableau_livres_for_livres_tab.insert("", tk.END, values=(
            livre.isbn,
            livre.titre,
            livre.auteur,
            livre.annee,
            livre.genre,
            livre.statut,
            id_membre,
            nom_membre
        ), tags=(tag,))# Tag utilisé pour le style (couleur de ligne pair/impair)

# Onglet Membres
cadre_membre = tk.Frame(notebook, bg="white")
if icones["membres_tab"]:
    notebook.add(cadre_membre, text=" Membres", image=icones["membres_tab"], compound="left")
else:
    print("WARNING: Image 'group.png' failed to load, falling back to emoji.")
    notebook.add(cadre_membre, text="\U0001F464 Membres")
# Configuration de la grille dans le cadre des membres (cadre_membre)
# Colonne 0 (à gauche) : ne s'étire pas (taille fixe)
cadre_membre.grid_columnconfigure(0, weight=0)
# Colonne 1 (à droite) : s'étire pour prendre l’espace restant
cadre_membre.grid_columnconfigure(1, weight=1)
# Ligne 0 : prend toute la hauteur disponible (utile si on veut que le contenu s’étire verticalement)
cadre_membre.grid_rowconfigure(0, weight=1)
# === Création du cadre du formulaire des membres (zone à gauche de l’onglet Membre) ===

form_frame_membre = tk.Frame(cadre_membre, bg="white")
form_frame_membre.grid(row=0, column=0, padx=10, pady=10, sticky="ns")

affichage_membre = tk.Text(form_frame_membre, height=5, bg="white", fg="#333333", font=("Arial", 10))
affichage_membre.pack(fill="x", padx=10, pady=5)
#Fonction pour afficher un message dans la zone de texte des membres
def afficher_message_membres_tab(texte):
    # Insère le texte donné à la fin de la zone de texte, suivi d’un saut de ligne
    affichage_membre.insert(tk.END, texte + "\n")
    affichage_membre.see(tk.END)
# Création d’un dictionnaire pour stocker les champs du formulaire des membres
fields_membre = {}
#  Champ ID Membre
#ID Membre
tk.Label(form_frame_membre, text="ID Membre", **style_label).pack(anchor="w", padx=10)
id_entry = tk.Entry(form_frame_membre, width=30)
id_entry.pack(padx=10)
fields_membre["id_membre"] = id_entry
#Nom
tk.Label(form_frame_membre, text="Nom", **style_label).pack(anchor="w", padx=10)
nom_entry = tk.Entry(form_frame_membre, width=30)
nom_entry.pack(padx=10, pady=3)
fields_membre["nom"] = nom_entry

def enregistrer_membre():
    try:
        membre = biblio.Membre(fields_membre["id_membre"].get().strip(), fields_membre["nom"].get().strip())
        biblio.enregistrer_membre(membre)
        afficher_message_membres_tab(" Membre enregistré.")
        maj_tout()
        # Modifications ici pour vider les champs après ajout
        fields_membre["id_membre"].delete(0, tk.END)
        fields_membre["nom"].delete(0, tk.END)
        # Fin des modifications ---
    except Exception as e:
        afficher_message_membres_tab(f" Erreur : {e}")
#  Fonction pour supprimer un membre

def supprimer_membre():
    try:
        # Appel à la méthode de suppression dans l'objet Bibliotheque
        biblio.supprimer_membre(fields_membre["id_membre"].get().strip())
        # Affiche un message de succès
        afficher_message_membres_tab("🗑 Membre supprimé.")
        maj_tout()
        # --- Vider les champs après suppression par ID ---
        fields_membre["id_membre"].delete(0, tk.END)
        fields_membre["nom"].delete(0, tk.END)
        # --- Fin des modifications ---
    except Exception as e:
        #En cad d'erreur on affiche ceci
        afficher_message_membres_tab(f" Erreur : {e}")

btn_frame_membre = tk.Frame(form_frame_membre, bg="white")
btn_frame_membre.pack(pady=5, anchor="w")

tk.Button(btn_frame_membre, text="Ajouter Membre", bg="#009933", fg="white", font=("Arial", 10, "bold"), command=enregistrer_membre).pack(side="left", padx=5)
tk.Button(btn_frame_membre, text="Supprimer Membre", bg="#cc0000", fg="white", font=("Arial", 10, "bold"), command=supprimer_membre).pack(side="left", padx=5)

if icones["book2_icon"]:
    tk.Label(form_frame_membre, text=" Livres disponibles", image=icones["book2_icon"], compound="left", **style_label).pack(anchor="w", padx=10)
else:
    print("WARNING: Image 'book2.png' failed to load, falling back to plain text.")
    tk.Label(form_frame_membre, text="Livres disponibles", **style_label).pack(anchor="w", padx=10)

livres_disponibles_cb = ttk.Combobox(form_frame_membre, width=50, state="readonly")
livres_disponibles_cb.pack(pady=2)

if icones["open_book_icon"]:
    tk.Label(form_frame_membre, text=" Livres empruntés", image=icones["open_book_icon"], compound="left", **style_label).pack(anchor="w", padx=10)
else:
    print("WARNING: Image 'open-book.png' failed to load, falling back to plain text.")
    tk.Label(form_frame_membre, text="Livres empruntés", **style_label).pack(anchor="w", padx=10)

livres_empruntes_listbox = tk.Listbox(form_frame_membre, width=50, height=6)
livres_empruntes_listbox.pack(pady=2)

def rafraichir_livres_disponibles():
    livres = [f"{livre.isbn} - {livre.titre}" for livre in biblio.livres.values() if livre.statut == "disponible"]
    livres_disponibles_cb['values'] = livres
    livres_disponibles_cb.set(livres[0] if livres else '')
    # --- Vider la sélection actuelle après rafraîchissement ---
    if not livres:
        livres_disponibles_cb.set('')

# === Fonction pour rafraîchir la liste des livres empruntés par le membre sélectionné ===

def rafraichir_livres_empruntes():
    livres_empruntes_listbox.delete(0, tk.END)
    id_membre = fields_membre["id_membre"].get().strip()
    if id_membre in biblio.membres:
        empruntes = biblio.membres[id_membre].livres_empruntes
        for isbn in empruntes:
            if isbn in biblio.livres:
                titre = biblio.livres[isbn].titre
                livres_empruntes_listbox.insert(tk.END, f"{isbn} - {titre}")

def emprunter_livre():
    id_m = fields_membre["id_membre"].get().strip()
    if not id_m:
        afficher_message_membres_tab(" Veuillez saisir l'ID du membre.")
        return
    if not livres_disponibles_cb.get():
        afficher_message_membres_tab("Veuillez sélectionner un livre disponible.")
        return
    isbn = livres_disponibles_cb.get().split(" - ")[0]
    try:
        biblio.emprunter_livre(isbn, id_m)
        afficher_message_membres_tab(f"Livre {isbn} emprunté.")
        maj_tout()
        # --- Vider la Combobox après emprunt réussi ---
        livres_disponibles_cb.set('')
    except Exception as e:
        afficher_message_membres_tab(f" {e}")

def retourner_livre():
    id_m = fields_membre["id_membre"].get().strip()
    selection = livres_empruntes_listbox.curselection()
    if not id_m:
        afficher_message_membres_tab(" Veuillez saisir l'ID du membre.")
        return
    if not selection:
        afficher_message_membres_tab(" Veuillez sélectionner un livre emprunté.")
        return
    isbn = livres_empruntes_listbox.get(selection[0]).split(" - ")[0]
    try:
        biblio.retourner_livre(isbn, id_m)
        afficher_message_membres_tab(f"Livre {isbn} retourné.")
        maj_tout()
        # --- Vider la sélection dans la Listbox après retour réussi ---
        livres_empruntes_listbox.selection_clear(0, tk.END)
    except Exception as e:
        afficher_message_membres_tab(f" {e}")

btn_emprunt_retour_frame = tk.Frame(form_frame_membre, bg="white")
btn_emprunt_retour_frame.pack(pady=5, anchor="w") # Pack this frame after the listbox

tk.Button(btn_emprunt_retour_frame, text="Emprunter livre", bg="#cc6600", fg="white", font=("Arial", 10, "bold"), command=emprunter_livre).pack(side="left", padx=5)
tk.Button(btn_emprunt_retour_frame, text="Retourner livre", bg="#336600", fg="white", font=("Arial", 10, "bold"), command=retourner_livre).pack(side="left", padx=5)

fields_membre["id_membre"].bind("<FocusOut>", lambda e: (rafraichir_livres_empruntes(), rafraichir_livres_disponibles()))


right_pane_membre = tk.Frame(cadre_membre, bg="white")
right_pane_membre.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
right_pane_membre.grid_rowconfigure(0, weight=1) # The table itself expands vertically
right_pane_membre.grid_columnconfigure(0, weight=1) # The table itself expands horizontally

# **MODIFICATION ICI : Utilisation de l'image membre.png pour le titre de la liste des membres**
if icones["member_list_icon"]:
    tk.Label(right_pane_membre, text=" Tous les Membres", image=icones["member_list_icon"], compound="left", font=("Arial", 12, "bold"), bg="white", fg="#003366").pack(fill="x")
else:
    print("WARNING: Image 'membre.png' failed to load, falling back to emoji for Tous les Membres.")
    tk.Label(right_pane_membre, text="👤 Tous les Membres", font=("Arial", 12, "bold"), bg="white", fg="#003366").pack(fill="x")
# **FIN DE LA MODIFICATION**

colonnes_membres = ("ID Membre", "Nom", "Livres Empruntés")
tableau_membres = ttk.Treeview(right_pane_membre, columns=colonnes_membres, show="headings", height=15) # Dedicated table for members

def remplir_champs_membre_depuis_selection(event):
    selection = tableau_membres.selection()
    if not selection:
        fields_membre["id_membre"].delete(0, tk.END)
        fields_membre["nom"].delete(0, tk.END)
        rafraichir_livres_empruntes()
        rafraichir_livres_disponibles()
        return
    item = tableau_membres.item(selection[0])
    valeurs = item['values']
    fields_membre["id_membre"].delete(0, tk.END)
    fields_membre["id_membre"].insert(0, valeurs[0])
    fields_membre["nom"].delete(0, tk.END)
    fields_membre["nom"].insert(0, valeurs[1])
    rafraichir_livres_empruntes()
    rafraichir_livres_disponibles()

tableau_membres.bind("<<TreeviewSelect>>", remplir_champs_membre_depuis_selection)

for col in colonnes_membres:
    tableau_membres.heading(col, text=col)

tableau_membres.column("ID Membre", width=100, anchor="w")
tableau_membres.column("Nom", width=150, anchor="w")
tableau_membres.column("Livres Empruntés", width=250, anchor="w")

tableau_membres.pack(fill="both", expand=True, padx=5, pady=5)

def rafraichir_tableau_membres():
    tableau_membres.delete(*tableau_membres.get_children())
    for i, membre in enumerate(biblio.membres.values()):
        livres_empruntes_noms = []
        for isbn in membre.livres_empruntes:
            if isbn in biblio.livres:
                livres_empruntes_noms.append(biblio.livres[isbn].titre)
            else:
                livres_empruntes_noms.append(f"Inconnu ({isbn})")
        livres_str = ", ".join(livres_empruntes_noms) if livres_empruntes_noms else "Aucun"
        tag = "evenrow" if i % 2 == 0 else "oddrow"
        tableau_membres.insert("", tk.END, values=(
            membre.id_membre,
            membre.nom,
            livres_str
        ), tags=(tag,))


# === Onglet Statistiques ===
cadre_stats = tk.Frame(notebook, bg="white")
if icones["stats_tab"]:
    notebook.add(cadre_stats, text=" Statistiques", image=icones["stats_tab"], compound="left")
else:
    print("WARNING: Image 'analytics.png' failed to load, falling back to emoji.")
    notebook.add(cadre_stats, text=" Statistiques")

tk.Label(cadre_stats, text="Visualisations Statistiques", font=("Arial", 14, "bold"), bg="white", fg="#003366").pack(pady=10)

def diagramme_genre():
    genres = [livre.genre for livre in biblio.livres.values()]
    compteur = Counter(genres)
    if not compteur:
        messagebox.showinfo("Info", "Aucun livre trouvé.")
        return
    plt.figure(figsize=(6, 6))
    plt.pie(compteur.values(), labels=compteur.keys(), autopct='%1.1f%%', startangle=90)
    plt.title("Répartition des Livres par Genre")
    plt.axis('equal')
    plt.tight_layout()
    plt.show()

def histogramme_auteurs():
    auteurs = [livre.auteur for livre in biblio.livres.values()]
    compteur = Counter(auteurs)
    top = compteur.most_common(10)
    if not top:
        messagebox.showinfo("Info", "Aucun auteur trouvé.")
        return
    noms, quantites = zip(*top)
    plt.figure(figsize=(10, 5))
    plt.bar(noms, quantites, color='skyblue')
    plt.title("Top 10 Auteurs les plus populaires")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def courbe_emprunts_30j():
    aujourd_hui = datetime.now().date()
    depuis = aujourd_hui - timedelta(days=30)
    dates = []
    for entry in biblio.historique:
        date_str, isbn, id_membre, action = entry
        if action == "emprunt":
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_obj >= depuis:
                    dates.append(date_obj)
            except:
                continue
    compteur = Counter(dates)
    jours = [depuis + timedelta(days=i) for i in range(31)]
    valeurs = [compteur.get(j, 0) for j in jours]
    plt.figure(figsize=(12, 5))
    plt.plot(jours, valeurs, marker='o', linestyle='-', color='green')
    plt.title("Activité des Emprunts (30 derniers jours)")
    plt.xlabel("Date")
    plt.ylabel("Nombre d'emprunts")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

boutons_frame = tk.Frame(cadre_stats, bg="white")
boutons_frame.pack(pady=5)

if icones["pie_chart"]:
    btn_diagramme_genre = tk.Button(boutons_frame, text=" Diagramme par Genre",
                                    image=icones["pie_chart"], compound="left",
                                    bg="#0059b3", fg="white", font=("Arial", 10, "bold"),
                                    command=diagramme_genre)
else:
    print("WARNING: Image 'pie-chart.png' failed to load, falling back to emoji for Diagramme par Genre.")
    btn_diagramme_genre = tk.Button(boutons_frame, text="Diagramme par Genre",
                                    bg="#0059b3", fg="white", font=("Arial", 10, "bold"),
                                    command=diagramme_genre)
btn_diagramme_genre.pack(side=tk.LEFT, padx=10)

if icones["bar_chart"]:
    btn_histogramme_auteurs = tk.Button(boutons_frame, text=" Top 10 Auteurs",
                                        image=icones["bar_chart"], compound="left",
                                        bg="#0059b3", fg="white", font=("Arial", 10, "bold"),
                                        command=histogramme_auteurs)
else:
    print("WARNING: Image 'analysis.png' failed to load, falling back to emoji for Top 10 Auteurs.")
    btn_histogramme_auteurs = tk.Button(boutons_frame, text=" Top 10 Auteurs",
                                        bg="#0059b3", fg="white", font=("Arial", 10, "bold"),
                                        command=histogramme_auteurs)
btn_histogramme_auteurs.pack(side=tk.LEFT, padx=10)

if icones["line_graph"]:
    btn_courbe_emprunts = tk.Button(boutons_frame, text=" Activité des emprunts (30j)",
                                    image=icones["line_graph"], compound="left",
                                    bg="#0059b3", fg="white", font=("Arial", 10, "bold"),
                                    command=courbe_emprunts_30j)
else:
    print("WARNING: Image 'graph.png' failed to load, falling back to emoji for Activité des emprunts.")
    btn_courbe_emprunts = tk.Button(boutons_frame, text=" Activité des emprunts (30j)",
                                    bg="#0059b3", fg="white", font=("Arial", 10, "bold"),
                                    command=courbe_emprunts_30j)
btn_courbe_emprunts.pack(side=tk.LEFT, padx=10)


def maj_tout():
    rafraichir_tableau_livres_livres_tab() # Refresh table on Livres tab
    rafraichir_tableau_membres() # Refresh table on Membres tab
    rafraichir_livres_disponibles() # Refresh combobox on Membres tab
    rafraichir_livres_empruntes() # Refresh listbox on Membres tab


def on_onglet_change(event):
    onglet_courant = notebook.tab(notebook.select(), "text")


    form_frame_livre.grid_forget()
    right_pane_livre.grid_forget()
    form_frame_membre.grid_forget()
    right_pane_membre.grid_forget()

    if "Livres" in onglet_courant:
        # Show specific elements for Livres tab
        form_frame_livre.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        right_pane_livre.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        rafraichir_tableau_livres_livres_tab() # Ensure the table is refreshed
        # Clear fields when switching to Livres tab to ensure a clean start
        for entry_field in fields_livre.values():
            entry_field.delete(0, tk.END)
    elif "Membres" in onglet_courant:
        form_frame_membre.grid(row=0, column=0, padx=10, pady=10, sticky="ns")
        right_pane_membre.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        maj_tout()
        fields_membre["id_membre"].delete(0, tk.END)
        fields_membre["nom"].delete(0, tk.END)
        livres_disponibles_cb.set('')
        livres_empruntes_listbox.delete(0, tk.END)


notebook.bind("<<NotebookTabChanged>>", on_onglet_change)

on_onglet_change(None)

bottom_frame = tk.Frame(fenetre, bg="white")
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)

btn_quitter_bas = tk.Button(
    bottom_frame,
    text="Quitter",
    bg="#0066cc", fg="white",
    font=("Arial", 10, "bold"),
    width=15,
    command=quitter
)
btn_quitter_bas.pack(pady=5)

fenetre.mainloop()