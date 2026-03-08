<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-r from-zinc-950 via-slate-900 to-orange-700 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-orange-100">
            平台公告
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">管理全局公告与置顶通知</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">这里维护 class_id 为空的平台级公告，适合发布系统通知、维护公告和全站提醒。</p>
        </div>

        <div class="grid w-full max-w-md gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">公告总数</p>
            <p class="mt-2 text-3xl font-semibold">{{ announcements.length }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">置顶公告</p>
            <p class="mt-2 text-3xl font-semibold">{{ pinnedCount }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">停用公告</p>
            <p class="mt-2 text-3xl font-semibold">{{ inactiveCount }}</p>
          </div>
        </div>
      </div>
    </section>

    <div class="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div class="border-b border-slate-100 pb-5">
          <h3 class="text-xl font-semibold text-slate-900">{{ editingId ? '编辑平台公告' : '新建平台公告' }}</h3>
          <p class="mt-1 text-sm text-slate-500">支持置顶和停用状态，停用公告仅在勾选“显示停用公告”时出现。</p>
        </div>

        <form class="mt-6 space-y-5" @submit.prevent="handleSubmit">
          <label class="block space-y-2">
            <span class="text-sm font-medium text-slate-700">公告标题</span>
            <input
              v-model.trim="form.title"
              type="text"
              maxlength="120"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-orange-500 focus:bg-white"
              placeholder="例如：平台维护通知"
            />
          </label>

          <label class="block space-y-2">
            <span class="text-sm font-medium text-slate-700">公告内容</span>
            <textarea
              v-model.trim="form.content"
              rows="8"
              class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-orange-500 focus:bg-white"
              placeholder="请输入平台级公告内容"
            ></textarea>
          </label>

          <label class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            <input v-model="form.is_pinned" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-orange-600" />
            置顶显示
          </label>

          <label class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-orange-600" />
            保持为启用状态
          </label>

          <div class="flex items-center justify-end gap-3">
            <button
              v-if="editingId"
              type="button"
              class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
              @click="resetForm"
            >
              取消编辑
            </button>
            <button
              type="submit"
              class="rounded-2xl bg-orange-600 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-orange-700 disabled:cursor-not-allowed disabled:bg-orange-400"
              :disabled="saving"
            >
              {{ saving ? '提交中...' : editingId ? '保存修改' : '发布公告' }}
            </button>
          </div>
        </form>
      </section>

      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">公告列表</h3>
            <p class="mt-1 text-sm text-slate-500">支持关键字搜索，并可切换查看停用公告。</p>
          </div>
          <div class="flex flex-wrap gap-3">
            <input
              v-model.trim="keyword"
              type="text"
              class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-orange-500 focus:bg-white"
              placeholder="搜索标题或内容"
            />
            <label class="flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
              <input v-model="includeInactive" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-orange-600" />
              显示停用公告
            </label>
            <button
              type="button"
              class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
              :disabled="loading"
              @click="loadAnnouncements"
            >
              {{ loading ? '刷新中...' : '刷新列表' }}
            </button>
          </div>
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
            :class="announcement.is_active ? 'border-slate-200 bg-white' : 'border-rose-200 bg-rose-50/40'"
          >
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <span v-if="announcement.is_pinned" class="rounded-full bg-orange-100 px-3 py-1 text-xs font-medium text-orange-700">置顶</span>
                  <span class="rounded-full px-3 py-1 text-xs font-medium" :class="announcement.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'">
                    {{ announcement.is_active ? '启用中' : '已停用' }}
                  </span>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{{ formatDateTime(announcement.created_at) }}</span>
                </div>
                <h4 class="mt-3 text-lg font-semibold text-slate-900">{{ announcement.title }}</h4>
                <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ announcement.content }}</p>
              </div>

              <div class="flex gap-3">
                <button
                  type="button"
                  class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                  @click="startEdit(announcement)"
                >
                  编辑
                </button>
                <button
                  type="button"
                  class="rounded-2xl bg-rose-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-rose-700 disabled:cursor-not-allowed disabled:bg-rose-400"
                  :disabled="deletingId === announcement.id"
                  @click="handleDelete(announcement.id)"
                >
                  {{ deletingId === announcement.id ? '处理中...' : '停用公告' }}
                </button>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
          <h4 class="text-lg font-semibold text-slate-900">暂无平台公告</h4>
          <p class="mt-2 text-sm leading-6 text-slate-500">发布后会出现在全站公告列表中。</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  createPlatformAnnouncement,
  deletePlatformAnnouncement,
  listPlatformAnnouncements,
  type AnnouncementItem,
  updatePlatformAnnouncement,
} from '@/services/announcements';

const loading = ref(false);
const saving = ref(false);
const deletingId = ref<number | null>(null);
const editingId = ref<number | null>(null);
const includeInactive = ref(false);
const keyword = ref('');
const announcements = ref<AnnouncementItem[]>([]);

const form = reactive({
  title: '',
  content: '',
  is_pinned: false,
  is_active: true,
});

const pinnedCount = computed(() => announcements.value.filter((item) => item.is_pinned).length);
const inactiveCount = computed(() => announcements.value.filter((item) => !item.is_active).length);

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

const resetForm = () => {
  editingId.value = null;
  form.title = '';
  form.content = '';
  form.is_pinned = false;
  form.is_active = true;
};

const loadAnnouncements = async () => {
  loading.value = true;
  try {
    announcements.value = await listPlatformAnnouncements({
      include_inactive: includeInactive.value,
      keyword: keyword.value || undefined,
    });
  } finally {
    loading.value = false;
  }
};

const startEdit = (announcement: AnnouncementItem) => {
  editingId.value = announcement.id;
  form.title = announcement.title;
  form.content = announcement.content;
  form.is_pinned = announcement.is_pinned;
  form.is_active = announcement.is_active;
};

const handleSubmit = async () => {
  if (!form.title.trim() || !form.content.trim()) {
    ElMessage.warning('请先填写完整的公告标题和内容');
    return;
  }

  saving.value = true;
  try {
    const payload = {
      title: form.title.trim(),
      content: form.content.trim(),
      is_pinned: form.is_pinned,
      is_active: form.is_active,
    };

    if (editingId.value) {
      await updatePlatformAnnouncement(editingId.value, payload);
      ElMessage.success('平台公告已更新');
    } else {
      await createPlatformAnnouncement(payload);
      ElMessage.success('平台公告已发布');
    }

    resetForm();
    await loadAnnouncements();
  } finally {
    saving.value = false;
  }
};

const handleDelete = async (announcementId: number) => {
  await ElMessageBox.confirm('该操作会将平台公告停用，是否继续？', '确认停用', {
    type: 'warning',
    confirmButtonText: '停用',
    cancelButtonText: '取消',
  });

  deletingId.value = announcementId;
  try {
    await deletePlatformAnnouncement(announcementId);
    ElMessage.success('平台公告已停用');
    if (editingId.value === announcementId) {
      resetForm();
    }
    await loadAnnouncements();
  } finally {
    deletingId.value = null;
  }
};

onMounted(() => {
  loadAnnouncements();
});
</script>