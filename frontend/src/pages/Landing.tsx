import React, { useState } from 'react';
import { sessionAPI } from '../services/api';
import '../styles/App.css';

interface LandingProps {
  onNavigate: (view: 'landing' | 'learner' | 'examiner', data?: any) => void;
}

export const Landing: React.FC<LandingProps> = ({ onNavigate }) => {
  const [mode, setMode] = useState<'create' | 'join' | null>(null);
  const [sessionCode, setSessionCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCreateSession = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await sessionAPI.createSession();
      onNavigate('learner', {
        sessionId: result.session_id,
        token: result.examiner_token,
        role: 'examiner'
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create session');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinAsLearner = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await sessionAPI.joinSession(sessionCode.toUpperCase(), 'learner');
      onNavigate('learner', {
        sessionId: sessionCode.toUpperCase(),
        token: result.token,
        role: 'learner'
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join session');
    } finally {
      setLoading(false);
    }
  };

  const handleJoinAsExaminer = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await sessionAPI.joinSession(sessionCode.toUpperCase(), 'examiner');
      onNavigate('examiner', {
        sessionId: sessionCode.toUpperCase(),
        token: result.token,
        role: 'examiner'
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to join session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h1>LearnTogether</h1>
        <p className="subtitle">1-zu-1 Lernabfragen</p>

        {error && <div className="error">{error}</div>}

        {!mode ? (
          <div className="button-group">
            <button onClick={() => setMode('create')} className="btn btn-primary">
              Neue Session erstellen
            </button>
            <button onClick={() => setMode('join')} className="btn btn-secondary">
              Session beitreten
            </button>
          </div>
        ) : mode === 'create' ? (
          <div>
            <p>Als Examiner werden Sie zur Upload-Seite weitergeleitet.</p>
            <button
              onClick={handleCreateSession}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Wird erstellt...' : 'Session erstellen'}
            </button>
            <button onClick={() => setMode(null)} className="btn btn-outline">
              Zurück
            </button>
          </div>
        ) : (
          <div>
            <input
              type="text"
              placeholder="Session Code eingeben"
              value={sessionCode}
              onChange={(e) => setSessionCode(e.target.value.toUpperCase())}
              maxLength={8}
              className="input"
            />
            <div className="button-group">
              <button
                onClick={handleJoinAsLearner}
                disabled={!sessionCode || loading}
                className="btn btn-primary"
              >
                {loading ? 'Wird beigetreten...' : 'Als Learner beitreten'}
              </button>
              <button
                onClick={handleJoinAsExaminer}
                disabled={!sessionCode || loading}
                className="btn btn-secondary"
              >
                {loading ? 'Wird beigetreten...' : 'Als Examiner beitreten'}
              </button>
            </div>
            <button onClick={() => setMode(null)} className="btn btn-outline">
              Zurück
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
