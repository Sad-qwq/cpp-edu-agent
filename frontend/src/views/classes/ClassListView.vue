<template>
  <div class="space-y-6">
    <section class="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
      <div class="relative overflow-hidden rounded-[30px] bg-[radial-gradient(circle_at_top_right,_rgba(37,99,235,0.24),_transparent_26%),linear-gradient(135deg,_#0f172a,_#123153_44%,_#2563eb_100%)] p-6 text-white shadow-[0_24px_70px_rgba(15,23,42,0.16)] sm:p-7">
        <div class="app-orb left-[-2rem] top-[-2rem] h-36 w-36 bg-blue-300/16"></div>
        <div class="app-orb bottom-[-3rem] right-[-1rem] h-44 w-44 bg-cyan-300/16"></div>
        <div class="space-y-4">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-blue-100">
            班级工作台
          </div>
          <h2 class="text-2xl font-semibold tracking-tight">{{ heroTitle }}</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">{{ heroDescription }}</p>
        </div>

        <div class="mt-6 grid gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">班级数量</p>
            <p class="mt-2 text-3xl font-semibold">{{ classes.length }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">当前身份</p>
            <p class="mt-2 text-3xl font-semibold">{{ roleLabel }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">最近同步</p>
            <p class="mt-2 text-3xl font-semibold">{{ lastUpdated }}</p>
          </div>
        </div>
      </div>

      <div class="app-panel rounded-[30px] p-6 sm:p-7">
        <div v-if="isTeachingRole" class="space-y-5">
          <div>
            <p class="text-sm font-medium uppercase tracking-[0.22em] text-blue-600">Create Class</p>
            <h3 class="mt-2 text-xl font-semibold text-slate-900">创建新班级</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">创建班级后系统会自动生成邀请码，学生可通过邀请码加入。</p>
          </div>

          <form class="space-y-4" @submit.prevent="handleCreateClass">
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-700">班级名称</label>
              <input
                v-model="createForm.name"
                type="text"
                placeholder="例如：2026 春季 C++ 提高班"
                class="h-[52px] w-full rounded-2xl border border-slate-200/80 bg-white/80 px-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
              />
            </div>

            <button
              type="submit"
              class="flex h-[52px] w-full items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,_#2563eb,_#1d4ed8,_#0f766e)] px-4 text-sm font-semibold text-white shadow-[0_16px_36px_rgba(37,99,235,0.22)] transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_20px_46px_rgba(37,99,235,0.28)] disabled:translate-y-0 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="createLoading"
            >
              <span v-if="createLoading" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
              {{ createLoading ? '创建中...' : '创建班级' }}
            </button>
          </form>
        </div>

        <div v-else class="space-y-5">
          <div>
            <p class="text-sm font-medium uppercase tracking-[0.22em] text-blue-600">Join Class</p>
            <h3 class="mt-2 text-xl font-semibold text-slate-900">通过邀请码加入班级</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">输入教师提供的邀请码，先预览班级信息，再决定是否加入。</p>
          </div>

          <form class="space-y-4" @submit.prevent="handlePreviewClass">
            <div class="space-y-2">
              <label class="text-sm font-medium text-slate-700">邀请码</label>
              <input
                v-model="joinForm.inviteCode"
                type="text"
                maxlength="6"
                placeholder="例如：A1B2C3"
                class="h-[52px] w-full rounded-2xl border border-slate-200/80 bg-white/80 px-4 text-sm uppercase tracking-[0.2em] text-slate-800 outline-none transition-all duration-300 placeholder:tracking-normal placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
              />
            </div>

            <button
              type="submit"
              class="flex h-[52px] w-full items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,_#2563eb,_#1d4ed8,_#0f766e)] px-4 text-sm font-semibold text-white shadow-[0_16px_36px_rgba(37,99,235,0.22)] transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_20px_46px_rgba(37,99,235,0.28)] disabled:translate-y-0 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="previewLoading"
            >
              <span v-if="previewLoading" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
              {{ previewLoading ? '预览中...' : '预览班级' }}
            </button>
          </form>

          <div v-if="previewClassroom" class="rounded-[24px] border border-slate-200/80 bg-[linear-gradient(180deg,_rgba(239,246,255,0.78)_0%,_rgba(255,255,255,0.82)_100%)] p-4 shadow-sm">
            <div class="flex items-start justify-between gap-4">
              <div>
                <h4 class="text-base font-semibold text-slate-900">{{ previewClassroom.name }}</h4>
                <p class="mt-2 text-sm text-slate-500">教师：{{ previewClassroom.teacher_name || '未提供' }}</p>
              </div>
              <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
                {{ previewClassroom.already_joined ? '已加入' : '可加入' }}
              </span>
            </div>

            <div class="mt-4 flex gap-3">
              <button
                type="button"
                class="flex-1 rounded-2xl bg-[linear-gradient(135deg,_#2563eb,_#1d4ed8,_#0f766e)] px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:shadow-sm"
                @click="handleJoinClass"
              >
                {{ previewClassroom.already_joined ? '进入班级' : '确认加入' }}
              </button>
              <button
                type="button"
                class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                @click="previewClassroom = null"
              >
                清除
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="app-panel rounded-[30px] p-6 sm:p-7">
      <div class="flex flex-col gap-3 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-xl font-semibold text-slate-900">{{ listTitle }}</h2>
          <p class="mt-1 text-sm text-slate-500">{{ listDescription }}</p>
        </div>
        <button
          type="button"
          class="inline-flex items-center justify-center rounded-2xl bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 transition-all duration-300 hover:-translate-y-1 hover:bg-blue-100 hover:shadow-sm"
          @click="loadClasses"
        >
          刷新列表
        </button>
      </div>

      <div v-if="loading" class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div v-for="index in 3" :key="index" class="animate-pulse rounded-[24px] border border-slate-200 bg-slate-50 p-6">
          <div class="h-5 w-32 rounded bg-slate-200"></div>
          <div class="mt-4 h-4 w-24 rounded bg-slate-200"></div>
          <div class="mt-8 grid grid-cols-2 gap-3">
            <div class="h-16 rounded-2xl bg-slate-200"></div>
            <div class="h-16 rounded-2xl bg-slate-200"></div>
          </div>
        </div>
      </div>

      <div v-else-if="classes.length" class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="classroom in classes"
          :key="classroom.id"
          class="app-panel cursor-pointer rounded-[26px] p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_22px_52px_rgba(15,23,42,0.12)]"
          @click="router.push(`/classes/${classroom.id}`)"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">班级</p>
              <h3 class="mt-3 text-xl font-semibold text-slate-900">{{ classroom.name }}</h3>
            </div>
            <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700 shadow-sm shadow-emerald-100/60">活跃</span>
          </div>

          <div class="mt-5 grid grid-cols-2 gap-3">
            <div class="rounded-2xl bg-slate-50/80 p-4">
              <p class="text-xs text-slate-400">邀请码</p>
              <p class="mt-2 text-lg font-semibold tracking-[0.18em] text-slate-900">{{ classroom.invite_code }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50/80 p-4">
              <p class="text-xs text-slate-400">教师</p>
              <p class="mt-2 text-lg font-semibold text-slate-900">{{ classroom.teacher_name || '待查看' }}</p>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between text-sm text-slate-500">
            <span>成员 {{ classroom.student_count ?? 0 }}</span>
            <span>作业 {{ classroom.assignment_count ?? 0 }}</span>
          </div>

          <div class="mt-5 border-t border-slate-100 pt-4 text-sm text-slate-400">
            创建时间：{{ formatDate(classroom.created_at) }}
          </div>
        </article>
      </div>

      <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50/80 px-6 py-12 text-center">
        <h3 class="text-lg font-semibold text-slate-900">{{ emptyTitle }}</h3>
        <p class="mt-2 text-sm leading-6 text-slate-500">{{ emptyDescription }}</p>
      </div>

      <div v-if="errorMessage" class="mt-4 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
        {{ errorMessage }}
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '@/api/request';
import { useUserStore } from '@/stores/user';

interface ClassroomItem {
  id: number;
  name: string;
  invite_code: string;
  teacher_id: number;
  teacher_name?: string | null;
  is_active: boolean;
  created_at: string;
  student_count?: number | null;
  assignment_count?: number | null;
  already_joined?: boolean | null;
}

const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);
const previewLoading = ref(false);
const createLoading = ref(false);
const errorMessage = ref('');
const lastUpdated = ref('--');
const classes = ref<ClassroomItem[]>([]);
const previewClassroom = ref<ClassroomItem | null>(null);

const createForm = reactive({
  name: '',
});

const joinForm = reactive({
  inviteCode: '',
});

const isTeachingRole = computed(() => userStore.user.role === 'teacher' || userStore.user.role === 'admin');
const roleLabel = computed(() => isTeachingRole.value ? '教师端' : '学生端');
const heroTitle = computed(() => isTeachingRole.value ? '创建并管理班级，统一组织作业、公告与成员。' : '通过邀请码加入班级，开始参与 C++ 学习任务。');
const heroDescription = computed(() => isTeachingRole.value
  ? '教师与管理员可以在这里创建班级、分发邀请码，并进入具体班级查看成员与公告。'
  : '学生可以预览邀请码对应的班级，确认无误后加入，并进入班级查看公告与后续作业。');
const listTitle = computed(() => isTeachingRole.value ? '我管理的班级' : '我加入的班级');
const listDescription = computed(() => isTeachingRole.value
  ? '这里展示当前账号创建的全部活跃班级。'
  : '这里展示当前账号已经加入且仍在激活状态的班级。');
const emptyTitle = computed(() => isTeachingRole.value ? '还没有创建任何班级' : '还没有加入任何班级');
const emptyDescription = computed(() => isTeachingRole.value
  ? '先创建第一个班级，系统会自动生成邀请码供学生加入。'
  : '输入教师提供的邀请码进行预览并加入班级。');

const formatDate = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date);
};

