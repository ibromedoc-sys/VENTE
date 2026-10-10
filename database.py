"""Firestore REST data access for the VENTE Android application."""

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen


_FIREBASE_CONFIG = None
_TOKEN_LOCK = threading.RLock()
_ID_TOKEN = None
_REFRESH_TOKEN = None
_TOKEN_EXPIRY = 0
_REQUEST_TIMEOUT = 20

_COLLECTIONS = {
    "produits": ("nom", "prix", "description", "image"),
    "publications": ("titre", "contenu", "date", "image"),
}


class FirebaseError(RuntimeError):
    """Raised when Firebase configuration, authentication, or a request fails."""


class AuthenticationRequiredError(FirebaseError):
    """Raised when an administrator token is required but not available."""


def _firebase_config():
    global _FIREBASE_CONFIG

    if _FIREBASE_CONFIG is None:
        config_path = Path(__file__).with_name("google-services.json")
        try:
            with config_path.open(encoding="utf-8") as config_file:
                data = json.load(config_file)
            client = data["client"][0]
            project_id = data["project_info"]["project_id"]
            api_key = client["api_key"][0]["current_key"]
            package_name = client["client_info"]["android_client_info"]["package_name"]
        except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
            raise FirebaseError(
                "Configuration Firebase invalide ou fichier google-services.json absent."
            ) from error

        if package_name != "com.vente.app":
            raise FirebaseError(
                "google-services.json ne correspond pas au package com.vente.app."
            )

        _FIREBASE_CONFIG = {
            "project_id": project_id,
            "api_key": api_key,
        }

    return _FIREBASE_CONFIG


def creer_base():
    """Keep the legacy entry point; validate Firebase config without touching SQLite."""
    _firebase_config()


def _decode_response(response):
    if not response:
        return {}
    try:
        return json.loads(response.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        raise FirebaseError("Firebase a renvoyé une réponse illisible.") from error


def _request_json(url, method="GET", payload=None, headers=None):
    request_headers = {"Accept": "application/json"}
    if payload is not None:
        request_headers["Content-Type"] = "application/json"
    if headers:
        request_headers.update(headers)

    content_type = request_headers.get("Content-Type", "")
    if payload is None:
        body = None
    elif content_type == "application/x-www-form-urlencoded":
        body = urlencode(payload).encode("utf-8")
    else:
        body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=request_headers, method=method)

    try:
        with urlopen(request, timeout=_REQUEST_TIMEOUT) as response:
            return _decode_response(response.read())
    except HTTPError as error:
        response_data = _decode_response(error.read())
        message = response_data.get("error", {}).get("message")
        if error.code in (401, 403):
            detail = message or "accès refusé par les règles Firebase."
        else:
            detail = message or "erreur HTTP {}.".format(error.code)
        raise FirebaseError("Firebase : {}".format(detail)) from error
    except (URLError, TimeoutError, OSError) as error:
        raise FirebaseError(
            "Connexion Firebase impossible : {}".format(error)
        ) from error


def authentifier_administrateur(email, mot_de_passe):
    """Sign in without persisting credentials; the returned tokens stay in memory."""
    global _ID_TOKEN, _REFRESH_TOKEN, _TOKEN_EXPIRY

    config = _firebase_config()
    url = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?"
        + urlencode({"key": config["api_key"]})
    )
    response = _request_json(
        url,
        method="POST",
        payload={
            "email": email,
            "password": mot_de_passe,
            "returnSecureToken": True,
        },
    )
    try:
        id_token = response["idToken"]
        refresh_token = response["refreshToken"]
        expires_in = int(response["expiresIn"])
    except (KeyError, TypeError, ValueError) as error:
        raise FirebaseError(
            "Firebase Authentication n'a pas fourni de jeton valide."
        ) from error

    with _TOKEN_LOCK:
        _ID_TOKEN = id_token
        _REFRESH_TOKEN = refresh_token
        _TOKEN_EXPIRY = datetime.now(timezone.utc).timestamp() + expires_in


def administrateur_connecte():
    with _TOKEN_LOCK:
        return _ID_TOKEN is not None


