// Thin wrapper around Firebase Auth. The Firebase SDK is only fetched
// (dynamic import) when a real project is configured, so demo mode never
// makes a network request to Google and never throws on a missing config.
import { isFirebaseConfigured } from "./firebase-config.js";
import { getFirebaseApp, SDK_VERSION } from "./firebase-core.js";

const AUTH_URL = `https://www.gstatic.com/firebasejs/${SDK_VERSION}/firebase-auth.js`;

let authApi = null; // { auth, GoogleAuthProvider, signInWithEmailAndPassword, ... }
let currentUser = null;
const authListeners = new Set();

export function isMembershipEnabled() {
  return isFirebaseConfigured();
}

export async function initAuth() {
  if (!isFirebaseConfigured() || authApi) return authApi;

  const [app, authMod] = await Promise.all([
    getFirebaseApp(),
    import(/* webpackIgnore: true */ AUTH_URL)
  ]);

  const auth = authMod.getAuth(app);

  authApi = {
    auth,
    createUserWithEmailAndPassword: authMod.createUserWithEmailAndPassword,
    signInWithEmailAndPassword: authMod.signInWithEmailAndPassword,
    signInWithPopup: authMod.signInWithPopup,
    GoogleAuthProvider: authMod.GoogleAuthProvider,
    updateProfile: authMod.updateProfile,
    signOut: authMod.signOut
  };

  authMod.onAuthStateChanged(auth, (user) => {
    currentUser = user;
    authListeners.forEach((cb) => cb(user));
  });

  return authApi;
}

export function getCurrentUser() {
  return currentUser;
}

export function onAuthChange(cb) {
  authListeners.add(cb);
  if (authApi) cb(currentUser);
  return () => authListeners.delete(cb);
}

export async function signUpWithEmail(email, password, displayName) {
  const api = await initAuth();
  if (!api) throw new Error("demo-mode");
  const cred = await api.createUserWithEmailAndPassword(api.auth, email, password);
  if (displayName) {
    await api.updateProfile(cred.user, { displayName });
  }
  return cred.user;
}

export async function signInWithEmail(email, password) {
  const api = await initAuth();
  if (!api) throw new Error("demo-mode");
  const cred = await api.signInWithEmailAndPassword(api.auth, email, password);
  return cred.user;
}

export async function signInWithGoogle() {
  const api = await initAuth();
  if (!api) throw new Error("demo-mode");
  const provider = new api.GoogleAuthProvider();
  const cred = await api.signInWithPopup(api.auth, provider);
  return cred.user;
}

export async function signOutUser() {
  const api = await initAuth();
  if (!api) return;
  await api.signOut(api.auth);
}
