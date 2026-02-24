
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/api/request';

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '');
  const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));
  const router = useRouter();

  const isLoggedIn = computed(() => !!token.value);
  const isAdmin = computed(() => user.value.role === 'admin');

  async function login(loginForm: any) {
    try {
      // 1. 获取 Token (OAuth2PasswordRequestForm 需要 x-www-form-urlencoded 格式)
      const params = new URLSearchParams();
      params.append('username', loginForm.username);
      params.append('password', loginForm.password);
      
      const res: any = await request.post('/auth/login', params);
      token.value = res.access_token;
      localStorage.setItem('token', token.value);

      // 2. 获取用户信息
      await fetchUserInfo();
      return true;
    } catch (error) {
      return false;
    }
  }

  async function fetchUserInfo() {
    if (!token.value) return;
    try {
      const res = await request.get('/users/me');
      user.value = res;
      localStorage.setItem('user', JSON.stringify(res));
    } catch (error) {
      logout();
    }
  }

  function logout() {
    token.value = '';
    user.value = {};
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    location.reload(); 
  }

  return { token, user, isLoggedIn, isAdmin, login, fetchUserInfo, logout };
});
