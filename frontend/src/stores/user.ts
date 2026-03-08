
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import request from '@/api/request';

interface LoginForm {
  username: string;
  password: string;
}

interface LoginSuccessResult {
  success: true;
  user: UserProfile;
}

interface LoginFailureResult {
  success: false;
  reason: 'invalid_credentials' | 'inactive' | 'teacher_pending' | 'unknown';
}

export type LoginResult = LoginSuccessResult | LoginFailureResult;

export interface UserProfile {
  id?: number;
  username?: string;
  email?: string;
  role?: string;
  is_active?: boolean;
  is_approved?: boolean;
  bio?: string | null;
  avatar_url?: string | null;
}

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '');
  const user = ref<UserProfile>(JSON.parse(localStorage.getItem('user') || '{}'));
  const authReady = ref(false);
  const authInitializing = ref(false);
  let initializePromise: Promise<boolean> | null = null;

  const isLoggedIn = computed(() => !!token.value && !!user.value.email);
  const isAdmin = computed(() => user.value.role === 'admin');

  const clearAuthState = () => {
    token.value = '';
    user.value = {};
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const handleSessionExpired = () => {
    clearAuthState();
    authReady.value = true;
  };

  const setUserProfile = (profile: UserProfile) => {
    user.value = profile;
    localStorage.setItem('user', JSON.stringify(profile));
  };

  const mapErrorToReason = (error: unknown): LoginFailureResult['reason'] => {
    const detail = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail;

    if (detail === 'Incorrect email or password') {
      return 'invalid_credentials';
    }

    if (detail === 'Inactive user') {
      return 'inactive';
    }

    if (detail === 'Teacher account not approved') {
      return 'teacher_pending';
    }

    return 'unknown';
  };

  async function login(loginForm: LoginForm): Promise<LoginResult> {
    try {
      const params = new URLSearchParams();
      params.append('username', loginForm.username);
      params.append('password', loginForm.password);
      
      const res = await request.post('/auth/login', params) as { access_token: string };
      token.value = res.access_token;
      localStorage.setItem('token', token.value);

      const profile = await fetchUserInfo({ silent: true });
      if (!profile) {
        clearAuthState();
        authReady.value = true;
        return { success: false, reason: 'unknown' };
      }

      authReady.value = true;
      return { success: true, user: profile };
    } catch (error) {
      clearAuthState();
      authReady.value = true;
      return { success: false, reason: mapErrorToReason(error) };
    }
  }

  async function fetchUserInfo(options?: { silent?: boolean }): Promise<UserProfile | null> {
    if (!token.value) return null;

    const res = await request.get('/users/me', {
      suppressErrorMessage: options?.silent,
      suppressAuthRedirect: options?.silent,
    }) as UserProfile;
    setUserProfile(res);
    return res;
  }

  async function initializeAuth(force = false): Promise<boolean> {
    if (!force && authReady.value) {
      return isLoggedIn.value;
    }

    if (!force && initializePromise) {
      return initializePromise;
    }

    initializePromise = (async () => {
      authInitializing.value = true;

      try {
        if (!token.value) {
          clearAuthState();
          authReady.value = true;
          return false;
        }

        const profile = await fetchUserInfo({ silent: true });
        authReady.value = true;
        return !!profile;
      } catch (error) {
        clearAuthState();
        authReady.value = true;
        return false;
      } finally {
        authInitializing.value = false;
        initializePromise = null;
      }
    })();

    return initializePromise;
  }

  function logout() {
    clearAuthState();
    authReady.value = true;
  }

  return {
    token,
    user,
    authReady,
    authInitializing,
    isLoggedIn,
    isAdmin,
    login,
    fetchUserInfo,
    setUserProfile,
    initializeAuth,
    handleSessionExpired,
    logout,
  };
});
