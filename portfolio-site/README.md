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
| `tags` | Optional array of short strings, up to 5, e.g. `["cyberpunk", "sdxl"]` |

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
- Forgot-password flow (email reset link) — doesn't reveal whether an email is registered, to prevent account enumeration
- Members can publish their own work and comment on others' — realtime updates
- Optional tags per work (up to 5), searched alongside title/tool/description — added after looking at how Civitai/OpenArt users complained search and filtering degrade once a community's content grows past a handful of broad categories
- Sort browsing by newest or oldest
- A "🚩 Report" button on every work and every comment files a report for the site owner to review from the Firebase console — added specifically because weak moderation tooling is the single most common complaint about Civitai, the largest platform in this space
- Optional wallet-connect and creator tipping in ETH
- Dark mode follows system setting; fully responsive down to phone width
- All user-generated text is HTML-escaped before rendering (see `render-utils.js`) — the real access control lives in `firestore.rules`, not in the client code
- Buttons that trigger a network request (sign up/in, publish, comment, save profile, send tip, report) disable themselves while pending, so a slow connection or an impatient double-click can't create duplicate posts/comments

## Ideas looked at and deliberately not built yet

- **WalletConnect (mobile wallet support).** Right now wallet-connect only works with a browser extension (MetaMask and friends), which shuts out most mobile visitors — a real gap for a "global community." Adding it properly needs a free project ID from [WalletConnect Cloud](https://cloud.reown.com) (the same kind of one-time setup as Firebase above), so it's scoped as a follow-up rather than half-wired with a placeholder that can't be tested end-to-end here.
- **"Most discussed" sort.** Doing this right means a denormalized comment-count on each work, kept in sync via a Cloud Function trigger on comment create/delete — trying to fake it with a client-side increment plus a security rule is a well-known way to end up with an insecure or racy counter, so it's left out rather than shipped half-safe.

## Security notes

- Never trust the client-side checks in `db.js` alone — they're for fast UI feedback. `firestore.rules` is what actually stops a malicious client from writing bad data. The rules apply the same validation on **update** as on **create** — an early version of this only checked create, which let an owner edit their own work into something invalid after the fact.
- Every field a member can write is validated in `firestore.rules`, including the `link` field on a work: it must be `http(s)://…` or empty. Without that check a work's "view full work" link could be set to a `javascript:` URI and executed in another visitor's browser when clicked (a stored XSS). The client (`script.js` and `db.js`) validates the same thing, but that's convenience, not the boundary.
- The site never sees or stores a user's private keys or seed phrase. All it does is ask an already-installed wallet extension to sign a transaction the user reviews and approves themselves.
- Re-read `firestore.rules` any time you add a new field members can write, and update the matching validation there — a field the rules don't check is a field an attacker can set to anything.
- `firestore.rules` couldn't be executed against a live Firestore emulator in the environment this was built in (network egress is locked down there) — it was reviewed carefully against Firebase's documented rules syntax instead. **Run `firebase emulators:start` once and exercise sign-up/publish/comment/edit-someone-else's-work locally before relying on these rules in production.**

## Known limitations (be aware of these for a public community site)

- **No spam/rate limiting.** Firestore rules can't easily rate-limit writes; a signed-in member could script hundreds of posts or comments. For now, moderation is manual: as the project owner, you can delete any document from the Firebase console (the console uses admin access and bypasses `firestore.rules`).
- **No email verification.** Anyone can sign up with any email address without proving they own it. Fine for a low-stakes community; add Firebase's email verification flow if impersonation becomes a problem.
- **Reports go into a write-only collection.** The in-app "Report" button files a report, but nothing in the app reads reports back — by design, so a member can't see who reported what. The site owner reviews `reports` from the Firebase console and acts manually (delete the offending work/comment, or ban a user via Authentication). There's no in-app admin queue yet.
- These are reasonable gaps for a first version, not oversights to ignore — revisit them before the community grows large enough that abuse becomes likely.

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
| `tags` | array ของคำสั้น ๆ ไม่บังคับ สูงสุด 5 อัน เช่น `["cyberpunk", "sdxl"]` |

## โครงสร้างไฟล์

ดูหัวข้อ "File structure" ด้านบน (ภาษาอังกฤษ) — โครงสร้างเดียวกัน

## ฟีเจอร์

- กรอง/ค้นหาผลงาน 12 หมวดหมู่
- สลับภาษาไทย/อังกฤษได้
- สมัครสมาชิก (อีเมล หรือ Google) เมื่อตั้งค่า Firebase แล้ว
- ลืมรหัสผ่าน? มีระบบส่งลิงก์รีเซ็ตทางอีเมล — ไม่บอกด้วยว่าอีเมลนั้นมีสมาชิกอยู่จริงไหม (กันการสืบว่าใครสมัครไว้บ้าง)
- สมาชิกโพสต์ผลงานและคอมเมนต์กันได้แบบเรียลไทม์
- ใส่แท็กให้ผลงานได้ (สูงสุด 5 แท็ก) ค้นหาได้ทั้งจากชื่อ/เครื่องมือ/คำอธิบาย/แท็ก — เพิ่มมาเพราะไปอ่านรีวิว Civitai/OpenArt แล้วพบว่าปัญหาที่คนบ่นบ่อยสุดคือค้นหา/filter แย่เมื่อผลงานเยอะขึ้น หมวดใหญ่ 12 อันอย่างเดียวไม่พอ
- เรียงลำดับผลงานได้ (ใหม่สุด/เก่าสุด)
- ปุ่ม "🚩 รายงาน" ที่ทุกผลงานและทุกคอมเมนต์ ส่งรายงานให้เจ้าของเว็บไปดูใน Firebase console — เพิ่มมาเพราะการโมเดอเรตอ่อนคือปัญหาที่คนบ่น Civitai (แพลตฟอร์มใหญ่สุดในสายนี้) มากที่สุด
- เชื่อมต่อ wallet และส่งทิปเป็น ETH (ไม่บังคับ)
- รองรับ dark mode และมือถือ
- ข้อความจากผู้ใช้ทุกจุดผ่านการ escape HTML ก่อน render (ป้องกัน XSS) — แต่การควบคุมสิทธิ์จริงอยู่ที่ `firestore.rules`
- ปุ่มที่ยิง request ทุกตัว (สมัคร/เข้าสู่ระบบ/โพสต์/คอมเมนต์/บันทึกโปรไฟล์/ส่งทิป/รายงาน) จะปิดตัวเองระหว่างรอผลลัพธ์ กันไม่ให้กดซ้ำจนโพสต์/คอมเมนต์ซ้ำ

## แนวคิดที่พิจารณาแล้วแต่ยังไม่ทำ

- **WalletConnect (รองรับ wallet มือถือ)** ตอนนี้เชื่อมต่อ wallet ได้แค่ผ่าน browser extension (MetaMask ฯลฯ) ซึ่งปิดกั้นคนใช้มือถือส่วนใหญ่ — เป็นช่องโหว่จริงสำหรับ "ชุมชนทั่วโลก" การทำให้ถูกต้องต้องมี project ID ฟรีจาก [WalletConnect Cloud](https://cloud.reown.com) (ตั้งค่าครั้งเดียวคล้าย Firebase) จึงเก็บไว้เป็นงานต่อยอด แทนที่จะใส่โค้ดครึ่งๆ กลางๆ ที่ทดสอบจบไม่ได้ในเซสชันนี้
- **เรียงตาม "คุยเยอะสุด"** ทำให้ถูกต้องต้องมีตัวนับคอมเมนต์แบบ denormalize ที่ sync ผ่าน Cloud Function ตอนสร้าง/ลบคอมเมนต์ — ถ้าทำแบบลวกๆ ด้วยการ increment ฝั่ง client + security rule เฉยๆ มักจบที่ตัวนับไม่ปลอดภัยหรือมี race condition จึงยังไม่ใส่ฟีเจอร์นี้ดีกว่าใส่แบบไม่ปลอดภัย

## ข้อควรระวังด้านความปลอดภัย

- อย่าเชื่อการตรวจสอบฝั่ง client ใน `db.js` เพียงอย่างเดียว มันมีไว้เพื่อ UX เท่านั้น `firestore.rules` คือสิ่งที่ป้องกัน client ที่ประสงค์ร้ายจริง ๆ และตอนนี้ validate เหมือนกันทั้งตอน create และ update แล้ว (เดิมเช็คแค่ตอน create ทำให้เจ้าของผลงานแก้ข้อมูลตัวเองให้ผิดรูปแบบภายหลังได้)
- ทุกฟิลด์ที่สมาชิกเขียนได้ผ่านการตรวจใน `firestore.rules` รวมถึงฟิลด์ `link` — ต้องเป็น `http(s)://…` หรือว่างเท่านั้น ถ้าไม่เช็ค จะมีคนตั้งเป็น `javascript:...` แล้วฝังโค้ดอันตรายที่รันตอนคนอื่นกดลิงก์ "ดูผลงานฉบับเต็ม" ได้ (stored XSS)
- เว็บนี้ไม่เห็นและไม่เก็บ private key หรือ seed phrase ของใครเลย ทำได้แค่ขอให้ wallet extension ที่ติดตั้งอยู่แล้วเซ็นธุรกรรมที่ผู้ใช้ตรวจสอบและกดยืนยันเอง
- ทุกครั้งที่เพิ่มฟิลด์ใหม่ที่สมาชิกเขียนได้ ต้องกลับไปอัปเดต `firestore.rules` ให้ตรวจสอบฟิลด์นั้นด้วย — ฟิลด์ที่ rules ไม่เช็ค คือช่องโหว่ที่ผู้ไม่หวังดีตั้งค่าอะไรก็ได้
- `firestore.rules` รันทดสอบจริงผ่าน Firestore emulator ในสภาพแวดล้อมที่พัฒนานี้ไม่ได้ (เน็ตออกถูกบล็อก) ตรวจสอบอย่างละเอียดตาม syntax ที่ Firebase เอกสารไว้แทน — **รัน `firebase emulators:start` แล้วลองสมัคร/โพสต์/คอมเมนต์/พยายามแก้ผลงานคนอื่นดูก่อนใช้งานจริง**

## ข้อจำกัดที่ควรรู้ (สำหรับเว็บชุมชนสาธารณะ)

- **ยังไม่มีการจำกัดสแปม** สมาชิกที่ล็อกอินแล้วเขียนสคริปต์โพสต์/คอมเมนต์รัว ๆ ได้ ตอนนี้ต้องจัดการเองผ่าน Firebase console (เจ้าของโปรเจกต์ลบเอกสารไหนก็ได้ เพราะ console ใช้สิทธิ์ admin ข้าม `firestore.rules`)
- **ยังไม่มีการยืนยันอีเมล** ใครก็สมัครด้วยอีเมลไหนก็ได้โดยไม่ต้องพิสูจน์ว่าเป็นเจ้าของจริง
- **รายงานเป็น write-only** ปุ่ม "รายงาน" ในเว็บส่งรายงานได้ แต่ตัวเว็บเองอ่านรายงานกลับไม่ได้เลย (ตั้งใจออกแบบแบบนี้ กันไม่ให้สมาชิกเห็นว่าใครรายงานอะไร) เจ้าของเว็บต้องเข้าไปดูใน Firebase console เอง แล้วจัดการเอง (ลบผลงาน/คอมเมนต์ หรือแบนผู้ใช้ผ่าน Authentication) ยังไม่มีหน้า admin queue ในตัวเว็บ
- ข้อจำกัดพวกนี้คือของที่รู้ตัวว่ายังไม่ทำ ไม่ใช่สิ่งที่มองข้าม ควรกลับมาทำเพิ่มก่อนที่ชุมชนจะโตจนมีความเสี่ยงเรื่องการใช้งานในทางที่ผิด
