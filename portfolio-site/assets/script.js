import { getLang, setLang, onLangChange, t, applyToDom } from "./js/i18n.js";
import {
  initAuth,
  isMembershipEnabled,
  onAuthChange,
  getCurrentUser,
  signUpWithEmail,
  signInWithEmail,
  signInWithGoogle,
  signOutUser
} from "./js/auth.js";
import { subscribeWorks, submitWork, subscribeComments, addComment, getUserProfile, saveUserProfile } from "./js/db.js";
import {
  hasInjectedWallet,
  connectWallet,
  disconnectWallet,
  getWalletState,
  onWalletChange,
  getBalanceEth,
  sendPaymentEth
} from "./js/wallet.js";
import { escapeHtml, isValidEthAddress } from "./js/render-utils.js";
import { AI_WORKS as DEMO_WORKS } from "./data/works.js";

const $ = (id) => document.getElementById(id);

// ---------------------------------------------------------------- state ---
let allWorks = [];
let activeCategory = "all";
let searchTerm = "";
let openWork = null; // the work object shown in the detail modal
let commentsUnsub = null;
let commentsGeneration = 0; // guards against a stale async subscription outliving its modal
let authMode = "signin"; // "signin" | "signup"

// ------------------------------------------------------------- elements ---
const els = {
  langToggle: $("langToggle"),
  authArea: $("authArea"),
  demoBanner: $("demoBanner"),
  filters: $("filters"),
  searchInput: $("searchInput"),
  submitWorkBtn: $("submitWorkBtn"),
  resultsCount: $("resultsCount"),
  grid: $("worksGrid"),
  emptyState: $("emptyState"),

  modalOverlay: $("modalOverlay"),
  modalClose: $("modalClose"),
  modalThumb: $("modalThumb"),
  modalCategory: $("modalCategory"),
  modalTitle: $("modalTitle"),
  modalTool: $("modalTool"),
  modalDescription: $("modalDescription"),
  modalDate: $("modalDate"),
  modalLink: $("modalLink"),
  modalSupport: $("modalSupport"),
  tipAmount: $("tipAmount"),
  tipSendBtn: $("tipSendBtn"),
  tipStatus: $("tipStatus"),
  commentsList: $("commentsList"),
  commentInput: $("commentInput"),
  commentSendBtn: $("commentSendBtn"),

  authOverlay: $("authOverlay"),
  authClose: $("authClose"),
  authTitle: $("authTitle"),
  authError: $("authError"),
  authForm: $("authForm"),
  authNameField: $("authNameField"),
  authName: $("authName"),
  authEmail: $("authEmail"),
  authPassword: $("authPassword"),
  authSubmitBtn: $("authSubmitBtn"),
  authGoogleBtn: $("authGoogleBtn"),
  authSwitchBtn: $("authSwitchBtn"),

  submitOverlay: $("submitOverlay"),
  submitClose: $("submitClose"),
  submitError: $("submitError"),
  submitForm: $("submitForm"),
  submitTitleInput: $("submitTitleInput"),
  submitCategoryInput: $("submitCategoryInput"),
  submitToolInput: $("submitToolInput"),
  submitDescriptionInput: $("submitDescriptionInput"),
  submitLinkInput: $("submitLinkInput"),
  submitThumbnailInput: $("submitThumbnailInput"),
  submitCancelBtn: $("submitCancelBtn"),

  profileOverlay: $("profileOverlay"),
  profileClose: $("profileClose"),
  profileForm: $("profileForm"),
  profileNameInput: $("profileNameInput"),
  profileBioInput: $("profileBioInput"),
  profileWalletInput: $("profileWalletInput"),
  walletStatus: $("walletStatus"),
  connectWalletBtn: $("connectWalletBtn"),
  profileSaveStatus: $("profileSaveStatus")
};

