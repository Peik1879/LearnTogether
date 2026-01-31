import React, { useState, useEffect } from 'react';
import { sessionAPI, QuestionsResponse } from '../services/api';
import '../styles/App.css';

type View = 'landing' | 'learner' | 'examiner';

interface ExaminerPageProps {
  sessionId: string;
  token: string;
  onNavigate: (view: View, data?: any) => void;
}

export const ExaminerPage: React.FC<ExaminerPageProps> = ({ sessionId, token, onNavigate }) => {
  const [session, setSession] = useState<QuestionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadSession();
    const interval = setInterval(loadSession, 1000);
    return () => clearInterval(interval);
  }, []);

  const loadSession = async () => {
    try {
      const data = await sessionAPI.getAllQuestions(sessionId, token);
      setSession(data);
      setLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load session');
      setLoading(false);
    }
  };

  const handleReveal = async () => {
    setActionLoading(true);
    try {
      await sessionAPI.revealQuestion(sessionId, token);
      await loadSession();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reveal question');
    } finally {
      setActionLoading(false);
    }
  };

  const handleGrade = async (status: 'ok' | 'meh' | 'fail') => {
    setActionLoading(true);
    try {
      await sessionAPI.gradeQuestion(sessionId, session!.current_index, status, token);
      await loadSession();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to grade question');
    } finally {
      setActionLoading(false);
    }
  };

  const handleNext = async () => {
    setActionLoading(true);
    try {
      await sessionAPI.nextQuestion(sessionId, token);
      await loadSession();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'No more questions or failed to move to next');
    } finally {
      setActionLoading(false);
    }
  };

  const handleLogout = () => {
    onNavigate('landing');
  };

  const handleQuestionClick = async (index: number) => {
    // Jump to a specific question
    setActionLoading(true);
    setError('');
    try {
      await sessionAPI.jumpToQuestion(sessionId, index, token);
      await loadSession();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Konnte nicht zu Frage springen');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="card">
          <div className="spinner"></div>
          <p>Session wird geladen...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="container">
        <div className="card">
          <h2>Session nicht gefunden</h2>
          <button onClick={() => onNavigate('landing')} className="btn btn-primary">
            Zurück
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = session.questions[session.current_index];
  const isAtEnd = session.current_index >= session.questions.length - 1;

  return (
    <div className="container">
      <div className="card">
        <div className="header">
          <h1>LearnTogether - Examiner</h1>
          <div className="session-info">
            <span>Session: <code>{sessionId}</code></span>
            <button onClick={handleLogout} className="btn btn-small">Logout</button>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        <div className="examiner-container">
          {/* Current Question Section */}
          <div className="current-question-box">
            <h2>Aktuelle Frage</h2>
            <div className="progress-text">
              Frage {session.current_index + 1} von {session.questions.length}
            </div>

            <div className="question-preview">
              <p>{currentQuestion}</p>
            </div>

            <div className="status-info">
              {session.revealed ? (
                <span className="status-revealed">✓ Freigebbar</span>
              ) : (
                <span className="status-locked">🔒 Gesperrt</span>
              )}
            </div>

            <div className="controls">
              {!session.revealed ? (
                <button
                  onClick={handleReveal}
                  disabled={actionLoading}
                  className="btn btn-primary btn-large"
                >
                  {actionLoading ? 'Wird freigegeben...' : 'Frage freigeben (Reveal)'}
                </button>
              ) : (
                <>
                  <div className="grade-buttons">
                    <button
                      onClick={() => handleGrade('ok')}
                      disabled={actionLoading}
                      className="btn btn-success"
                    >
                      ✓ OK
                    </button>
                    <button
                      onClick={() => handleGrade('meh')}
                      disabled={actionLoading}
                      className="btn btn-warning"
                    >
                      ~ MEH
                    </button>
                    <button
                      onClick={() => handleGrade('fail')}
                      disabled={actionLoading}
                      className="btn btn-danger"
                    >
                      ✗ FAIL
                    </button>
                  </div>

                  <button
                    onClick={handleNext}
                    disabled={actionLoading || isAtEnd}
                    className="btn btn-primary btn-large"
                  >
                    {isAtEnd ? 'Keine weiteren Fragen' : 'Weiter zur nächsten Frage'}
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Questions List */}
          <div className="questions-list-box">
            <h3>Fragenliste ({session.questions.length})</h3>
            <ul className="questions-list">
              {session.questions.map((q, idx) => (
                <li
                  key={idx}
                  className={`question-item ${idx === session.current_index ? 'current' : ''} ${session.grades[idx] ? 'graded-' + session.grades[idx] : ''}`}
                  onClick={() => handleQuestionClick(idx)}
                  style={{ cursor: 'pointer' }}
                  title="Klicken um zu dieser Frage zu springen"
                >
                  <span className="question-index">{idx + 1}</span>
                  <span className="question-text">{q}</span>
                  {session.grades[idx] && (
                    <span className="grade-badge">{session.grades[idx].toUpperCase()}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Summary */}
        <div className="summary-box">
          <h3>Zusammenfassung</h3>
          <div className="summary-stats">
            <div className="stat">
              <span className="label">OK:</span>
              <span className="value ok">{Object.values(session.grades).filter(g => g === 'ok').length}</span>
            </div>
            <div className="stat">
              <span className="label">MEH:</span>
              <span className="value meh">{Object.values(session.grades).filter(g => g === 'meh').length}</span>
            </div>
            <div className="stat">
              <span className="label">FAIL:</span>
              <span className="value fail">{Object.values(session.grades).filter(g => g === 'fail').length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
