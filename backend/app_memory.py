from flask import Flask, request, jsonify
from flask_cors import CORS
from suggester.suggestor import suggest_careers
from utility.affinda import Affinda
import io
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

def process_pdf_in_memory(file_stream):
    """Enhanced PDF processing with multiple extraction methods"""
    try:
        # Try multiple PDF extraction methods
        text = ""
        extraction_method = None
        
        # Method 1: Try pdfminer (more reliable)
        try:
            from pdfminer.high_level import extract_text
            file_stream.seek(0)
            text = extract_text(file_stream)
            extraction_method = "pdfminer"
        except ImportError:
            print("⚠️ pdfminer not available, trying PyPDF2...")
        except Exception as e:
            print(f"⚠️ pdfminer failed: {e}")
        
        # Method 2: Fallback to PyPDF2
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
        
        # Method 3: Try PyMuPDF if available
        if not text.strip():
            try:
                import fitz  # PyMuPDF
                file_stream.seek(0)
                doc = fitz.open(stream=file_stream.read(), filetype="pdf")
                
                for page in doc:
                    text += page.get_text()
                doc.close()
                extraction_method = "PyMuPDF"
            except ImportError:
                print("⚠️ PyMuPDF not available")
            except Exception as e:
                print(f"⚠️ PyMuPDF failed: {e}")
        
        if not text.strip():
            return {
                'status': 'error',
                'error': 'Could not extract text from PDF. File may be image-based or corrupted.'
            }
        
        # Clean up the text
        from unidecode import unidecode
        text = unidecode(text)
        
        # Parse the extracted text
        parsed_data = parse_resume_text(text)
        parsed_data['extraction_method'] = extraction_method
        parsed_data['text_preview'] = text[:500] + '...' if len(text) > 500 else text
        parsed_data['total_text_length'] = len(text)
        
        return parsed_data

    except Exception as e:
        return {
            'status': 'error',
            'error': f'PDF processing failed: {str(e)}'
        }

def parse_resume_text(text):
    """Enhanced text parsing with better extraction logic"""
    try:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Enhanced name detection
        name = extract_name(lines, text)
        
        # Enhanced contact info extraction
        email = extract_email(text)
        phone = extract_phone(text)
        
        # Enhanced skills extraction
        skills = extract_skills(text)
        
        # Extract sections
        sections = extract_sections(text)
        
        # Extract education with better parsing
        education = extract_education(text)
        
        # Extract work experience
        work_experience = extract_work_experience(text)
        
        # Generate career suggestions
        career_suggestions = suggest_careers({'skills': skills})
        
        return {
            'status': 'success',
            'name': name,
            'email': email,
            'phone': phone,
            'skills': skills,
            'education': education,
            'work_experience': work_experience,
            'sections': sections,
            'career_suggestions': career_suggestions
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Text parsing failed: {str(e)}'
        }

def extract_name(lines, text):
    """Improved name extraction logic"""
    # Look for name patterns at the beginning
    for i, line in enumerate(lines[:5]):  # Check first 5 lines
        line = line.strip()
        if not line:
            continue
            
        # Skip if line contains common non-name indicators
        skip_indicators = ['@', 'http', 'www', 'resume', 'cv', 'phone', 'email', 'address']
        if any(indicator in line.lower() for indicator in skip_indicators):
            continue
            
        # Skip if line is mostly numbers
        if sum(c.isdigit() for c in line) > len(line) * 0.3:
            continue
            
        # Skip if line is too long (likely a sentence)
        if len(line.split()) > 4:
            continue
            
        # Check if it looks like a name (2-4 words, mostly letters)
        words = line.split()
        if 2 <= len(words) <= 4 and all(word.isalpha() for word in words):
            return line
            
        # Single word that looks like a name
        if len(words) == 1 and words[0].isalpha() and len(words[0]) > 2:
            # Check if next line might be last name
            if i + 1 < len(lines) and lines[i + 1].strip().isalpha():
                return f"{line} {lines[i + 1].strip()}"
            return line
    
    return "Not found"

def extract_email(text):
    """Enhanced email extraction"""
    email_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}\b'
    ]
    
    for pattern in email_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group().replace(' ', '')
    
    return "Not found"

