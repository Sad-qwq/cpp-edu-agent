import request from '@/api/request';

export interface SandboxRequest {
  code: string;
  input_data: string;
}

export interface SandboxResponse {
  output: string;
  error: string;
  status: 'success' | 'compile_error' | 'runtime_error';
}

export const executeCode = async (payload: SandboxRequest) => {
  return request.post('/sandbox/execute', payload) as Promise<SandboxResponse>;
};