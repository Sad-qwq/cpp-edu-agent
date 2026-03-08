import request from '@/api/request';

export interface Assignment {
  id: number;
  title: string;
  description?: string | null;
  due_date?: string | null;
  classroom_id: number;
  created_at: string;
  my_submitted?: boolean | null;
  my_score?: number | null;
  my_submission_id?: number | null;
}

export interface Problem {
  id: number;
  assignment_id: number;
  type: 'choice' | 'short_answer' | 'coding';
  content: string;
  score: number;
  display_order: number;
  options: string[];
  correct_answer?: string | null;
  code_template?: string | null;
  test_cases: Array<Record<string, string>>;
}

export interface Submission {
  id: number;
  assignment_id: number;
  student_id: number;
  submitted_at: string;
  answers: Record<string, unknown>;
  score?: number | null;
  feedback?: string | null;
  student_name?: string | null;
}

export interface ProblemPayload {
  type: 'choice' | 'short_answer' | 'coding';
  content: string;
  score: number;
  display_order: number;
  options: string[];
  correct_answer?: string | null;
  code_template?: string | null;
  test_cases: Array<Record<string, string>>;
}

export const listAssignments = async (classroomId: number) => {
  return request.get('/assignments', {
    params: { classroom_id: classroomId },
  }) as Promise<Assignment[]>;
};

export const createAssignment = async (payload: {
  title: string;
  description?: string;
  due_date?: string | null;
  classroom_id: number;
}) => {
  return request.post('/assignments', payload) as Promise<Assignment>;
};

export const getAssignment = async (assignmentId: number) => {
  return request.get(`/assignments/${assignmentId}`) as Promise<Assignment>;
};

export const updateAssignment = async (assignmentId: number, payload: {
  title?: string;
  description?: string;
  due_date?: string | null;
}) => {
  return request.put(`/assignments/${assignmentId}`, payload) as Promise<Assignment>;
};

export const deleteAssignment = async (assignmentId: number) => {
  return request.delete(`/assignments/${assignmentId}`) as Promise<Assignment>;
};

export const listProblems = async (assignmentId: number) => {
  return request.get(`/assignments/${assignmentId}/problems`) as Promise<Problem[]>;
};

export const createProblem = async (assignmentId: number, payload: ProblemPayload) => {
  return request.post(`/assignments/${assignmentId}/problems`, payload) as Promise<Problem>;
};

export const updateProblem = async (assignmentId: number, problemId: number, payload: Partial<ProblemPayload>) => {
  return request.put(`/assignments/${assignmentId}/problems/${problemId}`, payload) as Promise<Problem>;
};

export const deleteProblem = async (assignmentId: number, problemId: number) => {
  return request.delete(`/assignments/${assignmentId}/problems/${problemId}`) as Promise<Problem>;
};

export const submitAssignment = async (assignmentId: number, answers: Record<string, unknown>) => {
  return request.post(`/assignments/${assignmentId}/submit`, { answers }) as Promise<Submission>;
};

export const getMySubmission = async (assignmentId: number) => {
  try {
    return await request.get(`/assignments/${assignmentId}/submissions/me`, {
      suppressErrorMessage: true,
    }) as Submission;
  } catch {
    return null;
  }
};

export const getSubmissions = async (assignmentId: number, page = 1, pageSize = 10) => {
  return request.get(`/assignments/${assignmentId}/submissions`, {
    params: {
      skip: (page - 1) * pageSize,
      limit: pageSize,
    },
  }) as Promise<Submission[]>;
};

export const gradeSubmission = async (assignmentId: number, submissionId: number, score: number, feedback: string) => {
  return request.put(`/assignments/${assignmentId}/submissions/${submissionId}`, {
    score,
    feedback,
  }) as Promise<Submission>;
};