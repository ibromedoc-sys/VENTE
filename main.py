import webbrowser
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.navigationbar import (
    MDNavigationBar,
    MDNavigationItem,
    MDNavigationItemIcon,
    MDNavigationItemLabel,
)

from database import (
    creer_base,
    administrateur_connecte,
    authentifier_administrateur,
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
from kivy.uix.label import Label as KivyLabel
from kivy.uix.textinput import TextInput


def kv_escape(value):
    if value is None:
        return ""

    return (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


class BaseNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()
    screen_name = StringProperty()


KV = """
<BaseNavigationItem>:
    MDNavigationItemIcon:
        icon: root.icon

    MDNavigationItemLabel:
        text: root.text

MDScreen:

    MDBoxLayout:
        orientation: "vertical"
        size_hint: None, None
        size: root.size
        pos: root.pos

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
        MDNavigationBar:
            id: navigation_bar
            on_switch_tabs: app.on_switch_tabs(*args)

            BaseNavigationItem:
                icon: "home"
                text: "Accueil"
                screen_name: "accueil"
                active: True

            BaseNavigationItem:
                icon: "shopping"
                text: "Produits"
                screen_name: "produits"

            BaseNavigationItem:
                icon: "newspaper"
                text: "Infos"
                screen_name: "infos"

            BaseNavigationItem:
                icon: "information"
                text: "À propos"
                screen_name: "apropos"

            BaseNavigationItem:
                icon: "cog"
                text: "Admin"
                screen_name: "admin"
"""


class VenteApp(MDApp):

    produit_a_modifier = None

    publication_a_modifier = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._database_executor = ThreadPoolExecutor(max_workers=4)

    def _executer_en_arriere_plan(self, operation, on_success=None, on_error=None):
        future = self._database_executor.submit(operation)

        def terminer(tache):
            try:
                resultat = tache.result()
            except Exception as error:
                Clock.schedule_once(
                    lambda dt, error=error: (
                        on_error(error) if on_error else self._afficher_erreur(error)
                    ),
                    0,
                )
                return

            if on_success:
                Clock.schedule_once(
                    lambda dt, resultat=resultat: on_success(resultat), 0
                )

        future.add_done_callback(terminer)

    def _afficher_erreur(self, error):
        Popup(
            title="Erreur de connexion",
            content=KivyLabel(
                text=str(error),
                text_size=(None, None),
            ),
            size_hint=(0.9, None),
            height="180dp",
        ).open()

    def _executer_action_admin(self, operation, on_success):
        if administrateur_connecte():
            self._executer_en_arriere_plan(operation, on_success)
            return
        self._demander_connexion_admin(operation, on_success)

    def _demander_connexion_admin(self, operation, on_success):
        contenu = BoxLayout(
            orientation="vertical",
            spacing="10dp",
            padding="12dp",
        )
        contenu.add_widget(KivyLabel(text="Connexion administrateur Firebase"))
        email = TextInput(
            hint_text="Adresse e-mail",
            multiline=False,
            size_hint_y=None,
            height="45dp",
        )
        mot_de_passe = TextInput(
            hint_text="Mot de passe",
            password=True,
            multiline=False,
            size_hint_y=None,
            height="45dp",
        )
        message = KivyLabel(
            text="",
            size_hint_y=None,
            height="35dp",
        )
        bouton = Button(
            text="Se connecter",
            size_hint_y=None,
            height="45dp",
        )
        contenu.add_widget(email)
        contenu.add_widget(mot_de_passe)
        contenu.add_widget(message)
        contenu.add_widget(bouton)
        popup = Popup(
            title="Authentification requise",
            content=contenu,
            size_hint=(0.9, None),
            height="300dp",
            auto_dismiss=False,
        )

        def connecter(instance):
            if not email.text.strip() or not mot_de_passe.text:
                message.text = "Saisissez l'adresse e-mail et le mot de passe."
                return

            bouton.disabled = True
            adresse_email = email.text.strip()
            mot_de_passe_saisi = mot_de_passe.text

            def connexion_reussie(_):
                popup.dismiss()
                self._executer_en_arriere_plan(operation, on_success)

            def connexion_echouee(error):
                message.text = str(error)
                bouton.disabled = False

            self._executer_en_arriere_plan(
                lambda: authentifier_administrateur(
                    adresse_email, mot_de_passe_saisi
                ),
                connexion_reussie,
                connexion_echouee,
            )

        bouton.bind(on_release=connecter)
        popup.open()

    def commander_whatsapp(self, produit, prix):

        numero = "22890000000"

        message = (
            f"Bonjour, je souhaite commander "
            f"{produit} au prix de {prix}."
        )

        url = f"https://wa.me/{numero}?text={quote(message)}"

        webbrowser.open(url)

    def on_switch_tabs(self, bar, item, item_icon, item_text):
        self.root.ids.screen_manager.current = item.screen_name

    def afficher_produits(self):
        self._executer_en_arriere_plan(
            obtenir_produits, self._afficher_produits
        )

    def _afficher_produits(self, produits):

        container = self.root.ids.produits_container

        for id_produit, nom, prix, description, image in produits:
            nom_escaped = kv_escape(nom)
            prix_escaped = kv_escape(prix)
            id_produit_escaped = kv_escape(str(id_produit))
            description_escaped = kv_escape(description)
            image_escaped = kv_escape(image)

            carte = Builder.load_string(f"""
MDCard:
    orientation: "vertical"
    size_hint_y: None
    height: "400dp"
    padding: "10dp"
    spacing: "10dp"
    elevation: 3

    Image:
        source: "{image_escaped}"
        size_hint_y: None
        height: "200dp"

    MDLabel:
        text: "{nom_escaped}"
        font_size: "22sp"
        bold: True
        halign: "center"
        size_hint_y: None
        height: "40dp"

    MDLabel:
        text: "{prix_escaped}"
        font_size: "20sp"
        halign: "center"
        size_hint_y: None
        height: "40dp"

    MDLabel:
        text: "{description_escaped}"
        halign: "center"
        size_hint_y: None
        height: "50dp"

    MDButton:
        style: "filled"
        pos_hint: {{"center_x": 0.5}}
        size_hint_x: None
        width: "220dp"
        on_release: app.commander_whatsapp("{nom_escaped}", "{prix_escaped}")

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

       self._executer_en_arriere_plan(
           obtenir_produits, self._afficher_produits_admin
       )

    def _afficher_produits_admin(self, produits):

       container = self.root.ids.admin_produits_container

       container.clear_widgets()

       for id_produit, nom, prix, description, image in produits:
           nom_escaped = kv_escape(nom)
           prix_escaped = kv_escape(prix)
           id_produit_escaped = kv_escape(str(id_produit))

           carte = Builder.load_string(f"""MDCard:
    orientation: "vertical"
    size_hint_y: None
    height: "135dp"
    padding: "10dp"
    spacing: "8dp"

    MDBoxLayout:
        orientation: "vertical"
        spacing: "2dp"

        MDLabel:
            text: "{nom_escaped}"
            bold: True
            font_size: "18sp"
            size_hint_y: None
            height: "26dp"

        MDLabel:
            text: "{prix_escaped}"
            font_size: "16sp"
            size_hint_y: None
            height: "24dp"

    MDBoxLayout:
        orientation: "horizontal"
        spacing: "8dp"
        size_hint_y: None
        height: "44dp"

        MDButton:
            style: "filled"
            size_hint_x: 1
            on_release: app.charger_produit_modifier("{id_produit_escaped}")

            MDButtonText:
                text: "Modifier"

        MDButton:
            style: "filled"
            size_hint_x: 1
            on_release: app.supprimer_produit_interface("{id_produit_escaped}")

            MDButtonText:
                text: "Supprimer"
""")

           container.add_widget(carte)


    def charger_produit_modifier(self, id_produit):
        self._executer_en_arriere_plan(
            obtenir_produits,
            lambda produits: self._charger_produit_modifier(
                produits, id_produit
            ),
        )

    def _charger_produit_modifier(self, produits, id_produit):

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
                text="Êtes-vous sûr de vouloir supprimer ce produit ?",
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
        id_produit = self.produit_a_supprimer

        def suppression_reussie(_):
            self.dialog_suppression.dismiss()
            self.actualiser_produits()
            self.afficher_produits_admin()
            self.produit_a_supprimer = None

        self._executer_action_admin(
            lambda: supprimer_produit(id_produit),
            suppression_reussie,
        )


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

        bouton_annuler.bind(on_release=annuler)

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

        id_produit = self.produit_a_modifier

        def modification_reussie(_):
            print("Produit modifié avec succès !")
            self.actualiser_produits()
            self.afficher_produits_admin()
            self.produit_a_modifier = None

        self._executer_action_admin(
            lambda: modifier_produit(
                id_produit, nom, prix, description, image
            ),
            modification_reussie,
        )



    def ajouter_produit_interface(self):

              nom = self.root.ids.nom_produit.text
              prix = self.root.ids.prix_produit.text
              description = self.root.ids.description_produit.text
              image = self.root.ids.image_produit.text

              if not nom or not prix:
                 print("Le nom et le prix sont obligatoires.")
                 return

              def ajout_reussi(_):
                 print("Produit ajouté avec succès !")
                 self.actualiser_produits()
                 self.afficher_produits_admin()

              self._executer_action_admin(
                  lambda: ajouter_produit(nom, prix, description, image),
                  ajout_reussi,
              )


    def ajouter_publication_interface(self):

        titre = self.root.ids.titre_publication.text
        contenu = self.root.ids.contenu_publication.text
        date = self.root.ids.date_publication.text
        image = self.root.ids.image_publication.text

        if not titre:
            print("Le titre de la publication est obligatoire.")
            return

        def ajout_reussi(_):
            print("Publication ajoutée avec succès !")
            self.afficher_publications_admin()
            self.afficher_publications()

        self._executer_action_admin(
            lambda: ajouter_publication(titre, contenu, date, image),
            ajout_reussi,
        )

   
    def charger_publication_modifier(self, id_publication):
        self._executer_en_arriere_plan(
            obtenir_publications,
            lambda publications: self._charger_publication_modifier(
                publications, id_publication
            ),
        )

    def _charger_publication_modifier(self, publications, id_publication):

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

        id_publication = self.publication_a_modifier

        def modification_reussie(_):
            print("Publication modifiée avec succès !")
            self.afficher_publications_admin()
            self.afficher_publications()
            self.publication_a_modifier = None

        self._executer_action_admin(
            lambda: modifier_publication(
                id_publication, titre, contenu, date, image
            ),
            modification_reussie,
        )



    def afficher_publications_admin(self):

        self._executer_en_arriere_plan(
            obtenir_publications, self._afficher_publications_admin
        )

    def _afficher_publications_admin(self, publications):

        container = self.root.ids.admin_publications_container

        container.clear_widgets()

        for id_publication, titre, contenu, date, image in publications:
            titre_escaped = kv_escape(titre)
            contenu_escaped = kv_escape(contenu)
            date_escaped = kv_escape(date)
            id_publication_escaped = kv_escape(str(id_publication))

            carte = Builder.load_string(f"""MDCard:
    orientation: "vertical"
    size_hint_y: None
    height: "165dp"
    padding: "10dp"
    spacing: "8dp"

    MDBoxLayout:
        orientation: "vertical"
        spacing: "2dp"

        MDLabel:
            text: "{titre_escaped}"
            bold: True
            font_size: "18sp"
            size_hint_y: None
            height: "26dp"

        MDLabel:
            text: "{date_escaped}"
            font_size: "15sp"
            size_hint_y: None
            height: "22dp"

        MDLabel:
            text: "{contenu_escaped}"
            font_size: "14sp"

    MDBoxLayout:
        orientation: "horizontal"
        spacing: "8dp"
        size_hint_y: None
        height: "44dp"

        MDButton:
            style: "filled"
            size_hint_x: 1
            on_release: app.charger_publication_modifier("{id_publication_escaped}")

            MDButtonText:
                text: "Modifier"

        MDButton:
            style: "filled"
            size_hint_x: 1
            on_release: app.supprimer_publication_interface("{id_publication_escaped}")

            MDButtonText:
                text: "Supprimer"
""")

            container.add_widget(carte)


    def supprimer_publication_interface(self, id_publication):
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
            text="Êtes-vous sûr de vouloir supprimer cette publication ?",
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

        id_publication = self.publication_a_supprimer

        def suppression_reussie(_):
            if hasattr(self, "dialog_suppression_publication"):
                self.dialog_suppression_publication.dismiss()
            self.publication_a_supprimer = None
            self.afficher_publications_admin()
            self.afficher_publications()
            print("Publication supprimée avec succès !")

        self._executer_action_admin(
            lambda: supprimer_publication(id_publication),
            suppression_reussie,
        )


    
    def afficher_publications(self):
        self._executer_en_arriere_plan(
            obtenir_publications, self._afficher_publications
        )

    def _afficher_publications(self, publications):

        container = self.root.ids.publications_container

        container.clear_widgets()

        for id_publication, titre, contenu, date, image in publications:
            titre_escaped = kv_escape(titre)
            contenu_escaped = kv_escape(contenu)
            date_escaped = kv_escape(date)
            image_escaped = kv_escape(image)

            carte = Builder.load_string(f"""
MDCard:
    orientation: "vertical"
    size_hint_y: None
    height: "400dp"
    padding: "10dp"
    spacing: "10dp"
    elevation: 3

    Image:
        source: "{image_escaped}"
        size_hint_y: None
        height: "200dp"

    MDLabel:
        text: "{titre_escaped}"
        font_size: "22sp"
        bold: True
        halign: "center"
        size_hint_y: None
        height: "45dp"

    MDLabel:
        text: "{date_escaped}"
        font_size: "15sp"
        halign: "center"
        size_hint_y: None
        height: "30dp"

    MDLabel:
        text: "{contenu_escaped}"
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