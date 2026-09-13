# AI Works Portfolio

Static site (plain HTML/CSS/JS, no build step) for a global community that shares and discusses works made with AI — images, video, writing, code, and more.

Not related to the caveman project in this repo. Kept in its own top-level folder.

Two languages are built in (Thai default, English toggle) so people anywhere can use it — see [ไทย](#ai-works-portfolio-ภาษาไทย) below for a Thai version of this doc.

## What's here

- **Browsing** — filter by 12 AI-capability categories, search, view details — works with zero setup, no backend required.
- **Membership** (optional, requires setup) — sign up, publish your own work, comment on others' — backed by Firebase (Auth + Firestore), because GitHub Pages is static hosting and can't run a server itself, but Firebase's client SDK can be called directly from the browser.
- **Wallet connect** (optional, requires a member's own crypto wallet) — connect a MetaMask-style wallet and receive small ETH tips from other members on works you've published.

Until Firebase is configured, the site runs in **demo mode**: browsing works fine with the sample data in `assets/data/works.js`, but sign-up/posting/comments show a "needs Firebase" message instead of crashing.

## Running it

Open `index.html` directly in a browser, or serve it locally:

```bash
cd portfolio-site
python3 -m http.server 8000
# open http://localhost:8000
```

## Turning on membership (Firebase setup)

This is a one-time setup the site owner does. Nothing here is secret — Firebase's web config is meant to be public; real security comes from `firestore.rules`, not from hiding these values.

1. Go to [Firebase console](https://console.firebase.google.com/), create a project (free tier is enough).
2. **Build → Authentication → Get started** → enable **Email/Password** and (optional) **Google** sign-in providers.
3. **Build → Firestore Database → Create database** → start in production mode (the rules file below replaces the defaults).
4. **Project settings → General → Your apps → Add app → Web** → copy the config object it gives you.
5. Paste those values into `assets/js/firebase-config.js`, replacing the `YOUR_...` placeholders. Commit the file — it's safe to publish.
6. Deploy the security rules (this is the part that actually protects the data):
   ```bash
   npm install -g firebase-tools
   firebase login
   firebase use --add          # pick your project
   firebase deploy --only firestore:rules
   ```
   `firestore.rules` in this folder is the rules file (`firebase.json` already points to it). **Read it before deploying** — it's short and documents exactly what each rule allows.
7. Reload the site — the demo banner disappears and Sign in/Sign up start working.

If you skip this, the site still works fine for browsing; members just can't sign up yet.

## Wallet connect / tipping (optional, involves real money)

Members can optionally add a wallet address to their profile (**My profile → Connect Wallet**, needs a browser extension like MetaMask). Once set, other members see a **Support creator** box on that member's works and can send them a small amount of ETH directly, wallet-to-wallet — this site never touches the funds or the member's keys.

**Before enabling this for real users:**
- Test the whole flow on a testnet (e.g. Sepolia) with test ETH first.
- The transaction is built in `assets/js/wallet.js`; the actual confirm screen your wallet extension shows is the real safety check — always verify the recipient address there.
- This is a from-scratch implementation, not a security-audited payments product. Treat it as a small tipping feature between consenting members, not a marketplace or financial service.

## Adding/editing sample (demo-mode) works

Edit [`assets/data/works.js`](./assets/data/works.js) — a plain array, each item:

| Field | Description |
|---|---|
| `id` | Unique number |
| `title` | Work title |
| `category` | One of `writing`, `code`, `image`, `video`, `audio`, `agent`, `data`, `research`, `business`, `science`, `design`, `education` |
| `tool` | AI tool used, e.g. Midjourney, Claude, Suno |
| `description` | Short description |
| `date` | `YYYY-MM-DD` |
| `link` | Link to the full work |
| `thumbnail` | An emoji (swap for an image URL with a small CSS/JS change) |

This file is only used in demo mode — once Firebase is configured, real member-submitted works from Firestore take over automatically and this file is ignored.

## File structure

```
portfolio-site/
├── index.html              # page structure + all modals (auth, submit, profile, work detail)
├── firestore.rules          # THE security boundary for member data — read before deploying
├── firebase.json             # points the Firebase CLI at firestore.rules
├── assets/
│   ├── style.css             # theme, layout, responsive, dark mode
│   ├── script.js              # main app: wires filters/search/modals/auth/wallet together
│   ├── js/
│   │   ├── i18n.js             # Thai/English strings + language toggle
│   │   ├── firebase-config.js  # your Firebase project config (public, not secret)
│   │   ├── firebase-core.js    # shared Firebase App instance
│   │   ├── auth.js             # sign up / sign in / sign out
│   │   ├── db.js               # Firestore reads/writes for works, comments, profiles
│   │   ├── wallet.js           # MetaMask connect + sending ETH tips
│   │   └── render-utils.js     # HTML-escaping and small DOM helpers (XSS prevention)
│   └── data/
│       └── works.js            # demo-mode sample works (ignored once Firebase is live)
└── README.md
```

## Features

- Browse/filter across 12 AI-capability categories, search by title/tool/description
- Thai + English UI, one click to switch
- Member sign-up/sign-in (email+password or Google), once Firebase is configured
- Members can publish their own work and comment on others' — realtime updates
- Optional wallet-connect and creator tipping in ETH
- Dark mode follows system setting; fully responsive down to phone width
- All user-generated text is HTML-escaped before rendering (see `render-utils.js`) — the real access control lives in `firestore.rules`, not in the client code

## Security notes

- Never trust the client-side checks in `db.js` alone — they're for fast UI feedback. `firestore.rules` is what actually stops a malicious client from writing bad data.
- The site never sees or stores a user's private keys or seed phrase. All it does is ask an already-installed wallet extension to sign a transaction the user reviews and approves themselves.
- Re-read `firestore.rules` any time you add a new field members can write, and update the matching validation there — a field the rules don't check is a field an attacker can set to anything.

---

# AI Works Portfolio (ภาษาไทย)

เว็บไซต์แบบ static (HTML/CSS/JS ล้วน ๆ ไม่ต้อง build) สำหรับชุมชนคนทั่วโลกมาแชร์และพูดคุยเรื่องผลงานที่สร้างด้วย AI

ไม่เกี่ยวข้องกับโปรเจกต์ caveman หลักในรีโปนี้ อยู่แยกเป็นโฟลเดอร์ของตัวเอง

## มีอะไรบ้าง

- **ดูผลงาน** — กรอง 12 หมวดหมู่ ค้นหา ดูรายละเอียด — ใช้งานได้ทันทีไม่ต้องตั้งค่าอะไร
- **ระบบสมาชิก** (ต้องตั้งค่าเพิ่ม) — สมัครสมาชิก โพสต์ผลงานของตัวเอง คอมเมนต์ผลงานคนอื่น — ใช้ Firebase (Auth + Firestore) เป็นระบบหลังบ้าน เพราะ GitHub Pages เป็น static hosting รันเซิร์ฟเวอร์เองไม่ได้ แต่เรียก Firebase ตรงจากเบราว์เซอร์ได้
- **เชื่อมต่อ Wallet** (ไม่บังคับ ต้องมี wallet ของตัวเอง) — เชื่อมต่อ wallet แบบ MetaMask เพื่อรับการสนับสนุนเป็น ETH จากสมาชิกคนอื่นบนผลงานที่คุณโพสต์

ถ้ายังไม่ตั้งค่า Firebase เว็บจะอยู่ใน **โหมดสาธิต**: ดูผลงานตัวอย่างได้ปกติ แต่สมัครสมาชิก/โพสต์/คอมเมนต์จะขึ้นข้อความแจ้งว่าต้องตั้งค่าก่อน (ไม่พัง)

## วิธีเปิดดู

เปิด `index.html` ด้วยเบราว์เซอร์ได้เลย หรือรันผ่าน local server:

```bash
cd portfolio-site
python3 -m http.server 8000
```

## เปิดใช้ระบบสมาชิก (ตั้งค่า Firebase)

ทำครั้งเดียวโดยเจ้าของเว็บ ค่าพวกนี้ไม่ใช่ความลับ — Firebase ออกแบบให้ config ฝั่ง client เปิดเผยได้ ความปลอดภัยจริงอยู่ที่ `firestore.rules`

1. เข้า [Firebase console](https://console.firebase.google.com/) สร้างโปรเจกต์ใหม่ (ใช้ free tier ได้)
2. **Build → Authentication → Get started** → เปิดใช้ **Email/Password** และ (ไม่บังคับ) **Google**
3. **Build → Firestore Database → Create database** → เลือก production mode
4. **Project settings → General → Your apps → Add app → Web** → copy ค่า config
5. นำค่าไปแทนที่ placeholder ใน `assets/js/firebase-config.js` แล้ว commit ได้เลย (ไม่ใช่ความลับ)
6. Deploy security rules (ส่วนที่ป้องกันข้อมูลจริง ๆ):
   ```bash
   npm install -g firebase-tools
   firebase login
   firebase use --add
   firebase deploy --only firestore:rules
   ```
7. รีเฟรชเว็บ — banner โหมดสาธิตจะหายไป สมัครสมาชิก/เข้าสู่ระบบใช้งานได้

ถ้ายังไม่ตั้งค่า เว็บก็ยังดูผลงานได้ปกติ แค่สมัครสมาชิกไม่ได้เท่านั้น

## เชื่อมต่อ Wallet / การสนับสนุน (เกี่ยวข้องกับเงินจริง)

สมาชิกใส่ที่อยู่ wallet ในโปรไฟล์ได้ (**โปรไฟล์ของฉัน → เชื่อมต่อ Wallet** ต้องมี MetaMask หรือ wallet ที่รองรับ) พอตั้งแล้ว สมาชิกคนอื่นจะเห็นกล่อง "สนับสนุนผู้สร้าง" บนผลงานนั้นและส่ง ETH ให้ตรงจาก wallet ถึง wallet ได้เลย เว็บนี้ไม่แตะเงินหรือ private key ของใครทั้งสิ้น

**ก่อนเปิดให้ใช้จริง:**
- ทดสอบบน testnet (เช่น Sepolia) ด้วยเงินทดสอบก่อนเสมอ
- โค้ดธุรกรรมอยู่ที่ `assets/js/wallet.js` แต่หน้าจอยืนยันของ wallet extension เองคือด่านความปลอดภัยจริง ตรวจที่อยู่ผู้รับที่นั่นทุกครั้ง
- นี่คือโค้ดที่เขียนขึ้นใหม่ ไม่ใช่ระบบชำระเงินที่ผ่านการตรวจสอบความปลอดภัยระดับองค์กร ใช้เป็นฟีเจอร์ทิปเล็ก ๆ ระหว่างสมาชิกที่ยินยอมกันเอง ไม่ใช่ marketplace หรือบริการการเงิน

## วิธีเพิ่ม/แก้ไขผลงานตัวอย่าง (โหมดสาธิต)

แก้ไฟล์ [`assets/data/works.js`](./assets/data/works.js) — ใช้เฉพาะตอนโหมดสาธิตเท่านั้น พอเปิด Firebase แล้วผลงานจริงจาก Firestore จะมาแทนอัตโนมัติ ไฟล์นี้จะถูกมองข้าม

| ฟิลด์ | คำอธิบาย |
|---|---|
| `id` | เลขไม่ซ้ำกัน |
| `title` | ชื่อผลงาน |
| `category` | หนึ่งใน `writing`, `code`, `image`, `video`, `audio`, `agent`, `data`, `research`, `business`, `science`, `design`, `education` |
| `tool` | ชื่อเครื่องมือ AI ที่ใช้ |
| `description` | คำอธิบายสั้น ๆ |
| `date` | รูปแบบ `YYYY-MM-DD` |
| `link` | ลิงก์ไปดูผลงานฉบับเต็ม |
| `thumbnail` | อีโมจิ |

## โครงสร้างไฟล์

ดูหัวข้อ "File structure" ด้านบน (ภาษาอังกฤษ) — โครงสร้างเดียวกัน

## ฟีเจอร์

- กรอง/ค้นหาผลงาน 12 หมวดหมู่
- สลับภาษาไทย/อังกฤษได้
- สมัครสมาชิก (อีเมล หรือ Google) เมื่อตั้งค่า Firebase แล้ว
- สมาชิกโพสต์ผลงานและคอมเมนต์กันได้แบบเรียลไทม์
- เชื่อมต่อ wallet และส่งทิปเป็น ETH (ไม่บังคับ)
- รองรับ dark mode และมือถือ
- ข้อความจากผู้ใช้ทุกจุดผ่านการ escape HTML ก่อน render (ป้องกัน XSS) — แต่การควบคุมสิทธิ์จริงอยู่ที่ `firestore.rules`

## ข้อควรระวังด้านความปลอดภัย

- อย่าเชื่อการตรวจสอบฝั่ง client ใน `db.js` เพียงอย่างเดียว มันมีไว้เพื่อ UX เท่านั้น `firestore.rules` คือสิ่งที่ป้องกัน client ที่ประสงค์ร้ายจริง ๆ
- เว็บนี้ไม่เห็นและไม่เก็บ private key หรือ seed phrase ของใครเลย ทำได้แค่ขอให้ wallet extension ที่ติดตั้งอยู่แล้วเซ็นธุรกรรมที่ผู้ใช้ตรวจสอบและกดยืนยันเอง
- ทุกครั้งที่เพิ่มฟิลด์ใหม่ที่สมาชิกเขียนได้ ต้องกลับไปอัปเดต `firestore.rules` ให้ตรวจสอบฟิลด์นั้นด้วย — ฟิลด์ที่ rules ไม่เช็ค คือช่องโหว่ที่ผู้ไม่หวังดีตั้งค่าอะไรก็ได้
