#!/usr/bin/env python3
"""
StudyDuel - API Testing Script

Führt grundlegende API-Tests durch.
Usage: python test_api.py
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

class Colors:
    OK = "\033[92m"
    FAIL = "\033[91m"
    INFO = "\033[94m"
    END = "\033[0m"

def test_header(name: str):
    print(f"\n{Colors.INFO}{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}{Colors.END}\n")

def success(msg: str):
    print(f"{Colors.OK}✓ {msg}{Colors.END}")

def fail(msg: str):
    print(f"{Colors.FAIL}✗ {msg}{Colors.END}")

def info(msg: str):
    print(f"{Colors.INFO}ℹ {msg}{Colors.END}")

def test_create_session():
    test_header("Create Session")
    
    response = requests.post(f"{BASE_URL}/session", headers=HEADERS)
    
    if response.status_code != 200:
        fail(f"Expected 200, got {response.status_code}")
        return None
    
    data = response.json()
    
    if "session_id" not in data or "examiner_token" not in data:
        fail("Response missing required fields")
        return None
    
    success(f"Session created: {data['session_id']}")
    info(f"Examiner Token: {data['examiner_token'][:10]}...")
    
    return data

def test_join_session(session_id: str, role: str):
    test_header(f"Join Session as {role.upper()}")
    
    payload = {"role": role}
    response = requests.post(
        f"{BASE_URL}/session/{session_id}/join",
        json=payload,
        headers=HEADERS
    )
    
    if response.status_code != 200:
        fail(f"Expected 200, got {response.status_code}: {response.json()}")
        return None
    
    data = response.json()
    
    if "token" not in data or "role" not in data:
        fail("Response missing required fields")
        return None
    
    success(f"Joined as {role}")
    info(f"Token: {data['token'][:10]}...")
    
    return data["token"]

def test_get_questions(session_id: str, token: str):
    test_header("Get Questions (Examiner)")
    
    headers = {**HEADERS, "X-Token": token}
    response = requests.get(
        f"{BASE_URL}/session/{session_id}/questions",
        headers=headers
    )
    
    if response.status_code != 200:
        fail(f"Expected 200, got {response.status_code}: {response.json()}")
        return None
    
    data = response.json()
    
    if "questions" not in data:
        fail("Response missing 'questions' field")
        return None
    
    success(f"Retrieved {len(data['questions'])} questions")
    for i, q in enumerate(data['questions'][:3]):
        info(f"  Q{i+1}: {q[:50]}...")
    
    return data

def test_role_denied(session_id: str, learner_token: str):
    test_header("Role Permission Denied (Learner)")
    
    headers = {**HEADERS, "X-Token": learner_token}
    response = requests.get(
        f"{BASE_URL}/session/{session_id}/questions",
        headers=headers
    )
    
    if response.status_code == 403:
        success("Learner correctly denied access to question list")
        return True
    else:
        fail(f"Expected 403, got {response.status_code}")
        return False

def test_missing_token(session_id: str):
    test_header("Missing X-Token Header")
    
    response = requests.get(
        f"{BASE_URL}/session/{session_id}/questions",
        headers=HEADERS
    )
    
    if response.status_code == 401:
        success("Request correctly rejected without token")
        return True
    else:
        fail(f"Expected 401, got {response.status_code}")
        return False

def test_invalid_session():
    test_header("Invalid Session ID")
    
    headers = {**HEADERS, "X-Token": "any-token"}
    response = requests.get(
        f"{BASE_URL}/session/INVALID99/questions",
        headers=headers
    )
    
    if response.status_code == 404:
        success("Invalid session correctly rejected")
        return True
    else:
        fail(f"Expected 404, got {response.status_code}")
        return False

def test_reveal_question(session_id: str, examiner_token: str):
    test_header("Reveal Question")
    
    headers = {**HEADERS, "X-Token": examiner_token}
    response = requests.post(
        f"{BASE_URL}/session/{session_id}/reveal",
        json={},
        headers=headers
    )
    
    if response.status_code != 200:
        fail(f"Expected 200, got {response.status_code}: {response.json()}")
        return False
    
    success("Question revealed")
    return True

def test_grade_question(session_id: str, examiner_token: str, index: int, status: str):
    test_header(f"Grade Question (status={status})")
    
    headers = {**HEADERS, "X-Token": examiner_token}
    payload = {"index": index, "status": status}
    response = requests.post(
        f"{BASE_URL}/session/{session_id}/grade",
        json=payload,
        headers=headers
    )
    
    if response.status_code != 200:
        fail(f"Expected 200, got {response.status_code}: {response.json()}")
        return False
    
    success(f"Question {index} graded as '{status}'")
    return True

def test_next_question(session_id: str, examiner_token: str):
    test_header("Move to Next Question")
    
    headers = {**HEADERS, "X-Token": examiner_token}
    response = requests.post(
        f"{BASE_URL}/session/{session_id}/next",
        json={},
        headers=headers
    )
    
    if response.status_code != 200:
        fail(f"Expected 200, got {response.status_code}: {response.json()}")
        return False
    
    success("Moved to next question")
    return True

def test_learner_current(session_id: str, learner_token: str):
    test_header("Get Current Question (Learner)")
    
    headers = {**HEADERS, "X-Token": learner_token}
    response = requests.get(
        f"{BASE_URL}/session/{session_id}/current",
        headers=headers
    )
    
    if response.status_code != 200:
        fail(f"Expected 200, got {response.status_code}: {response.json()}")
        return None
    
    data = response.json()
    status = data.get("status")
    
    if status == "locked":
        success("Learner sees locked status (question not revealed)")
    elif status == "revealed":
        success(f"Learner sees revealed question: {data.get('question', '')[:50]}...")
    else:
        success(f"Learner status: {status}")
    
    return data

def run_all_tests():
    print(f"\n{Colors.INFO}╔════════════════════════════════════════════════════════════╗")
    print(f"║           StudyDuel - API Test Suite                      ║")
    print(f"╚════════════════════════════════════════════════════════════╝{Colors.END}")
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        success("Backend is running")
    except requests.exceptions.ConnectionError:
        fail("Backend not running on http://localhost:8000")
        fail("Start backend with: uvicorn app.main:app --reload --port 8000")
        return
    
    # Test 1: Create session
    session_data = test_create_session()
    if not session_data:
        return
    
    session_id = session_data["session_id"]
    examiner_token = session_data["examiner_token"]
    
    # Test 2: Join as learner
    learner_token = test_join_session(session_id, "learner")
    
    # Test 3: Security tests
    test_role_denied(session_id, learner_token)
    test_missing_token(session_id)
    test_invalid_session()
    
    # Test 4: Get questions (examiner)
    questions_data = test_get_questions(session_id, examiner_token)
    
    # Test 5: Learner sees locked question
    test_learner_current(session_id, learner_token)
    
    # Test 6: Reveal question
    test_reveal_question(session_id, examiner_token)
    
    # Test 7: Learner sees revealed question
    test_learner_current(session_id, learner_token)
    
    # Test 8: Grade question
    test_grade_question(session_id, examiner_token, 0, "ok")
    
    # Test 9: Move to next
    test_next_question(session_id, examiner_token)
    
    # Test 10: Final questions check
    test_get_questions(session_id, examiner_token)
    
    print(f"\n{Colors.INFO}{'='*60}")
    print(f"All tests completed!")
    print(f"{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.FAIL}Tests interrupted{Colors.END}")
    except Exception as e:
        print(f"{Colors.FAIL}Test failed with error: {e}{Colors.END}")
