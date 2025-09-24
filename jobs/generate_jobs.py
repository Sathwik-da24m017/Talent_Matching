"""
Job generator (v2).
Now exports jobs in the target schema to CSV.
"""

import random, csv, json, yaml
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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

def generate_hr_requirements(roles_levels, settings):
    roles = roles_levels["roles"]
    levels = list(roles_levels["levels"].keys())
    reqs = {}
    n_roles = random.randint(1, 3)
    for _ in range(n_roles):
        role = random.choice(roles)
        level = random.choice(levels)
        count = random.randint(1, settings["hr_requirements_people"]["max"] // n_roles)
        reqs[f"{level} {role}"] = count
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

    # Skills
    relevant_cats = random.sample(list(skills_by_cat.keys()), 2)
    skills = []
    for cat in relevant_cats:
        skills += random.sample(skills_by_cat[cat], random.randint(1, 3))
    skills = list(set(skills))[:settings["skills_per_job"]["max"]]

    # HR requirements
    hr_reqs = generate_hr_requirements(roles_levels, settings)

    # Manager preferences (placeholder: pick some employee IDs later)
    manager_pref = []

    # Similar projects: sample from existing jobs
    similar = []
    if existing_jobs:
        similar = random.sample(existing_jobs, min(len(existing_jobs), random.randint(0, 2)))

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

    rows = []
    existing_ids = []
    for i in range(1, n + 1):
        job = generate_job(i, settings, domains, locations, skills_by_cat, roles_levels, existing_ids)
        rows.append(job)
        existing_ids.append(job["job_id"])

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Wrote {len(rows)} jobs to {out}")

if __name__ == "__main__":
    random.seed(42)
    main()
