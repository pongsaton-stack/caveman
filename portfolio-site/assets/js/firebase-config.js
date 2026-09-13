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
