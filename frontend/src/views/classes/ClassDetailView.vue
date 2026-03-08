<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-blue-100">
            班级详情
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">{{ classroom?.name || '班级加载中' }}</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">邀请码、公告、成员和作业概览都会以班级为中心统一呈现。</p>
        </div>

        <div class="grid w-full max-w-md grid-cols-2 gap-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">学生人数</p>
            <p class="mt-2 text-3xl font-semibold">{{ classroom?.student_count ?? 0 }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">作业数量</p>
            <p class="mt-2 text-3xl font-semibold">{{ classroom?.assignment_count ?? 0 }}</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="loading" class="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
      <div class="animate-pulse rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
        <div class="h-6 w-36 rounded bg-slate-200"></div>
        <div class="mt-4 h-4 w-56 rounded bg-slate-200"></div>
        <div class="mt-6 grid gap-3 sm:grid-cols-3">
          <div class="h-20 rounded-2xl bg-slate-100"></div>
          <div class="h-20 rounded-2xl bg-slate-100"></div>
          <div class="h-20 rounded-2xl bg-slate-100"></div>
        </div>
      </div>
      <div class="animate-pulse rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
        <div class="h-6 w-28 rounded bg-slate-200"></div>
        <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
        <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
      </div>
    </section>

    <section v-else-if="classroom" class="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
      <div class="space-y-4">
        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">班级概览</h3>
              <p class="mt-2 text-sm leading-6 text-slate-500">这是当前班级的基础信息和后端统计快照。</p>
            </div>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-2xl bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 transition-all duration-300 hover:-translate-y-1 hover:bg-blue-100"
              @click="loadClassroom"
            >
              刷新详情
            </button>
          </div>

          <div class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">邀请码</p>
              <p class="mt-2 text-xl font-semibold tracking-[0.18em] text-slate-900">{{ classroom.invite_code }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">教师</p>
              <p class="mt-2 text-xl font-semibold text-slate-900">{{ classroom.teacher_name || '未提供' }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">学生人数</p>
              <p class="mt-2 text-xl font-semibold text-slate-900">{{ classroom.student_count ?? 0 }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">作业数量</p>
              <p class="mt-2 text-xl font-semibold text-slate-900">{{ classroom.assignment_count ?? 0 }}</p>
            </div>
          </div>
        </div>

        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">班级公告</h3>
              <p class="mt-1 text-sm text-slate-500">展示当前班级中已发布的公告内容。</p>
            </div>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-2xl bg-sky-50 px-4 py-2 text-sm font-medium text-sky-700 transition-all duration-300 hover:-translate-y-1 hover:bg-sky-100"
              @click="router.push(`/classes/${classId}/announcements`)"
            >
              进入公告中心
            </button>
          </div>

          <div v-if="announcementLoading" class="mt-6 space-y-4">
            <div v-for="index in 2" :key="index" class="animate-pulse rounded-2xl bg-slate-50 p-5">
              <div class="h-5 w-40 rounded bg-slate-200"></div>
              <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
              <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
            </div>
          </div>

          <div v-else-if="announcements.length" class="mt-6 space-y-4">
            <article
              v-for="announcement in announcements"
              :key="announcement.id"
              class="rounded-2xl border border-slate-200 bg-slate-50 p-5"
            >
              <div class="flex items-start justify-between gap-4">
                <div>
                  <div class="flex items-center gap-2">
                    <h4 class="text-base font-semibold text-slate-900">{{ announcement.title }}</h4>
                    <span v-if="announcement.is_pinned" class="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">置顶</span>
                  </div>
                  <p class="mt-2 text-sm leading-6 text-slate-600">{{ announcement.content }}</p>
                </div>
                <span class="text-xs text-slate-400">{{ formatDateTime(announcement.created_at) }}</span>
              </div>
            </article>
          </div>

          <div v-else class="mt-8 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-6 py-10 text-center">
            <p class="text-sm font-medium text-slate-700">当前班级还没有公告</p>
            <p class="mt-2 text-sm text-slate-400">教师或管理员发布公告后，这里会自动展示。</p>
          </div>
        </div>

        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">班级作业</h3>
              <p class="mt-1 text-sm text-slate-500">查看当前班级已发布的作业，并进入完整作业工作区。</p>
            </div>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-2xl bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 transition-all duration-300 hover:-translate-y-1 hover:bg-blue-100"
              @click="router.push(`/classes/${classId}/assignments`)"
            >
              查看全部作业
            </button>
          </div>

          <div v-if="assignmentsLoading" class="mt-6 space-y-3">
            <div v-for="index in 2" :key="index" class="animate-pulse rounded-2xl bg-slate-50 p-4">
              <div class="h-5 w-36 rounded bg-slate-200"></div>
              <div class="mt-3 h-4 w-full rounded bg-slate-200"></div>
            </div>
          </div>

          <div v-else-if="assignments.length" class="mt-6 space-y-3">
            <button
              v-for="assignment in assignments.slice(0, 3)"
              :key="assignment.id"
              type="button"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 p-4 text-left transition-all duration-300 hover:-translate-y-1 hover:border-blue-200 hover:bg-white"
              @click="router.push(`/assignments/${assignment.id}`)"
            >
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-sm font-semibold text-slate-900">{{ assignment.title }}</p>
                  <p class="mt-1 text-sm text-slate-500">{{ assignment.description || '暂无作业说明' }}</p>
                </div>
                <span class="rounded-full px-3 py-1 text-xs font-medium" :class="assignment.my_submitted ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'">
                  {{ assignment.my_submitted ? '已提交' : '待完成' }}
                </span>
              </div>
            </button>
          </div>

          <div v-else class="mt-8 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-6 py-10 text-center">
            <p class="text-sm font-medium text-slate-700">当前班级还没有作业</p>
            <p class="mt-2 text-sm text-slate-400">可以从班级作业页继续创建或查看后续任务。</p>
          </div>
        </div>

        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">班级资料</h3>
              <p class="mt-1 text-sm text-slate-500">课件、讲义和视频资料统一在班级资料库中管理。</p>
            </div>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-2xl bg-cyan-50 px-4 py-2 text-sm font-medium text-cyan-700 transition-all duration-300 hover:-translate-y-1 hover:bg-cyan-100"
              @click="router.push(`/classes/${classId}/materials`)"
            >
              进入资料库
            </button>
          </div>
        </div>

        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">班级讨论</h3>
              <p class="mt-1 text-sm text-slate-500">学生提问、教师答疑和最佳答案采纳都在这里沉淀。</p>
            </div>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-2xl bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-100"
              @click="router.push(`/classes/${classId}/discussions`)"
            >
              进入讨论区
            </button>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div v-if="canManageAnnouncements" class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">发布公告</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">面向当前班级发布重要通知，学生会在公告区和通知系统中看到更新。</p>
          </div>

          <form class="mt-5 space-y-4" @submit.prevent="handleCreateAnnouncement">
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-700">公告标题</label>
              <input
                v-model="announcementForm.title"
                type="text"
                placeholder="例如：本周实验提交说明"
                class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
              />
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-700">公告内容</label>
              <textarea
                v-model="announcementForm.content"
                rows="5"
                placeholder="输入需要向班级同步的内容"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
              ></textarea>
            </div>

            <label class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
              <input v-model="announcementForm.is_pinned" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-blue-600" />
              将这条公告置顶显示
            </label>

            <button
              type="submit"
              class="flex h-[52px] w-full items-center justify-center gap-2 rounded-2xl bg-blue-600 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:bg-blue-700 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-blue-400"
              :disabled="createAnnouncementLoading"
            >
              <span v-if="createAnnouncementLoading" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
              {{ createAnnouncementLoading ? '发布中...' : '发布公告' }}
            </button>
          </form>
        </div>

        <div v-if="canViewStudents" class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex items-center justify-between gap-4 border-b border-slate-100 pb-5">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">班级成员</h3>
              <p class="mt-1 text-sm text-slate-500">仅教师和管理员可查看学生名单。</p>
            </div>
            <div class="flex items-center gap-3">
              <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">{{ students.length }} 人</span>
              <button
                type="button"
                class="inline-flex items-center justify-center rounded-2xl bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 transition-all duration-300 hover:-translate-y-1 hover:bg-blue-100"
                @click="router.push(`/classes/${classId}/members`)"
              >
                成员管理
              </button>
            </div>
          </div>

          <div v-if="studentsLoading" class="mt-6 space-y-3">
            <div v-for="index in 4" :key="index" class="animate-pulse rounded-2xl bg-slate-50 p-4">
              <div class="h-4 w-24 rounded bg-slate-200"></div>
              <div class="mt-2 h-4 w-36 rounded bg-slate-200"></div>
            </div>
          </div>

          <div v-else-if="students.length" class="mt-6 space-y-3">
            <div v-for="student in students" :key="student.id" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-sm font-semibold text-slate-900">{{ student.username || '未命名用户' }}</p>
              <p class="mt-1 text-sm text-slate-500">{{ student.email || '未提供邮箱' }}</p>
            </div>
          </div>

          <div v-else class="mt-8 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-6 py-10 text-center">
            <p class="text-sm font-medium text-slate-700">班级中还没有学生</p>
            <p class="mt-2 text-sm text-slate-400">学生通过邀请码加入后，这里会展示成员名单。</p>
          </div>
        </div>
      </div>
    </section>

    <section v-else class="rounded-[28px] border border-dashed border-slate-200 bg-white px-6 py-16 text-center shadow-sm">
      <h3 class="text-lg font-semibold text-slate-900">无法加载班级详情</h3>
      <p class="mt-2 text-sm text-slate-500">这个班级可能不存在，或者当前账号没有查看权限。</p>
      <button
        type="button"
        class="mt-6 inline-flex items-center justify-center rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-blue-700"
        @click="router.push('/classes')"
      >
        返回班级列表
      </button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '@/api/request';
import { useUserStore, type UserProfile } from '@/stores/user';
import { getClassroomDetail, listClassStudents, type ClassroomDetail } from '@/services/classes';

interface AnnouncementItem {
  id: number;
  class_id?: number | null;
  title: string;
  content: string;
  is_pinned: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by: number;
}

interface AssignmentPreviewItem {
  id: number;
  title: string;
  description?: string | null;
  due_date?: string | null;
  created_at: string;
  classroom_id: number;
  my_submitted?: boolean | null;
  my_score?: number | null;
}

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);
const announcementLoading = ref(false);
const studentsLoading = ref(false);
const createAnnouncementLoading = ref(false);
const classroom = ref<ClassroomDetail | null>(null);
const announcements = ref<AnnouncementItem[]>([]);
const students = ref<UserProfile[]>([]);
const assignmentsLoading = ref(false);
const assignments = ref<AssignmentPreviewItem[]>([]);

const announcementForm = reactive({
  title: '',
  content: '',
  is_pinned: false,
});

const classId = computed(() => Number(route.params.id));
const canViewStudents = computed(() => userStore.user.role === 'teacher' || userStore.user.role === 'admin');
const canManageAnnouncements = computed(() => userStore.user.role === 'teacher' || userStore.user.role === 'admin');

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

const loadStudents = async () => {
  if (!canViewStudents.value) {
    students.value = [];
    return;
  }

  studentsLoading.value = true;
  try {
    students.value = await listClassStudents(classId.value) as UserProfile[];
  } finally {
    studentsLoading.value = false;
  }
};

const loadAnnouncements = async () => {
  announcementLoading.value = true;
  try {
    announcements.value = await request.get(`/classes/${classId.value}/announcements`) as AnnouncementItem[];
  } finally {
    announcementLoading.value = false;
  }
};

const loadAssignments = async () => {
  assignmentsLoading.value = true;
  try {
    assignments.value = await request.get('/assignments', {
      params: { classroom_id: classId.value },
      suppressErrorMessage: true,
    }) as AssignmentPreviewItem[];
  } finally {
    assignmentsLoading.value = false;
  }
};

const loadClassroom = async () => {
  if (!classId.value) {
    classroom.value = null;
    return;
  }

  loading.value = true;
  try {
    classroom.value = await getClassroomDetail(classId.value);
    await Promise.all([loadAnnouncements(), loadStudents(), loadAssignments()]);
  } catch (error) {
    classroom.value = null;
  } finally {
    loading.value = false;
  }
};

const handleCreateAnnouncement = async () => {
  if (!announcementForm.title.trim() || !announcementForm.content.trim()) {
    ElMessage.warning('请填写完整的公告标题和内容');
    return;
  }

  createAnnouncementLoading.value = true;
  try {
    await request.post(`/classes/${classId.value}/announcements`, {
      title: announcementForm.title.trim(),
      content: announcementForm.content.trim(),
      is_pinned: announcementForm.is_pinned,
      is_active: true,
    });
    ElMessage.success('公告发布成功');
    announcementForm.title = '';
    announcementForm.content = '';
    announcementForm.is_pinned = false;
    await loadAnnouncements();
  } finally {
    createAnnouncementLoading.value = false;
  }
};

onMounted(() => {
  loadClassroom();
});
</script>