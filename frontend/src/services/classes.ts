import request from '@/api/request';
import type { UserProfile } from '@/stores/user';

export interface ClassroomDetail {
  id: number;
  name: string;
  invite_code: string;
  teacher_id: number;
  teacher_name?: string | null;
  is_active: boolean;
  created_at: string;
  student_count?: number | null;
  assignment_count?: number | null;
  already_joined?: boolean | null;
}

export const getClassroomDetail = async (classId: number) => {
  return request.get(`/classes/${classId}`) as Promise<ClassroomDetail>;
};

export const listClassStudents = async (classId: number) => {
  return request.get(`/classes/${classId}/students`) as Promise<UserProfile[]>;
};

export const removeClassStudent = async (classId: number, studentId: number) => {
  return request.delete(`/classes/${classId}/students/${studentId}`) as Promise<void>;
};