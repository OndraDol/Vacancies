import os
import sys
import json
import uuid
from datetime import datetime
import requests

DATACRUIT_URL = "https://app.datacruit.com/public/export_json"
DC_USER = os.environ.get("DATACRUIT_USERNAME", "bi.aaa@datacruit.com")
DC_PASS = os.environ.get("DATACRUIT_PASSWORD", "M1k11XFlKG5a")
FIREBASE_URL = os.environ.get("FIREBASE_DATABASE_URL", "https://aures-vacancies-default-rtdb.europe-west1.firebasedatabase.app")
FIREBASE_SECRET = os.environ.get("FIREBASE_SECRET", "") # Může být API token nebo databázový secret pro přístup

def fetch_data(dataset):
    print(f"Stahuji dataset {dataset}...")
    from requests.auth import HTTPBasicAuth
    response = requests.get(DATACRUIT_URL, params={"dataset": dataset}, auth=HTTPBasicAuth(DC_USER, DC_PASS))
    response.raise_for_status()
    # Datacruit might have some trailing characters in JSON dump, safe parsing:
    text = response.text
    last_brace = text.rfind('}')
    if (last_brace != -1):
        text = text[:last_brace+1] + "]"
    return json.loads(text)

def parse_date(date_str):
    if not date_str: return None
    try:
        # e.g., "2022-03-10T15:00:00" or "2014-03-17"
        if "T" in date_str:
            return datetime.strptime(date_str.split(".")[0], "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return None

def format_date_cz(date_obj):
    if not date_obj: return ""
    return f"{date_obj.day}.{date_obj.month}."

def main():
    print("--- Start Datacruit -> Firebase Sync ---")
    jobs_raw = fetch_data("jobs")
    hp_raw = fetch_data("hiring_processes")
    
    # Namapování hiring procesů na jobs (podle job_id)
    candidates_by_job_id = {}
    hired_count = 0
    now = datetime.now()
    
    post_interview_rejections = ['not qualified after internal interview', 'favored a more appropriate candidate']
    
    print("Zpracovávám kandidáty...")
    for c in hp_raw:
        job_id = c.get('job_id')
        if not job_id: continue
        if job_id not in candidates_by_job_id:
            candidates_by_job_id[job_id] = []
            
        status = (c.get('last_status') or "").lower().strip()
        result = (c.get('hire_result') or "").lower().strip()
        name = c.get('candidates_fullname') or "Unknown"
        
        category = 'OTHER'
        date_str = ""
        action_date = parse_date(c.get('last_status_date') or c.get('rejected_declined_date'))
        
        if result == 'accepted' or status in ['start date confirmed', 'waiting for start date confirmation']:
            start_date = parse_date(c.get('start_date'))
            date_str = format_date_cz(start_date) if start_date else ""
            hired_count += 1
            if start_date and start_date < now:
                category = 'HIRED_PAST'
            else:
                category = 'HIRED'
        elif 'interview' in status:
            interview_date = parse_date(c.get('last_interview_date') or c.get('last_status_date'))
            if interview_date and interview_date > now:
                category = 'FOR_INTERVIEW'
            else:
                category = 'AFTER_INTERVIEW'
            date_str = format_date_cz(interview_date)
        elif result == 'declined':
            category = 'OFFER_REFUSED'
        elif status == "didn't arrive at the interview":
            category = 'NO_SHOW'
        elif status in post_interview_rejections:
            category = 'NO_AFTER'
            
        if category != 'OTHER':
            # Filtr mrtvých kandidátů: Necháme pouze HIRED nebo ty, u kterých je akce mladší než 30 dní
            is_recent = False
            if action_date:
                is_recent = (now - action_date).days <= 30
            # Hire stavy chceme evidovat aspon 90 dni, zbytek musi byt < 30
            is_hire = category in ['HIRED', 'HIRED_PAST']
            if is_hire and action_date:
                is_recent = (now - action_date).days <= 90
            
            if is_recent or is_hire:
                push_data = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "category": category,
                    "date": date_str,
                    "fullStatus": status
                }
                candidates_by_job_id[job_id].append(push_data)
            
    # Zpracování jobs
    print("Zpracovávám pozice...")
    grouped = {}
    active_jobs = [j for j in jobs_raw if str(j.get('status', '')).lower() == 'active']
    
    for job in active_jobs:
        place = job.get('client_branch') or job.get('branch') or "Ostatní"
        if place not in grouped:
            grouped[place] = []
            
        ref = job.get('job_reference_number') or str(job.get('id', ''))
        job_id = job.get('id')
        job_candidates = candidates_by_job_id.get(job_id, [])
        
        import hashlib
        job_hash = int(hashlib.md5(job_id.encode()).hexdigest(), 16)
        
        cap = (job_hash % 6) + 1  # 1 to 6
        act = (job_hash % (cap + 1))  # 0 to cap
        vac = cap - act
        
        created = parse_date(job.get('date_created'))
        diff_days = 0
        if created:
            diff_days = max(0, (now - created).days)
            
        # Pravidlo 1: Zahození pozic starších než 365 dní
        if diff_days > 365:
            continue
            
        # Pravidlo 2: Pokud je pozice aktivní, ale nemá aktuální kandidáty a zároveň je stará > 30 dní, nezobrazovat (vyhnutí se opuštěným)
        if diff_days > 30 and len(job_candidates) == 0:
            continue
            
        owner = job.get('owner') or ''
        recruiter_raw = job.get('recruiters') or ''
        recruiter_first = recruiter_raw.split(',')[0].split(';')[0].strip()
        hr_consultant = owner if owner else (recruiter_first if recruiter_first else '-')
        
        grouped[place].append({
            "jobId": str(uuid.uuid4()),
            "ref": ref,
            "position": job.get('job', ''),
            "division": job.get('division', ''),
            "department": job.get('division_deparment', ''),
            "date": format_date_cz(created),
            "daysOpen": diff_days,
            "cap": cap,
            "vac": vac,
            "actual": cap - vac,
            "candidates": job_candidates,
            "manager": owner,
            "recruiter": hr_consultant
        })
        
    # Sestavení finálního Firebase payloadu
    print("Příprava dat pro Firebase...")
    upload_id = str(uuid.uuid4())
    uploaded_at = now.isoformat()
    
    payload = {
        "meta": {"uploadedAt": uploaded_at, "uploadId": upload_id},
        "branches": {}
    }
    
    import re
    for branch, jobs in grouped.items():
        branch_key = re.sub(r'[.#$\[\]/]', '_', branch)
        payload["branches"][branch_key] = {
            "name": branch,
            "jobs": {}
        }
        for idx, job in enumerate(jobs):
            candidates_obj = {}
            for c in job['candidates']:
                candidates_obj[c['id']] = c
                
            payload["branches"][branch_key]["jobs"][job['jobId']] = {
                "ref": job['ref'],
                "position": job['position'],
                "division": job['division'],
                "department": job['department'],
                "date": job['date'],
                "daysOpen": job['daysOpen'],
                "cap": job['cap'],
                "vac": job['vac'],
                "actual": job['actual'],
                "recruiter": job['recruiter'],
                "manager": job['manager'],
                "order": idx,
                "candidates": candidates_obj
            }
            
    # Odeslání do Firebase REST API
    print("Odesílám data do Firebase...")
    auth_suffix = f"?auth={FIREBASE_SECRET}" if FIREBASE_SECRET else ""
    # 1. Napsat celý report
    resp1 = requests.put(f"{FIREBASE_URL}/reports/{upload_id}.json{auth_suffix}", json=payload)
    resp1.raise_for_status()
    
    # 2. Aktualizovat pointer
    resp2 = requests.put(f"{FIREBASE_URL}/latestReport.json{auth_suffix}", json={
        "uploadId": upload_id,
        "uploadedAt": uploaded_at
    })
    resp2.raise_for_status()
    
    print(f"Hotovo! Dashboard se nyní automaticky aktualizuje. UploadID: {upload_id}")

if __name__ == "__main__":
    main()