def extract_phone(text):
    """Enhanced phone extraction for multiple formats"""
    phone_patterns = [
        r'(\+91|91)?\s*[6-9]\d{9}',  # Indian mobile
        r'\(\d{3}\)\s*\d{3}-\d{4}',  # US format
        r'\d{3}-\d{3}-\d{4}',        # US format
        r'\+\d{1,3}\s*\d{10}',       # International
        r'\d{10}'                    # 10 digits
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group().strip()
    
    return "Not found"

def extract_skills(text):
    """Enhanced skills extraction with categories"""
    skill_categories = {
        'programming': [
            'python', 'java', 'javascript', 'js', 'c++', 'c#', 'c', 'php', 'ruby', 'go', 'rust',
            'swift', 'kotlin', 'scala', 'r', 'matlab', 'typescript', 'dart', 'perl'
        ],
        'web': [
            'html', 'css', 'react', 'angular', 'vue', 'node', 'express', 'django', 'flask',
            'spring', 'laravel', 'bootstrap', 'jquery', 'sass', 'less', 'webpack'
        ],
        'database': [
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite', 'nosql',
            'cassandra', 'dynamodb', 'neo4j'
        ],
        'tools': [
            'git', 'github', 'gitlab', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure',
            'gcp', 'linux', 'jira', 'confluence', 'slack', 'trello'
        ],
        'data_science': [
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'matplotlib',
            'seaborn', 'plotly', 'jupyter', 'anaconda', 'spark', 'hadoop', 'tableau', 'power bi'
        ],
        'soft_skills': [
            'leadership', 'teamwork', 'communication', 'project management', 'agile', 'scrum',
            'problem solving', 'analytical thinking', 'creative thinking', 'time management'
        ]
    }
    
    found_skills = []
    lower_text = text.lower()
    
    # Extract skills with better matching
    for category, skills in skill_categories.items():
        for skill in skills:
            # Use word boundaries for better matching
            if re.search(r'\b' + re.escape(skill) + r'\b', lower_text):
                found_skills.append(skill.title())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in found_skills:
        if skill.lower() not in seen:
            seen.add(skill.lower())
            unique_skills.append(skill)
    
    return unique_skills

def extract_sections(text):
    """Extract various sections from resume"""
    sections = {}
    
    section_patterns = {
        'summary': r'\b(summary|profile|objective|about)\b',
        'education': r'\b(education|academic|qualification)\b',
        'experience': r'\b(experience|work|employment|professional)\b',
        'projects': r'\b(projects?|portfolio)\b',
        'certifications': r'\b(certifications?|certificates?)\b',
        'achievements': r'\b(achievements?|awards?|honors?)\b',
        'skills': r'\b(skills?|technical|competencies)\b'
    }
    
    for section_name, pattern in section_patterns.items():
        section_content = extract_section_content(text, pattern)
        if section_content:
            sections[section_name] = section_content
    
    return sections

def extract_section_content(text, pattern):
    """Extract content of a specific section"""
    lines = text.split('\n')
    section_start = None
    
    for i, line in enumerate(lines):
        if re.search(pattern, line, re.IGNORECASE):
            section_start = i
            break
    
    if section_start is None:
        return None
    
    # Find the end of the section
    section_end = len(lines)
    common_headers = [
        'education', 'experience', 'skills', 'projects', 'certifications',
        'achievements', 'summary', 'objective', 'contact', 'references'
    ]
    
    for i in range(section_start + 1, len(lines)):
        line = lines[i].strip().lower()
        if any(header in line for header in common_headers) and len(line) < 50:
            section_end = i
            break
    
    content = '\n'.join(lines[section_start:section_end]).strip()
    return content if len(content) > 10 else None

def extract_education(text):
    """Extract education information"""
    education_entries = []
    
    # Look for degree patterns
    degree_patterns = [
        r'\b(bachelor|master|phd|doctorate|diploma|certificate|b\.?tech|m\.?tech|b\.?sc|m\.?sc|b\.?com|m\.?com|mba|bba)\b',
        r'\b(engineering|computer science|information technology|business|management|arts|science)\b'
    ]
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in degree_patterns):
            # Try to extract year
            year_match = re.search(r'\b(19|20)\d{2}\b', line)
            year = year_match.group() if year_match else None
            
            education_entries.append({
                'degree': line,
                'year': year,
                'institution': 'Unknown'
            })
    
    return education_entries

def extract_work_experience(text):
    """Extract work experience"""
    experience_entries = []
    
    # Look for job title patterns
    job_indicators = [
        'developer', 'engineer', 'manager', 'analyst', 'consultant', 'intern',
        'lead', 'senior', 'junior', 'associate', 'specialist', 'coordinator'
    ]
    
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if any(indicator in line.lower() for indicator in job_indicators):
            # Try to extract dates
            date_match = re.search(r'\b(19|20)\d{2}\b', line)
            year = date_match.group() if date_match else None
            
            experience_entries.append({
                'title': line,
                'year': year,
                'company': 'Unknown'
            })
    
    return experience_entries

@app.route('/')
def home():
    return jsonify({
        'message': '🚀 Resume Analyzer API is running!',
        'status': 'success',
        'version': '2.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        print("🔍 Starting resume analysis...")

        if 'resume' not in request.files:
            print("❌ No file uploaded")
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['resume']
        if file.filename == '':
            print("❌ No file selected")
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            print("❌ Invalid file type")
            return jsonify({'error': 'Please upload a PDF file'}), 400

        # Try Affinda first
        print("📡 Attempting Affinda parsing...")
        try:
            affinda_result = Affinda.parse_resume(file.stream, file.filename)
            
            if affinda_result['status'] == 'success':
                print("✅ Affinda parsing successful")
                affinda_result['career_suggestions'] = suggest_careers({
                    'skills': affinda_result.get('skills', [])
                })
                affinda_result['source'] = 'affinda'
                return jsonify(affinda_result)
            else:
                print(f"❌ Affinda failed: {affinda_result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Affinda exception: {str(e)}")

        # Fallback to local processing
        print("⚠️ Affinda failed. Using enhanced fallback...")
        file.stream.seek(0)
        fallback_result = process_pdf_in_memory(file.stream)
        
        if fallback_result['status'] == 'success':
            fallback_result['source'] = 'fallback'
            fallback_result['note'] = 'Processed using local parser (Affinda unavailable)'
            print("✅ Fallback parsing successful")
        else:
            print(f"❌ Fallback failed: {fallback_result.get('error', 'Unknown error')}")
        
        return jsonify(fallback_result)

    except Exception as e:
        print(f"💥 Critical exception: {str(e)}")
        return jsonify({
            'error': 'Processing failed',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'resume-analyzer'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')