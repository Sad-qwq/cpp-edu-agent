
import axios from 'axios';
import { useUserStore } from '@/stores/user';
import { ElMessage } from 'element-plus';

const service = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1', // 后端地址
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
    const msg = error.response?.data?.detail || 'Unknown Error';
    ElMessage.error(msg);
    return Promise.reject(error);
  }
);

export default service;
