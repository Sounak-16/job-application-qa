"""
Job listings data store and search logic for the Job Application Portal.
Contains realistic job roles, compensation, requirements, and keyword search functionality.
"""

from typing import List, Dict, Any, Optional

JOBS_DATABASE: List[Dict[str, Any]] = [
    {
        "id": "qa-eng-101",
        "title": "Senior QA Automation Engineer",
        "department": "Engineering",
        "location": "Remote, US / Canada",
        "employment_type": "Full-Time",
        "experience": "5+ years",
        "salary_range": "$125,000 - $155,000 / year",
        "summary": "We are seeking a Senior QA Automation Engineer to design, implement, and maintain robust end-to-end test automation suites for our cloud-native platforms.",
        "responsibilities": [
            "Develop maintainable UI and API test automation frameworks using Playwright and pytest.",
            "Integrate automated smoke and regression test suites into CI/CD pipelines (GitHub Actions).",
            "Perform exploratory testing on new features and document clear defect reports with root-cause analysis.",
            "Partner with software engineers and product managers to define clear acceptance criteria.",
            "Drive test-driven development (TDD) and quality engineering best practices across the team."
        ],
        "requirements": [
            "Bachelor's degree in Computer Science, Software Engineering, or equivalent practical experience.",
            "5+ years of experience in test automation using Python, TypeScript, or Java.",
            "Deep hands-on expertise with Playwright, Cypress, or Selenium WebDriver.",
            "Proficiency in REST API testing, mock services, and contract testing.",
            "Solid experience with Git, Docker, and CI/CD pipelines."
        ],
        "tags": ["Python", "Playwright", "pytest", "CI/CD", "Automation"]
    },
    {
        "id": "fullstack-eng-102",
        "title": "Full Stack Software Engineer",
        "department": "Engineering",
        "location": "San Francisco, CA (Hybrid)",
        "employment_type": "Full-Time",
        "experience": "3+ years",
        "salary_range": "$135,000 - $165,000 / year",
        "summary": "Join our core product team to build high-scale, accessible web applications and resilient backend microservices.",
        "responsibilities": [
            "Design and build responsive user interfaces using React, TypeScript, and modern CSS.",
            "Build scalable RESTful and GraphQL APIs using Python (FastAPI/Flask) and PostgreSQL.",
            "Collaborate with UX designers to craft intuitive user experiences.",
            "Write comprehensive unit, integration, and end-to-end tests."
        ],
        "requirements": [
            "3+ years of professional full-stack development experience.",
            "Strong command of modern JavaScript/TypeScript and React.",
            "Demonstrated proficiency in Python, Go, or Node.js backend development.",
            "Experience with relational databases (PostgreSQL) and SQL query optimization."
        ],
        "tags": ["React", "TypeScript", "Python", "PostgreSQL", "FullStack"]
    },
    {
        "id": "devops-eng-103",
        "title": "Cloud DevOps & Site Reliability Engineer",
        "department": "Infrastructure",
        "location": "Remote, Global",
        "employment_type": "Full-Time",
        "experience": "4+ years",
        "salary_range": "$140,000 - $170,000 / year",
        "summary": "Help scale our multi-region Kubernetes infrastructure, optimize deployment pipelines, and maintain 99.99% system availability.",
        "responsibilities": [
            "Manage and optimize cloud infrastructure on AWS and GCP using Terraform.",
            "Maintain Kubernetes clusters (EKS/GKE), ingress controllers, and service meshes.",
            "Implement observability, tracing, and alerting using Prometheus, Grafana, and Datadog.",
            "Automate zero-downtime deployment workflows and disaster recovery strategies."
        ],
        "requirements": [
            "4+ years experience in DevOps, SRE, or Infrastructure Engineering.",
            "Hands-on expertise with Kubernetes, Docker, and Infrastructure as Code (Terraform).",
            "Strong scripting skills in Python, Bash, or Go.",
            "Solid understanding of networking, TLS/SSL, DNS, and cloud security best practices."
        ],
        "tags": ["Kubernetes", "AWS", "Terraform", "Docker", "SRE"]
    },
    {
        "id": "product-mgr-104",
        "title": "Technical Product Manager",
        "department": "Product",
        "location": "New York, NY (Hybrid)",
        "employment_type": "Full-Time",
        "experience": "4+ years",
        "salary_range": "$130,000 - $160,000 / year",
        "summary": "Lead product definition and feature delivery for developer platform APIs and analytics capabilities.",
        "responsibilities": [
            "Define product roadmaps, requirements specifications, and user stories.",
            "Conduct candidate and customer interviews to translate user needs into technical specs.",
            "Work closely with engineering and design to deliver iterative product releases.",
            "Analyze product metrics to measure user engagement and feature adoption."
        ],
        "requirements": [
            "4+ years of product management experience for technical SaaS or developer tools.",
            "Strong background in software engineering or technical degree preferred.",
            "Exceptional written communication and cross-functional leadership skills.",
            "Data-driven mindset with experience in SQL and analytics platforms."
        ],
        "tags": ["Product", "Roadmap", "Agile", "SaaS", "APIs"]
    },
    {
        "id": "data-analyst-105",
        "title": "Data Analyst & Business Intelligence",
        "department": "Analytics",
        "location": "Chicago, IL (Hybrid)",
        "employment_type": "Full-Time",
        "experience": "2+ years",
        "salary_range": "$90,000 - $115,000 / year",
        "summary": "Transform operational data into actionable insights through automated reporting, executive dashboards, and statistical analysis.",
        "responsibilities": [
            "Build and maintain interactive dashboards in Tableau and Looker.",
            "Write complex SQL queries and data models to answer ad-hoc business questions.",
            "Conduct statistical analysis on candidate retention and customer behavior.",
            "Collaborate with data engineering to ensure data warehouse data quality."
        ],
        "requirements": [
            "2+ years experience in business analytics or business intelligence.",
            "Advanced SQL proficiency (joins, window functions, aggregations).",
            "Experience with BI tools (Tableau, Looker, or Power BI).",
            "Working knowledge of Python (pandas/matplotlib) for data manipulation."
        ],
        "tags": ["SQL", "Tableau", "Looker", "Python", "Analytics"]
    }
]


def get_all_jobs() -> List[Dict[str, Any]]:
    """Return all available job listings."""
    return JOBS_DATABASE


def get_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single job posting by unique ID."""
    for job in JOBS_DATABASE:
        if job["id"] == job_id:
            return job
    return None


def search_jobs(keyword: str = "", department: str = "") -> List[Dict[str, Any]]:
    """
    Search and filter jobs by keyword and optional department.
    Keyword matches against title, summary, location, tags, and department.
    """
    results = JOBS_DATABASE
    cleaned_keyword = (keyword or "").strip().lower()
    cleaned_dept = (department or "").strip().lower()

    if cleaned_dept and cleaned_dept != "all":
        results = [j for j in results if j["department"].lower() == cleaned_dept]

    if cleaned_keyword:
        filtered = []
        for job in results:
            searchable_text = " ".join([
                job["title"],
                job["department"],
                job["location"],
                job["summary"],
                " ".join(job.get("tags", [])),
                " ".join(job.get("requirements", []))
            ]).lower()
            if cleaned_keyword in searchable_text:
                filtered.append(job)
        return filtered

    return results
