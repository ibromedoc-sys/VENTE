# SUPERLIFE TOGO — boutique Web et tableaux de bord

La boutique publique affiche les produits et publications Firestore du projet
`vente-24ed2` sur un site Firebase Hosting distinct du tableau de bord Web de
l'application. La boutique est prévue à `https://superlife-togo.web.app` ; le
tableau de bord de l'application reste sur `https://vente-24ed2.web.app`. Le
tableau de bord indépendant de la boutique est accessible depuis le lien
**Administration du site** en bas de la boutique. Le site ne stocke aucune
donnée de paiement et n'inclut aucun credential de compte de service. Les
fichiers du site sont regroupés séparément dans `site-web/` à la racine du
projet ; `web/` contient le tableau de bord de l'application.

## Administration indépendante de la boutique Web

`site-admin.html` fournit une interface distincte de `../web/dashboard.html` pour
gérer les produits Web (`site_produits`), les actualités Web
(`site_publications`) et les textes et coordonnées (`site_contenu/general`).
Ces collections sont séparées de `produits` et `publications`, qui restent
gérées par le tableau de bord de l'application. Les deux tableaux de bord
utilisent Firebase Authentication et la revendication personnalisée
`admin: true` ; les règles Firestore protègent les écritures.

La rubrique **Copie initiale du catalogue** permet de copier une seule fois
les produits et actualités existants de l'application vers les collections du
site. Elle conserve les identifiants des documents, ne supprime ni ne modifie
les sources, et refuse d'écrire si une des deux collections Web contient déjà
des documents. Après cette copie, toute modification du site est indépendante
de l'application. Les chemins d'images locaux historiques sont conservés et
pointent vers leurs copies statiques dans `assets/catalogue/`.

La boutique lit ces trois collections du site ; en cas de règles non déployées,
les modifications peuvent échouer ou la boutique afficher une erreur Firebase.
Pour publier les règles et la boutique ensemble, la commande explicite est :

```powershell
firebase deploy --only firestore:rules,hosting:dashboard,hosting:storefront --project vente-24ed2
```

Cette commande met à jour les deux tableaux de bord Web, mais ne touche pas à
l'APK Android. Le compte administrateur doit être configuré avec `admin: true`
pour accéder aux écritures. Les images du site utilisent le preset Cloudinary
public existant ; aucune clé secrète n'est placée dans le navigateur.

Le numéro de contact de l'application est géré dans l'onglet **Coordonnées**
du tableau de bord `web/`. Il est stocké séparément dans
`app_config/contact` et lu par l'application Android. L'APK doit être
reconstruite et réinstallée pour récupérer cette fonctionnalité ; en attendant,
l'application utilise son numéro par défaut. Le numéro de la boutique reste
modifiable dans son propre tableau de bord, sans affecter l'application.

Le diaporama d'accueil reprend les quatre images `../images/logo.png` à
`images/logo3.png` de l'application. Leurs versions WebP optimisées sont dans
`assets/slides/`.

## Installation sur téléphone et notifications

Le manifeste et les icônes rendent la boutique SUPERLIFE TOGO installable
depuis un navigateur compatible. Le visiteur choisit lui-même d'installer le site et d'autoriser les
notifications ; l'autorisation n'est jamais demandée automatiquement. Le
service worker sert aux notifications et ne met pas le site en cache : une
connexion Internet reste nécessaire pour consulter la boutique.

L'application Web Firebase et sa clé publique Web Push VAPID sont configurées
dans `firebase-config.js`. Activez Firebase Cloud Messaging API dans la
console Firebase et servez le site en HTTPS, par exemple avec Firebase
Hosting. Sur iPhone/iPad, l'installation préalable à l'écran d'accueil est
nécessaire pour les notifications Web ; dans Safari, utilisez **Partager** puis
**Sur l'écran d'accueil**.