// ------------------------------------------------------------------ i18n ---
function refreshI18n() {
  applyToDom();
  els.langToggle.textContent = t("langToggle");
  renderAuthArea(getCurrentUser());
  renderGrid();
  if (openWork) openWorkModal(openWork, { keepScroll: true });
}

els.langToggle.addEventListener("click", () => {
  setLang(getLang() === "th" ? "en" : "th");
});
onLangChange(refreshI18n);

// -------------------------------------------------------------- demo mode ---
els.demoBanner.hidden = isMembershipEnabled();
if (isMembershipEnabled()) initAuth();

// ------------------------------------------------------------- works data ---
function loadWorks() {
  if (!isMembershipEnabled()) {
    allWorks = DEMO_WORKS;
    renderGrid();
    return;
  }
  subscribeWorks(
    (works) => {
      allWorks = works;
      renderGrid();
    },
    (err) => console.error("subscribeWorks failed", err)
  );
}

function formatDate(value) {
  let d;
  if (value?.toDate) d = value.toDate(); // Firestore Timestamp
  else d = new Date(value);
  if (Number.isNaN(d?.getTime())) return "";
  return d.toLocaleDateString(getLang() === "th" ? "th-TH" : "en-US", {
    year: "numeric",
    month: "short",
    day: "numeric"
  });
}

function matchesFilters(work) {
  const categoryOk = activeCategory === "all" || work.category === activeCategory;
  if (!categoryOk) return false;
  if (!searchTerm) return true;
  const haystack = `${work.title} ${work.tool} ${work.description}`.toLowerCase();
  return haystack.includes(searchTerm);
}

function renderGrid() {
  const works = allWorks.filter(matchesFilters);
  els.grid.innerHTML = "";

  works.forEach((work) => {
    const card = document.createElement("button");
    card.className = "card";
    card.type = "button";
    card.innerHTML = `
      <div class="card-thumb">${escapeHtml(work.thumbnail || "✨")}</div>
      <span class="tag">${escapeHtml(t(`cat_${work.category}`))}</span>
      <h3>${escapeHtml(work.title)}</h3>
      <p>${escapeHtml(work.description || "")}</p>
      <div class="card-meta">
        <span>${escapeHtml(work.tool || "")}${work.ownerName ? ` · ${escapeHtml(work.ownerName)}` : ""}</span>
        <span>${escapeHtml(formatDate(work.createdAt ?? work.date))}</span>
      </div>
    `;
    card.addEventListener("click", () => openWorkModal(work));
    els.grid.appendChild(card);
  });

  els.emptyState.hidden = works.length !== 0;
  els.resultsCount.textContent = t("resultsCount", { n: works.length });
}

els.filters.querySelectorAll(".filter-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    els.filters.querySelectorAll(".filter-btn").forEach((b) => {
      b.classList.remove("is-active");
      b.setAttribute("aria-selected", "false");
    });
    btn.classList.add("is-active");
    btn.setAttribute("aria-selected", "true");
    activeCategory = btn.dataset.category;
    renderGrid();
  });
});

els.searchInput.addEventListener("input", (e) => {
  searchTerm = e.target.value.trim().toLowerCase();
  renderGrid();
});

// ---------------------------------------------------------- work modal ---
function isRealWork(work) {
  return isMembershipEnabled() && typeof work.id === "string";
}

function openWorkModal(work, { keepScroll = false } = {}) {
  openWork = work;
  els.modalThumb.textContent = work.thumbnail || "✨";
  els.modalCategory.textContent = t(`cat_${work.category}`);
  els.modalTitle.textContent = work.title;
  els.modalTool.textContent = `${t("madeWith")} ${work.tool || ""}`;
  els.modalDescription.textContent = work.description || "";
  els.modalDate.textContent = formatDate(work.createdAt ?? work.date);

  if (work.link) {
    els.modalLink.href = work.link;
    els.modalLink.hidden = false;
  } else {
    els.modalLink.hidden = true;
  }

  const hasWallet = isValidEthAddress(work.ownerWalletAddress);
  els.modalSupport.hidden = !hasWallet;
  els.tipStatus.textContent = "";
  els.tipAmount.value = "";

  renderComments(work);

  if (!keepScroll) {
    els.modalOverlay.hidden = false;
    document.body.style.overflow = "hidden";
  }
}

