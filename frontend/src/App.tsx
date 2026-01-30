import React, { useState } from 'react';
import { Landing } from './pages/Landing';
import { LearnerPage } from './pages/LearnerPage';
import { ExaminerPage } from './pages/ExaminerPage';
import './styles/App.css';

type View = 'landing' | 'learner' | 'examiner';

interface SessionData {
  sessionId: string;
  token: string;
  role: 'learner' | 'examiner';
}

export const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<View>('landing');
  const [sessionData, setSessionData] = useState<SessionData | null>(null);

  const handleNavigate = (view: View, data?: any) => {
    setCurrentView(view);
    if (data) {
      setSessionData(data);
    }
  };

  return (
    <div className="app">
      {currentView === 'landing' && <Landing onNavigate={handleNavigate} />}
      {currentView === 'learner' && sessionData && (
        <LearnerPage
          sessionId={sessionData.sessionId}
          token={sessionData.token}
          onNavigate={handleNavigate}
        />
      )}
      {currentView === 'examiner' && sessionData && (
        <ExaminerPage
          sessionId={sessionData.sessionId}
          token={sessionData.token}
          onNavigate={handleNavigate}
        />
      )}
    </div>
  );
};

export default App;
