import request from '@/api/request';

export interface AnnouncementItem {
  id: number;
  class_id?: number | null;
  title: string;
  content: string;
  is_pinned: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by: number;
}

export interface AnnouncementPayload {
  title: string;
  content: string;
  is_pinned?: boolean;
  is_active?: boolean;
}

export interface AnnouncementUpdatePayload {
  title?: string;
  content?: string;
  is_pinned?: boolean;
  is_active?: boolean;
}

export const listClassAnnouncements = async (classId: number, params?: { skip?: number; limit?: number }) => {
  return request.get(`/classes/${classId}/announcements`, {
    params,
  }) as Promise<AnnouncementItem[]>;
};

export const createClassAnnouncement = async (classId: number, payload: AnnouncementPayload) => {
  return request.post(`/classes/${classId}/announcements`, payload) as Promise<AnnouncementItem>;
};

export const updateClassAnnouncement = async (classId: number, announcementId: number, payload: AnnouncementUpdatePayload) => {
  return request.put(`/classes/${classId}/announcements/${announcementId}`, payload) as Promise<AnnouncementItem>;
};

export const deleteClassAnnouncement = async (classId: number, announcementId: number) => {
  return request.delete(`/classes/${classId}/announcements/${announcementId}`) as Promise<void>;
};

export const listPlatformAnnouncements = async (params?: { include_inactive?: boolean; keyword?: string }) => {
  return request.get('/announcements', {
    params,
  }) as Promise<AnnouncementItem[]>;
};

export const listPublicAnnouncements = async (params?: { limit?: number }) => {
  return request.get('/announcements/public', {
    params,
  }) as Promise<AnnouncementItem[]>;
};

export const createPlatformAnnouncement = async (payload: AnnouncementPayload) => {
  return request.post('/announcements', payload) as Promise<AnnouncementItem>;
};

export const updatePlatformAnnouncement = async (announcementId: number, payload: AnnouncementUpdatePayload) => {
  return request.patch(`/announcements/${announcementId}`, payload) as Promise<AnnouncementItem>;
};

export const deletePlatformAnnouncement = async (announcementId: number) => {
  return request.delete(`/announcements/${announcementId}`) as Promise<void>;
};