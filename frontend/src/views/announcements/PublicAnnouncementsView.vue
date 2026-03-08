<template>
  <div class="min-h-screen bg-slate-50 text-slate-800">
    <div class="mx-auto max-w-6xl px-6 py-10 lg:px-8">
      <section class="rounded-[32px] bg-gradient-to-r from-slate-950 via-slate-800 to-blue-900 p-8 text-white shadow-sm sm:p-10">
        <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div class="space-y-4">
            <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-blue-100">
              公共公告
            </div>
            <h1 class="text-4xl font-semibold tracking-tight">平台公告与系统通知</h1>
            <p class="max-w-2xl text-sm leading-7 text-slate-300">这里展示对所有访客和用户公开的最新平台公告，可在登录前直接查看系统维护、版本更新和全站通知。</p>
          </div>

          <div class="flex flex-wrap gap-3">
            <RouterLink
              to="/login"
              class="rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-slate-900 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
            >
              返回登录
            </RouterLink>
            <button
              type="button"
              class="rounded-2xl border border-white/15 bg-white/10 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-white/15"
              :disabled="loading"
              @click="loadAnnouncements"
            >
              {{ loading ? '刷新中...' : '刷新公告' }}
            </button>
          </div>
        </div>
      </section>

      <section class="mt-6 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-xl font-semibold text-slate-900">公开公告列表</h2>
            <p class="mt-1 text-sm text-slate-500">按置顶优先和发布时间倒序展示。</p>
          </div>
          <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">共 {{ announcements.length }} 条</span>
        </div>

        <div v-if="loading" class="mt-6 space-y-4">
          <div v-for="index in 4" :key="index" class="animate-pulse rounded-[24px] border border-slate-200 bg-slate-50 p-5">
            <div class="h-5 w-40 rounded bg-slate-200"></div>
            <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
            <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
          </div>
        </div>

        <div v-else-if="announcements.length" class="mt-6 space-y-4">
          <article
            v-for="announcement in announcements"
            :key="announcement.id"
            class="rounded-[24px] border p-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
            :class="announcement.is_pinned ? 'border-blue-200 bg-blue-50/50' : 'border-slate-200 bg-white'"
          >
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <span v-if="announcement.is_pinned" class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">置顶</span>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{{ formatDateTime(announcement.created_at) }}</span>
                </div>
                <h3 class="mt-3 text-lg font-semibold text-slate-900">{{ announcement.title }}</h3>
                <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ announcement.content }}</p>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
          <h3 class="text-lg font-semibold text-slate-900">当前没有公共公告</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">管理员发布平台级公开公告后，这里会自动展示。</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { listPublicAnnouncements, type AnnouncementItem } from '@/services/announcements';

const loading = ref(false);
const announcements = ref<AnnouncementItem[]>([]);

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

const loadAnnouncements = async () => {
  loading.value = true;
  try {
    announcements.value = await listPublicAnnouncements({ limit: 20 });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadAnnouncements();
});
</script>