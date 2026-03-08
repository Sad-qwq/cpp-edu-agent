import request from '@/api/request';

export type DraftValidationStatus = 'pending' | 'passed' | 'warning' | 'failed';
export type QuestionGenerationStatus = 'pending' | 'retrieving' | 'blueprinting' | 'generating' | 'validating' | 'reviewing' | 'published' | 'failed';
export type QuestionType = 'choice' | 'short_answer' | 'coding';

export interface QuestionDraft {
  id: number;
  job_id: number;
  draft_index: number;
  type: QuestionType;
  content: string;
  options: string[];
  correct_answer?: string | null;
  code_template?: string | null;
  test_cases: Array<Record<string, string>>;
  reference_solution?: string | null;
  explanation?: string | null;
  target_knowledge_points: string[];
  difficulty?: string | null;
  estimated_score?: number | null;
  source_chunk_ids: number[];
  validation_status: DraftValidationStatus;
  validation_report: Record<string, unknown>;
  teacher_action: string;
  published_problem_id?: number | null;
  created_at: string;
  updated_at: string;
}

export interface QuestionValidationRun {
  id: number;
  draft_id: number;
  validation_type: string;
  status: DraftValidationStatus;
  report_json: Record<string, unknown>;
  created_at: string;
}

export interface QuestionGenerationJobRead {
  id: number;
  teacher_id: number;
  class_id: number;
  assignment_id?: number | null;
  status: QuestionGenerationStatus;
  topic: string;
  knowledge_points: string[];
  request_payload: Record<string, unknown>;
  retrieval_summary: Record<string, unknown>;
  blueprint_json: Record<string, unknown>;
  error_message?: string | null;
  started_at?: string | null;
  finished_at?: string | null;
  created_at: string;
}

export interface QuestionGenerationJobDetail extends QuestionGenerationJobRead {
  drafts: QuestionDraft[];
  validations: QuestionValidationRun[];
}

export interface CreateQuestionGenerationJobPayload {
  class_id: number;
  assignment_id?: number | null;
  topic: string;
  knowledge_points: string[];
  total_count: number;
  question_type_distribution: Record<string, number>;
  difficulty_distribution: Record<string, number>;
  use_class_materials: boolean;
  use_admin_knowledge_base: boolean;
  use_history_questions: boolean;
  extra_constraints?: string;
}

const AI_GENERATION_TIMEOUT = 120000;

export const createQuestionGenerationJob = async (payload: CreateQuestionGenerationJobPayload) => {
  return request.post('/ai/question-generation/jobs', payload, {
    timeout: AI_GENERATION_TIMEOUT,
  }) as Promise<QuestionGenerationJobRead>;
};

export const getQuestionGenerationJobDetail = async (jobId: number) => {
  return request.get(`/ai/question-generation/jobs/${jobId}`) as Promise<QuestionGenerationJobDetail>;
};

export const regenerateQuestionDraft = async (jobId: number, draftId: number) => {
  return request.post(`/ai/question-generation/jobs/${jobId}/drafts/${draftId}/regenerate`, undefined, {
    timeout: AI_GENERATION_TIMEOUT,
  }) as Promise<{
    message: string;
    draft: QuestionDraft;
  }>;
};

export const publishQuestionGenerationJob = async (jobId: number, payload: { assignment_id: number; accepted_draft_ids: number[] }) => {
  return request.post(`/ai/question-generation/jobs/${jobId}/publish`, payload, {
    timeout: 60000,
  }) as Promise<{
    created_problem_ids: number[];
    message: string;
  }>;
};