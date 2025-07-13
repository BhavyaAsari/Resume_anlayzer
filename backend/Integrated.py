import io
import tempfile
import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Try to import the ResumeParser - handle if it doesn't exist
try:
    from resume_parser import ResumeParser
    ADVANCED_PARSER_AVAILABLE = True
except ImportError:
    print("⚠️  ResumeParser not found. Using basic extraction only.")
    ADVANCED_PARSER_AVAILABLE = False

# Try to import career suggester
try:
    from suggester.suggestor import suggest_careers
    CAREER_SUGGESTER_AVAILABLE = True
except ImportError:
    print("⚠️  Career suggester not found. Suggestions disabled.")
    CAREER_SUGGESTER_AVAILABLE = False

app = Flask(__name__)

def process_resume_with_parser(file_stream, filename):
    """
    Enhanced resume processing using the ResumeParser class
    """
    # Check if advanced parser is available
    if not ADVANCED_PARSER_AVAILABLE:
        print("Advanced parser not available, using basic extraction")
        return fallback_basic_extraction(file_stream, filename)
    
    try:
        # Create a temporary file to work with the ResumeParser
        # since it expects a file path or BytesIO with proper name attribute
        file_stream.seek(0)
        
        # Create a BytesIO object with the filename attribute
        resume_file = io.BytesIO(file_stream.read())
        resume_file.name = filename
        
        # Initialize the ResumeParser
        parser = ResumeParser(resume_file)
        
        # Extract data using the sophisticated parser
        extracted_data = parser.get_extracted_data()
        
        # Get career suggestions based on extracted skills
        career_suggestions = []
        if extracted_data.get('skills') and CAREER_SUGGESTER_AVAILABLE:
            career_suggestions = suggest_careers({'skills': extracted_data['skills']})
        
        # Format the response
        result = {
            'status': 'success',
            'name': extracted_data.get('name', 'Not found'),
            'email': extracted_data.get('email', 'Not found'),
            'phone': extracted_data.get('mobile_number', 'Not found'),
            'skills': extracted_data.get('skills', []),
            'education': {
                'college_name': extracted_data.get('college_name', 'Not found'),
                'degree': extracted_data.get('degree', 'Not found')
            },
            'experience': {
                'designation': extracted_data.get('designation', 'Not found'),
                'company_names': extracted_data.get('company_names', []),
                'total_experience': extracted_data.get('total_experience', 0),
                'experience_details': extracted_data.get('experience', [])
            },
            'document_info': {
                'no_of_pages': extracted_data.get('no_of_pages', 'Not found')
            },
            'career_suggestions': career_suggestions,
            'extraction_method': 'Advanced NLP Parser'
        }
        
        return result
        
    except Exception as e:
        # Fallback to basic extraction if advanced parser fails
        print(f"Advanced parser failed: {e}")
        return fallback_basic_extraction(file_stream, filename)

def fallback_basic_extraction(file_stream, filename):
    """
    Fallback to basic PDF extraction if the advanced parser fails
    """
    try:
        import PyPDF2
        
        file_stream.seek(0)
        reader = PyPDF2.PdfReader(file_stream)
        
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # Basic skill extraction
        skills = []
        skill_keywords = ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node', 'git',
                         'machine learning', 'data science', 'ai', 'tensorflow', 'pytorch', 'docker',
                         'kubernetes', 'aws', 'azure', 'mongodb', 'postgresql', 'spring', 'django',
                         'flask', 'angular', 'vue', 'c++', 'c#', 'scala', 'kotlin', 'swift']
        
        text_lower = text.lower()
        for skill in skill_keywords:
            if skill in text_lower:
                skills.append(skill.title())
        
        # Basic name extraction (first non-empty line)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        name = lines[0] if lines else "Not found"
        
        # Basic email extraction
        email = "Not found"
        phone = "Not found"
        
        import re
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_matches = re.findall(email_pattern, text)
        if email_matches:
            email = email_matches[0]
        
        # Phone pattern
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_matches = re.findall(phone_pattern, text)
        if phone_matches:
            phone = ''.join(phone_matches[0]) if isinstance(phone_matches[0], tuple) else phone_matches[0]
        
        return {
            'status': 'success',
            'name': name,
            'email': email,
            'phone': phone,
            'skills': skills,
            'education': {
                'college_name': 'Not found',
                'degree': 'Not found'
            },
            'experience': {
                'designation': 'Not found',
                'company_names': [],
                'total_experience': 0,
                'experience_details': []
            },
            'document_info': {
                'no_of_pages': len(reader.pages)
            },
            'career_suggestions': suggest_careers({'skills': skills}) if CAREER_SUGGESTER_AVAILABLE else [],
            'text_preview': text[:300] + '...' if len(text) > 300 else text,
            'total_text_length': len(text),
            'extraction_method': 'Basic PDF Parser (Fallback)'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'extraction_method': 'Failed'
        }

@app.route('/')
def home():
    return jsonify({
        'message': '🚀 Enhanced Resume Analyzer API with Advanced NLP is running!',
        'status': 'success',
        'features': [
            'Advanced NLP-based extraction using spaCy' if ADVANCED_PARSER_AVAILABLE else 'Basic extraction (Advanced parser not available)',
            'Name, email, phone extraction',
            'Skills identification',
            'Education details (college, degree)' if ADVANCED_PARSER_AVAILABLE else 'Basic education extraction',
            'Experience analysis (designation, companies, years)' if ADVANCED_PARSER_AVAILABLE else 'Basic experience extraction',
            'Career suggestions' if CAREER_SUGGESTER_AVAILABLE else 'Career suggestions (disabled)',
            'Fallback to basic extraction if needed'
        ],
        'modules': {
            'advanced_parser': ADVANCED_PARSER_AVAILABLE,
            'career_suggester': CAREER_SUGGESTER_AVAILABLE
        }
    })

@app.route('/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Support multiple file formats
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            return jsonify({
                'error': f'Unsupported file format. Please upload: {", ".join(allowed_extensions)}'
            }), 400
        
        # Process the resume using the enhanced parser
        result = process_resume_with_parser(file.stream, file.filename)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'error': 'Processing failed',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test if spaCy models are loaded
        import spacy
        nlp = spacy.load('en_core_web_sm')
        
        return jsonify({
            'status': 'healthy',
            'spacy_model': 'en_core_web_sm loaded',
            'timestamp': str(app.config.get('SERVER_START_TIME', 'Unknown'))
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/supported-formats', methods=['GET'])
def supported_formats():
    """Return supported file formats"""
    return jsonify({
        'supported_formats': [
            {
                'extension': '.pdf',
                'description': 'Portable Document Format'
            },
            {
                'extension': '.docx',
                'description': 'Microsoft Word Document'
            },
            {
                'extension': '.doc',
                'description': 'Microsoft Word Document (Legacy)'
            },
            {
                'extension': '.txt',
                'description': 'Plain Text File'
            }
        ]
    })

if __name__ == '__main__':
    # Store server start time for health checks
    from datetime import datetime
    app.config['SERVER_START_TIME'] = datetime.now()
    
    print("🔧 Starting Enhanced Resume Analyzer API...")
    print("📋 Features: Advanced NLP extraction, Multiple file formats, Career suggestions")
    print("🌐 Access: http://localhost:5000")
    
    app.run(debug=True, port=5000)