function closeWorkModal() {
  els.modalOverlay.hidden = true;
  document.body.style.overflow = "";
  openWork = null;
  commentsGeneration++; // invalidate any subscribeComments() still in flight
  if (commentsUnsub) {
    commentsUnsub();
    commentsUnsub = null;
  }
}

els.modalClose.addEventListener("click", closeWorkModal);
els.modalOverlay.addEventListener("click", (e) => {
  if (e.target === els.modalOverlay) closeWorkModal();
});

async function renderComments(work) {
  const myGeneration = ++commentsGeneration;
  if (commentsUnsub) {
    commentsUnsub();
    commentsUnsub = null;
  }
  els.commentsList.innerHTML = "";

  const commentFormVisible = isRealWork(work);
  els.commentInput.closest(".comment-form").hidden = !commentFormVisible;

  if (!commentFormVisible) {
    els.commentsList.innerHTML = `<p class="no-comments">${escapeHtml(t("noComments"))}</p>`;
    return;
  }

  const unsub = await subscribeComments(work.id, (comments) => {
    if (myGeneration !== commentsGeneration) return; // modal moved on; ignore stale update
    if (!comments.length) {
      els.commentsList.innerHTML = `<p class="no-comments">${escapeHtml(t("noComments"))}</p>`;
      return;
    }
    els.commentsList.innerHTML = comments
      .map(
        (c) => `
        <div class="comment">
          <span class="comment-author">${escapeHtml(c.authorName || "Anonymous")}</span>
          <p class="comment-text">${escapeHtml(c.text)}</p>
        </div>`
      )
      .join("");
  });

  // If the modal already moved to a different work (or closed) while the
  // subscription was being set up, tear it down immediately instead of
  // stashing it — otherwise it would leak for the rest of the session.
  if (myGeneration === commentsGeneration) {
    commentsUnsub = unsub;
  } else {
    unsub();
  }
}

els.commentSendBtn.addEventListener("click", async () => {
  const user = getCurrentUser();
  if (!user) return openAuthModal("signin");
  if (!openWork || !isRealWork(openWork)) return;
  const text = els.commentInput.value.trim();
  if (!text) return;
  try {
    await addComment(user, openWork.id, text);
    els.commentInput.value = "";
  } catch (err) {
    console.error("addComment failed", err);
  }
});

// ------------------------------------------------------- wallet / tipping ---
async function renderWalletStatus() {
  const state = getWalletState();
  if (!state.address) {
    els.walletStatus.textContent = "";
    els.connectWalletBtn.textContent = t("connectWallet");
    return;
  }

  els.profileWalletInput.value = state.address;
  els.connectWalletBtn.textContent = t("disconnectWallet");
  const shortAddr = `${state.address.slice(0, 6)}...${state.address.slice(-4)}`;
  els.walletStatus.textContent = `${shortAddr} (${state.chainName})`;

  try {
    const balance = await getBalanceEth();
    // Guard against the user disconnecting while this lookup was in flight.
    if (getWalletState().address === state.address) {
      els.walletStatus.textContent = `${shortAddr} (${state.chainName}) · ${t("walletBalance")}: ${Number(balance).toFixed(4)} ETH`;
    }
  } catch (err) {
    console.error("getBalanceEth failed", err);
  }
}
onWalletChange(renderWalletStatus);

els.connectWalletBtn.addEventListener("click", async () => {
  const state = getWalletState();
  if (state.address) {
    disconnectWallet();
    return;
  }
  if (!hasInjectedWallet()) {
    els.walletStatus.textContent = t("walletNotFound");
    return;
  }
  try {
    await connectWallet();
  } catch (err) {
    console.error("connectWallet failed", err);
    els.walletStatus.textContent = t("authErrGeneric");
  }
});

