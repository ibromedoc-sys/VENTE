import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
import {
  getAuth,
  getIdTokenResult,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signOut,
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";
import {
  collection,
  deleteDoc,
  doc,
  getFirestore,
  onSnapshot,
  runTransaction,
  serverTimestamp,
  setDoc,
  updateDoc,
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js";
import { firebaseConfig } from "./firebase-config.js";

const CLOUDINARY_CLOUD_NAME = "jvljzrue";
const CLOUDINARY_UPLOAD_PRESET = "vente_images";
const MAX_IMAGE_SIZE = 5 * 1024 * 1024;
const ALLOWED_IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
const DEFAULT_SITE_CONTENT = {
  accueilTitre: "Tout ce qu’il vous faut,\nau même endroit.",
  accueilDescription: "Découvrez nos produits et restez au courant des nouveautés de SUPERLIFE TOGO. Votre boutique vous accompagne, où que vous soyez.",
  aproposDescription: "Pour toute information sur notre entreprise, visitez notre site officiel ou contactez-nous directement.",
  telephoneWhatsapp: "22899057931",
  siteOfficiel: "https://superlife-togo.com",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const $ = (selector) => document.querySelector(selector);
const loginView = $("#login-view");
const loadingView = $("#loading-view");
const adminApp = $("#admin-app");
const notice = $("#notice");
const loginNotice = $("#login-notice");
const productForm = $("#site-product-form");
const newsForm = $("#site-news-form");
const contentForm = $("#site-content-form");
const copyButton = $("#copy-app-catalog");
const records = { site_produits: [], site_publications: [] };
const previewObjectUrls = new WeakMap();
const unsubscribers = [];
let contentDirty = false;
let noticeTimeout;

function showNotice(message, kind = "error") {
  notice.textContent = message;
  notice.className = `notice ${kind}`;
  notice.hidden = false;
  window.clearTimeout(noticeTimeout);
  noticeTimeout = window.setTimeout(() => {
    notice.hidden = true;
  }, 8000);
}

function showLoginNotice(message) {
  loginNotice.textContent = message;
  loginNotice.hidden = false;
}

function friendlyError(error) {
  const messages = {
    "auth/invalid-credential": "Adresse e-mail ou mot de passe incorrect.",
    "auth/too-many-requests": "Trop de tentatives. Réessayez plus tard.",
    "permission-denied": "Accès refusé par les règles Firebase.",
  };
  return messages[error.code] || error.message || "Une erreur inattendue est survenue.";
}

function setSignedIn(visible) {
  loadingView.hidden = true;
  loginView.hidden = visible;
  adminApp.hidden = !visible;
}

function stopListeners() {
  for (const unsubscribe of unsubscribers.splice(0)) unsubscribe();
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

function safeImageUrl(value) {
  const image = String(value || "").trim();
  if (/^images\/[A-Za-z0-9._-]+$/i.test(image)) {
    return `/assets/catalogue/${image.slice("images/".length)}`;
  }
  return safeHttpsUrl(image);
}

function setImagePreview(form, source, caption = "") {
  const previousObjectUrl = previewObjectUrls.get(form);
  if (previousObjectUrl) URL.revokeObjectURL(previousObjectUrl);

  const container = form.querySelector("[data-image-preview]");
  const image = container.querySelector("img");
  const captionElement = container.querySelector("[data-image-caption]");
  if (!source) {
    image.removeAttribute("src");
    captionElement.textContent = "";
    container.hidden = true;
    previewObjectUrls.delete(form);
    return;
  }

  image.src = source;
  captionElement.textContent = caption;
  container.hidden = false;
  if (source.startsWith("blob:")) previewObjectUrls.set(form, source);
  else previewObjectUrls.delete(form);
}

function validateImageFile(file) {
  if (!ALLOWED_IMAGE_TYPES.has(file.type)) {
    throw new Error("Choisissez une image JPEG, PNG ou WebP.");
  }
  if (file.size > MAX_IMAGE_SIZE) {
    throw new Error("L’image ne doit pas dépasser 5 Mo.");
  }
}

async function uploadImage(file) {
  const body = new FormData();
  body.append("file", file);
  body.append("upload_preset", CLOUDINARY_UPLOAD_PRESET);

  const response = await fetch(
    `https://api.cloudinary.com/v1_1/${CLOUDINARY_CLOUD_NAME}/image/upload`,
    { method: "POST", body },
  );
  let result;
  try {
    result = await response.json();
  } catch {
    throw new Error(`Réponse Cloudinary invalide (HTTP ${response.status}).`);
  }
  if (!response.ok) {
    throw new Error(result.error?.message || `Échec Cloudinary (HTTP ${response.status}).`);
  }

  const secureUrl = safeImageUrl(result.secure_url);
  if (!secureUrl) throw new Error("Cloudinary n’a pas renvoyé d’URL HTTPS valide.");
  return secureUrl;
}

function titleFor(collectionName, item) {
  return collectionName === "site_produits"
    ? item.nom || "Produit sans nom"
    : item.titre || "Actualité sans titre";
}

function updateCounts() {
  const productCount = records.site_produits.length;
  const newsCount = records.site_publications.length;
  $("#product-count").textContent = String(productCount);
  $("#product-count-card").textContent = String(productCount);
  $("#product-total").textContent = String(productCount);
  $("#news-count").textContent = String(newsCount);
  $("#news-count-card").textContent = String(newsCount);
  $("#news-total").textContent = String(newsCount);
  copyButton.disabled = productCount > 0 || newsCount > 0;
}

function renderRecords(collectionName) {
  const isProducts = collectionName === "site_produits";
  const list = isProducts ? $("#site-product-list") : $("#site-news-list");
  const sorted = [...records[collectionName]].sort((left, right) => {
    const leftDate = left._createdAt?.toMillis?.() || Date.parse(left.date || "") || 0;
    const rightDate = right._createdAt?.toMillis?.() || Date.parse(right.date || "") || 0;
    return rightDate - leftDate;
  });
  list.replaceChildren();

  if (!sorted.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "Aucun élément pour le moment.";
    list.append(empty);
    return;
  }

  for (const item of sorted) {
    const row = document.createElement("article");
    row.className = "record";
    const imageUrl = safeImageUrl(item.image);
    if (imageUrl) {
      const image = document.createElement("img");
      image.className = "record-image";
      image.src = imageUrl;
      image.alt = "";
      image.addEventListener("error", () => image.remove(), { once: true });
      row.append(image);
    } else {
      const placeholder = document.createElement("span");
      placeholder.className = "record-placeholder";
      placeholder.setAttribute("aria-hidden", "true");
      row.append(placeholder);
    }

    const copy = document.createElement("div");
    copy.className = "record-copy";
    const title = document.createElement("strong");
    title.textContent = titleFor(collectionName, item);
    const detail = document.createElement("span");
    detail.textContent = isProducts ? item.prix || "" : item.date || "";
    copy.append(title, detail);

    const actions = document.createElement("div");
    actions.className = "record-actions";
    for (const action of ["edit", "delete"]) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `icon-button${action === "delete" ? " danger" : ""}`;
      button.dataset.action = action;
      button.dataset.collection = collectionName;
      button.dataset.id = item.id;
      button.textContent = action === "edit" ? "Modifier" : "Supprimer";
      button.setAttribute(
        "aria-label",
        `${action === "edit" ? "Modifier" : "Supprimer"} ${titleFor(collectionName, item)}`,
      );
      actions.append(button);
    }
    row.append(copy, actions);
    list.append(row);
  }
}

function watchCollection(collectionName) {
  const unsubscribe = onSnapshot(
    collection(db, collectionName),
    (snapshot) => {
      records[collectionName] = snapshot.docs.map((item) => ({
        id: item.id,
        ...item.data(),
      }));
      renderRecords(collectionName);
      updateCounts();
    },
    (error) => showNotice(friendlyError(error)),
  );
  unsubscribers.push(unsubscribe);
}

function fillContentForm(content = {}) {
  const values = { ...DEFAULT_SITE_CONTENT, ...content };
  for (const [name, value] of Object.entries(values)) {
    contentForm.elements[name].value = value || "";
  }
}

function watchSiteContent() {
  const unsubscribe = onSnapshot(
    doc(db, "site_contenu", "general"),
    (snapshot) => {
      if (!contentDirty) fillContentForm(snapshot.exists() ? snapshot.data() : {});
    },
    (error) => showNotice(friendlyError(error)),
  );
  unsubscribers.push(unsubscribe);
}

function resetForm(form, collectionName) {
  setImagePreview(form, "");
  form.reset();
  form.elements.id.value = "";
  const isProduct = collectionName === "site_produits";
  $(`#${isProduct ? "site-product" : "site-news"}-form-title`).textContent =
    isProduct ? "Ajouter un produit" : "Ajouter une actualité";
  form.querySelector("[data-cancel-form]").hidden = true;
}

function getImageReference(form, oldRecord) {
  const enteredImageUrl = form.elements.imageUrl.value.trim();
  if (enteredImageUrl && !safeImageUrl(enteredImageUrl)) {
    throw new Error("L’image doit être une URL HTTPS valide.");
  }
  return enteredImageUrl || oldRecord?.image || "";
}

async function saveRecord(collectionName, form, event) {
  event.preventDefault();
  const isProduct = collectionName === "site_produits";
  const existingId = form.elements.id.value;
  const oldRecord = records[collectionName].find((item) => item.id === existingId);
  const submitButton = form.querySelector('[type="submit"]');
  submitButton.disabled = true;

  try {
    const formData = new FormData(form);
    const values = isProduct
      ? {
          nom: String(formData.get("nom") || "").trim(),
          prix: String(formData.get("prix") || "").trim(),
          description: String(formData.get("description") || "").trim(),
        }
      : {
          titre: String(formData.get("titre") || "").trim(),
          contenu: String(formData.get("contenu") || "").trim(),
          date: String(formData.get("date") || new Date().toISOString().slice(0, 10)),
        };
    if (!values[isProduct ? "nom" : "titre"]) {
      throw new Error(isProduct ? "Le nom du produit est obligatoire." : "Le titre est obligatoire.");
    }

    const imageFile = form.elements.imageFile.files[0] || null;
    if (imageFile) validateImageFile(imageFile);
    values.image = imageFile
      ? await uploadImage(imageFile)
      : getImageReference(form, oldRecord);

    const recordId = existingId || crypto.randomUUID();
    const recordRef = doc(collection(db, collectionName), recordId);
    if (existingId) {
      await updateDoc(recordRef, values);
      showNotice("Modifications enregistrées.", "success");
    } else {
      values._createdAt = serverTimestamp();
      await setDoc(recordRef, values);
      showNotice(isProduct ? "Produit ajouté au site." : "Actualité ajoutée au site.", "success");
    }
    resetForm(form, collectionName);
  } catch (error) {
    showNotice(friendlyError(error));
  } finally {
    submitButton.disabled = false;
  }
}

function editRecord(collectionName, id) {
  const item = records[collectionName].find((record) => record.id === id);
  if (!item) {
    showNotice("Cet élément n’est plus disponible.");
    return;
  }
  const isProduct = collectionName === "site_produits";
  const form = isProduct ? productForm : newsForm;
  form.elements.id.value = item.id;
  form.elements.imageUrl.value = "";
  const imageUrl = safeImageUrl(item.image);
  setImagePreview(form, imageUrl, imageUrl ? "Image actuelle" : "");

  if (isProduct) {
    form.elements.nom.value = item.nom || "";
    form.elements.prix.value = item.prix || "";
    form.elements.description.value = item.description || "";
    $("#site-product-form-title").textContent = "Modifier le produit";
  } else {
    form.elements.titre.value = item.titre || "";
    form.elements.contenu.value = item.contenu || "";
    form.elements.date.value = item.date || "";
    $("#site-news-form-title").textContent = "Modifier l’actualité";
  }
  form.querySelector("[data-cancel-form]").hidden = false;
  form.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function deleteRecord(collectionName, id) {
  const item = records[collectionName].find((record) => record.id === id);
  if (!item || !window.confirm(`Supprimer « ${titleFor(collectionName, item)} » du site ?`)) return;
  try {
    await deleteDoc(doc(db, collectionName, id));
    showNotice("Élément supprimé du site.", "success");
  } catch (error) {
    showNotice(friendlyError(error));
  }
}

function imageFormEvents(form, collectionName) {
  const updatePreview = () => {
    const file = form.elements.imageFile.files[0];
    if (file) return;
    const enteredImageUrl = safeImageUrl(form.elements.imageUrl.value.trim());
    if (enteredImageUrl) {
      setImagePreview(form, enteredImageUrl, "Aperçu de l’URL");
      return;
    }
    const item = records[collectionName].find((record) => record.id === form.elements.id.value);
    const imageUrl = safeImageUrl(item?.image);
    setImagePreview(form, imageUrl, imageUrl ? "Image actuelle" : "");
  };

  form.elements.imageUrl.addEventListener("input", updatePreview);
  form.elements.imageFile.addEventListener("change", () => {
    const file = form.elements.imageFile.files[0];
    if (!file) {
      updatePreview();
      return;
    }
    try {
      validateImageFile(file);
      setImagePreview(form, URL.createObjectURL(file), file.name);
    } catch (error) {
      form.elements.imageFile.value = "";
      updatePreview();
      showNotice(friendlyError(error));
    }
  });
}

async function saveSiteContent(event) {
  event.preventDefault();
  const submitButton = contentForm.querySelector('[type="submit"]');
  submitButton.disabled = true;
  try {
    const values = Object.fromEntries(new FormData(contentForm));
    values.accueilTitre = String(values.accueilTitre || "").trim();
    values.accueilDescription = String(values.accueilDescription || "").trim();
    values.aproposDescription = String(values.aproposDescription || "").trim();
    values.telephoneWhatsapp = String(values.telephoneWhatsapp || "").replace(/\D/g, "");
    values.siteOfficiel = String(values.siteOfficiel || "").trim();
    if (!values.accueilTitre) throw new Error("Le titre d’accueil est obligatoire.");
    if (!/^\d{8,15}$/.test(values.telephoneWhatsapp)) {
      throw new Error("Entrez un numéro WhatsApp international valide, de 8 à 15 chiffres.");
    }
    if (values.siteOfficiel && !safeHttpsUrl(values.siteOfficiel)) {
      throw new Error("Le site officiel doit utiliser une URL HTTPS valide.");
    }
    await setDoc(doc(db, "site_contenu", "general"), values, { merge: true });
    contentDirty = false;
    showNotice("Textes et coordonnées du site enregistrés.", "success");
  } catch (error) {
    showNotice(friendlyError(error));
  } finally {
    submitButton.disabled = false;
  }
}

async function copyAppCatalog() {
  if (!window.confirm(
    "Copier une seule fois les produits et actualités de l’application vers le site ? Les documents de l’application ne seront pas modifiés.",
  )) return;

  copyButton.disabled = true;
  try {
    const copied = await runTransaction(db, async (transaction) => {
      const [sourceProducts, sourceNews, siteProducts, siteNews] = await Promise.all([
        transaction.get(collection(db, "produits")),
        transaction.get(collection(db, "publications")),
        transaction.get(collection(db, "site_produits")),
        transaction.get(collection(db, "site_publications")),
      ]);
      if (!siteProducts.empty || !siteNews.empty) {
        throw new Error("La copie est bloquée : le site contient déjà des produits ou actualités.");
      }
      const total = sourceProducts.size + sourceNews.size;
      if (!total) {
        throw new Error("Aucun produit ni aucune actualité à copier depuis l’application.");
      }
      if (total > 450) {
        throw new Error("Le catalogue dépasse la taille d’une copie sécurisée en une seule opération.");
      }
      for (const item of sourceProducts.docs) {
        transaction.set(doc(db, "site_produits", item.id), item.data());
      }
      for (const item of sourceNews.docs) {
        transaction.set(doc(db, "site_publications", item.id), item.data());
      }
      return { products: sourceProducts.size, news: sourceNews.size };
    });
    showNotice(
      `Copie terminée : ${copied.products} produit(s) et ${copied.news} actualité(s). Les deux catalogues sont maintenant indépendants.`,
      "success",
    );
  } catch (error) {
    showNotice(friendlyError(error));
  } finally {
    updateCounts();
  }
}

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  try {
    await signInWithEmailAndPassword(
      auth,
      form.elements.email.value.trim(),
      form.elements.password.value,
    );
  } catch (error) {
    showLoginNotice(friendlyError(error));
  }
});

$("#sign-out").addEventListener("click", async () => {
  try {
    stopListeners();
    await signOut(auth);
  } catch (error) {
    showNotice(friendlyError(error));
  }
});

productForm.addEventListener("submit", (event) =>
  saveRecord("site_produits", productForm, event));
newsForm.addEventListener("submit", (event) =>
  saveRecord("site_publications", newsForm, event));
contentForm.addEventListener("submit", saveSiteContent);
contentForm.addEventListener("input", () => {
  contentDirty = true;
});
copyButton.addEventListener("click", copyAppCatalog);
imageFormEvents(productForm, "site_produits");
imageFormEvents(newsForm, "site_publications");

document.addEventListener("click", async (event) => {
  const target = event.target.closest("[data-panel], [data-action], [data-cancel-form]");
  if (!target) return;

  if (target.dataset.panel) {
    document.querySelectorAll(".side-link").forEach((button) =>
      button.classList.toggle("active", button === target));
    document.querySelectorAll(".management-panel").forEach((panel) => {
      panel.hidden = panel.id !== target.dataset.panel;
    });
  } else if (target.dataset.cancelForm) {
    resetForm(
      target.dataset.cancelForm === "site-product" ? productForm : newsForm,
      target.dataset.cancelForm === "site-product" ? "site_produits" : "site_publications",
    );
  } else if (target.dataset.action === "edit") {
    editRecord(target.dataset.collection, target.dataset.id);
  } else if (target.dataset.action === "delete") {
    await deleteRecord(target.dataset.collection, target.dataset.id);
  }
});

onAuthStateChanged(auth, async (user) => {
  stopListeners();
  if (!user) {
    contentDirty = false;
    setSignedIn(false);
    $("#admin-email").textContent = "";
    return;
  }
  try {
    const token = await getIdTokenResult(user, true);
    if (token.claims.admin !== true) {
      await signOut(auth);
      setSignedIn(false);
      showLoginNotice("Ce compte n'a pas la revendication administrateur requise.");
      return;
    }
    $("#admin-email").textContent = user.email || "";
    setSignedIn(true);
    watchCollection("site_produits");
    watchCollection("site_publications");
    watchSiteContent();
  } catch (error) {
    setSignedIn(false);
    showLoginNotice(friendlyError(error));
  }
});