def _refresh_id_token():
    global _ID_TOKEN, _REFRESH_TOKEN, _TOKEN_EXPIRY

    with _TOKEN_LOCK:
        refresh_token = _REFRESH_TOKEN
    if refresh_token is None:
        raise AuthenticationRequiredError(
            "Connectez-vous avec un compte administrateur Firebase pour modifier les données."
        )

    config = _firebase_config()
    url = (
        "https://securetoken.googleapis.com/v1/token?"
        + urlencode({"key": config["api_key"]})
    )
    response = _request_json(
        url,
        method="POST",
        payload={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        id_token = response["id_token"]
        new_refresh_token = response["refresh_token"]
        expires_in = int(response["expires_in"])
    except (KeyError, TypeError, ValueError) as error:
        raise FirebaseError(
            "Firebase Authentication n'a pas renouvelé le jeton."
        ) from error

    with _TOKEN_LOCK:
        _ID_TOKEN = id_token
        _REFRESH_TOKEN = new_refresh_token
        _TOKEN_EXPIRY = datetime.now(timezone.utc).timestamp() + expires_in


def _firestore_request(url, method="GET", payload=None, require_admin=False):
    headers = {}
    if require_admin:
        with _TOKEN_LOCK:
            token = _ID_TOKEN
            token_expiry = _TOKEN_EXPIRY
        if token is None:
            raise AuthenticationRequiredError(
                "Connectez-vous avec un compte administrateur Firebase pour modifier les données."
            )
        if token_expiry <= datetime.now(timezone.utc).timestamp() + 60:
            _refresh_id_token()
            with _TOKEN_LOCK:
                token = _ID_TOKEN
        headers["Authorization"] = "Bearer {}".format(token)

    try:
        return _request_json(url, method=method, payload=payload, headers=headers)
    except FirebaseError as error:
        if not require_admin or "Firebase :" not in str(error):
            raise
        if "INVALID_ID_TOKEN" not in str(error) and "UNAUTHENTICATED" not in str(error):
            raise
        _refresh_id_token()
        with _TOKEN_LOCK:
            refreshed_token = _ID_TOKEN
        return _request_json(
            url,
            method=method,
            payload=payload,
            headers={"Authorization": "Bearer {}".format(refreshed_token)},
        )


def _firestore_collection_url(collection, document_id=None):
    config = _firebase_config()
    project_id = config["project_id"]
    url = (
        "https://firestore.googleapis.com/v1/projects/{}/databases/(default)"
        "/documents/{}".format(project_id, collection)
    )
    if document_id is not None:
        url += "/" + quote(str(document_id), safe="")
    return "{}?{}".format(url, urlencode({"key": config["api_key"]}))


def _firestore_fields(values):
    return {
        key: {"stringValue": "" if value is None else str(value)}
        for key, value in values.items()
    }


def _decode_fields(fields, field_names):
    values = []
    for field_name in field_names:
        field = fields.get(field_name, {})
        value = field.get("stringValue", "")
        values.append("" if value is None else str(value))
    return values


def _list_documents(collection):
    documents = []
    url = _firestore_collection_url(collection)
    query = {"pageSize": 1000}

    while True:
        response = _firestore_request(
            "{}&{}".format(url, urlencode(query))
        )
        documents.extend(response.get("documents", []))
        page_token = response.get("nextPageToken")
        if not page_token:
            break
        query["pageToken"] = page_token

    return documents


def _document_id(document):
    return document["name"].rsplit("/", 1)[-1]


def _timestamp_sort_value(document):
    value = document.get("fields", {}).get("_createdAt", {}).get("timestampValue")
    if value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except (TypeError, ValueError, OverflowError):
            pass

    date_value = document.get("fields", {}).get("date", {}).get("stringValue", "")
    try:
        return datetime.fromisoformat(
            date_value.replace("Z", "+00:00")
        ).timestamp()
    except (TypeError, ValueError, OverflowError):
        pass

    for date_format in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_value, date_format).replace(
                tzinfo=timezone.utc
            ).timestamp()
        except (TypeError, ValueError, OverflowError):
            pass
    return 0


def obtenir_produits():
    documents = _list_documents("produits")
    return [
        (_document_id(document), *_decode_fields(
            document.get("fields", {}), _COLLECTIONS["produits"]
        ))
        for document in documents
    ]


def ajouter_produit(nom, prix, description, image):
    values = dict(zip(_COLLECTIONS["produits"], (nom, prix, description, image)))
    document = _firestore_request(
        _firestore_collection_url("produits"),
        method="POST",
        payload={"fields": _firestore_fields(values)},
        require_admin=True,
    )
    return _document_id(document)


def modifier_produit(id_produit, nom, prix, description, image):
    _modifier_document(
        "produits",
        id_produit,
        dict(zip(_COLLECTIONS["produits"], (nom, prix, description, image))),
    )


def supprimer_produit(id_produit):
    _supprimer_document("produits", id_produit)


def obtenir_publications():
    documents = _list_documents("publications")
    documents.sort(
        key=lambda document: (
            _timestamp_sort_value(document),
            _document_id(document),
        ),
        reverse=True,
    )
    return [
        (_document_id(document), *_decode_fields(
            document.get("fields", {}), _COLLECTIONS["publications"]
        ))
        for document in documents
    ]


def ajouter_publication(titre, contenu, date, image):
    values = dict(zip(
        _COLLECTIONS["publications"], (titre, contenu, date, image)
    ))
    fields = _firestore_fields(values)
    fields["_createdAt"] = {
        "timestampValue": datetime.now(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        )
    }
    document = _firestore_request(
        _firestore_collection_url("publications"),
        method="POST",
        payload={"fields": fields},
        require_admin=True,
    )
    return _document_id(document)


def modifier_publication(id_publication, titre, contenu, date, image):
    _modifier_document(
        "publications",
        id_publication,
        dict(zip(
            _COLLECTIONS["publications"], (titre, contenu, date, image)
        )),
    )


def supprimer_publication(id_publication):
    _supprimer_document("publications", id_publication)


def _modifier_document(collection, document_id, values):
    if document_id is None or not str(document_id):
        raise ValueError("L'identifiant Firestore ne peut pas être vide.")
    query = urlencode(
        [("updateMask.fieldPaths", field_name) for field_name in values]
    )
    _firestore_request(
        "{}&{}".format(
            _firestore_collection_url(collection, document_id), query
        ),
        method="PATCH",
        payload={"fields": _firestore_fields(values)},
        require_admin=True,
    )


def _supprimer_document(collection, document_id):
    if document_id is None or not str(document_id):
        raise ValueError("L'identifiant Firestore ne peut pas être vide.")
    _firestore_request(
        _firestore_collection_url(collection, document_id),
        method="DELETE",
        require_admin=True,
    )
