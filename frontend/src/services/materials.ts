import request from '@/api/request';

const MATERIAL_UPLOAD_TIMEOUT = 120000;

export interface MaterialItem {
  id: number;
  title: string;
  description?: string | null;
  file_url: string;
  file_type: string;
  size?: number | null;
  class_id: number;
  uploader_id: number;
  created_at: string;
}

export interface MaterialListResponse {
  items: MaterialItem[];
  total: number;
}

export const listMaterials = async (params: {
  class_id: number;
  file_type?: string;
  keyword?: string;
  skip?: number;
  limit?: number;
}) => {
  return request.get('/materials', { params }) as Promise<MaterialListResponse>;
};

export const uploadMaterial = async (payload: {
  class_id: number;
  title: string;
  description?: string;
  file: File;
}) => {
  const formData = new FormData();
  formData.append('class_id', String(payload.class_id));
  formData.append('title', payload.title);
  formData.append('description', payload.description || '');
  formData.append('file', payload.file);

  return request.post('/materials', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    timeout: MATERIAL_UPLOAD_TIMEOUT,
  }) as Promise<MaterialItem>;
};

export const deleteMaterial = async (materialId: number) => {
  return request.delete(`/materials/${materialId}`) as Promise<MaterialItem>;
};