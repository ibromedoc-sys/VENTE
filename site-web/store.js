import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
import {
  collection,
  doc,
  getFirestore,
  onSnapshot,
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js";
import {
  getMessaging,
  getToken,
  isSupported,
  onMessage,
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging.js";
import { firebaseConfig, firebaseVapidKey } from "./firebase-config.js";

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const $ = (selector) => document.querySelector(selector);
const productList = $("[data-product-list]");
const publicationList = $("[data-publication-list]");
const firebaseStatus = $("[data-firebase-status]");
const appStatus = $("[data-app-status]");
const toast = $("[data-toast]");
const productSearch = $("[data-product-search]");
const siteContentDefaults = {
  accueilTitre: "Tout ce qu’il vous faut,\nau même endroit.",
  accueilDescription: "Découvrez nos produits et restez au courant des nouveautés de SUPERLIFE TOGO. Votre boutique vous accompagne, où que vous soyez.",
  aproposDescription: "Pour toute information sur notre entreprise, visitez notre site officiel ou contactez-nous directement.",
  telephoneWhatsapp: "22899057931",
  siteOfficiel: "https://superlife-togo.com",
};
const productState = { all: [], loaded: false };
const loadedCollections = new Set();
let whatsappNumber = siteContentDefaults.telephoneWhatsapp;
let toastTimeout;
let deferredInstallPrompt;
let foregroundMessagingReady = false;
let serviceWorkerPromise;

function showToast(message, kind = "") {
  toast.textContent = message;
  toast.className = `toast ${kind}`.trim();
  toast.hidden = false;
  window.clearTimeout(toastTimeout);
  toastTimeout = window.setTimeout(() => {
    toast.hidden = true;
  }, 6500);
}

function showAppStatus(message) {
  appStatus.textContent = message;
  appStatus.hidden = false;
}

function showFirebaseError(error) {
  firebaseStatus.textContent = `Impossible de charger la boutique depuis Firebase : ${error.message || error}`;
  firebaseStatus.classList.add("error");
  firebaseStatus.hidden = false;
}

function hideFirebaseStatusWhenReady(collectionName) {
  loadedCollections.add(collectionName);
  if (loadedCollections.size === 3) firebaseStatus.hidden = true;
}

function safeHttpsUrl(value) {
  try {
    const url = new URL(String(value || ""));
    return url.protocol === "https:" && !url.username && !url.password
      ? url.href : "";
  } catch {
    return "";
  }
}

function applySiteContent(content = {}) {
  const values = { ...siteContentDefaults, ...content };
  $("[data-home-title]").textContent = values.accueilTitre;
  $("[data-home-description]").textContent = values.accueilDescription;
  $("[data-about-description]").textContent = values.aproposDescription;

  const phone = String(values.telephoneWhatsapp || "").replace(/\D/g, "");
  if (/^\d{8,15}$/.test(phone)) whatsappNumber = phone;
  document.querySelectorAll("[data-whatsapp-link]").forEach((link) => {
    link.href = `https://wa.me/${whatsappNumber}`;
  });

  const officialSiteUrl = safeHttpsUrl(values.siteOfficiel);
  if (officialSiteUrl) {
    const officialSiteLink = $("[data-official-site]");
    officialSiteLink.href = officialSiteUrl;
    $("[data-official-site-label]").textContent = new URL(officialSiteUrl).hostname;
  }
}

function safeImageUrl(value) {
  const image = String(value || "").trim();
  if (/^images\/[A-Za-z0-9._-]+$/i.test(image)) {
    return `/assets/catalogue/${image.slice("images/".length)}`;
  }
  try {
    const url = new URL(image);
    return url.protocol === "https:" && !url.username && !url.password
      ? url.href : "";
  } catch {
    return "";
  }
}

function addImage(parent, value, className, alt) {
  const imageUrl = safeImageUrl(value);
  if (!imageUrl) return false;
  const image = document.createElement("img");
  image.className = className;
  image.alt = alt;
  image.loading = "lazy";
  image.src = imageUrl;
  image.addEventListener("error", () => image.remove(), { once: true });
  parent.append(image);
  return true;
}

function whatsappOrderUrl(name, price) {
  const message = `Bonjour, je souhaite commander ${name} au prix de ${price}.`;
  return `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;
}

function createProductCard(product) {
  const card = document.createElement("article");
  card.className = "product-card";

  const imageWrap = document.createElement("div");
  imageWrap.className = "product-image-wrap";
  if (!addImage(imageWrap, product.image, "product-image", product.nom || "Produit")) {
    const placeholder = document.createElement("span");
    placeholder.className = "product-placeholder";
    placeholder.setAttribute("aria-hidden", "true");
    placeholder.textContent = "◇";
    imageWrap.append(placeholder);
  }

  const copy = document.createElement("div");
  copy.className = "product-copy";
  const name = document.createElement("h3");
  name.textContent = product.nom || "Produit sans nom";
  copy.append(name);

  if (product.prix) {
    const price = document.createElement("p");
    price.className = "product-price";
    price.textContent = product.prix;
    copy.append(price);
  }

  if (product.description) {
    const description = document.createElement("p");
    description.className = "product-description";
    description.textContent = product.description;
    copy.append(description);
  }

  const order = document.createElement("a");
  order.className = "product-order";
  order.href = whatsappOrderUrl(product.nom || "ce produit", product.prix || "");
  order.target = "_blank";
  order.rel = "noopener noreferrer";
  order.textContent = "Commander sur WhatsApp ↗";
  copy.append(order);
  card.append(imageWrap, copy);
  return card;
}

function renderProducts() {
  const search = productSearch.value.trim().toLocaleLowerCase("fr");
  const filtered = productState.all.filter((product) =>
    `${product.nom || ""} ${product.description || ""} ${product.prix || ""}`
      .toLocaleLowerCase("fr").includes(search),
  );
  productList.replaceChildren();

  const count = $("[data-product-count]");
  count.textContent = `${filtered.length} produit${filtered.length === 1 ? "" : "s"}`;
  if (!filtered.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = productState.loaded
      ? (search ? "Aucun produit ne correspond à votre recherche." : "Aucun produit n’est disponible pour le moment.")
      : "Chargement des produits…";
    productList.append(empty);
    return;
  }

  for (const product of filtered) productList.append(createProductCard(product));
}

function publicationDate(publication) {
  const value = String(publication.date || "").trim();
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("fr-FR", { dateStyle: "long" }).format(date);
}

function sortPublications(left, right) {
  const dateValue = (item) => item._createdAt?.toMillis?.() || Date.parse(item.date || "") || 0;
  return dateValue(right) - dateValue(left);
}

function createPublicationCard(publication) {
  const card = document.createElement("article");
  card.className = "news-card";
  if (safeImageUrl(publication.image)) {
    const imageWrap = document.createElement("div");
    imageWrap.className = "news-image-wrap";
    addImage(imageWrap, publication.image, "news-image", publication.titre || "Actualité SUPERLIFE TOGO");
    card.append(imageWrap);
  }

  const copy = document.createElement("div");
  copy.className = "news-copy";
  if (publication.date) {
    const date = document.createElement("p");
    date.className = "news-date";
    date.textContent = publicationDate(publication);
    copy.append(date);
  }

  const title = document.createElement("h3");
  title.textContent = publication.titre || "Information SUPERLIFE TOGO";
  copy.append(title);
  if (publication.contenu) {
    const content = document.createElement("p");
    content.className = "news-content";
    content.textContent = publication.contenu;
    copy.append(content);
  }
  card.append(copy);
  return card;
}

function renderPublications(publications) {
  publicationList.replaceChildren();
  if (!publications.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "Aucune actualité n’est disponible pour le moment.";
    publicationList.append(empty);
    return;
  }
  for (const publication of publications.sort(sortPublications)) {
    publicationList.append(createPublicationCard(publication));
  }
}

function watchCollection(name, onRecords) {
  onSnapshot(
    collection(db, name),
    (snapshot) => {
      const records = snapshot.docs.map((item) => ({ id: item.id, ...item.data() }));
      onRecords(records);
      hideFirebaseStatusWhenReady(name);
    },
    showFirebaseError,
  );
}

function watchSiteContent() {
  onSnapshot(
    doc(db, "site_contenu", "general"),
    (snapshot) => {
      applySiteContent(snapshot.exists() ? snapshot.data() : {});
      hideFirebaseStatusWhenReady("site_contenu");
    },
    showFirebaseError,
  );
}

function isStandalone() {
  return window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;
}

const installButton = $("[data-install-app]");
const installedBadge = $("[data-installed-badge]");
const notificationsButton = $("[data-enable-notifications]");
const notificationsBadge = $("[data-notifications-ready]");

function updateInstallState() {
  if (isStandalone()) {
    installButton.hidden = true;
    installedBadge.hidden = false;
  }
}

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  deferredInstallPrompt = event;
});

window.addEventListener("appinstalled", () => {
  deferredInstallPrompt = null;
  updateInstallState();
  showAppStatus("SUPERLIFE TOGO a été ajouté à l’écran d’accueil.");
});

installButton.addEventListener("click", async () => {
  if (isStandalone()) {
    updateInstallState();
    return;
  }
  if (deferredInstallPrompt) {
    deferredInstallPrompt.prompt();
    const choice = await deferredInstallPrompt.userChoice;
    deferredInstallPrompt = null;
    if (choice.outcome === "accepted") {
      showAppStatus("Installation de SUPERLIFE TOGO confirmée.");
    } else {
      showAppStatus("Installation annulée. Vous pourrez réessayer depuis ce bouton.");
    }
    return;
  }

  const isAppleMobile = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  showAppStatus(isAppleMobile
    ? "Dans Safari, touchez Partager puis « Sur l’écran d’accueil »."
    : "Dans le menu de votre navigateur, choisissez « Installer l’application » ou « Ajouter à l’écran d’accueil ».");
});

notificationsButton.addEventListener("click", async () => {
  if (!window.isSecureContext) {
    showAppStatus("Les notifications et l’installation nécessitent une adresse HTTPS (ou localhost pour les tests).");
    return;
  }
  if (!("Notification" in window)) {
    showAppStatus("Ce navigateur ne prend pas en charge les notifications Web.");
    return;
  }
  if (Notification.permission === "denied") {
    showAppStatus("Les notifications sont bloquées dans les réglages du navigateur. Autorisez-les pour ce site puis réessayez.");
    return;
  }

  notificationsButton.disabled = true;
  try {
    if (Notification.permission === "default") {
      const permission = await Notification.requestPermission();
      if (permission !== "granted") {
        showAppStatus("L’autorisation des notifications n’a pas été accordée.");
        return;
      }
    }
    if (!await isSupported()) {
      throw new Error("Firebase Messaging n’est pas pris en charge par ce navigateur.");
    }
    const registration = await serviceWorkerPromise;
    if (!registration) {
      throw new Error("Le service worker de notifications n’a pas pu être démarré.");
    }
    const messaging = getMessaging(app);
    if (!foregroundMessagingReady) {
      onMessage(messaging, (payload) => {
        const title = payload.notification?.title || payload.data?.title || "SUPERLIFE TOGO";
        const body = payload.notification?.body || payload.data?.body || "Une nouvelle actualité vous attend.";
        showToast(`${title} — ${body}`);
      });
      foregroundMessagingReady = true;
    }
    const token = await getToken(messaging, {
      vapidKey: firebaseVapidKey,
      serviceWorkerRegistration: registration,
    });
    if (!token) throw new Error("Firebase n’a pas délivré de jeton pour cet appareil.");
    notificationsBadge.hidden = false;
    showAppStatus("Notifications activées sur cet appareil.");
  } catch (error) {
    showAppStatus(`Activation impossible : ${error.message || error}`);
  } finally {
    notificationsButton.disabled = false;
  }
});

$(".menu-toggle").addEventListener("click", (event) => {
  const button = event.currentTarget;
  const isOpen = button.getAttribute("aria-expanded") === "true";
  button.setAttribute("aria-expanded", String(!isOpen));
  $("#main-nav").classList.toggle("open", !isOpen);
});

$("#main-nav").addEventListener("click", (event) => {
  if (event.target.closest("a")) {
    $("#main-nav").classList.remove("open");
    $(".menu-toggle").setAttribute("aria-expanded", "false");
  }
});

productSearch.addEventListener("input", renderProducts);
$("[data-current-year]").textContent = String(new Date().getFullYear());
updateInstallState();

if ("serviceWorker" in navigator) {
  serviceWorkerPromise = navigator.serviceWorker.register("/firebase-messaging-sw.js")
    .catch((error) => {
      showAppStatus(`Impossible de démarrer le service worker : ${error.message || error}`);
      return null;
    });
}

watchCollection("site_produits", (products) => {
  productState.all = products;
  productState.loaded = true;
  renderProducts();
});
watchCollection("site_publications", renderPublications);
watchSiteContent();
