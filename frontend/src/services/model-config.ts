import request from '@/api/request';

export interface ModelConfigItem {
  id: number;
  provider: string;
  model_name: string;
  temperature: number;
  max_tokens: number;
  rate_limit_per_minute: number;
  daily_quota?: number | null;
  updated_at: string;
}

export interface UpdateModelConfigPayload {
  provider?: string;
  model_name?: string;
  temperature?: number;
  max_tokens?: number;
  rate_limit_per_minute?: number;
  daily_quota?: number | null;
}

export interface ModelUsageLogItem {
  id: number;
  user_id: number;
  model_name: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  cost?: number | null;
  created_at: string;
}

export interface ModelUsageLogListResponse {
  items: ModelUsageLogItem[];
  total: number;
}

export interface ListModelUsageLogsParams {
  user_id?: number;
  model_name?: string;
  skip?: number;
  limit?: number;
}

export const getModelConfig = async () => {
  return request.get('/model/config') as Promise<ModelConfigItem>;
};

export const updateModelConfig = async (payload: UpdateModelConfigPayload) => {
  return request.put('/model/config', payload) as Promise<ModelConfigItem>;
};

export const listModelUsageLogs = async (params: ListModelUsageLogsParams = {}) => {
  return request.get('/model/logs', { params }) as Promise<ModelUsageLogListResponse>;
};