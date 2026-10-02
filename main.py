import webbrowser
from urllib.parse import quote

from kivy.lang import Builder
from kivymd.app import MDApp

from database import (
    creer_base,
    obtenir_produits,
    ajouter_produit,
    modifier_produit,
    supprimer_produit,
    obtenir_publications,
    ajouter_publication,
    modifier_publication,
    supprimer_publication
)

from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

import os
import shutil

from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button


KV = """
MDScreen:

    MDBoxLayout:
        orientation: "vertical"

        # =========================
        # BARRE DU HAUT
        # =========================
        MDTopAppBar:
            title: "MON APPLICATION"

        # =========================
        # ZONE PRINCIPALE
        # =========================
        MDScreenManager:
            id: screen_manager

            # =========================
            # ACCUEIL
            # =========================
            MDScreen:
                name: "accueil"

                MDBoxLayout:
                    orientation: "vertical"
                    padding: "30dp"
                    spacing: "20dp"

                    MDLabel:
                        text: "Bienvenue !"
                        halign: "center"
                        font_size: "30sp"
                        bold: True

                    MDLabel:
                        text: "Découvrez nos produits et nos informations."
                        halign: "center"
                        font_size: "18sp"

            # =========================
            # PRODUITS
            # =========================
            MDScreen:
                name: "produits"

                ScrollView:

                    MDBoxLayout:
                        id: produits_container

                        orientation: "vertical"
                        padding: "15dp"
                        spacing: "20dp"
                        size_hint_y: None
                        height: self.minimum_height

                        MDLabel:
                            text: "NOS PRODUITS"
                            halign: "center"
                            font_size: "30sp"
                            bold: True
                            size_hint_y: None
                            height: "50dp"

            # =========================
            # INFOS
            # =========================
            MDScreen:
                name: "infos"

                ScrollView:

                    MDBoxLayout:
                        orientation: "vertical"
                        padding: "15dp"
                        spacing: "20dp"
                        size_hint_y: None
                        height: self.minimum_height

                        MDLabel:
                            text: "INFOS & ACTUALITÉS"
                            halign: "center"
                            font_size: "30sp"
                            bold: True
                            size_hint_y: None
                            height: "50dp"

                        MDBoxLayout:
                            id: publications_container
                            orientation: "vertical"
                            spacing: "20dp"
                            size_hint_y: None
                            height: self.minimum_height

            # =========================
            # À PROPOS
            # =========================
            MDScreen:
                name: "apropos"

                MDBoxLayout:
                    orientation: "vertical"
                    padding: "30dp"
                    spacing: "20dp"

                    MDLabel:
                        text: "À PROPOS"
                        halign: "center"
                        font_size: "30sp"
                        bold: True

                    MDLabel:
                        text: "Informations sur notre entreprise."
                        halign: "center"
                        font_size: "18sp"

                        MDScreen:
    
            # =========================
            # ADMINISTRATION
            # =========================
            MDScreen:
                name: "admin"

                ScrollView:

                    MDBoxLayout:
                        orientation: "vertical"
                        padding: "30dp"
                        spacing: "20dp"
                        size_hint_y: None
                        height: self.minimum_height

                        MDLabel:
                            text: "ADMINISTRATION"
                            halign: "center"
                            font_size: "30sp"
                            bold: True
                            size_hint_y: None
                            height: "50dp"

                        MDTextField:
                            id: nom_produit
                            mode: "outlined"

                            MDTextFieldHintText:
                                text: "Nom du produit"

                        MDTextField:
                            id: prix_produit
                            mode: "outlined"

                            MDTextFieldHintText:
                                text: "Prix"

                        MDTextField:
                            id: description_produit
                            mode: "outlined"

                            MDTextFieldHintText:
                                text: "Description"

                        MDTextField:
                            id: image_produit
                            mode: "outlined"

                            MDTextFieldHintText:
                                text: "Image"

                        MDButton:
                            style: "outlined"
                            pos_hint: {"center_x": 0.5}
                            on_release: app.choisir_image()

                            MDButtonText:
                                text: "📷 Choisir une image"

                        MDButton:
                            style: "filled"
                            pos_hint: {"center_x": 0.5}
                            on_release: app.ajouter_produit_interface()

                            MDButtonText:
                                text: "Ajouter le produit"

                        MDButton:
                            style: "filled"
                            pos_hint: {"center_x": 0.5}
                            on_release: app.enregistrer_modification()

                            MDButtonText:
                                text: "Enregistrer la modification"

                        MDLabel:
                            text: "PRODUITS EXISTANTS"
                            halign: "center"
                            font_size: "24sp"
                            bold: True
                            size_hint_y: None
                            height: "50dp"

                        MDBoxLayout:
                            id: admin_produits_container
                            orientation: "vertical"
                            spacing: "10dp"
                            size_hint_y: None
                            height: self.minimum_height

                        MDLabel:
                            text: "GESTION DES PUBLICATIONS"
                            halign: "center"
                            font_size: "26sp"
                            bold: True
                            size_hint_y: None
                            height: "50dp"

                        MDTextField:
                            id: titre_publication
                            mode: "outlined"

                            MDTextFieldHintText:
                                text: "Titre de la publication"

                        MDTextField:
                            id: contenu_publication
                            mode: "outlined"

                            MDTextFieldHintText:
                                text: "Contenu de la publication"

                        MDTextField:
                            id: date_publication
                            mode: "outlined"

                            MDTextFieldHintText:
                                text: "Date de publication"

                        MDTextField:
                            id: image_publication
                            mode: "outlined"

                            MDTextFieldHintText:
                                text: "Image de la publication"

                        MDButton:
                            style: "outlined"
                            pos_hint: {"center_x": 0.5}
                            on_release: app.choisir_image_publication()

                            MDButtonText:
                                text: "📷 Choisir une image"

                        MDButton:
                            style: "filled"
                            pos_hint: {"center_x": 0.5}
                            on_release: app.ajouter_publication_interface()

                            MDButtonText:
                                text: "Ajouter la publication"

                        MDButton:
                            style: "filled"
                            pos_hint: {"center_x": 0.5}
                            on_release: app.enregistrer_modification_publication()

                            MDButtonText:
                                text: "Enregistrer la modification"

                        MDLabel:
                            text: "PUBLICATIONS EXISTANTES"
                            halign: "center"
                            font_size: "24sp"
                            bold: True
                            size_hint_y: None
                            height: "50dp"

                        MDBoxLayout:
                            id: admin_publications_container
                            orientation: "vertical"
                            spacing: "10dp"
                            size_hint_y: None
                            height: self.minimum_height    

        # =========================
        # NAVIGATION
        # =========================
        MDBoxLayout:
            size_hint_y: None
            height: "70dp"
            spacing: "5dp"
            padding: "5dp"

            MDButton:
                style: "filled"
                on_release: screen_manager.current = "accueil"

                MDButtonIcon:
                    icon: "home"

                MDButtonText:
                    text: "Accueil"

            MDButton:
                style: "filled"
                on_release: screen_manager.current = "produits"

                MDButtonIcon:
                    icon: "shopping"

                MDButtonText:
                    text: "Produits"

            MDButton:
                style: "filled"
                on_release: screen_manager.current = "infos"

                MDButtonIcon:
                    icon: "newspaper"

                MDButtonText:
                    text: "Infos"

            MDButton:
                style: "filled"
                on_release: screen_manager.current = "apropos"

                MDButtonIcon:
                    icon: "information"

                MDButtonText:
                    text: "À propos"
    
            MDButton:
                style: "filled"
                on_release: screen_manager.current = "admin"

                MDButtonIcon:
                    icon: "cog"

                MDButtonText:
                    text: "Admin"       
"""


