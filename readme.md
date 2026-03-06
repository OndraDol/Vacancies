# Aures Vacancy Dashboard 🚀

## 📋 Project Overview
This is a **Single File Application (SFA)** designed to visualize recruitment data exported from the ATS (Applicant Tracking System).
The application runs entirely in the browser (client-side) using vanilla JavaScript. It parses an Excel/CSV file, processes the data using specific business logic, and renders an interactive dashboard.

## 🛠 Tech Stack
* **Core:** HTML5, Vanilla JavaScript (ES6+)
* **Styling:** [Tailwind CSS](https://tailwindcss.com/) (loaded via CDN)
* **Data Parsing:** [SheetJS (xlsx)](https://sheetjs.com/) (loaded via CDN)
* **Icons:** [Lucide Icons](https://lucide.dev/) (loaded via CDN)
* **Environment:** No build step required. Works directly in the browser.

## 📂 Data Structure (Input)
The application expects an Excel file (`.xlsx`) containing at least two sheets.

### 1. Sheet: "Jobs" (Positions)
Key columns used for mapping:
* `Ref. number` (Primary Key - links to Candidates)
* `Job vacancy` (Position Name)
* `Client branch` or `Branch` (Location, e.g., "Ostrava", "Brno")
* `Division` (e.g., "Car Sales", "Call Centre")
* `Department in division`
* `Owner` (Hiring Manager)
* `Recruiters` (Generalist)
* `Date created` (Used to calculate "Days Open")
* `Job status` (Filter: only 'active' or where vacancies exist)
* `Headcount` (CAP)
* `Headcount - left to fill` (VAC)

### 2. Sheet: "Hiring processes" (Candidates)
Key columns used for status tracking:
* `Ref. number` (Foreign Key - links to Jobs)
* `Candidate` (Full Name)
* `Last status` (Current state in ATS)
* `Result` (Accepted/Not accepted)
* `Start date` (Hired date)
* `Last interview` or `Last activity` (Date of interaction)

## 🧠 Business Logic & Calculations

### KPIs
* **Time to fill:** Calculated as `Current Date - Date created`.
* **CAP / VAC / ACTUAL:**
    * `CAP` = Headcount column.
    * `VAC` = Headcount - left to fill.
    * `ACTUAL` = CAP - VAC.

### Candidate Classification (Badges)
Candidates are grouped into categories based on `Last status` and `Result`:
1.  **HIRED:** `Result == 'accepted'` OR status contains 'hired', 'start date confirmed'.
    * *Display:* Green Badge + Start Date.
2.  **OFFER:** Status contains 'offer'.
    * *Display:* Purple Badge.
3.  **HIRING (Interviews):** Status contains 'interview' or 'presentation'.
    * *Display:* Blue Badge + Interview Date.
4.  **REFUSED:** Result is 'not accepted' AND status indicates an interview took place.
    * *Display:* Red Badge (Strikethrough).

## 🎨 UI/UX Features
* **Drag & Drop:** Visual zone for file upload.
* **Grouping:** Jobs are grouped by `Client branch` (Location).
* **Sorting:** Within branches, jobs are sorted by `Division`.
* **Visual Feedback:** Red text for positions open > 60 days.

## 🚀 How to Run
1.  Simply open `index.html` in any modern web browser.
2.  Drag and drop the ATS export file (`report-xx-xx-xxxx.xlsx`).

## 📝 Future Improvements (TODO)
* Add export functionality to download the processed table as a formatted Excel file.
* Add filtering by specific Division or Recruiter.
* Visualize "Time to Fill" trends in a chart.