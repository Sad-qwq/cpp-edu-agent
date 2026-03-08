
import axios, { type AxiosRequestConfig } from 'axios';
import { useUserStore } from '@/stores/user';
import { ElMessage } from 'element-plus';

export const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
export const API_ORIGIN = new URL(API_BASE_URL).origin;

declare module 'axios' {
  export interface AxiosRequestConfig {
    suppressErrorMessage?: boolean;
    suppressAuthRedirect?: boolean;
  }
}

const formatApiError = (detail: unknown) => {
  if (Array.isArray(detail)) {
    const firstIssue = detail[0] as { msg?: string; loc?: Array<string | number> } | undefined;
    if (firstIssue?.msg) {
      const fieldPath = Array.isArray(firstIssue.loc) ? firstIssue.loc.slice(1).join('.') : '';
      return fieldPath ? `${fieldPath}: ${firstIssue.msg}` : firstIssue.msg;
    }
  }

  if (typeof detail === 'string') {
    return detail;
  }

  if (detail && typeof detail === 'object') {
    return '请求参数不符合后端接口要求';
  }

  return 'Unknown Error';
};

const service = axios.create({
  baseURL: API_BASE_URL,
  timeout: 5000,
});

// 请求拦截器：自动加 Token
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore();
    if (userStore.token) {
      config.headers['Authorization'] = `Bearer ${userStore.token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：统一处理错误
service.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const config = (error.config || {}) as AxiosRequestConfig;
    const status = error.response?.status as number | undefined;
    const isLoginRequest = typeof config.url === 'string' && config.url.includes('/auth/login');

    if ((status === 401 || status === 403) && !config.suppressAuthRedirect && !isLoginRequest) {
      const userStore = useUserStore();
      userStore.handleSessionExpired();

      if (window.location.pathname !== '/login') {
        window.location.assign('/login?session=expired');
      }
    }

    if (!config.suppressErrorMessage) {
      const msg = formatApiError(error.response?.data?.detail);
      ElMessage.error(msg);
    }

    return Promise.reject(error);
  }
);

export default service;
