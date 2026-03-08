<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-br from-slate-900 via-slate-800 to-orange-900 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-orange-100">
            通知中心
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">统一查看平台提醒与待办</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">这里汇总与你相关的公告提醒、作业通知和班级动态，便于快速处理未读信息。</p>
        </div>

        <div class="grid w-full max-w-md grid-cols-3 gap-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">通知总数</p>
            <p class="mt-2 text-3xl font-semibold">{{ notifications.length }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">未读通知</p>
            <p class="mt-2 text-3xl font-semibold">{{ unreadCount }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">当前身份</p>
            <p class="mt-2 text-xl font-semibold">{{ roleLabel }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
      <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-xl font-semibold text-slate-900">我的通知</h2>
          <p class="mt-1 text-sm text-slate-500">按时间倒序展示当前账号收到的最新通知。</p>
        </div>
        <div class="flex gap-3">
          <button
            type="button"
            class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
            @click="loadNotifications"
          >
            刷新列表
          </button>
          <button
            type="button"
            class="rounded-2xl bg-orange-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-orange-700 disabled:cursor-not-allowed disabled:bg-orange-400"
            :disabled="markingAll || unreadCount === 0"
            @click="handleMarkAllRead"
          >
            {{ markingAll ? '处理中...' : '全部标记已读' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="mt-6 space-y-4">
        <div v-for="index in 4" :key="index" class="animate-pulse rounded-[24px] border border-slate-200 bg-slate-50 p-6">
          <div class="h-5 w-48 rounded bg-slate-200"></div>
          <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
          <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
        </div>
      </div>

      <div v-else-if="notifications.length" class="mt-6 space-y-4">
        <article
          v-for="notification in notifications"
          :key="notification.id"
          class="rounded-[24px] border p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
          :class="notification.is_read ? 'border-slate-200 bg-white' : 'border-orange-200 bg-orange-50/60'"
        >
          <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span
                  class="rounded-full px-3 py-1 text-xs font-medium"
                  :class="notification.is_read ? 'bg-slate-100 text-slate-700' : 'bg-orange-100 text-orange-700'"
                >
                  {{ notification.is_read ? '已读' : '未读' }}
                </span>
                <span class="text-xs text-slate-400">{{ formatDateTime(notification.created_at) }}</span>
              </div>
              <h3 class="mt-4 text-xl font-semibold text-slate-900">{{ notification.title }}</h3>
              <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ notification.content }}</p>
            </div>

            <div class="flex gap-3">
              <button
                v-if="!notification.is_read"
                type="button"
                class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                @click="handleMarkRead(notification.id)"
              >
                标记已读
              </button>
              <button
                v-if="notification.link"
                type="button"
                class="rounded-2xl bg-orange-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-orange-700"
                @click="handleOpenLink(notification)"
              >
                查看详情
              </button>
            </div>
          </div>
        </article>
      </div>

      <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
        <h3 class="text-lg font-semibold text-slate-900">当前没有通知</h3>
        <p class="mt-2 text-sm leading-6 text-slate-500">后续班级公告、作业动态和系统提醒会在这里集中展示。</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { listNotifications, markAllNotificationsRead, markNotificationRead, type NotificationItem } from '@/services/notifications';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);
const markingAll = ref(false);
const notifications = ref<NotificationItem[]>([]);

const unreadCount = computed(() => notifications.value.filter((item) => !item.is_read).length);
const roleLabel = computed(() => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生',
  };

  return roleMap[userStore.user.role || ''] || '平台用户';
});

const formatDateTime = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

const loadNotifications = async () => {
  loading.value = true;
  try {
    notifications.value = await listNotifications({ limit: 100 });
  } finally {
    loading.value = false;
  }
};

const handleMarkRead = async (notificationId: number) => {
  const updated = await markNotificationRead(notificationId);
  notifications.value = notifications.value.map((item) => item.id === notificationId ? updated : item);
  ElMessage.success('已标记为已读');
};

const handleMarkAllRead = async () => {
  markingAll.value = true;
  try {
    const result = await markAllNotificationsRead();
    notifications.value = notifications.value.map((item) => ({ ...item, is_read: true }));
    ElMessage.success(`已处理 ${result.updated} 条通知`);
  } finally {
    markingAll.value = false;
  }
};

const handleOpenLink = async (notification: NotificationItem) => {
  if (!notification.is_read) {
    await handleMarkRead(notification.id);
  }
  if (notification.link) {
    router.push(notification.link);
  }
};

onMounted(() => {
  loadNotifications();
});
</script>