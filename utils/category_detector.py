def detect_category(text):

    text = text.lower()

    hr_keywords = [
        "employee",
        "salary",
        "leave",
        "recruitment",
        "attendance",
        "payroll",
        "benefits",
    ]

    finance_keywords = [
        "invoice",
        "revenue",
        "tax",
        "budget",
        "profit",
        "loss",
    ]

    legal_keywords = [
        "agreement",
        "contract",
        "law",
        "legal",
        "compliance",
        "court",
    ]

    hr_score = sum(
        keyword in text
        for keyword in hr_keywords
    )

    finance_score = sum(
        keyword in text
        for keyword in finance_keywords
    )

    legal_score = sum(
        keyword in text
        for keyword in legal_keywords
    )

    scores = {
        "HR": hr_score,
        "Finance": finance_score,
        "Legal": legal_score,
    }

    best_category = max(
        scores,
        key=scores.get
    )

    if scores[best_category] == 0:
        return "General"

    return best_category


def detect_query_category(query):

    return detect_category(query)