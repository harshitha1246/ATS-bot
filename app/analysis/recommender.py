COURSE_CATALOG = {
    "aws": {"title": "AWS Cloud Practitioner Essentials", "provider": "AWS Skill Builder", "url": "https://skillbuilder.aws/", "reason": "Build foundational AWS cloud and deployment knowledge."},
    "azure": {"title": "Azure Fundamentals", "provider": "Microsoft Learn", "url": "https://learn.microsoft.com/training/paths/azure-fundamentals-describe-cloud-concepts/", "reason": "Learn core Azure services and cloud concepts."},
    "docker": {"title": "Get Started with Docker", "provider": "Docker Docs", "url": "https://docs.docker.com/get-started/", "reason": "Learn containers, images, and running applications with Docker."},
    "kubernetes": {"title": "Kubernetes Basics", "provider": "Kubernetes Documentation", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/", "reason": "Practice deploying and managing containerized applications."},
    "python": {"title": "The Python Tutorial", "provider": "Python.org", "url": "https://docs.python.org/3/tutorial/", "reason": "Strengthen core Python syntax and programming concepts."},
    "sql": {"title": "SQL Tutorial", "provider": "PostgreSQL Documentation", "url": "https://www.postgresql.org/docs/current/tutorial-sql.html", "reason": "Practice queries, joins, filtering, and relational data work."},
    "react": {"title": "Learn React", "provider": "React Documentation", "url": "https://react.dev/learn", "reason": "Learn components, state, events, and modern React patterns."},
    "testing": {"title": "Get Started with pytest", "provider": "pytest Documentation", "url": "https://docs.pytest.org/en/stable/getting-started.html", "reason": "Build a practical automated testing workflow in Python."},
    "machine learning": {"title": "Machine Learning Crash Course", "provider": "Google for Developers", "url": "https://developers.google.com/machine-learning/crash-course", "reason": "Learn the core concepts behind practical machine learning."},
    "ci/cd": {"title": "GitHub Actions Documentation", "provider": "GitHub Docs", "url": "https://docs.github.com/actions", "reason": "Learn how to automate build, test, and deployment workflows."},
}


def _matching_key(gap: str) -> str | None:
    normalized = gap.lower().strip()
    for key in COURSE_CATALOG:
        if normalized == key or key in normalized:
            return key
    return None


def course_link_details(gaps: list[str]) -> list[dict[str, str]]:
    details = []
    seen = set()
    for gap in gaps:
        key = _matching_key(gap)
        if key and key not in seen:
            details.append(dict(COURSE_CATALOG[key]))
            seen.add(key)
        if len(details) == 4:
            break
    return details


def recommend_courses(gaps: list[str]) -> list[str]:
    return [item["title"] for item in course_link_details(gaps)]
