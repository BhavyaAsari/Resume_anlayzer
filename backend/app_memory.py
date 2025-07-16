from flask import Flask, request, jsonify
from flask_cors import CORS
from suggester.suggestor import suggest_careers
from utility.affinda import Affinda
from utility.ai_agent import career_guidance_agent
import io
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# -----------------------------
# PDF Processing Logic (fallback)
# -----------------------------

def process_pdf_in_memory(file_stream):
    try:
        text = ""
        extraction_method = None

        # Try pdfminer
        try:
            from pdfminer.high_level import extract_text
            file_stream.seek(0)
            text = extract_text(file_stream)
            extraction_method = "pdfminer"
        except Exception as e:
            print(f"⚠️ pdfminer failed: {e}")

        # Fallback: PyPDF2
        if not text.strip():
            try:
                import PyPDF2
                file_stream.seek(0)
                reader = PyPDF2.PdfReader(file_stream)
                for page in reader.pages:
                    text += page.extract_text() or ""
                extraction_method = "PyPDF2"
            except Exception as e:
                print(f"⚠️ PyPDF2 failed: {e}")

        # Fallback: PyMuPDF
        if not text.strip():
            try:
                import fitz  # PyMuPDF
                file_stream.seek(0)
                doc = fitz.open(stream=file_stream.read(), filetype="pdf")
                for page in doc:
                    text += page.get_text()
                doc.close()
                extraction_method = "PyMuPDF"
            except Exception as e:
                print(f"⚠️ PyMuPDF failed: {e}")

        if not text.strip():
            return {'status': 'error', 'error': 'Unable to extract text from PDF.'}

        from unidecode import unidecode
        text = unidecode(text)

        parsed_data = parse_resume_text(text)
        parsed_data['extraction_method'] = extraction_method
        parsed_data['text_preview'] = text[:500] + '...' if len(text) > 500 else text
        parsed_data['total_text_length'] = len(text)

        return parsed_data

    except Exception as e:
        return {'status': 'error', 'error': f'PDF processing failed: {str(e)}'}

# -----------------------------
# Resume Parsing Logic
# -----------------------------

def parse_resume_text(text):
    """Parse resume text and extract structured information"""
    try:
        result = {
            'status': 'success',
            'name': extract_name(text),
            'email': extract_email(text),
            'phone': extract_phone(text),
            'skills': extract_skills(text),
            'education': extract_education(text),
            'work_experience': extract_work_experience(text),
            'sections': extract_sections(text),
            'summary': extract_summary(text),
            'certifications': extract_certifications(text),
            'projects': extract_projects(text)
        }
        return result
    except Exception as e:
        return {'status': 'error', 'error': f'Parsing failed: {str(e)}'}

def extract_name(text):
    """Extract name from resume text"""
    lines = text.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line and len(line.split()) <= 4 and not re.search(r'[@\d]', line):
            # Simple heuristic: likely a name if short, no email/numbers
            return line
    return "Name not found"

