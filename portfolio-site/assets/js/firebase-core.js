// Shared Firebase App instance. Both auth.js and db.js import from here so
// initializeApp() is only ever called once — calling it twice with the same
// config throws ("Firebase App named '[DEFAULT]' already exists").
import { firebaseConfig, isFirebaseConfigured, appCheckSiteKey, isAppCheckConfigured } from "./firebase-config.js";

const SDK_VERSION = "10.13.0";
let appPromise = null;

export function getFirebaseApp() {
  if (!isFirebaseConfigured()) return Promise.resolve(null);
  if (!appPromise) {
    appPromise = import(
      /* webpackIgnore: true */ `https://www.gstatic.com/firebasejs/${SDK_VERSION}/firebase-app.js`
    )
      .then(({ initializeApp }) => initializeApp(firebaseConfig))
      .then(async (app) => {
        // App Check is optional and additive — a failure here (bad site
        // key, domain not registered yet) must never take the whole app
        // down with it, so it's isolated in its own try/catch.
        if (isAppCheckConfigured()) {
          try {
            const { initializeAppCheck, ReCaptchaV3Provider } = await import(
              /* webpackIgnore: true */ `https://www.gstatic.com/firebasejs/${SDK_VERSION}/firebase-app-check.js`
            );
            initializeAppCheck(app, {
              provider: new ReCaptchaV3Provider(appCheckSiteKey),
              isTokenAutoRefreshEnabled: true
            });
          } catch (err) {
            console.error("Firebase App Check failed to initialize", err);
          }
        }
        return app;
      });
  }
  return appPromise;
}

export { SDK_VERSION };
