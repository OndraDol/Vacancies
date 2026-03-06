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
* **Collaborative Backend:** [Firebase Realtime Database](https://firebase.google.com/) (Implementation in progress)
* **Hosting:** GitHub Pages (Planned)

## 🔄 Architecture Evolution: Real-Time Collaboration

### Current State (Client-Side + Persistent Overrides)
* **Storage:** Data is stored locally in the browser using `IndexedDB`.
  * `files` store — persists the last uploaded `.xlsx` file so the dashboard auto-loads on next visit.
  * `jobOverrides` store — persists manually edited **CAP / ACT / VAC** values keyed by `Ref. number` (e.g. `A123456`). These survive file re-uploads and are merged with fresh ATS data on every render.
* **Flow:** User uploads an Excel file → Parsed by SheetJS → Overrides loaded from IndexedDB → Rendered to DOM.
* **Limitation:** Manual edits only exist in the current user's browser session. Edits are not shared with colleagues.

### Target State (Firebase Real-Time)
To achieve simultaneous collaboration, the architecture is shifting:
1. **Source of Truth:** Firebase Realtime Database replaces local IndexedDB as the master data source.
2. **Initial Upload:** When a user uploads an ATS report, the parsed JSON data is assigned unique IDs (UUIDs) and pushed to Firebase.
3. **Real-Time Sync:** The browser establishes a WebSocket connection to Firebase (`onValue` listeners). Any data changes are instantly pushed to all connected clients.
4. **Data-Driven Actions:** Inline editing actions (moving rows, adding phases, editing names) will be rewritten to push targeted updates to Firebase paths (e.g., `update(/jobs/{jobId}/candidates/{candidateId})`) rather than mutating the HTML DOM directly. Firebase then triggers a UI re-render for everyone.

## 📂 Data Structure (ATS Input)
The application expects an Excel file (`.xlsx`) exported from the ATS.

### 1. Sheet: "Jobs" (Positions)
* `Ref. number` (Primary Key — links to Candidates, also used as persistent override key)
* `Job vacancy` (Position Name)
* `Client branch` (Location)
* `Division` & `Department in division`
* `Recruiters` (HR Consultant)
* `Date created` (To calculate "Days Open")
* `Job status` (Filter: `active`)
* `Headcount` (CAP) & `Headcount - left to fill` (VAC)

### 2. Sheet: "Hiring processes" (Candidates)
* `Ref. number` (Foreign Key)
* `Candidate` (Full Name)
* `Last status` & `Result` (Current state in ATS)
* `Start date` & `Last interview` / `Last activity`

## 🧠 Business Logic & Calculations

### Candidate Classification
Candidates are placed into categories based on `Last status` and `Result`:
* **Hired** (🔴 Red): Accepted or Start date confirmed (future date).
* **Hired in past** (🔴 Light red): Start date is in the past.
* **For interview** (🟢 Green): Interview scheduled in the future.
* **After interview** (🟢 Dark green): Interview date in the past.
* **Offer refused** (⚫ Grey): Result = declined.
* **No show** (⚫ Grey): Didn't arrive at the interview.
* **No after interview** (⚫ Grey strikethrough): Rejected after interview.

### KPIs (Premium Cards)
* **Celkem Pozic:** Count of active jobs.
* **Volná Místa (VAC):** Sum of `Headcount - left to fill`.
* **Aktivní Nábory:** Count of candidates in 'interview' status.
* **Úspěšné Nástupy:** Count of Hired candidates.

## 🗺 Branch & Division Ordering
1. **Branches:** Rendered in a strict custom order matching internal planning logic (Prague HQ, Regions, etc.).
2. **Divisions:** 
   * HQ Branches use a strategic order (Call Centre → Marketing → ... → Mototechna).
   * Regional Branches use a simplified order (Car Sales → Financial Services → Automotive Operations).

## 🎨 Design & UI (Aures Branded)
* **Glassmorphism:** Frosted floating headers and translucent borders.
* **Brand Palette:** Sky-blue gradients (`#0ea5e9` to `#38bdf8`) with clean slate/white surfaces.
* **Micro-interactions:** Morphing blob background, 6-degree logo rotation on hover, scaling KPI icons.

## ✅ Completed Features
- [x] **CAP/ACT/VAC Persistence** — Values edited in the dashboard are stored in IndexedDB under the job's `Ref. number`. They survive file re-uploads and browser restarts. (2026-03-06)

## 📝 Firebase Implementation Tasks
- [x] **Step 1:** Add Firebase SDKs (`app`, `database`) to `index.html` via CDN.
- [x] **Step 2:** Add Firebase configuration object with placeholders (`YOUR_API_KEY`, etc.).
- [x] **Step 3:** Refactor data parser to generate unique IDs (`crypto.randomUUID()`) for every branch, job, and candidate to allow precise targeted updates. (2026-03-06)
- [x] **Step 4:** Implement Firebase write logic (`set()`) for the initial Excel upload — writes full report to `/reports/{uploadId}` and updates `/latestReport` pointer. (2026-03-06)
- [x] **Step 5:** Implement Firebase read logic (`onValue()`) to listen for real-time changes on `/latestReport` and trigger `renderDashboard()` for all connected clients. Falls back to IndexedDB if `FIREBASE_ENABLED = false`. (2026-03-06)
- [ ] **Step 6:** Rewrite all manual UI controls:
  * ContentEditable (Recruiter, CAP, ACT, VAC) → triggers Firebase `update()`
  * Candidate chip rename / delete → triggers Firebase `update() / remove()`
  * Add candidate / add phase → pushes new object to Firebase
  * Delete job / move job → updates Firebase list order
- [ ] **Step 7:** Deploy updated single-file app to GitHub Pages.