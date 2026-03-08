import request from '@/api/request';

export interface NotificationItem {
  id: number;
  title: string;
  content: string;
  link?: string | null;
  is_read: boolean;
  created_at: string;
}

export const listNotifications = async (params?: { skip?: number; limit?: number }) => {
  return request.get('/notifications', { params }) as Promise<NotificationItem[]>;
};

export const markNotificationRead = async (notificationId: number) => {
  return request.post(`/notifications/${notificationId}/read`) as Promise<NotificationItem>;
};

export const markAllNotificationsRead = async () => {
  return request.post('/notifications/read_all') as Promise<{ updated: number }>;
};