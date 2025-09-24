# Employee-Project Matching System (MTP)

A synthetic-data-driven prototype for intelligently matching employees to open projects within a large organization (e.g., Cognizant/X). This project simulates real-world workforce planning and talent allocation scenarios by combining skill embeddings, adjacent-skill mapping, optimization under constraints (bench time, budget, bandwidth), and two-stage matching workflows.

---

## Project Goals

* **Simulate a realistic talent marketplace** for internal project staffing using artificial data.
* **Generate synthetic employee and project datasets** using a shared skill ontology, roles, domains, and preferences.
* Build a **matching pipeline**:

  * Employee-to-employee similarity (E2E clustering)
  * Job-to-ideal-employee embedding (J2E matching)
* Implement an **optimization engine** that respects:

  * Headcount & budget constraints
  * Bench time reduction
  * Employee preferences and project priority
* Support **adjacent skill matching** via a weighted skill similarity graph.
* Prepare for integration with real-world HR data.

---

## Big Picture Workflow

```
     [Shared Dictionaries]       
          |
     ------------------
     |                |
[Employee Generator]  [Job Generator]
     |                |
     |                |---------> [Adjacent Skill Graph]
     |                        |
     ------------------       |
             |                |
      [Employee Dataset]  [Job Dataset]
             \                /
           [Matching Engine]
                   |
            [Optimizer Engine]
                   |
            [Final Allocation]
```

---

## Folder Structure

```
.
├── shared/          # Shared dictionaries: skills, roles, domains, locations, settings
├── employees/       # Employee generator (Smita's side)
├── jobs/            # Job generator + skill similarity graph (Your side)
├── src/             # Reusable code modules (utils, schemas, validation, optimization)
├── data/            # Generated CSVs (employees.csv, jobs.csv)
├── notebooks/       # Jupyter notebooks for EDA, similarity, embeddings, matching
├── experiments/     # Prototyping of optimization logic, clustering, evaluation
├── docs/            # Project reports, summaries, architecture diagrams
├── requirements.txt # Dependencies
└── README.md        # This file
```

---

## Key Features

* **Skill Ontology**: Shared, hierarchical skill dictionary across employees and projects.
* **Adjacent Skill Matching**: Weighted similarity graph enables intelligent substitutions.
* **E2E Similarity**: Employee clustering based on multi-dimensional embeddings.
* **J2E Ideal Matching**: Every job creates a virtual "ideal employee" to compare against.
* **Optimization Engine**: Budget-aware, bench-minimizing assignment with HR constraints.

---

## Current Progress

* [x] Folder structure created
* [x] Virtual environment setup with dependencies
* [x] Shared dictionaries drafted and frozen
* [ ] Employee & job generation scripts
* [ ] Embedding + similarity computation
* [ ] Constraint-aware assignment engine
* [ ] Evaluation dashboards & KPIs

---

## Next Steps

* Finalize schema for both employees and jobs
* Implement synthetic data generation for jobs and employees
* Run initial cross-validation for skill coverage
* Build job → ideal employee embedding logic
* Develop core optimization solver

---

## 🔗 Collaboration

* Smita: employee generation, clustering, preferences
* Sathwik: job generation, skill graph, matching logic, optimization
* Shared files must remain version-controlled and stable under `shared/`

---

## Final Deliverables

* `employees.csv`, `jobs.csv` (generated, realistic datasets)
* Matching and optimization scripts
* Visualization notebooks
* Final report summarizing approach, architecture, results, insights
* (Optional) Streamlit demo for interactive matching

---

## Notes

This repo is designed for experimentation and prototyping. When the structure is stable and validated, the same workflow can be extended to real anonymized HR datasets from partner organizations.
