import sqlite3


def creer_base():

    connexion = sqlite3.connect("database.db")
    curseur = connexion.cursor()

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prix TEXT NOT NULL,
            description TEXT,
            image TEXT
        )
    """)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            contenu TEXT,
            date TEXT,
            image TEXT
        )
    """)

    # Vérifier si des produits existent déjà
    curseur.execute("SELECT COUNT(*) FROM produits")
    nombre_produits = curseur.fetchone()[0]

    if nombre_produits == 0:

        produits = [
            (
                "Produit 1",
                "25 000 FCFA",
                "Description de notre produit.",
                "images/produit1.jpg"
            ),
            (
                "Produit 2",
                "15 000 FCFA",
                "Description de notre deuxième produit.",
                "images/produit2.jpg"
            )
        ]

        curseur.executemany("""
            INSERT INTO produits
            (nom, prix, description, image)
            VALUES (?, ?, ?, ?)
        """, produits)

        print("2 produits ajoutés à la base de données.")

    else:
        print("Les produits existent déjà.")

    connexion.commit()
    connexion.close()

def obtenir_produits():

    connexion = sqlite3.connect("database.db")
    curseur = connexion.cursor()

    curseur.execute("""
        SELECT id, nom, prix, description, image
        FROM produits
    """)

    produits = curseur.fetchall()

    connexion.close()

    return produits


def ajouter_produit(nom, prix, description, image):

    connexion = sqlite3.connect("database.db")
    curseur = connexion.cursor()

    curseur.execute("""
        INSERT INTO produits
        (nom, prix, description, image)
        VALUES (?, ?, ?, ?)
    """, (nom, prix, description, image))

    connexion.commit()
    connexion.close()

def modifier_produit(id_produit, nom, prix, description, image):

    connexion = sqlite3.connect("database.db")
    curseur = connexion.cursor()

    curseur.execute("""
        UPDATE produits
        SET nom = ?,
            prix = ?,
            description = ?,
            image = ?
        WHERE id = ?
    """, (nom, prix, description, image, id_produit))

    connexion.commit()
    connexion.close()

def supprimer_produit(id_produit):

    connexion = sqlite3.connect("database.db")
    curseur = connexion.cursor()

    curseur.execute("""
        DELETE FROM produits
        WHERE id = ?
    """, (id_produit,))

    connexion.commit()
    connexion.close()

    print("Produit supprimé avec succès !")


def obtenir_publications():

    connexion = sqlite3.connect("database.db")
    curseur = connexion.cursor()

    curseur.execute("""
        SELECT id, titre, contenu, date, image
        FROM publications
        ORDER BY id DESC
    """)

    publications = curseur.fetchall()

    connexion.close()

    return publications


def ajouter_publication(titre, contenu, date, image):

    connexion = sqlite3.connect("database.db")
    curseur = connexion.cursor()

    curseur.execute("""
        INSERT INTO publications
        (titre, contenu, date, image)
        VALUES (?, ?, ?, ?)
    """, (titre, contenu, date, image))

    connexion.commit()
    connexion.close()


def modifier_publication(id_publication, titre, contenu, date, image):

    connexion = sqlite3.connect("database.db")
    curseur = connexion.cursor()

    curseur.execute("""
        UPDATE publications
        SET titre = ?,
            contenu = ?,
            date = ?,
            image = ?
        WHERE id = ?
    """, (titre, contenu, date, image, id_publication))

    connexion.commit()
    connexion.close()


def supprimer_publication(id_publication):

    connexion = sqlite3.connect("database.db")
    curseur = connexion.cursor()

    curseur.execute("""
        DELETE FROM publications
        WHERE id = ?
    """, (id_publication,))

    connexion.commit()
    connexion.close()

    print("Publication supprimée avec succès !")    

if __name__ == "__main__":
    creer_base()