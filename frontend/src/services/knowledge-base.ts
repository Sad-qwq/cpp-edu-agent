import request from '@/api/request';

export interface KnowledgeDocumentItem {
  id: number;
  source_type: string;
  source_id?: number | null;
  class_id?: number | null;
  teacher_id?: number | null;
  title: string;
  file_path?: string | null;
  mime_type?: string | null;
  parse_status: 'pending' | 'processing' | 'completed' | 'failed';
  parse_error?: string | null;
  metadata_json: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeDocumentListResponse {
  items: KnowledgeDocumentItem[];
  total: number;
}

export const listAdminKnowledgeDocuments = async (params: { keyword?: string; skip?: number; limit?: number } = {}) => {
  return request.get('/ai/knowledge/admin-materials', { params }) as Promise<KnowledgeDocumentListResponse>;
};

export const uploadAdminKnowledgeDocument = async (payload: { title: string; description?: string; file: File }) => {
  const formData = new FormData();
  formData.append('title', payload.title);
  formData.append('description', payload.description || '');
  formData.append('file', payload.file);

  return request.post('/ai/knowledge/admin-materials', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: 120000,
  }) as Promise<KnowledgeDocumentItem>;
};

export const deleteAdminKnowledgeDocument = async (documentId: number) => {
  return request.delete(`/ai/knowledge/admin-materials/${documentId}`) as Promise<KnowledgeDocumentItem>;
};