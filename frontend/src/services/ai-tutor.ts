import request from '@/api/request';

export type TutorMode = 'concept' | 'hint' | 'code_review' | 'practice';
export type TutorMessageRole = 'user' | 'assistant';

export interface TutorReplyPayload {
  answer: string;
  hint_level?: number | null;
  cited_chunk_ids: number[];
  related_knowledge_points: string[];
  follow_up_questions: string[];
  recommended_action: string;
  risk_flags: string[];
}

export interface TutorMessage {
  id: number;
  session_id: number;
  role: TutorMessageRole;
  content: string;
  hint_level?: number | null;
  cited_chunk_ids: number[];
  related_knowledge_points: string[];
  reply_json: Record<string, unknown>;
  created_at: string;
}

export interface TutorSessionDetail {
  id: number;
  class_id: number;
  student_id: number;
  assignment_id?: number | null;
  problem_id?: number | null;
  mode: TutorMode;
  title: string;
  latest_summary?: string | null;
  created_at: string;
  updated_at: string;
  messages: TutorMessage[];
}

export interface TutorSessionListResponse {
  items: Array<Omit<TutorSessionDetail, 'messages'>>;
  total: number;
}

export interface PracticeRecommendation {
  title: string;
  reason: string;
  target_knowledge_points: string[];
  action_type: string;
  assignment_id?: number | null;
  problem_id?: number | null;
}

export const createTutorSession = async (payload: {
  class_id: number;
  assignment_id?: number | null;
  problem_id?: number | null;
  mode: TutorMode;
  title?: string;
}) => {
  return request.post('/ai/tutor/sessions', payload, {
    timeout: 20000,
  }) as Promise<TutorSessionDetail>;
};

export const getTutorSession = async (sessionId: number) => {
  return request.get(`/ai/tutor/sessions/${sessionId}`) as Promise<TutorSessionDetail>;
};

export const listTutorSessions = async (params: { class_id: number; skip?: number; limit?: number }) => {
  return request.get('/ai/tutor/sessions', { params }) as Promise<TutorSessionListResponse>;
};

export const sendTutorMessage = async (sessionId: number, payload: {
  content: string;
  hint_level?: number;
  student_answer?: string;
  current_code?: string;
  compiler_output?: string;
  expected_output?: string;
}) => {
  return request.post(`/ai/tutor/sessions/${sessionId}/messages`, payload, {
    timeout: 120000,
  }) as Promise<TutorSessionDetail>;
};

export const getProblemHint = async (problemId: number, payload: {
  class_id: number;
  assignment_id?: number | null;
  student_answer?: string;
  current_code?: string;
  hint_level: number;
}) => {
  return request.post(`/ai/tutor/problems/${problemId}/hint`, payload, {
    timeout: 60000,
  }) as Promise<TutorReplyPayload>;
};

export const reviewCodeWithTutor = async (payload: {
  class_id: number;
  assignment_id?: number | null;
  problem_id?: number | null;
  code: string;
  compiler_output?: string;
  input_data?: string;
  expected_output?: string;
  student_question?: string;
}) => {
  return request.post('/ai/tutor/code-review', payload, {
    timeout: 120000,
  }) as Promise<TutorReplyPayload>;
};

export const getPracticeRecommendations = async (studentId: number, classId: number) => {
  return request.get(`/ai/tutor/students/${studentId}/recommendations`, {
    params: { class_id: classId },
  }) as Promise<{ items: PracticeRecommendation[] }>;
};

export const deleteTutorSession = async (sessionId: number) => {
  return request.delete(`/ai/tutor/sessions/${sessionId}`) as Promise<{ message: string }>;
};
