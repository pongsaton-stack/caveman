// Shared Firebase App instance. Both auth.js and db.js import from here so
// initializeApp() is only ever called once — calling it twice with the same
// config throws ("Firebase App named '[DEFAULT]' already exists").
import { firebaseConfig, isFirebaseConfigured } from "./firebase-config.js";

const SDK_VERSION = "10.13.0";
let appPromise = null;

export function getFirebaseApp() {
  if (!isFirebaseConfigured()) return Promise.resolve(null);
  if (!appPromise) {
    appPromise = import(
      /* webpackIgnore: true */ `https://www.gstatic.com/firebasejs/${SDK_VERSION}/firebase-app.js`
    ).then(({ initializeApp }) => initializeApp(firebaseConfig));
  }
  return appPromise;
}

export { SDK_VERSION };
