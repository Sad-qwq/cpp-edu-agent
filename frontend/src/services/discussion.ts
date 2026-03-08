import request from '@/api/request';

export interface DiscussionUserBrief {
  id: number;
  username?: string | null;
  role: 'admin' | 'teacher' | 'student';
  avatar_url?: string | null;
}

export interface DiscussionAnswer {
  id: number;
  question_id: number;
  user_id: number;
  content: string;
  upvote_count: number;
  is_accepted: boolean;
  created_at: string;
  updated_at: string;
  author?: DiscussionUserBrief | null;
}

export interface DiscussionQuestion {
  id: number;
  class_id: number;
  user_id: number;
  title: string;
  content: string;
  upvote_count: number;
  accepted_answer_id?: number | null;
  is_locked: boolean;
  created_at: string;
  updated_at: string;
  author?: DiscussionUserBrief | null;
  answer_count: number;
}

export interface DiscussionQuestionDetail extends DiscussionQuestion {
  answers: DiscussionAnswer[];
}

export interface DiscussionQuestionListResponse {
  items: DiscussionQuestion[];
  total: number;
}

export interface VoteResponse {
  target_id: number;
  upvote_count: number;
  user_voted: boolean;
}

export const listQuestions = async (classId: number, params?: {
  status?: string;
  keyword?: string;
  sort_by?: string;
  skip?: number;
  limit?: number;
}) => {
  return request.get(`/discussion/classes/${classId}/discussions`, { params }) as Promise<DiscussionQuestionListResponse>;
};

export const createQuestion = async (classId: number, payload: { title: string; content: string }) => {
  return request.post(`/discussion/classes/${classId}/discussions`, payload) as Promise<DiscussionQuestion>;
};

export const getQuestionDetail = async (classId: number, questionId: number) => {
  return request.get(`/discussion/classes/${classId}/discussions/${questionId}`) as Promise<DiscussionQuestionDetail>;
};

export const createAnswer = async (classId: number, questionId: number, payload: { content: string }) => {
  return request.post(`/discussion/classes/${classId}/discussions/${questionId}/answers`, payload) as Promise<DiscussionAnswer>;
};

export const acceptAnswer = async (classId: number, questionId: number, answerId: number) => {
  return request.post(`/discussion/classes/${classId}/discussions/${questionId}/accept/${answerId}`) as Promise<DiscussionQuestionDetail>;
};

export const toggleQuestionUpvote = async (classId: number, questionId: number) => {
  return request.post(`/discussion/classes/${classId}/discussions/${questionId}/upvote`) as Promise<VoteResponse>;
};

export const toggleAnswerUpvote = async (classId: number, questionId: number, answerId: number) => {
  return request.post(`/discussion/classes/${classId}/discussions/${questionId}/answers/${answerId}/upvote`) as Promise<VoteResponse>;
};