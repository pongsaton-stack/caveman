// Demo/fallback data shown when no Firebase backend is configured (see
// README "Turning on membership"). Once Firebase is connected, real
// member-submitted works from Firestore replace this list automatically.
//
// Three examples per category so filtering/sorting/search all have
// something real to browse in demo mode.
//
// Valid categories:
// writing, code, image, video, audio, agent, data, research, business, science, design, education
export const AI_WORKS = [
  // ---- writing ----
  {
    id: 1,
    title: "Weekly Newsletter Draft",
    category: "writing",
    tool: "Claude",
    description: "First-pass draft for the product newsletter, edited and shipped.",
    date: "2026-08-10",
    link: "",
    thumbnail: "📝"
  },
  {
    id: 2,
    title: "Blog Post Outline",
    category: "writing",
    tool: "Claude",
    description: "Structured outline and intro paragraph for a technical blog post series.",
    date: "2026-07-14",
    link: "",
    thumbnail: "🗒️",
    tags: ["blogging", "outline"]
  },
  {
    id: 3,
    title: "Product Documentation Rewrite",
    category: "writing",
    tool: "ChatGPT",
    description: "Simplified a dense API reference page into plain-language docs for new users.",
    date: "2026-09-05",
    link: "",
    thumbnail: "📚"
  },

  // ---- code ----
  {
    id: 4,
    title: "Expense Tracker App",
    category: "code",
    tool: "GitHub Copilot",
    description: "Small React app for tracking personal expenses, scaffolded and refined.",
    date: "2026-08-15",
    link: "",
    thumbnail: "💻"
  },
  {
    id: 5,
    title: "CLI Tool for Log Parsing",
    category: "code",
    tool: "Claude Code",
    description: "Command-line utility that filters and summarizes noisy server logs.",
    date: "2026-07-22",
    link: "",
    thumbnail: "⌨️",
    tags: ["cli", "devtools"]
  },
  {
    id: 6,
    title: "API Rate Limiter Middleware",
    category: "code",
    tool: "Cursor",
    description: "Drop-in Express middleware implementing a token-bucket rate limiter.",
    date: "2026-09-02",
    link: "",
    thumbnail: "🧰"
  },

  // ---- image ----
  {
    id: 7,
    title: "Neon City Skyline",
    category: "image",
    tool: "Midjourney",
    description: "Cyberpunk cityscape at dusk, generated for a game concept board.",
    date: "2026-08-02",
    link: "",
    thumbnail: "🌆",
    tags: ["cyberpunk", "concept-art"]
  },
  {
    id: 8,
    title: "Portrait Study Series",
    category: "image",
    tool: "Stable Diffusion",
    description: "Set of five stylized portrait studies exploring lighting.",
    date: "2026-09-01",
    link: "",
    thumbnail: "🖼️",
    tags: ["portrait", "lighting-study", "sdxl"]
  },
  {
    id: 9,
    title: "Logo Concept Set",
    category: "image",
    tool: "DALL-E 3",
    description: "Ten logo directions explored for an early-stage startup rebrand.",
    date: "2026-07-30",
    link: "",
    thumbnail: "🎯",
    tags: ["branding", "logo"]
  },

  // ---- video ----
  {
    id: 10,
    title: "Product Launch Teaser",
    category: "video",
    tool: "Runway",
    description: "15-second teaser clip for a product launch announcement.",
    date: "2026-08-20",
    link: "",
    thumbnail: "🎬"
  },
  {
    id: 11,
    title: "Explainer Animation",
    category: "video",
    tool: "Sora",
    description: "60-second animated explainer walking through a new app feature.",
    date: "2026-09-07",
    link: "",
    thumbnail: "🎞️"
  },
  {
    id: 12,
    title: "Social Media Short Cuts",
    category: "video",
    tool: "Runway Gen-3",
    description: "Vertical-format highlight cuts from a longer conference talk.",
    date: "2026-07-18",
    link: "",
    thumbnail: "📱"
  },

  // ---- audio ----
  {
    id: 13,
    title: "Lo-fi Study Beat",
    category: "audio",
    tool: "Suno",
    description: "Instrumental lo-fi track made for a study playlist.",
    date: "2026-08-25",
    link: "",
    thumbnail: "🎵"
  },
  {
    id: 14,
    title: "Travel Vlog Voiceover",
    category: "audio",
    tool: "ElevenLabs",
    description: "AI-generated voiceover narration for a travel vlog edit.",
    date: "2026-09-08",
    link: "",
    thumbnail: "🎙️"
  },
  {
    id: 15,
    title: "Podcast Intro Jingle",
    category: "audio",
    tool: "Suno",
    description: "10-second branded jingle used as the podcast's intro and outro.",
    date: "2026-07-25",
    link: "",
    thumbnail: "🎶"
  },

  // ---- agent ----
  {
    id: 16,
    title: "Weekly Report Automation",
    category: "agent",
    tool: "Claude Agent",
    description: "Autonomous agent that pulls data from three tools and drafts the weekly status report.",
    date: "2026-09-10",
    link: "",
    thumbnail: "🤖"
  },
  {
    id: 17,
    title: "Customer Support Triage Bot",
    category: "agent",
    tool: "Claude Agent",
    description: "Reads incoming tickets, tags urgency, and routes them to the right queue.",
    date: "2026-08-12",
    link: "",
    thumbnail: "🎫"
  },
  {
    id: 18,
    title: "Inbox Cleanup Agent",
    category: "agent",
    tool: "ChatGPT Agent",
    description: "Archives newsletters, flags action items, and drafts replies to routine emails.",
    date: "2026-07-28",
    link: "",
    thumbnail: "📥"
  },

  // ---- data ----
  {
    id: 19,
    title: "Churn Prediction Dashboard",
    category: "data",
    tool: "ChatGPT + Python",
    description: "Forecasting model and dashboard flagging customers likely to churn next quarter.",
    date: "2026-09-03",
    link: "",
    thumbnail: "📊"
  },
  {
    id: 20,
    title: "Sales Forecast Model",
    category: "data",
    tool: "Claude + Python",
    description: "Quarterly sales forecast built from three years of historical order data.",
    date: "2026-08-05",
    link: "",
    thumbnail: "📈"
  },
  {
    id: 21,
    title: "Anomaly Detection Pipeline",
    category: "data",
    tool: "Claude Code",
    description: "Flags unusual spikes in server error rates before they become outages.",
    date: "2026-07-16",
    link: "",
    thumbnail: "🚨"
  },

  // ---- research ----
  {
    id: 22,
    title: "Market Landscape Brief",
    category: "research",
    tool: "Perplexity",
    description: "Deep-research summary comparing five competitors, sourced and fact-checked.",
    date: "2026-08-28",
    link: "",
    thumbnail: "🔍"
  },
  {
    id: 23,
    title: "Literature Review Summary",
    category: "research",
    tool: "Perplexity",
    description: "Summarized 20 papers on a niche topic into a one-page briefing.",
    date: "2026-07-10",
    link: "",
    thumbnail: "📖"
  },
  {
    id: 24,
    title: "Competitor Pricing Analysis",
    category: "research",
    tool: "ChatGPT",
    description: "Side-by-side pricing and feature comparison across six competing products.",
    date: "2026-09-04",
    link: "",
    thumbnail: "💹"
  },

  // ---- business ----
  {
    id: 25,
    title: "Contract Review Assistant",
    category: "business",
    tool: "Claude",
    description: "Flags risky clauses and summarizes vendor contracts before legal sign-off.",
    date: "2026-08-30",
    link: "",
    thumbnail: "💼"
  },
  {
    id: 26,
    title: "Vendor RFP Response Draft",
    category: "business",
    tool: "Claude",
    description: "First draft of a request-for-proposal response, tailored to the client's brief.",
    date: "2026-07-21",
    link: "",
    thumbnail: "📄"
  },
  {
    id: 27,
    title: "Meeting Notes to Action Items",
    category: "business",
    tool: "ChatGPT",
    description: "Turns raw meeting transcripts into a clean list of owners and deadlines.",
    date: "2026-09-06",
    link: "",
    thumbnail: "✅"
  },

  // ---- science ----
  {
    id: 28,
    title: "Protein Folding Snapshot",
    category: "science",
    tool: "AlphaFold",
    description: "Predicted 3D structure used as a starting point for a lab research question.",
    date: "2026-07-20",
    link: "",
    thumbnail: "🧬"
  },
  {
    id: 29,
    title: "Climate Model Summary",
    category: "science",
    tool: "Claude",
    description: "Plain-language summary of a regional climate model's key projections.",
    date: "2026-08-08",
    link: "",
    thumbnail: "🌡️"
  },
  {
    id: 30,
    title: "Genomic Variant Report",
    category: "science",
    tool: "AlphaMissense",
    description: "Pathogenicity predictions for a shortlist of genomic variants of interest.",
    date: "2026-09-11",
    link: "",
    thumbnail: "🔬"
  },

  // ---- design ----
  {
    id: 31,
    title: "Game Level Concept Kit",
    category: "design",
    tool: "Meshy",
    description: "3D asset pack and level layout sketches generated for an indie game prototype.",
    date: "2026-09-06",
    link: "",
    thumbnail: "🎨"
  },
  {
    id: 32,
    title: "Brand Style Guide Mockup",
    category: "design",
    tool: "Midjourney + Figma",
    description: "Moodboard and mockup pages for a new brand's style guide.",
    date: "2026-07-27",
    link: "",
    thumbnail: "🖌️",
    tags: ["branding"]
  },
  {
    id: 33,
    title: "3D Character Sculpt",
    category: "design",
    tool: "Meshy",
    description: "Base mesh and texture pass for a stylized game character.",
    date: "2026-08-18",
    link: "",
    thumbnail: "🧱",
    tags: ["3d", "game-art"]
  },

  // ---- education ----
  {
    id: 34,
    title: "Personalized Quiz Generator",
    category: "education",
    tool: "Claude",
    description: "Generates practice quizzes adapted to a student's weak topics from past results.",
    date: "2026-09-09",
    link: "",
    thumbnail: "🎓"
  },
  {
    id: 35,
    title: "Lesson Plan Generator",
    category: "education",
    tool: "Claude",
    description: "Draft lesson plan with objectives, activities, and a short assessment.",
    date: "2026-07-12",
    link: "",
    thumbnail: "🏫"
  },
  {
    id: 36,
    title: "Flashcard Deck Creator",
    category: "education",
    tool: "ChatGPT",
    description: "Turned a chapter of course notes into a 40-card spaced-repetition deck.",
    date: "2026-08-22",
    link: "",
    thumbnail: "🗂️"
  }
];