L'inscription produit un jeton FCM géré par Firebase dans le navigateur ; le
site ne l'affiche pas et ne l'enregistre pas dans Firestore, comme DJAMI Web.
Le choix actuel n'active pas Analytics et n'inclut aucun serveur : il ne
constitue donc pas de liste et ne permet pas de cibler une diffusion générale.
Un test individuel demande un jeton FCM connu. Les campagnes d'audience
nécessiteraient Analytics et son consentement ; la diffusion à une liste gérée
par SUPERLIFE TOGO nécessiterait un service d'envoi sécurisé. Aucun credential
d'envoi ne doit être placé dans le navigateur.

## Préparation Firebase

1. Dans Firebase Console, activer le fournisseur **E-mail/Mot de passe** dans
   Authentication et vérifier que `ibromedoc@gmail.com` peut se connecter.
2. Conserver les configurations Web dans `../web/firebase-config.js` (tableau
   de bord de l'application) et `firebase-config.js` (site). La clé API Firebase
   de configuration est publique ;
   elle ne doit pas être confondue avec un credential de compte de service.
3. Vérifier la revendication personnalisée `admin: true` du compte admin. Les
   règles Firestore font autorité ; masquer l'interface n'est pas une
   protection des données.

## Nom de l'application Android

Le nom affiché sous l'icône Android et dans l'écran principal est
`SUPERLIFE TOGO`. Il est défini par `title` dans `buildozer.spec` ; l'identifiant
Android `com.vente.app` reste inchangé pour conserver la possibilité de publier
une mise à jour de la même application. Il faut reconstruire l'APK (ou le
bundle AAB) pour que le nouveau nom apparaisse sur le téléphone.

## Déployer le site et le tableau de bord

Après avoir créé le site `superlife-togo` dans le projet Firebase et avec
Firebase CLI authentifié :

```powershell
firebase hosting:sites:create superlife-togo --project vente-24ed2
firebase deploy --only firestore:rules,hosting:dashboard,hosting:storefront --project vente-24ed2
```

La cible `storefront` publie uniquement la boutique à
`https://superlife-togo.web.app` ; la cible `dashboard` sert le tableau de bord
de l'application à `https://vente-24ed2.web.app`. Ce dossier contient la
boutique, son administration et ses ressources Web ; `../web/` contient le
tableau de bord de l'application. La commande déploie les règles
Firestore nécessaires aux collections du site et au numéro de contact de
l'application, sans modifier les règles Storage. Les
identifiants de sites Hosting doivent être uniques. Si le site `superlife-togo`
existe déjà dans le projet, ne relancez pas la commande de création ; s'il
appartient à un autre projet, choisissez un autre identifiant et mettez à jour
sa cible dans `.firebaserc`.

Ne pas ouvrir les pages directement depuis `file://` : les modules Firebase
et le service worker exigent un serveur Web. Pour les tests, lancez depuis le
dossier `site-web` :

```powershell
python -m http.server 8000
```

Le serveur local permet de vérifier l'affichage, mais les notifications et
l'installation doivent être testées sur HTTPS (ou `localhost` pour le
développement).

## Distribuer l'application et les mises à jour via Google Play

Les mises à jour de VENTE seront distribuées par Google Play ; l'application ne
vérifie plus un manifeste distant et ne télécharge ni n'installe d'APK depuis
GitHub. Le fichier `web/app-update.json` et l'ancien mécanisme d'installation
directe ne sont plus utilisés. Firebase Hosting sert la boutique Web et le
tableau de bord sur deux sites distincts.

L'identifiant Android actuel est `com.vente.app` (`package.domain` +
`package.name` dans `buildozer.spec`) : il doit rester identique pour publier
des mises à jour de la même application Play. Le format de sortie release est
une APK. Le workflow GitHub Actions construit et publie une APK release signée
comme artefact téléchargeable.

Avant une publication Play, il faudra :

1. Créer l'application dans la Play Console et compléter les informations
   demandées, puis activer Play App Signing.
