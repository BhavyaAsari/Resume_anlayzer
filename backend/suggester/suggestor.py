def suggest_careers(parsed_data):
    skills = parsed_data.get("skills", [])
    if not skills:
        return ["Unable to detect career path (no skills found)"]

    skills = [s.lower() for s in skills]
    suggestions = set()

    role_map = {
        # TECH
        "Python Developer": ["python", "flask", "django"],
        "Java Developer": ["java", "spring", "hibernate"],
        "Frontend Developer": ["html", "css", "javascript", "react", "bootstrap"],
        "Backend Developer": ["node", "express", "api", "mongodb", "mysql", "postgresql"],
        "Full Stack Developer": ["react", "node", "html", "css", "mongodb", "express"],
        "Data Analyst": ["excel", "sql", "pandas", "tableau", "data analysis"],
        "Data Scientist": ["python", "pandas", "sklearn", "matplotlib", "statistics", "regression"],
        "ML Engineer": ["tensorflow", "pytorch", "scikit", "ml", "ai", "deep learning"],
        "AI Researcher": ["nlp", "vision", "transformer", "bert", "ai"],
        "DevOps Engineer": ["docker", "jenkins", "ci/cd", "aws", "linux", "ansible"],
        "Cloud Engineer": ["aws", "azure", "gcp", "cloud", "kubernetes", "terraform"],
        "Mobile App Developer": ["flutter", "android", "kotlin", "react native", "ios", "swift"],
        "Cybersecurity Analyst": ["cybersecurity", "network security", "kali", "nmap", "vulnerability", "penetration"],
        "QA Tester": ["selenium", "testcase", "junit", "bug tracking", "qa"],
        "UI/UX Designer": ["figma", "xd", "wireframe", "ui", "ux", "prototyping", "design thinking"],

        # CREATIVE & CONTENT
        "Graphic Designer": ["photoshop", "illustrator", "canva", "branding", "logo", "poster"],
        "Animator / Video Editor": ["after effects", "premiere", "animation", "editing", "motion graphics"],
        "Content Writer": ["writing", "storytelling", "copywriting", "articles", "blog", "seo writing"],
        "Social Media Manager": ["instagram", "twitter", "content calendar", "hashtag", "reels", "analytics"],
        "YouTube Creator": ["youtube", "script", "editing", "voiceover", "thumbnail"],

        # BUSINESS & MANAGEMENT
        "Project Manager": ["agile", "scrum", "kanban", "jira", "project planning", "sprint", "team lead"],
        "Product Manager": ["roadmap", "market fit", "prioritization", "requirements", "user stories"],
        "HR Executive": ["recruitment", "interviews", "hr", "people ops", "employee engagement"],
        "Operations Manager": ["logistics", "inventory", "supply chain", "erp", "vendor", "ops"],
        "Business Analyst": ["gap analysis", "requirement", "bpmn", "process modeling", "reports"],

        # FINANCE & MARKETING
        "Accountant": ["tally", "ledger", "gst", "income tax", "reconciliation"],
        "Financial Analyst": ["budget", "forecast", "excel", "valuation", "balance sheet", "finance"],
        "Digital Marketer": ["seo", "sem", "google ads", "meta ads", "email marketing", "analytics"],
        "Market Researcher": ["survey", "sampling", "qualitative", "quantitative", "market trends"],

        # EDUCATION & RESEARCH
        "Academic Researcher": ["publication", "paper", "journal", "thesis", "research methodology"],
        "Teacher / Instructor": ["teaching", "lesson plan", "classroom", "curriculum", "blackboard", "school"],
        "Trainer / Coach": ["training", "workshop", "upskilling", "facilitation"],

        # HEALTHCARE & LAW
        "Healthcare Assistant": ["medical", "nursing", "patient care", "hospital", "clinical"],
        "Pharmacist": ["pharma", "prescription", "medicines", "drug", "inventory"],
        "Legal Assistant / Paralegal": ["contracts", "legal", "case law", "court", "compliance", "legal drafting"],

        # GENERAL & TRANSFERABLE
        "Customer Support Representative": ["customer service", "support", "call center", "crm", "ticket"],
        "Administrative Assistant": ["admin", "ms office", "calendar", "clerical", "report"],
        "Sales Executive": ["lead gen", "crm", "cold call", "deal", "sales funnel"],
        "Entrepreneur / Startup Founder": ["startup", "pitch deck", "fundraising", "mvp", "growth", "bootstrap"],
        "Soft Skill Trainer": ["communication", "leadership", "teamwork", "empathy", "negotiation"]
    }

    for role, keywords in role_map.items():
        if any(k in skills for k in keywords):
            suggestions.add(role)

    if not suggestions:
        suggestions.add("General Career Path (consider exploring more domains)")

    return sorted(list(suggestions))
