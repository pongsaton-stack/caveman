// Small DOM/string helpers used everywhere user-supplied text gets rendered.
// Every value that came from a user (Firestore doc, form input, wallet address)
// MUST go through escapeHtml() before landing in a template string, or be set
// via textContent instead. Never interpolate raw user text into innerHTML.

export function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[ch]));
}

// Truncate long user text defensively so one giant paste can't blow up layout.
export function clampText(value, maxLen) {
  const str = String(value ?? "");
  return str.length > maxLen ? `${str.slice(0, maxLen - 1)}…` : str;
}

export function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else if (key.startsWith("on") && typeof value === "function") {
      node.addEventListener(key.slice(2).toLowerCase(), value);
    } else {
      node.setAttribute(key, value);
    }
  }
  for (const child of [].concat(children)) {
    if (child === undefined || child === null) continue;
    node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
  }
  return node;
}

export function isValidEthAddress(address) {
  return /^0x[a-fA-F0-9]{40}$/.test(String(address || ""));
}

export function isValidHttpUrl(value) {
  try {
    const u = new URL(value);
    return u.protocol === "http:" || u.protocol === "https:";
  } catch {
    return false;
  }
}