class VenteApp(MDApp):

    produit_a_modifier = None

    publication_a_modifier = None

    def commander_whatsapp(self, produit, prix):

        numero = "22890000000"

        message = (
            f"Bonjour, je souhaite commander "
            f"{produit} au prix de {prix}."
        )

        url = f"https://wa.me/{numero}?text={quote(message)}"

        webbrowser.open(url)

    def afficher_produits(self):

        produits = obtenir_produits()

        container = self.root.ids.produits_container

        for id_produit, nom, prix, description, image in produits:

            carte = Builder.load_string(f"""
MDCard:
    orientation: "vertical"
    size_hint_y: None
    height: "400dp"
    padding: "10dp"
    spacing: "10dp"
    elevation: 3

    Image:
        source: "{image}"
        size_hint_y: None
        height: "200dp"

    MDLabel:
        text: "{nom}"
        font_size: "22sp"
        bold: True
        halign: "center"
        size_hint_y: None
        height: "40dp"

    MDLabel:
        text: "{prix}"
        font_size: "20sp"
        halign: "center"
        size_hint_y: None
        height: "40dp"

    MDLabel:
        text: "{description}"
        halign: "center"
        size_hint_y: None
        height: "50dp"

    MDButton:
        style: "filled"
        pos_hint: {{"center_x": 0.5}}
        size_hint_x: None
        width: "220dp"
        on_release: app.commander_whatsapp("{nom}", "{prix}")

        MDButtonIcon:
            icon: "whatsapp"

        MDButtonText:
            text: "Commander"
""")

            container.add_widget(carte)
    
    def actualiser_produits(self):

        container = self.root.ids.produits_container

        # Supprimer les anciennes cartes
        container.clear_widgets()

        # Recréer les cartes
        self.afficher_produits()
    
    def afficher_produits_admin(self):

       produits = obtenir_produits()

       container = self.root.ids.admin_produits_container

       container.clear_widgets()

       for id_produit, nom, prix, description, image in produits:

           carte = Builder.load_string(f"""MDCard:
    orientation: "horizontal"
    size_hint_y: None
    height: "100dp"
    padding: "10dp"
    spacing: "15dp"

    MDBoxLayout:
        orientation: "vertical"
        spacing: "5dp"

        MDLabel:
            text: "{nom}"
            bold: True
            font_size: "18sp"
            size_hint_y: None
            height: "30dp"

        MDLabel:
            text: "{prix}"
            font_size: "16sp"
            size_hint_y: None
            height: "25dp"

    MDBoxLayout:
        orientation: "horizontal"
        spacing: "10dp"
        size_hint_x: None
        width: "270dp"
        pos_hint: {{"center_y": 0.5}}

    MDButton:
        style: "filled"
        size_hint_x: None
        width: "130dp"
        on_release: app.charger_produit_modifier({id_produit})

        MDButtonText:
            text: "Modifier"

    MDButton:
        style: "filled"
        size_hint_x: None
        width: "130dp"
        on_release: app.supprimer_produit_interface({id_produit})

        MDButtonText:
            text: "Supprimer"
""")

           container.add_widget(carte)


    def charger_produit_modifier(self, id_produit):

        produits = obtenir_produits()

        for produit in produits:

            if produit[0] == id_produit:

                self.produit_a_modifier = id_produit

                self.root.ids.nom_produit.text = produit[1]
                self.root.ids.prix_produit.text = produit[2]
                self.root.ids.description_produit.text = produit[3]
                self.root.ids.image_produit.text = produit[4]

                print("Produit chargé pour modification :", produit[1])

                break

    def supprimer_produit_interface(self, id_produit):

        produits = obtenir_produits()

        nom_produit = ""

        for produit in produits:

             if produit[0] == id_produit:
                nom_produit = produit[1]
                break

        self.produit_a_supprimer = id_produit

        self.dialog_suppression = MDDialog()

        contenu = MDBoxLayout(
                     orientation="vertical",
                     spacing="15dp",
                     padding="20dp",
                     size_hint_y=None,
                     height="130dp"
                     )

        titre = MDLabel(
                text="Supprimer le produit ?",
                font_size="22sp",
                bold=True,
                halign="center",
                size_hint_y=None,
                height="40dp"
                )

        message = MDLabel(
                text=f"Êtes-vous sûr de vouloir supprimer « {nom_produit} » ?",
                halign="center",
                size_hint_y=None,
                height="50dp"
                )

        contenu.add_widget(titre)
        contenu.add_widget(message)

        self.dialog_suppression.add_widget(contenu)

        boutons = MDBoxLayout(
                orientation="horizontal",
                spacing="10dp",
                size_hint_y=None,
                height="50dp",
                padding="10dp"
                )

        bouton_annuler = MDButton(
                style="text",
                on_release=self.annuler_suppression
                )

        bouton_annuler.add_widget(
            MDButtonText(
                text="ANNULER"
            )
        )

        bouton_supprimer = MDButton(
                style="filled",
                on_release=self.confirmer_suppression
        )

        bouton_supprimer.add_widget(
            MDButtonText(
                text="SUPPRIMER"
            )
        )

        boutons.add_widget(bouton_annuler)
        boutons.add_widget(bouton_supprimer)

        self.dialog_suppression.add_widget(boutons)

        self.dialog_suppression.open()


    def annuler_suppression(self, instance):

        self.dialog_suppression.dismiss()


    def confirmer_suppression(self, instance):

        supprimer_produit(self.produit_a_supprimer)

        self.dialog_suppression.dismiss()

        self.actualiser_produits()

        self.afficher_produits_admin()

        self.produit_a_supprimer = None

        print("Produit supprimé avec succès !")


    def choisir_image(self):

        layout = BoxLayout(
           orientation="vertical",
           spacing=10,
           padding=10
        )

        filechooser = FileChooserListView(
           path=os.path.expanduser("~"),
           filters=["*.png", "*.jpg", "*.jpeg", "*.webp"]
        )

        layout.add_widget(filechooser)

        boutons = BoxLayout(
           orientation="horizontal",
           size_hint_y=None,
           height="50dp",
           spacing=10
           )

        bouton_annuler = Button(
           text="Annuler"
        )

        bouton_selectionner = Button(
           text="Sélectionner"
        )

        boutons.add_widget(bouton_annuler)
        boutons.add_widget(bouton_selectionner)

        layout.add_widget(boutons)

        popup = Popup(
           title="Choisir une image",
           content=layout,
           size_hint=(0.9, 0.9)
           )

        def annuler(instance):
           popup.dismiss()

        def selectionner(instance):

           if not filechooser.selection:
              print("Aucune image sélectionnée.")
              return

           fichier_source = filechooser.selection[0]

           dossier_images = os.path.join(
              os.path.dirname(__file__),
               "images"
            )

           os.makedirs(dossier_images, exist_ok=True)

           nom_fichier = os.path.basename(fichier_source)

           fichier_destination = os.path.join(
              dossier_images,
              nom_fichier
            )

           if os.path.abspath(fichier_source) != os.path.abspath(fichier_destination):

              shutil.copy2(
                  fichier_source,
                  fichier_destination
              )

           self.root.ids.image_produit.text = (
              f"images/{nom_fichier}"
              )

           print("Image sélectionnée :", nom_fichier)

           popup.dismiss()

           bouton_annuler.bind(
               on_release=annuler
           )

        bouton_selectionner.bind(
           on_release=selectionner
           )

        popup.open()

    
    def choisir_image_publication(self):

        layout = BoxLayout(
           orientation="vertical",
           spacing=10,
           padding=10
        )

        filechooser = FileChooserListView(
           path=os.path.expanduser("~"),
           filters=["*.png", "*.jpg", "*.jpeg", "*.webp"]
        )

        layout.add_widget(filechooser)

        boutons = BoxLayout(
           orientation="horizontal",
           size_hint_y=None,
           height="50dp",
           spacing=10
        )

        bouton_annuler = Button(
           text="Annuler"
        )

        bouton_selectionner = Button(
           text="Sélectionner"
        )

        boutons.add_widget(bouton_annuler)
        boutons.add_widget(bouton_selectionner)

        layout.add_widget(boutons)

        popup = Popup(
           title="Choisir une image pour la publication",
           content=layout,
           size_hint=(0.9, 0.9)
        )

        def annuler(instance):
           popup.dismiss()

        def selectionner(instance):

           if not filechooser.selection:
               print("Aucune image sélectionnée.")
               return

           fichier_source = filechooser.selection[0]

           dossier_images = os.path.join(
               os.path.dirname(__file__),
               "images"
            )

           os.makedirs(dossier_images, exist_ok=True)

           nom_fichier = os.path.basename(fichier_source)

           fichier_destination = os.path.join(
               dossier_images,
               nom_fichier
            )

           if os.path.abspath(fichier_source) != os.path.abspath(fichier_destination):

               shutil.copy2(
                   fichier_source,
                   fichier_destination
           )

           self.root.ids.image_publication.text = (
                f"images/{nom_fichier}"
           )

           print("Image de publication sélectionnée :", nom_fichier)

        popup.dismiss()

        bouton_annuler.bind(
           on_release=annuler
        )

        bouton_selectionner.bind(
           on_release=selectionner
        )

        popup.open()



    def enregistrer_modification(self):

        if self.produit_a_modifier is None:

            print("Aucun produit sélectionné pour modification.")
            return

        nom = self.root.ids.nom_produit.text
        prix = self.root.ids.prix_produit.text
        description = self.root.ids.description_produit.text
        image = self.root.ids.image_produit.text

        if not nom or not prix:

            print("Le nom et le prix sont obligatoires.")
            return

        modifier_produit(
            self.produit_a_modifier,
            nom,
            prix,
            description,
            image
         )

        print("Produit modifié avec succès !")

        self.actualiser_produits()

        self.afficher_produits_admin()

        self.produit_a_modifier = None



    def ajouter_produit_interface(self):

              nom = self.root.ids.nom_produit.text
              prix = self.root.ids.prix_produit.text
              description = self.root.ids.description_produit.text
              image = self.root.ids.image_produit.text

              if not nom or not prix:
                 print("Le nom et le prix sont obligatoires.")
                 return

              ajouter_produit(
                  nom,
              prix,
              description,
              image
                  )

              print("Produit ajouté avec succès !")
              self.actualiser_produits()


    def ajouter_publication_interface(self):

        titre = self.root.ids.titre_publication.text
        contenu = self.root.ids.contenu_publication.text
        date = self.root.ids.date_publication.text
        image = self.root.ids.image_publication.text

        if not titre:
            print("Le titre de la publication est obligatoire.")
            return

        ajouter_publication(
           titre,
           contenu,
           date,
           image
        )

        print("Publication ajoutée avec succès !")

        # TEST : vérifier ce que SQLite contient réellement
        publications = obtenir_publications()

        print("===================================")
        print("PUBLICATIONS DANS LA BASE :")
        print(publications)
        print("NOMBRE DE PUBLICATIONS :", len(publications))
        print("===================================")

        # Actualiser la liste des publications dans ADMIN
        self.afficher_publications_admin()

        # Actualiser la liste des publications dans INFOS
        self.afficher_publications()

   
    def charger_publication_modifier(self, id_publication):

        publications = obtenir_publications()

        for publication in publications:

            if publication[0] == id_publication:

               self.publication_a_modifier = id_publication

               self.root.ids.titre_publication.text = publication[1]
               self.root.ids.contenu_publication.text = publication[2]
               self.root.ids.date_publication.text = publication[3]
               self.root.ids.image_publication.text = publication[4]

               print(
                    "Publication chargée pour modification :",
                    publication[1]
               )

               break


    def enregistrer_modification_publication(self):

        if self.publication_a_modifier is None:

            print("Aucune publication sélectionnée pour modification.")
            return

        titre = self.root.ids.titre_publication.text
        contenu = self.root.ids.contenu_publication.text
        date = self.root.ids.date_publication.text
        image = self.root.ids.image_publication.text

        if not titre:

            print("Le titre de la publication est obligatoire.")
            return

        modifier_publication(
            self.publication_a_modifier,
            titre,
            contenu,
            date,
            image
        )

        print("Publication modifiée avec succès !")

        self.afficher_publications_admin()

        # Actualiser INFOS
        self.afficher_publications()

        self.publication_a_modifier = None



    def afficher_publications_admin(self):

        publications = obtenir_publications()

        container = self.root.ids.admin_publications_container

        container.clear_widgets()

        for id_publication, titre, contenu, date, image in publications:

            carte = Builder.load_string(f"""MDCard:
    orientation: "horizontal"
    size_hint_y: None
    height: "120dp"
    padding: "10dp"
    spacing: "15dp"

    MDBoxLayout:
        orientation: "vertical"
        spacing: "5dp"

        MDLabel:
            text: "{titre}"
            bold: True
            font_size: "18sp"
            size_hint_y: None
            height: "30dp"

        MDLabel:
            text: "{date}"
            font_size: "15sp"
            size_hint_y: None
            height: "25dp"

        MDLabel:
            text: "{contenu}"
            font_size: "14sp"

    MDBoxLayout:
        orientation: "horizontal"
        spacing: "10dp"
        size_hint_x: None
        width: "270dp"
        pos_hint: {{"center_y": 0.5}}

        MDButton:
            style: "filled"
            size_hint_x: None
            width: "130dp"
            on_release: app.charger_publication_modifier({id_publication})

            MDButtonText:
                text: "Modifier"

        MDButton:
            style: "filled"
            size_hint_x: None
            width: "130dp"
            on_release: app.supprimer_publication_interface({id_publication})

            MDButtonText:
                text: "Supprimer"
""")

            container.add_widget(carte)


    def supprimer_publication_interface(self, id_publication):

        publications = obtenir_publications()

        titre_publication = ""

        for publication in publications:

            if publication[0] == id_publication:
                titre_publication = publication[1]
                break

        self.publication_a_supprimer = id_publication

        self.dialog_suppression_publication = MDDialog()

        contenu = MDBoxLayout(
            orientation="vertical",
            spacing="15dp",
            padding="20dp",
            size_hint_y=None,
            height="130dp"
        )

        titre = MDLabel(
            text="Supprimer la publication ?",
            font_size="22sp",
            bold=True,
            halign="center",
            size_hint_y=None,
            height="40dp"
            )

        message = MDLabel(
            text=f"Êtes-vous sûr de vouloir supprimer « {titre_publication} » ?",
            halign="center",
            size_hint_y=None,
            height="50dp"
            )

        contenu.add_widget(titre)
        contenu.add_widget(message)

        self.dialog_suppression_publication.add_widget(contenu)

        boutons = MDBoxLayout(
            orientation="horizontal",
            spacing="10dp",
            size_hint_y=None,
            height="50dp",
            padding="10dp"
            )

        bouton_annuler = MDButton(
            style="text",
            on_release=self.annuler_suppression_publication
        )

        bouton_annuler.add_widget(
            MDButtonText(
                text="ANNULER"
            )
        )

        bouton_supprimer = MDButton(
            style="filled",
            on_release=self.confirmer_suppression_publication
        )

        bouton_supprimer.add_widget(
            MDButtonText(
                text="SUPPRIMER"
            )
        )

        boutons.add_widget(bouton_annuler)
        boutons.add_widget(bouton_supprimer)

        self.dialog_suppression_publication.add_widget(boutons)

        self.dialog_suppression_publication.open()



    def annuler_suppression_publication(self, instance):

        if hasattr(self, "dialog_suppression_publication"):
            self.dialog_suppression_publication.dismiss()


    def confirmer_suppression_publication(self, instance):

        if self.publication_a_supprimer is None:
            return

    # Supprimer réellement dans la base
        supprimer_publication(
            self.publication_a_supprimer
        )

    # Fermer immédiatement la fenêtre de confirmation
        if hasattr(self, "dialog_suppression_publication"):
            self.dialog_suppression_publication.dismiss()

    # Réinitialiser l'identifiant
        self.publication_a_supprimer = None

    # Actualiser les deux listes
        self.afficher_publications_admin()
        self.afficher_publications()

        print("Publication supprimée avec succès !")


    
    def afficher_publications(self):

        publications = obtenir_publications()

        container = self.root.ids.publications_container

        container.clear_widgets()

        for id_publication, titre, contenu, date, image in publications:

            carte = Builder.load_string(f"""
MDCard:
    orientation: "vertical"
    size_hint_y: None
    height: "400dp"
    padding: "10dp"
    spacing: "10dp"
    elevation: 3

    Image:
        source: "{image}"
        size_hint_y: None
        height: "200dp"

    MDLabel:
        text: "{titre}"
        font_size: "22sp"
        bold: True
        halign: "center"
        size_hint_y: None
        height: "45dp"

    MDLabel:
        text: "{date}"
        font_size: "15sp"
        halign: "center"
        size_hint_y: None
        height: "30dp"

    MDLabel:
        text: "{contenu}"
        font_size: "16sp"
        halign: "center"
        size_hint_y: None
        height: "100dp"
""")

            container.add_widget(carte)


    def build(self):

        creer_base()

        interface = Builder.load_string(KV)

        self.root = interface

        self.afficher_produits()

        self.afficher_produits_admin()

        self.afficher_publications_admin()

        self.afficher_publications()

        return interface


if __name__ == "__main__":
    VenteApp().run()