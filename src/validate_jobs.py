"""
Job dataset validator.
Checks that generated jobs match schema and reference only valid roles/skills.
"""

import json
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_shared():
    import yaml
    skills = json.loads((ROOT / "shared" / "skills.json").read_text())
    roles_levels = json.loads((ROOT / "shared" / "roles_levels.json").read_text())
    domains = json.loads((ROOT / "shared" / "domains.json").read_text())
    locations = json.loads((ROOT / "shared" / "locations.json").read_text())
    settings = yaml.safe_load((ROOT / "shared" / "settings.yaml").read_text())
    return skills, roles_levels, domains, locations, settings

def validate_jobs(path="data/jobs.csv"):
    print(f"Loading {path}...")
    jobs = pd.read_csv(ROOT / path)
    skills, roles_levels, domains, locations, settings = load_shared()

    all_skills = {s for cat in skills for s in skills[cat]}
    all_roles = set(roles_levels["roles"])
    all_levels = set(roles_levels["levels"].keys())
    all_domains = set(domains["industry_verticals"] + domains["service_lines"])
    all_locations = set(locations["india"] + locations["global"] + locations["virtual"])

    errors = []

    # Check each job
    for row in jobs.itertuples():
        # 1. Dates valid
        if row.start_date >= row.end_date:
            errors.append((row.job_id, "Invalid dates"))

        # 2. Domain valid
        if row.domain not in domains["industry_verticals"]:
            errors.append((row.job_id, f"Invalid domain {row.domain}"))

        # 3. Location valid
        if row.location not in all_locations:
            errors.append((row.job_id, f"Invalid location {row.location}"))

        # 4. Skills valid
        for s in str(row.technologies).split("|"):
            if s and s not in all_skills:
                errors.append((row.job_id, f"Unknown skill {s}"))

        # 5. HR requirements valid JSON + roles/levels exist
        try:
            hr = json.loads(row.hr_requirements)
            for k in hr.keys():
                parts = k.split(" ", 1)
                if len(parts) != 2:
                    errors.append((row.job_id, f"Malformed HR key {k}"))
                    continue
                level, role = parts
                if level not in all_levels:
                    errors.append((row.job_id, f"Invalid level {level} in HR req"))
                if role not in all_roles:
                    errors.append((row.job_id, f"Invalid role {role} in HR req"))
        except Exception as e:
            errors.append((row.job_id, f"HR requirements not JSON: {e}"))

    if errors:
        print("Validation errors:")
        for eid, msg in errors[:20]:
            print(f"  {eid}: {msg}")
        print(f"... total {len(errors)} errors")
    else:
        print("All jobs passed validation!")

if __name__ == "__main__":
    validate_jobs()
