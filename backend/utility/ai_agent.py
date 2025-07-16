import os
import cohere
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)


def format_with_headings(text: str, title: str = "") -> str:
    """
    Format output with markdown-style section titles and proper spacing.
    Converts numbered sections to bolded headings with spacing.
    """
    if title:
        text = f"**{title}**\n\n{text.strip()}"

    # Replace numbered points with bolded markdown-style headings
    for i in range(1, 11):
        text = text.replace(f"{i}.", f"\n\n**{i}.**")

    return text.strip()


def career_guidance_agent(parsed_resume: dict) -> str:
    """
    Generate formal, markdown-formatted career guidance using Cohere AI.
    """
    try:
        name = parsed_resume.get('name', 'Candidate')
        skills = parsed_resume.get('skills', [])
        summary = parsed_resume.get('summary', '')
        work_experience = parsed_resume.get('work_experience', '')
        education = parsed_resume.get('education', [])
        certifications = parsed_resume.get('certifications', [])
        projects = parsed_resume.get('projects', [])

        skills_text = ', '.join(skills) or "No specific skills"
        cert_text = ', '.join(certifications) or "No certifications listed"
        project_text = '; '.join(projects) or "No projects listed"

        education_str = '; '.join(
            [f"{edu.get('degree', '')} from {edu.get('organization', '')} ({edu.get('year', '')})"
             for edu in education if isinstance(edu, dict)]
        ) or "No education details"

        prompt = f"""You are a professional AI career advisor.

Candidate Profile:
- Name: {name}
- Skills: {skills_text}
- Summary: {summary}
- Work Experience: {work_experience}
- Education: {education_str}
- Certifications: {cert_text}
- Projects: {project_text}

Now provide:
1. Career Path Suggestions (2-3 options)
2. Technical Skills to Focus On (3 skills)
3. Soft Skills to Build (2 soft skills)
4. A 30-Day Action Plan (step-wise)
5. Industry Market Insight
6. One Personalized Tip
"""

        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=600,
            temperature=0.7
        )

        return format_with_headings(response.generations[0].text, title="Career Guidance")

    except Exception as e:
        return f"""**Career Guidance Unavailable**

**Error:** {str(e)}

**Fallback Suggestions:**
- Strengthen your project portfolio
- Join relevant communities and network
- Contribute to open-source repositories
- Refine your resume and LinkedIn profile
"""


def get_industry_trends(skills: list) -> str:
    """
    Generate formal industry trends with markdown-style formatting using Cohere AI.
    """
    try:
        skills_text = ', '.join(skills) if skills else "general technology skills"

        prompt = f"""
Analyze the following skills: {skills_text}

Provide:
1. Demand and hiring trends
2. Emerging technologies and roles
3. Future growth outlook (next 2-3 years)
4. Complementary skills to learn

Be concise, professional, and markdown-friendly.
"""

        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=400,
            temperature=0.7
        )

        return format_with_headings(response.generations[0].text, title="Industry Trends")

    except Exception as e:
        return f"""**Industry Trends Unavailable**

**Error:** {str(e)}

**Suggestion:** Use platforms like LinkedIn Insights, HackerRank Reports, or Coursera's Job Skills Trends to research in-demand technologies.
"""


def generate_interview_questions(role: str, skills: list) -> str:
    """
    Generate formal markdown-formatted interview questions for the role and skills.
    """
    try:
        role = role or "Software Engineer"
        skills_text = ', '.join(skills) if skills else "general skills"

        prompt = f"""
You are an expert interviewer.

Generate 8-10 questions for a {role} role with skills in: {skills_text}.

Include:
- 3-4 technical questions
- 2-3 behavioral questions
- 2-3 situational questions

Mention what each question is assessing.
"""

        response = co.generate(
            model="command-r-plus",
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )

        return format_with_headings(response.generations[0].text, title="Interview Questions")

    except Exception as e:
        return f"""**Interview Questions Unavailable**

**Error:** {str(e)}

**Tip:** Visit job portals or use Glassdoor/Leetcode to find real-world interview questions for similar roles.
"""
