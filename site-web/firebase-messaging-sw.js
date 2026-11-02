importScripts("https://www.gstatic.com/firebasejs/10.14.1/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.14.1/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyCOLl2-1Mb311a9ZMmY0r4b7CJSXeXwHJU",
  authDomain: "vente-24ed2.firebaseapp.com",
  projectId: "vente-24ed2",
  storageBucket: "vente-24ed2.firebasestorage.app",
  messagingSenderId: "609198798927",
  appId: "1:609198798927:web:90cd498385d5434e1e123a",
});

const messaging = firebase.messaging();
const defaultNotificationUrl = new URL("/#actualites", self.location.origin).href;

function safeNotificationUrl(value) {
  try {
    const url = new URL(value || defaultNotificationUrl, self.location.origin);
    return url.origin === self.location.origin ? url.href : defaultNotificationUrl;
  } catch {
    return defaultNotificationUrl;
  }
}

messaging.onBackgroundMessage((payload) => {
  if (payload.notification) return;

  const data = payload.data || {};
  return self.registration.showNotification(data.title || "SUPERLIFE TOGO", {
    body: data.body || "Une nouvelle actualité vous attend.",
    icon: "/assets/vente-icon-192.png",
    badge: "/assets/vente-icon-192.png",
    data: { url: safeNotificationUrl(data.url) },
  });
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const requestedUrl = event.notification.data && event.notification.data.url;
  if (!requestedUrl) return;

  const destination = safeNotificationUrl(requestedUrl);
  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({
      type: "window",
      includeUncontrolled: true,
    });
    const client = windows.find((windowClient) =>
      new URL(windowClient.url).origin === self.location.origin,
    );
    if (client) {
      if (client.url !== destination && "navigate" in client) {
        await client.navigate(destination);
      }
      return client.focus();
    }
    return self.clients.openWindow(destination);
  })());
});
