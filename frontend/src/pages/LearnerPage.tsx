import React, { useState, useEffect, useRef } from 'react';
import { sessionAPI, CurrentQuestionResponse } from '../services/api';
import '../styles/App.css';

type View = 'landing' | 'learner' | 'examiner';

interface LearnerPageProps {
  sessionId: string;
  token: string;
  role: 'learner' | 'examiner';
  onNavigate: (view: View, data?: any) => void;
}

export const LearnerPage: React.FC<LearnerPageProps> = ({ sessionId, token, role, onNavigate }) => {
  const [step, setStep] = useState<'upload' | 'waiting' | 'question'>(
    role === 'learner' ? 'waiting' : 'upload'
  );
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<CurrentQuestionResponse | null>(null);
  const [error, setError] = useState('');
  const pollingIntervalRef = useRef<number | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
      setError('');
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError('Bitte wählen Sie mindestens eine PDF aus');
      return;
    }

    setUploading(true);
    setError('');
    try {
      await sessionAPI.uploadPdfs(sessionId, selectedFiles, token);
      setStep('waiting');
      startPolling();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload fehlgeschlagen');
    } finally {
      setUploading(false);
    }
  };

  const startPolling = () => {
    // Immediate first call
    fetchCurrentQuestion();

    // Then poll every 1 second
    pollingIntervalRef.current = setInterval(fetchCurrentQuestion, 1000);
  };

  const fetchCurrentQuestion = async () => {
    try {
      const response = await sessionAPI.getCurrentQuestion(sessionId, token);
      setCurrentQuestion(response);

      if (response.status === 'revealed') {
        setStep('question');
      } else if (response.status === 'completed') {
        setStep('waiting');
      }
    } catch (err) {
      // Silently fail during polling
      console.error('Polling error:', err);
    }
  };

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = null;
    }
  };

  useEffect(() => {
    if (role === 'learner') {
      startPolling();
    }
    return () => stopPolling();
  }, [role]);

  const handleLogout = () => {
    stopPolling();
    onNavigate('landing');
  };

  return (
    <div className="container">
      <div className="card">
        <div className="header">
          <h1>LearnTogether - Learner</h1>
          <div className="session-info">
            <span>Session: <code>{sessionId}</code></span>
            <button onClick={handleLogout} className="btn btn-small">Logout</button>
          </div>
        </div>

        {error && <div className="error">{error}</div>}

        {step === 'upload' && role === 'examiner' && (
          <div className="upload-section">
            <h2>PDFs hochladen</h2>
            <p>Laden Sie die Lernmaterialien hoch, aus denen Fragen generiert werden.</p>

            <div className="file-input-wrapper">
              <input
                type="file"
                multiple
                accept=".pdf"
                onChange={handleFileSelect}
                id="pdf-input"
              />
              <label htmlFor="pdf-input" className="file-label">
                {selectedFiles.length > 0
                  ? `${selectedFiles.length} Datei(en) ausgewählt`
                  : 'PDFs auswählen oder hier ablegen'}
              </label>
            </div>

            {selectedFiles.length > 0 && (
              <ul className="file-list">
                {selectedFiles.map((file, idx) => (
                  <li key={idx}>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</li>
                ))}
              </ul>
            )}

            <button
              onClick={handleUpload}
              disabled={uploading || selectedFiles.length === 0}
              className="btn btn-primary btn-large"
            >
              {uploading ? 'Wird hochgeladen...' : 'Hochladen'}
            </button>
          </div>
        )}

        {step === 'waiting' && (
          <div className="waiting-section">
            <h2>Warten auf nächste Frage...</h2>
            <div className="spinner"></div>
            <p>Der Examiner wird Ihnen in Kürze eine Frage stellen.</p>
            {currentQuestion && (
              <p className="progress">
                Frage {currentQuestion.index + 1} von {currentQuestion.total}
              </p>
            )}
          </div>
        )}

        {step === 'question' && currentQuestion && (
          <div className="question-section">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${((currentQuestion.index + 1) / (currentQuestion.total || 1)) * 100}%`
                }}
              ></div>
            </div>

            <h2>Frage {currentQuestion.index + 1} von {currentQuestion.total}</h2>

            <div className="question-box">
              <p className="question-text">{currentQuestion.question}</p>
            </div>

            <p className="info-text">Beantworten Sie diese Frage. Der Examiner wird Ihre Antwort bewerten.</p>

            <div className="waiting-section">
              <div className="spinner"></div>
              <p>Warten auf Bewertung...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
