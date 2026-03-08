<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-r from-blue-950 via-sky-900 to-cyan-700 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-cyan-100">
            班级公告中心
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">{{ className || '班级公告' }}</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">集中查看本班公告。教师和管理员可以在这里发布、编辑和删除公告，学生则能按时间浏览班级通知。</p>
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
            <p class="text-xs text-slate-300">我的权限</p>
            <p class="mt-2 text-xl font-semibold">{{ canManage ? '可管理' : '只读' }}</p>
          </div>
        </div>
      </div>
    </section>

    <div class="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <section v-if="canManage" class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div class="border-b border-slate-100 pb-5">
          <h3 class="text-xl font-semibold text-slate-900">{{ editingId ? '编辑公告' : '发布公告' }}</h3>
          <p class="mt-1 text-sm text-slate-500">公告发布后会在班级详情和通知中心同步可见。</p>
        </div>

        <form class="mt-6 space-y-5" @submit.prevent="handleSubmit">
          <label class="block space-y-2">
            <span class="text-sm font-medium text-slate-700">公告标题</span>
            <input
              v-model.trim="form.title"
              type="text"
              maxlength="120"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white"
              placeholder="例如：实验二提交时间调整"
            />
          </label>

          <label class="block space-y-2">
            <span class="text-sm font-medium text-slate-700">公告内容</span>
            <textarea
              v-model.trim="form.content"
              rows="8"
              class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white"
              placeholder="请输入要同步给班级成员的内容"
            ></textarea>
          </label>

          <label class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
            <input v-model="form.is_pinned" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-sky-600" />
            置顶显示这条公告
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
              class="rounded-2xl bg-sky-600 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-sky-400"
              :disabled="saving"
            >
              {{ saving ? '提交中...' : editingId ? '保存修改' : '发布公告' }}
            </button>
          </div>
        </form>
      </section>

      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7" :class="canManage ? '' : 'xl:col-span-2'">
        <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">公告列表</h3>
            <p class="mt-1 text-sm text-slate-500">默认按置顶优先、发布时间倒序排列。</p>
          </div>
          <button
            type="button"
            class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
            :disabled="loading"
            @click="loadAnnouncements"
          >
            {{ loading ? '刷新中...' : '刷新列表' }}
          </button>
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
            :class="announcement.is_pinned ? 'border-sky-200 bg-sky-50/50' : 'border-slate-200 bg-white'"
          >
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <span v-if="announcement.is_pinned" class="rounded-full bg-sky-100 px-3 py-1 text-xs font-medium text-sky-700">置顶</span>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{{ formatDateTime(announcement.created_at) }}</span>
                </div>
                <h4 class="mt-3 text-lg font-semibold text-slate-900">{{ announcement.title }}</h4>
                <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ announcement.content }}</p>
              </div>

              <div v-if="canManage" class="flex gap-3">
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
                  {{ deletingId === announcement.id ? '删除中...' : '删除' }}
                </button>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
          <h4 class="text-lg font-semibold text-slate-900">还没有班级公告</h4>
          <p class="mt-2 text-sm leading-6 text-slate-500">教师发布公告后，这里会自动同步展示。</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import request from '@/api/request';
import { useUserStore } from '@/stores/user';
import {
  createClassAnnouncement,
  deleteClassAnnouncement,
  listClassAnnouncements,
  type AnnouncementItem,
  updateClassAnnouncement,
} from '@/services/announcements';

const route = useRoute();
const userStore = useUserStore();

const classId = computed(() => Number(route.params.id));
const className = ref('');
const loading = ref(false);
const saving = ref(false);
const deletingId = ref<number | null>(null);
const editingId = ref<number | null>(null);
const announcements = ref<AnnouncementItem[]>([]);

const form = reactive({
  title: '',
  content: '',
  is_pinned: false,
});

const canManage = computed(() => userStore.user.role === 'teacher' || userStore.user.role === 'admin');
const pinnedCount = computed(() => announcements.value.filter((item) => item.is_pinned).length);

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
};

const loadClassInfo = async () => {
  const detail = await request.get(`/classes/${classId.value}`, {
    suppressErrorMessage: true,
  }) as { name?: string };
  className.value = detail.name || '';
};

const loadAnnouncements = async () => {
  loading.value = true;
  try {
    announcements.value = await listClassAnnouncements(classId.value, { limit: 100 });
  } finally {
    loading.value = false;
  }
};

const startEdit = (announcement: AnnouncementItem) => {
  editingId.value = announcement.id;
  form.title = announcement.title;
  form.content = announcement.content;
  form.is_pinned = announcement.is_pinned;
};

const handleSubmit = async () => {
  if (!form.title.trim() || !form.content.trim()) {
    ElMessage.warning('请先填写完整的公告标题和内容');
    return;
  }

  saving.value = true;
  try {
    if (editingId.value) {
      await updateClassAnnouncement(classId.value, editingId.value, {
        title: form.title.trim(),
        content: form.content.trim(),
        is_pinned: form.is_pinned,
      });
      ElMessage.success('公告已更新');
    } else {
      await createClassAnnouncement(classId.value, {
        title: form.title.trim(),
        content: form.content.trim(),
        is_pinned: form.is_pinned,
        is_active: true,
      });
      ElMessage.success('公告已发布');
    }
    resetForm();
    await loadAnnouncements();
  } finally {
    saving.value = false;
  }
};

const handleDelete = async (announcementId: number) => {
  await ElMessageBox.confirm('删除后该公告将不再展示，是否继续？', '确认删除', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  });

  deletingId.value = announcementId;
  try {
    await deleteClassAnnouncement(classId.value, announcementId);
    ElMessage.success('公告已删除');
    if (editingId.value === announcementId) {
      resetForm();
    }
    await loadAnnouncements();
  } finally {
    deletingId.value = null;
  }
};

onMounted(async () => {
  await Promise.all([loadClassInfo(), loadAnnouncements()]);
});
</script>