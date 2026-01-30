import string
import random
import re
from typing import List
from io import BytesIO


def generate_session_code(length: int = 8) -> str:
    """Generate a random session code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_token(length: int = 32) -> str:
    """Generate a random token"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF using pdfplumber"""
    try:
        import pdfplumber
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
                text += "\n"
            return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""


def generate_questions_from_text(text: str, num_questions: int = 10) -> List[str]:
    """
    Generate simple questions from extracted text.
    Strategy: split by newlines, create "Erkläre X" or "Was ist X" questions
    from non-empty segments.
    """
    questions = []
    
    # Split text into lines and filter empty ones
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # If text is very short, create generic questions
    if not lines:
        return [f"Frage {i+1}: Erklären Sie den Inhalt des Dokuments" for i in range(num_questions)]
    
    # Create questions from lines
    for i, line in enumerate(lines[:num_questions]):
        # Clean up line
        line = line[:100]  # limit length
        
        # Create various question templates
        question_type = i % 3
        if question_type == 0:
            questions.append(f"Erkläre: {line}")
        elif question_type == 1:
            questions.append(f"Was bedeutet: {line}?")
        else:
            questions.append(f"Nenne Informationen zu: {line}")
    
    # If we don't have enough questions, fill with generic ones
    while len(questions) < num_questions:
        questions.append(f"Frage {len(questions)+1}: Erklären Sie den Inhalt des Dokuments")
    
    return questions[:num_questions]
