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


def recommend_courses(gaps: list[str]) -> list[str]:
    recommendations = []
    for gap in gaps:
        key = gap.lower()
        if key in COURSES:
            recommendations.append(COURSES[key])
        elif "years" not in key and "experience" not in key:
            recommendations.append(f"{gap.title()} Fundamentals")
    return recommendations[:5]