2. Incrémenter `android.numeric_version` à chaque publication (la version
   préparée est actuellement le code `2`) et modifier `version` pour le nom
   affiché.
3. Enregistrer les secrets GitHub Actions `ANDROID_KEYSTORE_BASE64`,
   `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS` et `ANDROID_KEY_PASSWORD`.
   Le workflow `Build SUPERLIFE TOGO signed APK` utilise ces secrets pour
   construire une APK release signée ; téléchargez-la dans **Actions → run →
   Artifacts**. Garder une sauvegarde privée de la clé ; ne pas la committer.
   Pour publier dans Google Play, préférer un AAB signé et utiliser la clé
   d'envoi Play appropriée.
4. Installer la version de test depuis Play. Ensuite, Play gère la distribution
   des mises à jour selon les réglages de l'utilisateur (mises à jour
   automatiques, ou mise à jour manuelle depuis le Play Store).

L'APK debug distribuée auparavant hors Play peut avoir une signature différente
de celle installée par Play. Si Android refuse la première installation Play
par-dessus, il faudra désinstaller l'ancienne APK puis installer l'application
depuis la piste de test Play ; les données locales peuvent être effacées.

Les lectures des collections `produits` et `publications` sont publiques pour
les appareils clients. Seuls les jetons portant `admin: true` peuvent écrire
dans Firestore. Le compte admin doit se déconnecter puis se reconnecter (ou
renouveler son jeton) après modification de ses claims.

## Hébergement d'images

Les tableaux de bord téléversent directement les images vers Cloudinary avec le
cloud `jvljzrue` et le preset non signé `vente_images`. Aucune clé secrète ni
Firebase Storage n'est utilisé. Firestore conserve l'URL HTTPS `secure_url`
renvoyée par Cloudinary dans le champ `image` des collections correspondantes :
`produits` et `publications` pour le tableau de bord de l'application,
`site_produits` et `site_publications` pour celui du site. Une URL HTTPS saisie
manuellement reste possible. Lors d'une modification, ne pas choisir de fichier
ni saisir d'URL conserve la référence actuelle, y compris les références locales
historiques.

Les fichiers sont limités à JPEG, PNG ou WebP et à 5 Mo pour rester compatibles
avec le client Android, qui lit les images HTTPS selon leur type MIME et les met
en cache localement. Les chemins historiques tels que `images/produit1.jpg` ne
sont pas réécrits et les fichiers locaux ne doivent pas être supprimés : ils
restent nécessaires aux références locales de l'APK.

Un preset non signé et son cloud name sont visibles dans le code du navigateur
et l'endpoint Cloudinary ne vérifie pas la connexion Firebase : toute personne
qui connaît ces paramètres peut tenter un téléversement. Restreindre le preset
dans Cloudinary aux formats image attendus et à la taille maximale autorisée,
désactiver l'écrasement si possible et surveiller les quotas. Ne jamais ajouter
de secret Cloudinary au client. Ne pas activer Firebase Storage, modifier la
facturation ni déployer `storage.rules`.

## Vérification

- Connexion avec l'administrateur : affichage des produits et publications.
- Création, modification et suppression de chaque type dans Firestore.
- Téléversement Cloudinary d'une image JPEG, PNG ou WebP et enregistrement de
  son URL HTTPS dans Firestore.
- Conservation de l'image existante si aucun nouveau fichier n'est sélectionné.
- Connexion d'un compte sans `admin: true` : aucune écriture autorisée.
- Affichage des URL d'images sur l'application Android et un second appareil.
- Boutique publique : affichage des produits et actualités dans un navigateur.
- Installation sur Android et iOS depuis l'origine HTTPS définitive.
- Réception d'une notification FCM en premier plan puis en arrière-plan.
- Publication Android via une piste de test interne Google Play.
- Ne pas déployer les règles Storage ni modifier le forfait Firebase pour
  cette solution.
