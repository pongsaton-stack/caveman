// Firebase Web config is NOT a secret — it's meant to be public in client
// code (Firebase enforces security via Auth + Firestore rules, not by hiding
// this object). Replace the placeholders below with your own project's
// values from Firebase console > Project settings > General > Your apps.
// See README.md "Turning on membership (Firebase setup)" for the full
// step-by-step. Until you do, the site runs in demo/read-only mode.
export const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};

export function isFirebaseConfigured() {
  return Boolean(
    firebaseConfig.apiKey &&
      !firebaseConfig.apiKey.startsWith("YOUR_") &&
      firebaseConfig.projectId &&
      !firebaseConfig.projectId.startsWith("YOUR_")
  );
}

// Optional: Firebase App Check with reCAPTCHA v3. This is what actually
// stops a bot or a script from hitting your Firestore/Auth APIs directly
// (bypassing this web app entirely) — get a site key from
// https://www.google.com/recaptcha/admin (choose reCAPTCHA v3), register
// this site's domain there, then also turn on enforcement for Firestore
// and Authentication in Firebase console > App Check. Leave blank to skip;
// the site works fine without it, just without this extra bot-abuse layer.
export const appCheckSiteKey = "";

export function isAppCheckConfigured() {
  return Boolean(appCheckSiteKey);
}
