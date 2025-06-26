import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime, timedelta

def diagramme_genre(biblio):
    """
    Affiche un diagramme circulaire représentant la répartition des livres par genre.
    :param biblio: instance de Bibliotheque avec attribut livres (dict)
    """
    genres = [livre.genre for livre in biblio.livres.values()]
    compteur = Counter(genres)
    if not compteur:
        print("Aucun livre dans la bibliothèque.")
        return

    plt.figure(figsize=(6, 6))
    #circulaire par genre
    plt.pie(
        compteur.values(),
        labels=compteur.keys(),
        autopct='%1.1f%%',
        startangle=90,
        shadow=True,
        textprops={'fontsize': 10}
    )
    plt.title("Répartition des livres par genre")
    plt.axis('equal')  # Assure un cercle parfait
    plt.show()


def histogramme_auteurs(biblio):
    """
    Affiche un histogramme des 10 auteurs les plus populaires.
    :param biblio: instance de Bibliotheque avec attribut livres (dict)
    """
    auteurs = [livre.auteur for livre in biblio.livres.values()]
    compteur = Counter(auteurs)
    top = compteur.most_common(10)
    if not top:
        print("Aucun auteur trouvé.")
        return

    auteurs, quantites = zip(*top)
    plt.figure(figsize=(8, 5))
    #bar
    plt.bar(auteurs, quantites, color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.title("Top 10 des auteurs les plus populaires")
    plt.ylabel("Nombre de livres")
    plt.tight_layout()
    plt.show()


def courbe_activite_emprunts(biblio):
    """
    Affiche la courbe temporelle de l'activité des emprunts sur les 30 derniers jours.
    :param biblio: instance de Bibliotheque avec attribut historique (list de tuples)
    """
    today = datetime.now().date()
    date_limite = today - timedelta(days=30)

    # Extraire les dates des emprunts récents
    dates_emprunts = [
        datetime.strptime(entry[0], "%Y-%m-%d").date()
        for entry in biblio.historique
        if entry[3] == "emprunt" and datetime.strptime(entry[0], "%Y-%m-%d").date() >= date_limite
    ]

    compteur = Counter(dates_emprunts)

    jours = [date_limite + timedelta(days=i) for i in range(31)]
    valeurs = [compteur.get(jour, 0) for jour in jours]

    plt.figure(figsize=(10, 5))
    plt.plot(jours, valeurs, marker='o', linestyle='-', color='tab:blue')
    plt.xticks(rotation=45)
    plt.title("Activité des emprunts (30 derniers jours)")
    plt.xlabel("Date")
    plt.ylabel("Nombre d'emprunts")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
