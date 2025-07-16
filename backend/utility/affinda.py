import os
import requests
import json
from dotenv import load_dotenv
from pdfminer.high_level import extract_text
from unidecode import unidecode

# Load API key from .env file
load_dotenv()
AFFINDA_API_KEY = os.getenv("AFFINDA_API_KEY")


class Affinda:
    FILE_UPLOAD_URL = "https://api.affinda.com/v2/resumes"
    TEXT_PARSE_URL = "https://api.affinda.com/v2/resume_parsing_requests"

    @staticmethod
    def parse_resume(file_stream, filename="resume.pdf"):
        if not AFFINDA_API_KEY:
            return {
                "status": "error",
                "error": "Missing AFFINDA_API_KEY in .env file"
            }

        try:
            # Reset file stream position
            file_stream.seek(0)

            # Option 1: Send the actual PDF file
            headers = {
                "Authorization": f"Bearer {AFFINDA_API_KEY}",
            }

            files = {
                'file': (filename, file_stream, 'application/pdf')
            }

            response = requests.post(Affinda.FILE_UPLOAD_URL, headers=headers, files=files)

            # If file upload fails, try fallback method
            if response.status_code not in [200, 201]:
                print(f"⚠️ File upload failed ({response.status_code}), trying text fallback...")
                return Affinda._parse_with_text_fallback(file_stream)

            return Affinda._process_response(response)

        except Exception as e:
            print("💥 Affinda exception:", str(e))
            return {
                "status": "error",
                "error": f"Request to Affinda failed: {str(e)}"
            }

    @staticmethod
    def _parse_with_text_fallback(file_stream):
        """Fallback method using extracted text instead of PDF file"""
        try:
            # Extract text from PDF using pdfminer
            file_stream.seek(0)
            raw_text = extract_text(file_stream)

            # Clean Unicode issues
            clean_text = unidecode(raw_text)

            if not clean_text.strip():
                return {
                    "status": "error",
                    "error": "Extracted text is empty or unreadable. Possibly scanned or image-based PDF."
                }

            print("🧾 Cleaned Text Preview:\n", clean_text[:500])
            print("📄 Text length:", len(clean_text))

            headers = {
                "Authorization": f"Bearer {AFFINDA_API_KEY}",
                "Content-Type": "application/json"
            }

            json_payload = {
                "resume": {
                    "text": clean_text
                }
            }

            response = requests.post(Affinda.TEXT_PARSE_URL, headers=headers, json=json_payload)

            return Affinda._process_response(response)

        except Exception as e:
            print("💥 Text fallback exception:", str(e))
            return {
                "status": "error",
                "error": f"Text fallback failed: {str(e)}"
            }

    @staticmethod
    def _process_response(response):
        """Process the API response and extract resume data"""
        if response.status_code in [200, 201]:
            try:
                raw = response.json()
                data = raw.get("data")

                if not data or not isinstance(data, dict):
                    return {
                        "status": "error",
                        "error": f"Affinda API response missing or invalid: {raw}"
                    }

                # Extract fields with better error handling
                name_data = data.get("name", {})
                name = name_data.get("raw") if isinstance(name_data, dict) else str(name_data) if name_data else "Not found"

                emails = data.get("emails", [])
                email = emails[0] if emails else "Not found"

                phones = data.get("phoneNumbers", [])
                phone = phones[0] if phones else "Not found"

                skills = []
                for skill in data.get("skills", []):
                    if isinstance(skill, dict) and skill.get("name"):
                        skills.append(skill.get("name"))
                    elif isinstance(skill, str):
                        skills.append(skill)

                summary = data.get("summary") or ""

                education_entries = []
                for edu in data.get("education", []):
                    if not isinstance(edu, dict):
                        continue

                    degree = "Not specified"
                    accreditation = edu.get("accreditation")
                    if isinstance(accreditation, dict):
                        degree = accreditation.get("education") or "Not specified"

                    org = edu.get("organization") or "Unknown"
                    dates = edu.get("dates", {})
                    start = dates.get("startDate") if isinstance(dates, dict) else None
                    end = dates.get("completionDate") if isinstance(dates, dict) else None

                    grade = None
                    grade_data = edu.get("grade")
                    if isinstance(grade_data, dict):
                        grade = grade_data.get("value")

                    education_entries.append({
                        "degree": degree,
                        "organization": org,
                        "start_date": start,
                        "end_date": end,
                        "grade": grade
                    })

                return {
                    "status": "success",
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "skills": skills,
                    "summary": summary,
                    "education": education_entries,
                    "affinda_raw": data
                }

            except json.JSONDecodeError:
                return {
                    "status": "error",
                    "error": f"Invalid JSON response from Affinda: {response.text}"
                }
        else:
            print("❌ Affinda error response:", response.status_code, response.text)
            return {
                "status": "error",
                "error": f"Affinda API returned {response.status_code}: {response.text}"
            }


# Optional fallback function for text extraction only
def extract_text_fallback(file_stream):
    try:
        file_stream.seek(0)
        raw_text = extract_text(file_stream)
        clean_text = unidecode(raw_text)

        if not clean_text.strip():
            return {
                "status": "error",
                "error": "No text could be extracted from the PDF"
            }

        return {
            "status": "success",
            "text": clean_text,
            "length": len(clean_text)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Text extraction failed: {str(e)}"
        }
