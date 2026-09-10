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
    "tableau": {"title": "Tableau Training and Tutorials", "provider": "Tableau", "url": "https://www.tableau.com/learn/training", "reason": "Build dashboards and communicate insights with Tableau."},
    "power bi": {"title": "Power BI Learning", "provider": "Microsoft Learn", "url": "https://learn.microsoft.com/training/powerplatform/power-bi/", "reason": "Learn data modeling, reports, and interactive Power BI dashboards."},
    "javascript": {"title": "JavaScript Guide", "provider": "MDN Web Docs", "url": "https://developer.mozilla.org/docs/Web/JavaScript/Guide", "reason": "Strengthen practical JavaScript language and browser development skills."},
    "typescript": {"title": "TypeScript Handbook", "provider": "TypeScript Documentation", "url": "https://www.typescriptlang.org/docs/handbook/intro.html", "reason": "Learn typed JavaScript for maintainable application development."},
    "java": {"title": "Java Tutorials", "provider": "Dev.java", "url": "https://dev.java/learn/", "reason": "Build core Java programming and application development skills."},
    "fastapi": {"title": "FastAPI Tutorial", "provider": "FastAPI Documentation", "url": "https://fastapi.tiangolo.com/tutorial/", "reason": "Learn how to build production-ready Python APIs with FastAPI."},
    "django": {"title": "Django Tutorial", "provider": "Django Documentation", "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "reason": "Practice building web applications with Django."},
    "pandas": {"title": "Getting Started with pandas", "provider": "pandas Documentation", "url": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/", "reason": "Learn practical data cleaning and analysis with pandas."},
    "spark": {"title": "Spark Quick Start", "provider": "Apache Spark Documentation", "url": "https://spark.apache.org/docs/latest/quick-start.html", "reason": "Practice distributed data processing with Apache Spark."},
    "practical project experience": {"title": "GitHub Skills: Introduction to GitHub", "provider": "GitHub Skills", "url": "https://skills.github.com/", "reason": "Build and publish a practical project that demonstrates hands-on experience."},
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
    return details


def recommend_courses(gaps: list[str]) -> list[str]:
    return [item["title"] for item in course_link_details(gaps)]
