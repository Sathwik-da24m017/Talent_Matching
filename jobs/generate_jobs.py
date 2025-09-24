"""
Job generator (v3).
Generates synthetic projects with schema-aligned fields and exports to CSV.
Adds realism: service-line–aligned skills, weighted levels, coherent HR requirements.
"""

import random, csv, json, yaml
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# --- Rule tables for realism ---

SERVICE_LINE_TO_ROLES = {
    "Application Development & Maintenance": [
        "Software Engineer", "Backend Engineer", "Frontend Engineer", "Full-Stack Developer"
    ],
    "Data Engineering & Analytics": [
        "Data Engineer", "Business Analyst", "QA/Test Engineer"
    ],
    "AI/ML & MLOps": [
        "Data Scientist", "ML Engineer", "Data Engineer"
    ],
    "Cloud Migration & Modernization": [
        "Cloud Engineer", "DevOps/SRE Engineer", "Solutions/Technical Architect"
    ],
    "DevOps & SRE": [
        "DevOps/SRE Engineer", "Cloud Engineer"
    ],
    "Cybersecurity": [
        "Cybersecurity Analyst"
    ],
    "ERP & SAP": [
        "ERP/SAP Consultant", "Solutions/Technical Architect"
    ],
    "Salesforce & ServiceNow": [
        "Salesforce/ServiceNow Developer", "Solutions/Technical Architect"
    ],
    "Quality Engineering & Testing": [
        "QA/Test Engineer", "Business Analyst"
    ],
    "Consulting & Business Analysis": [
        "Business Analyst", "Project Manager"
    ]
}

SERVICE_LINE_TO_SKILL_CATS = {
    "Application Development & Maintenance": ["Programming", "Web_Mobile"],
    "Data Engineering & Analytics": ["Data_Engineering", "BI_Analytics", "Integration_ETL", "Programming"],
    "AI/ML & MLOps": ["AI_ML", "Data_Engineering", "Programming"],
    "Cloud Migration & Modernization": ["Cloud_Infrastructure", "DevOps_SRE", "Programming"],
    "DevOps & SRE": ["DevOps_SRE", "Cloud_Infrastructure"],
    "Cybersecurity": ["Cybersecurity", "Cloud_Infrastructure"],
    "ERP & SAP": ["ERP_Platforms", "Integration_ETL"],
    "Salesforce & ServiceNow": ["ERP_Platforms", "Integration_ETL", "Programming"],
    "Quality Engineering & Testing": ["Testing_QA", "Programming"],
    "Consulting & Business Analysis": ["BI_Analytics", "Data_Engineering"]
}

LEVEL_WEIGHTS = {
    "PAT": 0.05, "PA": 0.20, "Associate": 0.35, "SrAssociate": 0.25,
    "Manager": 0.10, "SrManager": 0.04, "Arch/AD": 0.01, "Director+": 0.0
}

# --- Utils ---

def read_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

def rand_date_range(months: int):
    today = date.today()
    start = today + timedelta(days=random.randint(0, 60))
    end = start + timedelta(days=int(30.4 * months))
    return start.isoformat(), end.isoformat()

def _weighted_choice(weights_dict):
    items = list(weights_dict.items())
    r = random.random() * sum(w for _, w in items)
    upto = 0.0
    for k, w in items:
        if upto + w >= r:
            return k
        upto += w
    return items[-1][0]

# --- Core generation ---

