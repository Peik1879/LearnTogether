import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface SessionResponse {
  session_id: string;
  examiner_token?: string;
  token?: string;
  role?: string;
}

export interface CurrentQuestionResponse {
  status: 'locked' | 'revealed' | 'completed';
  index: number;
  question?: string;
  total?: number;
}

export interface QuestionsResponse {
  session_id: string;
  questions: string[];
  current_index: number;
  revealed: boolean;
  grades: Record<number, string>;
  pdfs: Array<{ filename: string; size: number }>;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Helper to add X-Token header
const withToken = (token: string) => ({
  headers: {
    'X-Token': token
  }
});

export const sessionAPI = {
  createSession: async (): Promise<SessionResponse> => {
    const response = await api.post('/session');
    return response.data;
  },

  joinSession: async (sessionId: string, role: 'learner' | 'examiner'): Promise<SessionResponse> => {
    const response = await api.post(`/session/${sessionId}/join`, { role });
    return response.data;
  },

  uploadPdfs: async (sessionId: string, files: File[], token: string): Promise<any> => {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    const response = await api.post(
      `/session/${sessionId}/upload`,
      formData,
      {
        headers: {
          'X-Token': token,
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    return response.data;
  },

  generateQuestions: async (sessionId: string, pdfTexts: Record<string, string>, token: string): Promise<any> => {
    const response = await api.post(
      `/session/${sessionId}/generate`,
      { pdf_texts: pdfTexts },
      withToken(token)
    );
    return response.data;
  },

  getCurrentQuestion: async (sessionId: string, token: string): Promise<CurrentQuestionResponse> => {
    const response = await api.get(
      `/session/${sessionId}/current`,
      withToken(token)
    );
    return response.data;
  },

  getAllQuestions: async (sessionId: string, token: string): Promise<QuestionsResponse> => {
    const response = await api.get(
      `/session/${sessionId}/questions`,
      withToken(token)
    );
    return response.data;
  },

  revealQuestion: async (sessionId: string, token: string): Promise<any> => {
    const response = await api.post(
      `/session/${sessionId}/reveal`,
      {},
      withToken(token)
    );
    return response.data;
  },

  nextQuestion: async (sessionId: string, token: string): Promise<any> => {
    const response = await api.post(
      `/session/${sessionId}/next`,
      {},
      withToken(token)
    );
    return response.data;
  },

  jumpToQuestion: async (sessionId: string, index: number, token: string): Promise<any> => {
    const response = await api.post(
      `/session/${sessionId}/jump/${index}`,
      {},
      withToken(token)
    );
    return response.data;
  },

  gradeQuestion: async (sessionId: string, index: number, status: 'ok' | 'meh' | 'fail', token: string): Promise<any> => {
    const response = await api.post(
      `/session/${sessionId}/grade`,
      { index, status },
      withToken(token)
    );
    return response.data;
  }
};

export const extractPdfText = async (file: File): Promise<string> => {
  // For MVP, we'll use a simple approach: store file content as base64
  // In real scenario, backend would handle PDF parsing
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      // Placeholder: return file name as extracted text
      // Backend will handle real PDF parsing when files are sent
      resolve(`Content from ${file.name}`);
    };
    reader.onerror = reject;
    reader.readAsArrayBuffer(file);
  });
};