const updateLastUpdated = () => {
  lastUpdated.value = new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date());
};

const normalizeInviteCode = (value: string) => value.trim().toUpperCase();

const loadClasses = async () => {
  loading.value = true;
  errorMessage.value = '';

  try {
    const endpoint = isTeachingRole.value ? '/classes/teaching' : '/classes/my';
    classes.value = await request.get(endpoint) as ClassroomItem[];
    updateLastUpdated();
  } catch (error) {
    classes.value = [];
    errorMessage.value = '班级列表加载失败，请稍后重试。';
  } finally {
    loading.value = false;
  }
};

const handleCreateClass = async () => {
  if (!createForm.name.trim()) {
    ElMessage.warning('请输入班级名称');
    return;
  }

  createLoading.value = true;
  try {
    const created = await request.post('/classes', {
      name: createForm.name.trim(),
    }) as ClassroomItem;
    ElMessage.success('班级创建成功');
    createForm.name = '';
    await loadClasses();
    router.push(`/classes/${created.id}`);
  } finally {
    createLoading.value = false;
  }
};

const handlePreviewClass = async () => {
  const inviteCode = normalizeInviteCode(joinForm.inviteCode);
  if (!inviteCode) {
    ElMessage.warning('请输入邀请码');
    return;
  }

  previewLoading.value = true;
  try {
    previewClassroom.value = await request.get('/classes/join/preview', {
      params: { invite_code: inviteCode },
    }) as ClassroomItem;
    joinForm.inviteCode = inviteCode;
  } finally {
    previewLoading.value = false;
  }
};

const handleJoinClass = async () => {
  if (!previewClassroom.value) {
    return;
  }

  if (previewClassroom.value.already_joined) {
    router.push(`/classes/${previewClassroom.value.id}`);
    return;
  }

  const joined = await request.post('/classes/join', {
    invite_code: joinForm.inviteCode,
  }) as ClassroomItem;
  ElMessage.success('已成功加入班级');
  previewClassroom.value = null;
  joinForm.inviteCode = '';
  await loadClasses();
  router.push(`/classes/${joined.id}`);
};

onMounted(() => {
  loadClasses();
});
</script>