def generate_hr_requirements(roles_levels, settings, service_line):
    candidate_roles = SERVICE_LINE_TO_ROLES.get(service_line, roles_levels["roles"])
    total = random.randint(settings["hr_requirements_people"]["min"], settings["hr_requirements_people"]["max"])
    n_buckets = random.randint(1, min(3, len(candidate_roles)))
    chosen_roles = random.sample(candidate_roles, n_buckets)

    reqs = {}
    remaining = total
    for idx, role in enumerate(chosen_roles, 1):
        level = _weighted_choice(LEVEL_WEIGHTS)
        if idx < n_buckets:
            alloc = max(1, int(round((total / n_buckets) + random.uniform(-1, 1))))
            alloc = min(alloc, remaining - (n_buckets - idx))
        else:
            alloc = max(1, remaining)
        remaining -= alloc
        if role in ("Solutions/Technical Architect", "Project Manager") and level in ("PAT", "PA"):
            level = "Associate"
        key = f"{level} {role}"
        reqs[key] = reqs.get(key, 0) + alloc

    return reqs

def generate_job(i, settings, domains, locations, skills_by_cat, roles_levels, existing_jobs):
    job_id = f"P{i:04d}"
    domain = random.choice(domains["industry_verticals"])
    service_line = random.choice(domains["service_lines"])
    project_name = f"{service_line} for {domain}"

    location = random.choice(locations["india"] + locations["global"] + locations["virtual"])
    remote_possible = (location == "Remote") or (random.random() < settings["remote_mix_probability"])

    months = random.randint(settings["duration_months"]["min"], settings["duration_months"]["max"])
    start_date, end_date = rand_date_range(months)

    budget = random.randint(settings["budget_lakhs_inr"]["min"], settings["budget_lakhs_inr"]["max"])
    min_exp = random.randint(settings["min_experience_years"]["min"], settings["min_experience_years"]["max"])
    priority = random.choices(
        population=list(settings["priority_weights"].keys()),
        weights=list(settings["priority_weights"].values()),
        k=1
    )[0]

    # Skills aligned with service line
    allowed_cats = SERVICE_LINE_TO_SKILL_CATS.get(service_line, list(skills_by_cat.keys()))
    pick_cats = random.sample(allowed_cats, k=min(2, len(allowed_cats)))
    skills = []
    for cat in pick_cats:
        k_cat = min(random.randint(1, 3), len(skills_by_cat[cat]))
        skills += random.sample(skills_by_cat[cat], k_cat)
    skills = list(dict.fromkeys(skills))[:settings["skills_per_job"]["max"]]

    # HR requirements
    hr_reqs = generate_hr_requirements(roles_levels, settings, service_line)

    # Manager preferences (placeholder until employees exist)
    manager_pref = []

    # Similar projects
    similar = []
    if existing_jobs:
        pool = [jid for jid in existing_jobs if random.random() < 0.6]
        if not pool:
            pool = existing_jobs
        k = random.randint(0, 2)
        similar = random.sample(pool, k) if len(pool) >= k else pool[:k]

    return {
        "job_id": job_id,
        "project_name": project_name,
        "domain": domain,
        "location": location,
        "start_date": start_date,
        "end_date": end_date,
        "duration_months": months,
        "budget": budget,
        "technologies": "|".join(skills),
        "hr_requirements": json.dumps(hr_reqs),
        "min_experience": min_exp,
        "manager_pref": "|".join(manager_pref),
        "priority": priority,
        "similar_projects": "|".join(similar),
        "remote_possible": remote_possible
    }

# --- Main ---

def main(out_path="data/jobs.csv"):
    print("Reading config...")
    cfg = read_yaml(ROOT / "shared" / "settings.yaml")
    settings = cfg["jobs"]
    domains = read_json(ROOT / "shared" / "domains.json")
    locations = read_json(ROOT / "shared" / "locations.json")
    skills_by_cat = read_json(ROOT / "shared" / "skills.json")
    roles_levels = read_json(ROOT / "shared" / "roles_levels.json")

    n = settings["n"]
    print(f"Generating {n} synthetic job records...")

    rows, existing_ids = [], []
    for i in range(1, n + 1):
        job = generate_job(i, settings, domains, locations, skills_by_cat, roles_levels, existing_ids)
        rows.append(job)
        existing_ids.append(job["job_id"])

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} jobs to {out}")

if __name__ == "__main__":
    random.seed(42)
    main()