def extract_email(text):
    """Extract email from resume text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else "Email not found"

def extract_phone(text):
    """Extract phone number from resume text"""
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',
        r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            return phones[0]
    return "Phone not found"

def extract_skills(text):
    """Extract skills from resume text"""
    # Common technical skills keywords
    tech_skills = [
        'python', 'java', 'javascript', 'react', 'node.js', 'html', 'css',
        'sql', 'mongodb', 'postgresql', 'git', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'machine learning', 'data science',
        'angular', 'vue.js', 'spring', 'django', 'flask', 'express'
    ]
    
    # Common soft skills
    soft_skills = [
        'communication', 'teamwork', 'leadership', 'problem-solving',
        'adaptability', 'time management', 'critical thinking',
        'project management', 'analytical thinking'
    ]
    
    all_skills = tech_skills + soft_skills
    found_skills = []
    
    text_lower = text.lower()
    for skill in all_skills:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    return list(set(found_skills))  # Remove duplicates

def extract_education(text):
    """Extract education information"""
    education_patterns = [
        r'(bachelor|master|phd|doctorate|diploma|certificate).*?(\d{4})',
        r'(b\.?s\.?|m\.?s\.?|b\.?a\.?|m\.?a\.?|phd).*?(\d{4})'
    ]
    
    education = []
    for pattern in education_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            education.append({
                'degree': match[0],
                'year': match[1],
                'organization': 'University/College',
                'grade': 'N/A'
            })
    
    return education

def extract_work_experience(text):
    """Extract work experience"""
    # Look for years that might indicate work experience
    year_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'
    experiences = re.findall(year_pattern, text, re.IGNORECASE)
    
    if experiences:
        return f"Found {len(experiences)} work experience entries"
    return "No work experience found"

def extract_sections(text):
    """Extract different sections from resume"""
    sections = {}
    
    # Look for common section headers
    section_patterns = {
        'projects': r'projects?:?\s*(.*?)(?=\n\n|\n[A-Z]|$)',
        'certifications': r'certifications?:?\s*(.*?)(?=\n\n|\n[A-Z]|$)',
        'achievements': r'achievements?:?\s*(.*?)(?=\n\n|\n[A-Z]|$)',
        'interests': r'interests?:?\s*(.*?)(?=\n\n|\n[A-Z]|$)'
    }
    
    for section, pattern in section_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        sections[section] = matches[0].strip() if matches else ""
    
    return sections

def extract_summary(text):
    """Extract professional summary"""
    summary_patterns = [
        r'summary:?\s*(.*?)(?=\n\n|\n[A-Z]|$)',
        r'objective:?\s*(.*?)(?=\n\n|\n[A-Z]|$)',
        r'profile:?\s*(.*?)(?=\n\n|\n[A-Z]|$)'
    ]
    
    for pattern in summary_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            return matches[0].strip()
    
    # If no explicit summary, return first few lines
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if len(line.strip()) > 50:  # Substantial line
            return line.strip()
    
    return "No summary available"

def extract_certifications(text):
    """Extract certifications"""
    cert_keywords = ['certified', 'certification', 'certificate', 'aws', 'azure', 'google cloud']
    certifications = []
    
    lines = text.split('\n')
    for line in lines:
        line_lower = line.lower()
        for keyword in cert_keywords:
            if keyword in line_lower:
                certifications.append(line.strip())
                break
    
    return certifications

def extract_projects(text):
    """Extract project information"""
    project_patterns = [
        r'projects?:?\s*(.*?)(?=education|experience|skills|$)',
        r'project\s+\d+:?\s*(.*?)(?=project|\n\n|$)'
    ]
    
    projects = []
    for pattern in project_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if match.strip():
                projects.append(match.strip())
    
    return projects

# -----------------------------
# Flask Routes
# -----------------------------

@app.route('/')
def home():
    return jsonify({
        'message': '🚀 Resume Analyzer API is running!',
        'status': 'success',
        'version': '2.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'resume-analyzer'
    })

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        print("🔍 Starting resume analysis...")

        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Please upload a PDF file'}), 400

        # ✅ Try Affinda first
        print("📡 Attempting Affinda parsing...")
        try:
            affinda_result = Affinda.parse_resume(file.stream, file.filename)
            if affinda_result['status'] == 'success':
                # Add career suggestions
                affinda_result['career_suggestions'] = suggest_careers({
                    'skills': affinda_result.get('skills', [])
                })
                
                # Add AI agent career guidance
                print("🧠 Generating AI career advice with Gemini...")
                affinda_result["ai_agent_career_advice"] = career_guidance_agent(affinda_result)
                
                affinda_result['source'] = 'affinda'
                return jsonify(affinda_result)
            else:
                print(f"❌ Affinda failed: {affinda_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Affinda exception: {str(e)}")

        # 🔁 Fallback parser
        print("⚠️ Affinda failed. Using enhanced fallback...")
        file.stream.seek(0)
        fallback_result = process_pdf_in_memory(file.stream)

        if fallback_result['status'] == 'success':
            fallback_result['source'] = 'fallback'
            fallback_result['note'] = 'Processed using local parser (Affinda unavailable)'

            # Add career suggestions
            fallback_result['career_suggestions'] = suggest_careers({
                'skills': fallback_result.get('skills', [])
            })

            # ✅ Inject AI agent career guidance using Gemini
            print("🧠 Generating AI career advice with Gemini...")
            fallback_result["ai_agent_career_advice"] = career_guidance_agent(fallback_result)

            print("✅ Fallback parsing successful with AI agent advice")
        else:
            print(f"❌ Fallback failed: {fallback_result.get('error')}")

        return jsonify(fallback_result)

    except Exception as e:
        print(f"💥 Critical exception: {str(e)}")
        return jsonify({
            'error': 'Processing failed',
            'message': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')