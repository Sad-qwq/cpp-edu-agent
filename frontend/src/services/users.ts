import request from '@/api/request';

export interface UserProfileResponse {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  is_approved: boolean;
  bio?: string | null;
  avatar_url?: string | null;
}

export interface UpdateMyProfilePayload {
  username?: string;
  bio?: string;
  avatar_url?: string;
}

export interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
}

export interface UploadAvatarResponse {
  avatar_url: string;
}

export interface ListUsersParams {
  skip?: number;
  limit?: number;
  role?: string;
  is_active?: boolean;
  is_approved?: boolean;
}

export interface AdminUpdateUserPayload {
  username?: string;
  role?: string;
  is_active?: boolean;
  is_approved?: boolean;
  bio?: string;
  avatar_url?: string;
}

export const getMyProfile = async () => {
  return request.get('/users/me') as Promise<UserProfileResponse>;
};

export const updateMyProfile = async (payload: UpdateMyProfilePayload) => {
  return request.put('/users/me', payload) as Promise<UserProfileResponse>;
};

export const changeMyPassword = async (payload: ChangePasswordPayload) => {
  return request.post('/users/me/password', payload) as Promise<{ msg: string }>;
};

export const uploadMyAvatar = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  return request.post('/users/me/avatar', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }) as Promise<UploadAvatarResponse>;
};

export const listUsers = async (params: ListUsersParams = {}) => {
  return request.get('/users', { params }) as Promise<UserProfileResponse[]>;
};

export const listPendingTeachers = async () => {
  return request.get('/users/pending/teachers') as Promise<UserProfileResponse[]>;
};

export const adminUpdateUser = async (userId: number, payload: AdminUpdateUserPayload) => {
  return request.patch(`/users/${userId}`, payload) as Promise<UserProfileResponse>;
};

export const approveTeacher = async (userId: number) => {
  return request.post(`/users/${userId}/approve-teacher`) as Promise<UserProfileResponse>;
};

export const rejectTeacher = async (userId: number) => {
  return request.post(`/users/${userId}/reject-teacher`) as Promise<UserProfileResponse>;
};