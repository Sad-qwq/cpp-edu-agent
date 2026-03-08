<script setup lang="ts">
import { computed } from 'vue';
import { ElMessage } from 'element-plus';
import { Bell, ChatDotRound, Document, Monitor, Odometer, Reading, Setting, SwitchButton, UserFilled } from '@element-plus/icons-vue';
import { RouterView, useRoute, useRouter } from 'vue-router';
import { API_ORIGIN } from '@/api/request';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';

const resolveAssetUrl = (url?: string | null) => {
  if (!url) {
    return defaultAvatar;
  }

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  return `${API_ORIGIN}${url}`;
};

const displayName = computed(() => userStore.user.username || userStore.user.email || '用户');
const avatarSrc = computed(() => resolveAssetUrl(userStore.user.avatar_url));
const roleLabel = computed(() => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生',
  };

  return roleMap[userStore.user.role || ''] || '平台用户';
});

const pageTitle = computed(() => String(route.meta.title || '工作台'));
const pageDescription = computed(() => String(route.meta.description || '统一管理你的 C++ 教学与学习任务。'));
const currentClassId = computed(() => {
  const rawValue = route.params.id;
  return typeof rawValue === 'string' ? rawValue : '';
});

const navItems = computed(() => {
  const items = [
    { key: 'dashboard', label: '仪表盘', icon: Odometer, to: '/', available: true },
    { key: 'classes', label: '班级', icon: Reading, to: '/classes', available: true },
    { key: 'notifications', label: '通知中心', icon: Bell, to: '/notifications', available: true },
    { key: 'sandbox', label: 'C++ 沙箱', icon: Monitor, to: '/sandbox', available: true },
    { key: 'settings', label: '设置', icon: Setting, to: '/settings', available: true },
  ];

  if (userStore.isAdmin) {
    items.splice(3, 0, { key: 'users', label: '用户管理', icon: UserFilled, to: '/admin/users', available: true });
    items.splice(4, 0, { key: 'admin-announcements', label: '平台公告', icon: Document, to: '/admin/announcements', available: true });
    items.splice(5, 0, { key: 'admin-model-config', label: '模型配置', icon: Setting, to: '/admin/model-config', available: true });
  }

  if (route.path.startsWith('/classes/') && currentClassId.value) {
    items.splice(2, 0, {
      key: 'class-announcements',
      label: '班级公告',
      icon: Bell,
      to: `/classes/${currentClassId.value}/announcements`,
      available: true,
    });
    items.splice(3, 0, {
      key: 'class-materials',
      label: '班级资料',
      icon: Document,
      to: `/classes/${currentClassId.value}/materials`,
      available: true,
    });
    items.splice(4, 0, {
      key: 'class-discussions',
      label: '班级讨论',
      icon: ChatDotRound,
      to: `/classes/${currentClassId.value}/discussions`,
      available: true,
    });

    if (userStore.user.role === 'teacher' || userStore.user.role === 'admin') {
      items.splice(5, 0, {
        key: 'class-members',
        label: '班级成员',
        icon: UserFilled,
        to: `/classes/${currentClassId.value}/members`,
        available: true,
      });
    }
  }

  return items;
});

const isNavItemActive = (to: string) => {
  if (!to) {
    return false;
  }

  if (to === '/') {
    return route.path === '/';
  }

  return route.path === to || route.path.startsWith(`${to}/`);
};

const handleNavigate = (to: string, available: boolean) => {
  if (!available) {
    ElMessage.info('该模块会在下一阶段继续实现');
    return;
  }

  router.push(to);
};

const handleLogout = () => {
  userStore.logout();
  router.push('/login');
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-800">
    <div class="mx-auto flex min-h-screen max-w-[1600px] flex-col lg:flex-row">
      <aside class="border-b border-slate-200 bg-white px-6 py-6 lg:sticky lg:top-0 lg:h-screen lg:w-72 lg:border-b-0 lg:border-r lg:px-5 lg:py-8">
        <div class="flex h-full flex-col gap-8">
          <div class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm">
            <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20">
              <element-plus class="h-6 w-6" />
            </div>
            <div>
              <p class="text-xs font-medium uppercase tracking-[0.22em] text-blue-600">EduPilot</p>
              <p class="mt-1 text-sm text-slate-500">C++ 教学平台</p>
            </div>
          </div>

          <nav class="grid gap-2">
            <button
              v-for="item in navItems"
              :key="item.key"
              type="button"
              class="flex items-center justify-between rounded-2xl px-4 py-3 text-left transition-all duration-300"
              :class="isNavItemActive(item.to)
                ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/20'
                : item.available
                  ? 'bg-white text-slate-600 hover:-translate-y-1 hover:bg-slate-100 hover:text-slate-900'
                  : 'bg-slate-100 text-slate-400'"
              @click="handleNavigate(item.to, item.available)"
            >
              <span class="flex items-center gap-3 text-sm font-medium">
                <component :is="item.icon" class="h-5 w-5" />
                {{ item.label }}
              </span>
              <span
                v-if="isNavItemActive(item.to)"
                class="rounded-full bg-white/15 px-2.5 py-1 text-xs font-medium text-white"
              >
                当前
              </span>
            </button>
          </nav>

          <div class="mt-auto rounded-3xl bg-slate-900 p-5 text-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
            <div class="flex items-center gap-3">
              <img :src="avatarSrc" alt="avatar" class="h-12 w-12 rounded-2xl object-cover ring-2 ring-white/10" />
              <div>
                <p class="text-sm font-semibold">{{ displayName }}</p>
                <p class="text-xs text-slate-400">{{ roleLabel }}</p>
              </div>
            </div>
            <button
              type="button"
              class="mt-5 flex w-full items-center justify-center gap-2 rounded-2xl bg-white/10 px-4 py-3 text-sm font-medium text-white transition-all duration-300 hover:bg-white/15"
              @click="handleLogout"
            >
              <SwitchButton class="h-4 w-4" />
              退出登录
            </button>
          </div>
        </div>
      </aside>

      <main class="flex-1 px-6 py-6 lg:px-8 lg:py-8">
        <div class="space-y-6">
          <header class="flex flex-col gap-4 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7 xl:flex-row xl:items-center xl:justify-between">
            <div class="space-y-3">
              <div class="flex items-center gap-2 text-sm text-slate-400">
                <span>首页</span>
                <span>/</span>
                <span class="font-medium text-slate-500">{{ pageTitle }}</span>
              </div>
              <div>
                <h1 class="text-3xl font-semibold tracking-tight text-slate-900">{{ pageTitle }}</h1>
                <p class="mt-2 text-sm leading-6 text-slate-500">{{ pageDescription }}</p>
              </div>
            </div>

            <div class="grid gap-3 sm:grid-cols-2">
              <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 transition-all duration-300 hover:-translate-y-1 hover:bg-white hover:shadow-sm">
                <p class="text-xs font-medium uppercase tracking-[0.22em] text-slate-400">在线状态</p>
                <div class="mt-2 flex items-center gap-2 text-sm font-medium text-slate-700">
                  <span class="h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
                  {{ userStore.authInitializing ? '同步登录状态中' : '工作台运行正常' }}
                </div>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 transition-all duration-300 hover:-translate-y-1 hover:bg-white hover:shadow-sm">
                <p class="text-xs font-medium uppercase tracking-[0.22em] text-slate-400">当前身份</p>
                <div class="mt-2 inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
                  {{ roleLabel }}
                </div>
              </div>
            </div>
          </header>

          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>