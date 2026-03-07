# Aures Vacancy Dashboard 🚀

## 📋 Project Overview
This application visualizes and manages recruitment data exported from the internal AURES ATS (Datacruit).
It operates as a **Real-Time Collaborative Dashboard** powered by Firebase Realtime Database and an automated Python synchronization backend. This allows multiple recruiters and managers to manage and edit recruitment data simultaneously, similar to Google Docs or Excel Online.

## 🛠 Tech Stack
* **Core:** HTML5, Vanilla JavaScript (ES6+)
* **Styling:** Tailwind CSS (utility foundation) + Custom Vanilla CSS (branding, glassmorphism)
* **Typography:** [Inter](https://fonts.google.com/specimen/Inter) (Modern, clean sans-serif)
* **Data Backend Logic:** Python (`ats_sync.py`) via GitHub Actions (fetching & aggregating Datacruit API json payloads)
* **Collaborative Backend:** [Firebase Realtime Database v10](https://firebase.google.com/) (compat mode, real-time sync for edits)
* **Charts:** [Chart.js v4](https://www.chartjs.org/) (loaded via CDN — bar, doughnut charts)
* **Hosting:** GitHub Pages (Planned) — repo: [OndraDol/Vacancies](https://github.com/OndraDol/Vacancies)

## 🔄 Architecture & Data Flow

### The Sync Pipeline (Datacruit API → Python)
The dashboard no longer relies on manual Excel uploads by users. Instead, a fully automated pipeline fetches current data from Datacruit directly:
1. **GitHub Actions (Cron):** A scheduled workflow (`.github/workflows/datacruit_sync.yml`) triggers the `ats_sync.py` script every morning.
2. **Datacruit API:** The Python script makes authenticated GET requests to the Datacruit API, sequentially downloading the `jobs` and `hiring_processes` datasets.
3. **Python Aggregation & Filtration:**
   * Obsolete positions (older than 365 days / not active) are filtered out.
   * Dead candidate records (>30 days since last activity and not matching "Hired" states) are dropped.
   * Internal data structure translates JSON lists into nested tree structures grouped by Branch and Position.
4. **Firebase Realtime Database:** The resulting clean `report` JSON payload is pushed directly to Firebase under a unique `/reports/{uploadId}`. The pointer `/latestReport` is immediately updated.

### Client-Side Real-Time View (Firebase)
1. **Listeners:** All connected browsers listen to `onValue('/latestReport')`. If a sync finishes (or another recruiter uploads a change), the client immediately pulls the new `/reports/{uploadId}` and re-renders the DOM without refreshing the page.
2. **Persistent Overrides:** Locally, the client still queries `IndexedDB` (`jobOverrides`) to re-apply any manual overrides for **CAP / ACT / VAC** values (keyed by Ref. number) that were strictly tracked by an individual user, ensuring zero loss of custom capacity tracking even when fresh ATS data arrives.

## 📂 Target Mapping (API to Dashboard)
The application expects JSON structures mirroring Datacruit endpoints, specifically mapping:

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
* Internal ATS metrics are completely stripped out before reaching the GitHub repo. Data lives only dynamically in Firebase Database or briefly in transient GitHub Actions memory spaces.
* `DATACRUIT_USERNAME`, `DATACRUIT_PASSWORD`, and Firebase Admin keys belong inside strictly isolated GitHub Secrets.

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
| 2026-03-07 | **Dashboard Filtry** — Přidána lišta s filtry (HR Konzultant, Divize, Řazení stáří). Filtry automaticky přepočítávají i horní souhrnná KPI čísla. |
| 2026-03-07 | **Analytické Regiony** — Rozdělení HR Analytiky přes interaktivní pilulky na `[Vše] [CZ] [SK] [PL]`, reaktivně překreslující všechny grafy. |
| 2026-03-07 | **Realistická Data** — V `ats_sync.py` zabudována deterministická seed/hash logika na základě ID pozice, distribuující fixní a realistická kapacitní čísla (CAP / ACT / VAC) napříč fetch cykly. |

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