COURSES = {
    "aws": "AWS Cloud Practitioner Fundamentals",
    "azure": "Microsoft Azure Fundamentals",
    "docker": "Docker and Container Fundamentals",
    "kubernetes": "Kubernetes for Developers",
    "python": "Python Programming Fundamentals",
    "sql": "SQL for Data and Applications",
    "react": "React Frontend Development",
    "testing": "Automated Testing with Pytest",
    "machine learning": "Practical Machine Learning Foundations",
    "ci/cd": "CI/CD with GitHub Actions",
}

COURSE_LINKS = {
    "aws": "https://skillbuilder.aws/",
    "azure": "https://learn.microsoft.com/training/azure/",
    "docker": "https://docs.docker.com/get-started/",
    "kubernetes": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
    "python": "https://docs.python.org/3/tutorial/",
    "sql": "https://www.postgresql.org/docs/current/tutorial-sql.html",
    "react": "https://react.dev/learn",
    "testing": "https://docs.pytest.org/en/stable/getting-started.html",
    "machine learning": "https://developers.google.com/machine-learning/crash-course",
    "ci/cd": "https://docs.github.com/actions",
}


def recommend_courses(gaps: list[str]) -> list[str]:
    recommendations = []
    for gap in gaps:
        key = gap.lower()
        if key in COURSES:
            recommendations.append(COURSES[key])
        elif "years" not in key and "experience" not in key:
            recommendations.append(f"{gap.title()} Fundamentals")
    return recommendations[:5]


def course_link_details(gaps: list[str]) -> list[dict[str, str]]:
    details = []
    for course in recommend_courses(gaps):
        key = next((name for name, title in COURSES.items() if title == course), None)
        if key and key in COURSE_LINKS:
            details.append({"title": course, "url": COURSE_LINKS[key]})
    return details[:5]
