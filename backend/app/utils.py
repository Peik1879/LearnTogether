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
    Extract questions from the text and generate similar ones.
    Strategy: 
    1. First, extract existing questions from the document
    2. Then generate contextual questions from content
    3. Combine both for variety
    """
    questions = []
    
    # Clean text and normalize whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    if not text or len(text) < 50:
        return [f"Frage {i+1}: Erklären Sie den Inhalt des Dokuments" for i in range(num_questions)]
    
    # ========================================================================
    # STEP 1: Extract existing questions from the document
    # ========================================================================
    extracted_questions = []
    
    # Pattern 1: Sentences ending with question mark
    question_pattern = r'([^.!?]*\?)'
    potential_questions = re.findall(question_pattern, text)
    
    for q in potential_questions:
        q = q.strip()
        # Filter out very short or very long questions
        if 10 < len(q) < 200:
            # Clean up numbering (e.g., "1.", "a)", etc.)
            q = re.sub(r'^\s*\d+[\.)]\s*', '', q)
            q = re.sub(r'^\s*[a-z][\.)]\s*', '', q, flags=re.IGNORECASE)
            q = q.strip()
            if q and q not in extracted_questions:
                extracted_questions.append(q)
    
    # Pattern 2: Common question starters (even without ?)
    question_starters = [
        r'(?:^|\n)\s*(?:Wie|Was|Warum|Wann|Wo|Welche|Welcher|Welches|Wer|Wozu|Womit|Wodurch)\s+[^.!?]{10,150}[.?]',
        r'(?:^|\n)\s*(?:Erklären Sie|Beschreiben Sie|Nennen Sie|Erläutern Sie|Definieren Sie)\s+[^.!?]{10,150}[.?]',
        r'(?:^|\n)\s*(?:Was versteht man unter|Was bedeutet|Was ist)\s+[^.!?]{10,150}[.?]',
    ]
    
    for pattern in question_starters:
        matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            q = match.strip()
            if q and q not in extracted_questions and len(q) > 15:
                # Clean up
                q = re.sub(r'^\s*\d+[\.)]\s*', '', q)
                q = re.sub(r'^\s*[a-z][\.)]\s*', '', q, flags=re.IGNORECASE)
                q = q.strip()
                if q:
                    extracted_questions.append(q)
    
    # Add extracted questions to our list
    questions.extend(extracted_questions[:num_questions])
    
    print(f"[QUESTIONS] Extracted {len(extracted_questions)} questions from document")
    
    # If we have enough questions, return them
    if len(questions) >= num_questions:
        return questions[:num_questions]
    
    # ========================================================================
    # STEP 2: Generate additional questions from content
    # ========================================================================
    
    # Identify potential key concepts (words that appear to be important)
    # Look for capitalized words (except sentence starts), technical terms
    potential_topics = []
    
    # Only generate additional questions if needed
    remaining_needed = num_questions - len(questions)
    if remaining_needed <= 0:
        return questions[:num_questions]
    
    print(f"[QUESTIONS] Need {remaining_needed} more questions, generating from content...")
    
    # Extract capitalized phrases (potential proper nouns, technical terms)
    capitalized_pattern = r'\b[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)*\b'
    for match in re.finditer(capitalized_pattern, text):
        word = match.group()
        # Skip common sentence starters
        if word not in ['Der', 'Die', 'Das', 'Ein', 'Eine', 'Im', 'In', 'Auf', 'Bei', 'Mit', 'Für']:
            if len(word) > 3 and word not in potential_topics:
                potential_topics.append(word)
    
    # Extract phrases after common patterns
    concept_patterns = [
        r'(?:wird bezeichnet als|ist|bedeutet|bezeichnet|definiert als)\s+([^.?!]{10,80})',
        r'(?:Unter|Begriff|Konzept von)\s+([A-ZÄÖÜ][a-zäöüß\s]{5,50})',
        r'(?:Verfahren|Methode|Prinzip|Ansatz)\s+(?:der|des|zur)\s+([^.?!]{10,60})'
    ]
    
    for pattern in concept_patterns:
        for match in re.finditer(pattern, text):
            concept = match.group(1).strip()
            if concept and len(concept) > 5:
                potential_topics.append(concept)
    
    # Question templates with more variety
    templates = [
        ("Erkläre das Konzept: {}", 0.2),
        ("Was versteht man unter {}?", 0.2),
        ("Beschreibe die Bedeutung von: {}", 0.15),
        ("Welche Rolle spielt {}?", 0.15),
        ("Wie funktioniert {}?", 0.15),
        ("Was sind die Hauptmerkmale von {}?", 0.15),
    ]
    
    # Generate questions from topics
    used_topics = set()
    for topic in potential_topics[:remaining_needed * 2]:
        if len(questions) >= num_questions:
            break
        
        # Avoid duplicates
        topic_lower = topic.lower()
        if topic_lower in used_topics:
            continue
        
        # Choose template based on weights
        template = random.choices(
            [t[0] for t in templates],
            weights=[t[1] for t in templates],
            k=1
        )[0]
        
        # Truncate if too long
        if len(topic) > 80:
            topic = topic[:77] + "..."
        
        questions.append(template.format(topic))
        used_topics.add(topic_lower)
    
    # Fill remaining with sentence-based questions
    sentence_templates = [
        "Erläutere folgenden Aspekt: {}",
        "Was wird mit folgendem gemeint: {}",
        "Erkläre den Zusammenhang: {}",
    ]
    
    for sentence in sentences:
        if len(questions) >= num_questions:
            break
        
        # Skip very short or very long sentences
        if len(sentence) < 30 or len(sentence) > 150:
            continue
        
        # Truncate and add
        snippet = sentence[:120]
        if len(sentence) > 120:
            snippet += "..."
        
        template = random.choice(sentence_templates)
        questions.append(template.format(snippet))
    
    # Fill remaining with paragraph-based questions
    for i, para in enumerate(paragraphs):
        if len(questions) >= num_questions:
            break
        
        snippet = para[:100]
        if len(para) > 100:
            snippet += "..."
        questions.append(f"Erkläre den Inhalt: {snippet}")
    
    # If still not enough, add generic questions
    while len(questions) < num_questions:
        questions.append(f"Erläutere einen weiteren wichtigen Aspekt des Themas")
    
    return questions[:num_questions]