els.tipSendBtn.addEventListener("click", async () => {
  if (!openWork) return;
  els.tipStatus.textContent = "";

  if (!hasInjectedWallet()) {
    els.tipStatus.textContent = t("walletNotFound");
    return;
  }
  try {
    if (!getWalletState().address) await connectWallet();
    const hash = await sendPaymentEth(openWork.ownerWalletAddress, els.tipAmount.value);
    els.tipStatus.textContent = `${t("tipSuccess")} (${hash.slice(0, 10)}...)`;
  } catch (err) {
    console.error("sendPaymentEth failed", err);
    els.tipStatus.textContent = t("tipError");
  }
});

// -------------------------------------------------------------- auth UI ---
function renderAuthArea(user) {
  els.authArea.innerHTML = "";
  if (user) {
    const profileBtn = document.createElement("button");
    profileBtn.className = "btn btn-ghost";
    profileBtn.textContent = user.displayName || user.email || "•";
    profileBtn.addEventListener("click", openProfileModal);

    const signOutBtn = document.createElement("button");
    signOutBtn.className = "btn btn-ghost";
    signOutBtn.textContent = t("signOut");
    signOutBtn.addEventListener("click", () => signOutUser());

    els.authArea.append(profileBtn, signOutBtn);
  } else {
    const signInBtn = document.createElement("button");
    signInBtn.className = "btn btn-ghost";
    signInBtn.textContent = t("signIn");
    signInBtn.addEventListener("click", () => openAuthModal("signin"));

    const signUpBtn = document.createElement("button");
    signUpBtn.className = "btn btn-primary";
    signUpBtn.textContent = t("signUp");
    signUpBtn.addEventListener("click", () => openAuthModal("signup"));

    els.authArea.append(signInBtn, signUpBtn);
  }
}

onAuthChange((user) => {
  renderAuthArea(user);
  renderGrid();
});

function setAuthMode(mode) {
  authMode = mode;
  const isSignUp = mode === "signup";
  els.authTitle.textContent = t(isSignUp ? "authSignUpTitle" : "authSignInTitle");
  els.authNameField.hidden = !isSignUp;
  els.authSubmitBtn.textContent = t(isSignUp ? "authSubmitSignUp" : "authSubmitSignIn");
  els.authSwitchBtn.textContent = t(isSignUp ? "authSwitchToSignIn" : "authSwitchToSignUp");
  els.authError.hidden = true;
}

function openAuthModal(mode) {
  setAuthMode(mode);
  const disabled = !isMembershipEnabled();
  els.authForm.hidden = disabled;
  els.authGoogleBtn.hidden = disabled;
  els.authSwitchBtn.hidden = disabled;
  els.authError.hidden = !disabled;
  if (disabled) els.authError.textContent = t("authDisabledDemo");
  els.authOverlay.hidden = false;
}

function closeAuthModal() {
  els.authOverlay.hidden = true;
  els.authForm.reset();
}

els.authClose.addEventListener("click", closeAuthModal);
els.authOverlay.addEventListener("click", (e) => {
  if (e.target === els.authOverlay) closeAuthModal();
});
els.authSwitchBtn.addEventListener("click", () => setAuthMode(authMode === "signin" ? "signup" : "signin"));

function friendlyAuthError(err) {
  const code = err?.code || "";
  if (code.includes("email-already-in-use")) return t("authErrEmailInUse");
  if (code.includes("invalid-credential") || code.includes("wrong-password") || code.includes("user-not-found")) {
    return t("authErrWrongCreds");
  }
  if (code.includes("weak-password")) return t("authErrWeakPassword");
  if (code.includes("invalid-email")) return t("authErrInvalidEmail");
  return t("authErrGeneric");
}

