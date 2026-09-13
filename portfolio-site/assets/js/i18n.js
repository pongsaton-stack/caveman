// Minimal i18n: two languages (Thai default, English for global visitors),
// persisted in localStorage. Every user-facing string lives here so adding a
// language later means adding one object, not hunting through markup.

const STRINGS = {
  th: {
    siteName: "AI Works",
    tagline: "รวมผลงานจาก AI ทุกรูปแบบ ไว้ในที่เดียว",
    heroTitle: "ผลงานที่สร้างด้วย AI จากทั่วโลก",
    heroSubtitle:
      "แลกเปลี่ยนผลงานและความรู้เรื่อง AI กับคนทั้งโลก — สมัครสมาชิกเพื่อเผยแพร่ผลงานของคุณเองและพูดคุยกับคนอื่น",
    searchPlaceholder: "ค้นหาผลงาน หรือเครื่องมือ AI...",
    resultsCount: "พบ {n} ผลงาน",
    emptyState: "ไม่พบผลงานที่ตรงกับการค้นหา",
    footerNote: "สร้างด้วย HTML/CSS/JS ล้วน ๆ — แก้ไขผลงานตัวอย่างได้ที่ assets/data/works.js",
    demoModeBanner:
      "โหมดสาธิต: ยังไม่ได้เชื่อมต่อระบบสมาชิก (Firebase) — ดูผลงานตัวอย่างได้ แต่สมัครสมาชิก/โพสต์/คอมเมนต์ยังใช้ไม่ได้จนกว่าเจ้าของเว็บจะตั้งค่า",
    signIn: "เข้าสู่ระบบ",
    signUp: "สมัครสมาชิก",
    signOut: "ออกจากระบบ",
    myProfile: "โปรไฟล์ของฉัน",
    submitWork: "+ แชร์ผลงาน",
    langToggle: "EN",
    all: "ทั้งหมด",
    cat_writing: "งานเขียน",
    cat_code: "โค้ด",
    cat_image: "ภาพ",
    cat_video: "วิดีโอ",
    cat_audio: "เสียง/เพลง",
    cat_agent: "AI Agent/อัตโนมัติ",
    cat_data: "วิเคราะห์ข้อมูล",
    cat_research: "ค้นหา/วิจัย",
    cat_business: "ธุรกิจ/องค์กร",
    cat_science: "วิทยาศาสตร์/สุขภาพ",
    cat_design: "ออกแบบ/3D/เกม",
    cat_education: "การศึกษา",
    authSignInTitle: "เข้าสู่ระบบ",
    authSignUpTitle: "สมัครสมาชิกใหม่",
    emailLabel: "อีเมล",
    passwordLabel: "รหัสผ่าน (อย่างน้อย 6 ตัวอักษร)",
    displayNameLabel: "ชื่อที่แสดง",
    authSubmitSignIn: "เข้าสู่ระบบ",
    authSubmitSignUp: "สมัครสมาชิก",
    authSwitchToSignUp: "ยังไม่มีบัญชี? สมัครสมาชิก",
    authSwitchToSignIn: "มีบัญชีอยู่แล้ว? เข้าสู่ระบบ",
    authGoogle: "เข้าสู่ระบบด้วย Google",
    authDisabledDemo: "ฟีเจอร์นี้ต้องเชื่อมต่อ Firebase ก่อน (ดู README)",
    authErrEmailInUse: "อีเมลนี้ถูกใช้สมัครสมาชิกแล้ว",
    authErrWrongCreds: "อีเมลหรือรหัสผ่านไม่ถูกต้อง",
    authErrWeakPassword: "รหัสผ่านสั้นเกินไป (อย่างน้อย 6 ตัวอักษร)",
    authErrInvalidEmail: "รูปแบบอีเมลไม่ถูกต้อง",
    authErrGeneric: "เกิดข้อผิดพลาด กรุณาลองใหม่",
    authForgotPassword: "ลืมรหัสผ่าน?",
    authResetSent: "ส่งลิงก์รีเซ็ตรหัสผ่านไปที่อีเมลแล้ว (เช็คใน spam ด้วย)",
    authResetNeedEmail: "กรอกอีเมลก่อน แล้วกด \"ลืมรหัสผ่าน?\" อีกครั้ง",
    submitTitle: "แชร์ผลงานของคุณ",
    titleLabel: "ชื่อผลงาน",
    categoryLabel: "หมวดหมู่",
    toolLabel: "เครื่องมือ AI ที่ใช้",
    descriptionLabel: "คำอธิบายสั้น ๆ",
    linkLabel: "ลิงก์ไปดูผลงาน (ไม่บังคับ)",
    thumbnailLabel: "อีโมจิไอคอน (เช่น 🎨)",
    submitButton: "เผยแพร่ผลงาน",
    cancelButton: "ยกเลิก",
    madeWith: "สร้างด้วย",
    commentsTitle: "ความคิดเห็น",
    addCommentPlaceholder: "แลกเปลี่ยนความคิดเห็น...",
    postComment: "โพสต์",
    noComments: "ยังไม่มีความคิดเห็น เป็นคนแรกสิ",
    supportCreator: "สนับสนุนผู้สร้าง",
    connectWallet: "เชื่อมต่อ Wallet",
    disconnectWallet: "ยกเลิกการเชื่อมต่อ",
    walletBalance: "ยอดคงเหลือ",
    walletNetwork: "เครือข่าย",
    walletNotFound: "ไม่พบ wallet ในเบราว์เซอร์ (ติดตั้ง MetaMask หรือ wallet ที่รองรับ)",
    tipAmountLabel: "จำนวน (ETH)",
    sendTip: "ส่ง",
    tipSuccess: "ส่งสำเร็จ! ดูธุรกรรมได้จาก wallet ของคุณ",
    tipError: "ส่งไม่สำเร็จ",
    testnetWarning:
      "⚠️ ฟีเจอร์ธุรกรรมบล็อกเชนเกี่ยวข้องกับเงินจริง ทดสอบบน testnet ก่อนใช้เงินจริงเสมอ และตรวจสอบที่อยู่ผู้รับให้ถูกต้องทุกครั้ง",
    profileTitle: "โปรไฟล์ของฉัน",
    bioLabel: "แนะนำตัวสั้น ๆ",
    walletAddressLabel: "ที่อยู่ Wallet (ไม่บังคับ) สำหรับรับการสนับสนุน",
    saveProfile: "บันทึก",
    profileSaved: "บันทึกโปรไฟล์แล้ว",
    close: "ปิด",
    viewFull: "ดูผลงานฉบับเต็ม →"
  },
  en: {
    siteName: "AI Works",
    tagline: "Every kind of AI-made work, in one place",
    heroTitle: "AI-made works from around the world",
    heroSubtitle:
      "Trade AI knowledge and work with people everywhere — sign up to publish your own work and join the discussion",
    searchPlaceholder: "Search works or AI tools...",
    resultsCount: "{n} works found",
    emptyState: "No works match your search",
    footerNote: "Plain HTML/CSS/JS — edit sample works at assets/data/works.js",
    demoModeBanner:
      "Demo mode: membership backend (Firebase) isn't connected yet — browsing works, but sign-up/posting/comments are disabled until the site owner configures it.",
    signIn: "Sign in",
    signUp: "Sign up",
    signOut: "Sign out",
    myProfile: "My profile",
    submitWork: "+ Share work",
    langToggle: "ไทย",
    all: "All",
    cat_writing: "Writing",
    cat_code: "Code",
    cat_image: "Image",
    cat_video: "Video",
    cat_audio: "Audio/Music",
    cat_agent: "AI Agent/Automation",
    cat_data: "Data Analysis",
    cat_research: "Search/Research",
    cat_business: "Business",
    cat_science: "Science/Health",
    cat_design: "Design/3D/Gaming",
    cat_education: "Education",
    authSignInTitle: "Sign in",
    authSignUpTitle: "Create an account",
    emailLabel: "Email",
    passwordLabel: "Password (min 6 characters)",
    displayNameLabel: "Display name",
    authSubmitSignIn: "Sign in",
    authSubmitSignUp: "Sign up",
    authSwitchToSignUp: "No account yet? Sign up",
    authSwitchToSignIn: "Already have an account? Sign in",
    authGoogle: "Continue with Google",
    authDisabledDemo: "This feature needs Firebase connected first (see README)",
    authErrEmailInUse: "Email already registered.",
    authErrWrongCreds: "Incorrect email or password.",
    authErrWeakPassword: "Password too weak (min 6 characters).",
    authErrInvalidEmail: "Invalid email address.",
    authErrGeneric: "Something went wrong. Please try again.",
    authForgotPassword: "Forgot password?",
    authResetSent: "Password reset link sent to your email (check spam too).",
    authResetNeedEmail: "Enter your email first, then click \"Forgot password?\" again.",
    submitTitle: "Share your work",
    titleLabel: "Title",
    categoryLabel: "Category",
    toolLabel: "AI tool used",
    descriptionLabel: "Short description",
    linkLabel: "Link to full work (optional)",
    thumbnailLabel: "Emoji icon (e.g. 🎨)",
    submitButton: "Publish",
    cancelButton: "Cancel",
    madeWith: "Made with",
    commentsTitle: "Comments",
    addCommentPlaceholder: "Join the discussion...",
    postComment: "Post",
    noComments: "No comments yet — be the first",
    supportCreator: "Support creator",
    connectWallet: "Connect Wallet",
    disconnectWallet: "Disconnect",
    walletBalance: "Balance",
    walletNetwork: "Network",
    walletNotFound: "No wallet found in this browser (install MetaMask or a compatible wallet)",
    tipAmountLabel: "Amount (ETH)",
    sendTip: "Send",
    tipSuccess: "Sent! Check your wallet for the transaction.",
    tipError: "Send failed",
    testnetWarning:
      "⚠️ Blockchain transactions involve real money. Always test on a testnet first and double-check the recipient address.",
    profileTitle: "My profile",
    bioLabel: "Short bio",
    walletAddressLabel: "Wallet address (optional) to receive support",
    saveProfile: "Save",
    profileSaved: "Profile saved",
    close: "Close",
    viewFull: "View full work →"
  }
};

const STORAGE_KEY = "ai-works-lang";
let currentLang = localStorage.getItem(STORAGE_KEY) || "th";
const listeners = new Set();

export function getLang() {
  return currentLang;
}

export function setLang(lang) {
  if (!STRINGS[lang]) return;
  currentLang = lang;
  try {
    localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    /* localStorage unavailable (private mode) — language just won't persist */
  }
  listeners.forEach((cb) => cb(lang));
  applyToDom();
}

export function onLangChange(cb) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

export function t(key, vars = {}) {
  const template = STRINGS[currentLang][key] ?? STRINGS.th[key] ?? key;
  return template.replace(/\{(\w+)\}/g, (_, name) => (vars[name] ?? ""));
}

export function applyToDom(root = document) {
  root.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  root.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", t(node.dataset.i18nPlaceholder));
  });
  root.querySelectorAll("[data-i18n-title]").forEach((node) => {
    node.setAttribute("title", t(node.dataset.i18nTitle));
  });
}
