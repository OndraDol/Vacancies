# Aures Vacancy Dashboard 🚀

## 📋 Project Overview
This application visualizes and manages recruitment data exported from the ATS (Applicant Tracking System).
It is currently transitioning from a **Single File Application (SFA)** running entirely client-side to a **Real-Time Collaborative Dashboard** powered by Firebase. This will allow multiple recruiters and managers (typically up to 5 concurrent users) to manage and edit recruitment data simultaneously, similar to Google Docs or Excel Online.

## 🛠 Tech Stack
* **Core:** HTML5, Vanilla JavaScript (ES6+)
* **Styling:** Tailwind CSS (utility foundation) + Custom Vanilla CSS (branding, glassmorphism)
* **Typography:** [Inter](https://fonts.google.com/specimen/Inter) (Modern, clean sans-serif)
* **Data Parsing:** [SheetJS (xlsx)](https://sheetjs.com/) (loaded via CDN)
* **Icons:** [Lucide Icons](https://lucide.dev/) (loaded via CDN)
* **Collaborative Backend:** [Firebase Realtime Database v10](https://firebase.google.com/) (compat mode, implementation in progress)
* **Charts:** [Chart.js v4](https://www.chartjs.org/) (loaded via CDN — bar, doughnut charts)
* **Hosting:** GitHub Pages (Planned) — repo: [OndraDol/Vacancies](https://github.com/OndraDol/Vacancies)

## 🔄 Architecture: Current State

### Client-Side + Persistent Overrides (Active)
* **Storage:** Data is stored locally in the browser using `IndexedDB` (two stores):
  * `files` — persists the last uploaded `.xlsx` file so the dashboard auto-loads on next visit
  * `jobOverrides` — persists manually edited **CAP / ACT / VAC** values, keyed by `Ref. number` (e.g. `A123456`). These survive file re-uploads and are merged with fresh ATS data on every render.
* **Flow:** Upload `.xlsx` → SheetJS parses → `jobOverrides` loaded from IndexedDB → rendered to DOM

### Firebase Real-Time (In Progress)
When `FIREBASE_ENABLED = true` (i.e. real config values filled in `FIREBASE_CONFIG`):
1. **Upload** → ATS data is pushed to `/reports/{uploadId}` in Firebase Realtime Database
2. **Pointer** → `/latestReport` node is updated with the new `uploadId`
3. **Listeners** → all connected browsers have `onValue('/latestReport')` active; on change they fetch the new report and re-render the dashboard automatically
4. **Fallback** → if Firebase is not configured, the app silently falls back to IndexedDB

## 📂 Data Structure (ATS Input)
The application expects an Excel `.xlsx` file exported from the ATS.

### Sheet: "Jobs" (Positions)
| Column | Usage |
|---|---|
| `Ref. number` | Primary Key — links to candidates; used as persistent override key (e.g. `A123456`) |
| `Job vacancy` | Position name |
| `Client branch` | Location / branch |
| `Division` & `Department in division` | Organisational hierarchy |
| `Owner` | **HR Consultant** (primary — always one person) |
| `Recruiters` | Fallback if Owner is empty (first name taken if comma-separated list) |
| `Date created` | To calculate "Days Open" |
| `Job status` | Filter: `active` |
| `Headcount` | CAP |
| `Headcount - left to fill` | VAC |

### Sheet: "Hiring processes" (Candidates)
| Column | Usage |
|---|---|
| `Ref. number` | Foreign Key — links to Jobs |
| `Candidate` | Full name |
| `Last status` & `Result` | Current state in ATS (used for category classification) |
| `Start date` | For Hired / Hired in past logic |
| `Last interview` / `Last activity` | For interview date display |

## 🧠 Business Logic & Calculations

### Candidate Classification
| Category | Color | Condition |
|---|---|---|
| **Hired** | 🔴 Red | `result = accepted` OR `status = start date confirmed / waiting for start date` AND future start date |
| **Hired in past** | 🔴 Light red | Same as above, but start date is in the past |
| **For interview** | 🟢 Green | `status = interview / internal interview` AND future interview date |
| **After interview** | 🟢 Dark green | `status = interview / internal interview` AND past interview date |
| **Offer refused** | ⚫ Grey | `result = declined` |
| **No show** | ⚫ Grey | `status = didn't arrive at the interview` |
| **No after interview** | ⚫ Grey strikethrough | `status = not qualified after internal interview / favored a more appropriate candidate` |

### KPIs (Top Cards)
| KPI | Calculation |
|---|---|
| **Celkem Pozic** | Count of active jobs |
| **Volná Místa (VAC)** | Sum of `Headcount - left to fill` |
| **Aktivní Nábory** | Count of candidates with `interview` in status |
| **Úspěšné Nástupy** | Count of Hired candidates |

## 🗺 Branch & Division Ordering
1. **Branches:** Strict custom order — Prague HQ → Reg. Praha → Bohemia 1 → Bohemia 2 → Moravia 1 → Moravia 2. Unknown branches appended alphabetically.
2. **Divisions (HQ):** Call Centre → Marketing → Innovations → Commerce → Economic → IT → Data Science → Cost Control → Office Ops → HR → Stock & Logistics → Service → Financial Services → Car Sales → Car Purchase → Automotive Ops → Mototechna
3. **Divisions (Regional):** Car Sales → Financial Services → Automotive Operations

## 🎨 Design & UI (Aures Branded)
* **Glassmorphism:** Frosted floating header with backdrop blur
* **Brand Palette:** Sky-blue gradients (`#0ea5e9` to `#38bdf8`) with clean slate/white surfaces
* **Micro-interactions:** Morphing blob background, 6° logo rotation on hover, scaling KPI icons, animated left-border accent on row hover
* **Zebra striping:** Subtle alternating row backgrounds for easier horizontal reading
* **Column dividers:** Thin vertical lines between table columns
* **Branch cards:** Rounded with shadow, stronger header border, `font-weight: 800`

## 🔒 Data & Repository Rules
* Excel / CSV files are excluded from git via `.gitignore` — ATS reports are internal data and must never be committed
* Files are uploaded locally by the user at runtime via `<input type="file">`, not from the repo

## ✅ Completed Features

| Date | Feature |
|---|---|
| 2026-03-06 | **CAP / ACT / VAC Persistence** — values survive file re-uploads, stored per `Ref. number` in IndexedDB |
| 2026-03-06 | **Firebase Step 1+2** — SDK added via CDN, config object with placeholders + `FIREBASE_ENABLED` flag |
| 2026-03-06 | **Firebase Step 3** — `crypto.randomUUID()` IDs for every job (`jobId`) and candidate (`id`) |
| 2026-03-06 | **Firebase Step 4** — `pushReportToFirebase()` writes full report to `/reports/{uploadId}` + `/latestReport` pointer |
| 2026-03-06 | **Firebase Step 5** — `startFirebaseListener()` with `onValue()` on `/latestReport`; auto-rerenders all clients on new upload; falls back to IndexedDB offline |
| 2026-03-06 | **HR Consultant logic** — uses `Owner` field (one person); fallback to first name from `Recruiters` |
| 2026-03-06 | **Visual separation** — stronger row borders, zebra striping, column dividers, larger branch card margins + shadow, animated left-border row accent on hover |
| 2026-03-06 | **📊 HR Analytics page** — toggled via header button, includes: 10 summary KPIs, VAC by Branch chart, VAC by Division chart, Pipeline doughnut, Age distribution bar chart, Recruiter workload table, Branch comparison table, Top 10 longest open positions |
| 2026-03-06 | **Firebase Step 6** — Inline edits push to Firebase directly (`db.ref(...).update/remove/set`); added list sorting by order property. |
| 2026-03-06 | **Firebase Zabezpečení (Authentication)** — Passwordless Sign-in (přidání ochrany přístupu pouze pro e-maily domény `@aaaauto.cz` a `@auresholdings.eu`). |
| 2026-03-07 | **Datacruit API Sync** — Automatické denní (cron) stahování, filtrování a synchronizace 600MB+ dat z ATS přímo do Firebase přes GitHub Actions (`ats_sync.py`). Zahození mrtvých pozic (>365d) a kandidátů (>30d bez aktivity). |

## ✅ Firebase Zabezpečení & Synchronizace (Kompletně nasazeno v produkci)

- [x] **Step 1:** Add Firebase SDKs (`app`, `database`) to `index.html` via CDN
- [x] **Step 2:** Add Firebase configuration object with placeholders + `FIREBASE_ENABLED` flag
- [x] **Step 3:** Unique IDs (`crypto.randomUUID()`) for every job and candidate
- [x] **Step 4:** Firebase write logic — `pushReportToFirebase()` on every upload
- [x] **Step 5:** Firebase read logic — `onValue()` listener + auto re-render for all clients
- [x] **Step 6:** Rewrite inline UI controls to push targeted Firebase updates:
  * ContentEditable (Recruiter, CAP, ACT, VAC) → `db.ref(...).update()`
  * Candidate chip rename / delete → `update()` / `remove()`
  * Add candidate / add phase → `db.ref(...).push()`
  * Delete job / move job → update order in Firebase
- [x] **Step 7:** Fill in real `FIREBASE_CONFIG` values from Firebase Console
- [x] **Step 8:** Zabezpečení databáze aplikováním ověření "Passwordless Sign-in" a nasazení na GitHub Pages. (COMPLETED)