els.authForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  els.authError.hidden = true;
  const email = els.authEmail.value.trim();
  const password = els.authPassword.value;
  try {
    if (authMode === "signup") {
      await signUpWithEmail(email, password, els.authName.value.trim());
    } else {
      await signInWithEmail(email, password);
    }
    closeAuthModal();
  } catch (err) {
    console.error("auth failed", err);
    els.authError.textContent = friendlyAuthError(err);
    els.authError.hidden = false;
  }
});

els.authGoogleBtn.addEventListener("click", async () => {
  try {
    await signInWithGoogle();
    closeAuthModal();
  } catch (err) {
    console.error("google sign-in failed", err);
    els.authError.textContent = friendlyAuthError(err);
    els.authError.hidden = false;
  }
});

// -------------------------------------------------------- submit work UI ---
els.submitWorkBtn.addEventListener("click", () => {
  if (!isMembershipEnabled()) return openAuthModal("signin");
  const user = getCurrentUser();
  if (!user) return openAuthModal("signin");
  els.submitForm.reset();
  els.submitError.hidden = true;
  els.submitOverlay.hidden = false;
});

function closeSubmitModal() {
  els.submitOverlay.hidden = true;
}
els.submitClose.addEventListener("click", closeSubmitModal);
els.submitCancelBtn.addEventListener("click", closeSubmitModal);
els.submitOverlay.addEventListener("click", (e) => {
  if (e.target === els.submitOverlay) closeSubmitModal();
});

els.submitForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const user = getCurrentUser();
  if (!user) return;
  els.submitError.hidden = true;

  try {
    await submitWork(user, {
      title: els.submitTitleInput.value,
      category: els.submitCategoryInput.value,
      tool: els.submitToolInput.value,
      description: els.submitDescriptionInput.value,
      link: els.submitLinkInput.value,
      thumbnail: els.submitThumbnailInput.value || "✨",
      ownerWalletAddress: getWalletState().address || ""
    });
    closeSubmitModal();
  } catch (err) {
    console.error("submitWork failed", err);
    els.submitError.textContent = t("authErrGeneric");
    els.submitError.hidden = false;
  }
});

// ----------------------------------------------------------- profile UI ---
async function openProfileModal() {
  const user = getCurrentUser();
  if (!user) return;
  els.profileSaveStatus.textContent = "";
  els.profileNameInput.value = user.displayName || "";
  renderWalletStatus();

  try {
    const profile = await getUserProfile(user.uid);
    if (profile) {
      els.profileBioInput.value = profile.bio || "";
      // Don't clobber a wallet that's live-connected in this tab with a
      // possibly-stale address saved on a previous visit.
      if (profile.walletAddress && !getWalletState().address) {
        els.profileWalletInput.value = profile.walletAddress;
      }
    }
  } catch (err) {
    console.error("getUserProfile failed", err);
  }

  els.profileOverlay.hidden = false;
}

function closeProfileModal() {
  els.profileOverlay.hidden = true;
}
els.profileClose.addEventListener("click", closeProfileModal);
els.profileOverlay.addEventListener("click", (e) => {
  if (e.target === els.profileOverlay) closeProfileModal();
});

els.profileForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const user = getCurrentUser();
  if (!user) return;
  try {
    await saveUserProfile(user, {
      displayName: els.profileNameInput.value,
      bio: els.profileBioInput.value,
      walletAddress: els.profileWalletInput.value
    });
    els.profileSaveStatus.textContent = t("profileSaved");
  } catch (err) {
    console.error("saveUserProfile failed", err);
    els.profileSaveStatus.textContent = t("authErrGeneric");
  }
});

// ------------------------------------------------------------- keyboard ---
document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  if (!els.modalOverlay.hidden) closeWorkModal();
  if (!els.authOverlay.hidden) closeAuthModal();
  if (!els.submitOverlay.hidden) closeSubmitModal();
  if (!els.profileOverlay.hidden) closeProfileModal();
});

// --------------------------------------------------------------- start! ---
refreshI18n();
loadWorks();
