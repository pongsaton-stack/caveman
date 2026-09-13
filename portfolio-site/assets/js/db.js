// Firestore data access. Client-side validation here is defense in depth
// for UX only — the real security boundary is firestore.rules (see that
// file and the README setup section). Never trust this layer alone.
import { isFirebaseConfigured } from "./firebase-config.js";
import { getFirebaseApp, SDK_VERSION } from "./firebase-core.js";
import { isValidEthAddress, isValidHttpUrl, clampText } from "./render-utils.js";

const FIRESTORE_URL = `https://www.gstatic.com/firebasejs/${SDK_VERSION}/firebase-firestore.js`;

export const VALID_CATEGORIES = [
  "writing", "code", "image", "video", "audio",
  "agent", "data", "research", "business", "science", "design", "education"
];

const LIMITS = {
  title: 120,
  tool: 60,
  description: 500,
  comment: 500,
  bio: 300,
  displayName: 60
};

let fsApi = null;

async function getFirestore() {
  if (!isFirebaseConfigured()) return null;
  if (fsApi) return fsApi;
  const [app, mod] = await Promise.all([getFirebaseApp(), import(/* webpackIgnore: true */ FIRESTORE_URL)]);
  fsApi = { db: mod.getFirestore(app), mod };
  return fsApi;
}

function requireAuthUid(user) {
  if (!user) throw new Error("not-signed-in");
  return user.uid;
}

export async function submitWork(user, work) {
  const { db, mod } = (await getFirestore()) || {};
  if (!db) throw new Error("demo-mode");
  const uid = requireAuthUid(user);

  if (!VALID_CATEGORIES.includes(work.category)) throw new Error("invalid-category");
  const title = clampText(String(work.title || "").trim(), LIMITS.title);
  if (!title) throw new Error("title-required");
  if (work.link && !isValidHttpUrl(work.link)) throw new Error("invalid-link");

  const doc = {
    title,
    category: work.category,
    tool: clampText(String(work.tool || "").trim(), LIMITS.tool),
    description: clampText(String(work.description || "").trim(), LIMITS.description),
    link: work.link ? String(work.link).trim() : "",
    thumbnail: clampText(String(work.thumbnail || "✨").trim(), 8),
    ownerId: uid,
    ownerName: clampText(user.displayName || "Anonymous", LIMITS.displayName),
    ownerWalletAddress: isValidEthAddress(work.ownerWalletAddress) ? work.ownerWalletAddress : "",
    createdAt: mod.serverTimestamp()
  };

  await mod.addDoc(mod.collection(db, "works"), doc);
}

// Returns a Promise<unsubscribeFn>. Callers that care about tearing the
// listener down (anything opened/closed repeatedly, like per-work comments)
// must await this and hold onto the returned function — a bare `.then()`
// here would swallow onSnapshot's unsubscribe and leak listeners.
export async function subscribeWorks(onChange, onError) {
  const api = await getFirestore();
  if (!api) {
    onChange([]); // demo mode: caller falls back to static sample data
    return () => {};
  }
  const { db, mod } = api;
  const q = mod.query(mod.collection(db, "works"), mod.orderBy("createdAt", "desc"), mod.limit(200));
  return mod.onSnapshot(
    q,
    (snap) => onChange(snap.docs.map((d) => ({ id: d.id, ...d.data() }))),
    onError
  );
}

export async function addComment(user, workId, text) {
  const { db, mod } = (await getFirestore()) || {};
  if (!db) throw new Error("demo-mode");
  const uid = requireAuthUid(user);

  const trimmed = clampText(String(text || "").trim(), LIMITS.comment);
  if (!trimmed) throw new Error("comment-empty");

  await mod.addDoc(mod.collection(db, "works", workId, "comments"), {
    text: trimmed,
    authorId: uid,
    authorName: clampText(user.displayName || "Anonymous", LIMITS.displayName),
    createdAt: mod.serverTimestamp()
  });
}

export async function subscribeComments(workId, onChange, onError) {
  const api = await getFirestore();
  if (!api) {
    onChange([]);
    return () => {};
  }
  const { db, mod } = api;
  const q = mod.query(
    mod.collection(db, "works", workId, "comments"),
    mod.orderBy("createdAt", "asc"),
    mod.limit(500)
  );
  return mod.onSnapshot(
    q,
    (snap) => onChange(snap.docs.map((d) => ({ id: d.id, ...d.data() }))),
    onError
  );
}

export async function getUserProfile(uid) {
  const { db, mod } = (await getFirestore()) || {};
  if (!db) return null;
  const snap = await mod.getDoc(mod.doc(db, "users", uid));
  return snap.exists() ? snap.data() : null;
}

export async function saveUserProfile(user, profile) {
  const { db, mod } = (await getFirestore()) || {};
  if (!db) throw new Error("demo-mode");
  const uid = requireAuthUid(user);

  if (profile.walletAddress && !isValidEthAddress(profile.walletAddress)) {
    throw new Error("invalid-wallet-address");
  }

  await mod.setDoc(
    mod.doc(db, "users", uid),
    {
      displayName: clampText(String(profile.displayName || "").trim() || "Anonymous", LIMITS.displayName),
      bio: clampText(String(profile.bio || "").trim(), LIMITS.bio),
      walletAddress: profile.walletAddress || "",
      updatedAt: mod.serverTimestamp()
    },
    { merge: true }
  );
}
