import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


def career_guidance_agent(parsed_resume: dict) -> str:
    """
    Generate AI-powered career guidance using Gemini AI.

    Args:
        parsed_resume (dict): Parsed resume data containing skills, experience, etc.

    Returns:
        str: AI-generated career guidance and suggestions.
    """
    try:
        # ✅ Correct Gemini model name
        model = genai.GenerativeModel('gemini-1.5-pro')

        # Extract fields safely
        name = parsed_resume.get('name', 'Candidate')
        skills = parsed_resume.get('skills', [])
        summary = parsed_resume.get('summary', '')
        work_experience = parsed_resume.get('work_experience', '')
        education = parsed_resume.get('education', [])
        certifications = parsed_resume.get('certifications', [])
        projects = parsed_resume.get('projects', [])

        skills_text = ', '.join(skills) if skills else 'No specific skills identified'
        cert_text = ', '.join(certifications) if certifications else 'No certifications listed'
        project_text = '; '.join(projects) if projects else 'No projects listed'

        education_text = []
        if education:
            for edu in education:
                if isinstance(edu, dict):
                    degree = edu.get('degree', '')
                    org = edu.get('organization', '')
                    year = edu.get('year', '')
                    education_text.append(f"{degree} from {org} ({year})")
                else:
                    education_text.append(str(edu))
        education_str = '; '.join(education_text) if education_text else 'No education information'

        prompt = f"""
You are an expert AI career advisor with knowledge of job market trends, skills demand, and career development.

Candidate Profile:
- Name: {name}
- Skills: {skills_text}
- Professional Summary: {summary}
- Work Experience: {work_experience}
- Education: {education_str}
- Certifications: {cert_text}
- Projects: {project_text}

Provide clear guidance with headings and bullet points on:

1️⃣ Career Paths (Suggest 2-3 realistic options based on profile)
2️⃣ Technical Skills to Learn (3-4 suggestions)
3️⃣ Soft Skills to Improve (2-3 suggestions)
4️⃣ Action Plan (What to improve in 30 days)
5️⃣ Market Insights (Demand, trends, location insights)
6️⃣ Personalized Tip (Networking, resume, portfolio)
"""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"""
⚠️ AI Career Guidance Unavailable

Error: {str(e)}

Temporary General Advice:
- Focus on strengthening your portfolio
- Update your resume with clear achievements
- Network on platforms like LinkedIn
- Obtain relevant certifications
- Build projects showcasing your core skills
"""


def get_industry_trends(skills: list) -> str:
    """
    Get industry trends based on candidate's skills.

    Args:
        skills (list): List of candidate's skills.

    Returns:
        str: Industry trends and insights.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')

        skills_text = ', '.join(skills) if skills else 'general technology'

        prompt = f"""
Analyze these skills: {skills_text}

Provide:
1️⃣ Market demand for these skills
2️⃣ Emerging trends in related industries
3️⃣ Future growth potential
4️⃣ Complementary skills worth learning

Keep it short, clear, and actionable.
"""
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"Industry trends analysis unavailable: {str(e)}"


def generate_interview_questions(role: str, skills: list) -> str:
    """
    Generate potential interview questions for a specific role.

    Args:
        role (str): Target job role.
        skills (list): Candidate's skills.

    Returns:
        str: Interview questions list.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')

        skills_text = ', '.join(skills) if skills else 'general skills'

        prompt = f"""
Generate 8-10 potential interview questions for a {role} role. The candidate has skills in: {skills_text}.

Include:
- 3-4 technical questions
- 2-3 behavioral questions
- 2-3 situational questions

Format as a numbered list. Briefly mention what the interviewer is assessing.
"""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"Interview questions generation unavailable: {str(e)}"
