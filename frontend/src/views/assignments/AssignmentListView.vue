<template>
  <div class="space-y-6">
    <section class="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
      <div class="rounded-[28px] bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 p-6 text-white shadow-sm sm:p-7">
        <div class="space-y-4">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-blue-100">
            班级作业
          </div>
          <h2 class="text-2xl font-semibold tracking-tight">{{ classroom?.name || '作业中心' }}</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">这里汇总当前班级的全部作业。学生可查看状态并进入作答，教师可发布新的作业任务。</p>
        </div>

        <div class="mt-6 grid gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">作业总数</p>
            <p class="mt-2 text-3xl font-semibold">{{ assignments.length }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">班级成员</p>
            <p class="mt-2 text-3xl font-semibold">{{ classroom?.student_count ?? 0 }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">教师</p>
            <p class="mt-2 text-xl font-semibold">{{ classroom?.teacher_name || '待同步' }}</p>
          </div>
        </div>
      </div>

      <div v-if="canManageAssignments" class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div>
          <p class="text-sm font-medium uppercase tracking-[0.22em] text-blue-600">Assignment Editor</p>
          <h3 class="mt-2 text-xl font-semibold text-slate-900">{{ editingAssignmentId ? '编辑作业' : '发布新作业' }}</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">在这里创建或更新作业，具体题目内容可进入作业详情继续维护。</p>
        </div>

        <button
          type="button"
          class="mt-5 flex w-full items-center justify-center rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-700"
          @click="router.push(`/classes/${classId}/ai-question-generation`)"
        >
          打开 AI 智能出题工作台
        </button>

        <form class="mt-5 space-y-4" @submit.prevent="handleSaveAssignment">
          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">作业标题</label>
            <input
              v-model="createForm.title"
              type="text"
              placeholder="例如：指针与引用综合练习"
              class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
            />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">作业说明</label>
            <textarea
              v-model="createForm.description"
              rows="4"
              placeholder="补充题目要求、提交说明或评分标准"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
            ></textarea>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">截止时间</label>
            <input
              v-model="createForm.due_date"
              type="datetime-local"
              class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
            />
          </div>

          <div class="flex gap-3">
            <button
              v-if="editingAssignmentId"
              type="button"
              class="flex h-[52px] flex-1 items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
              @click="resetCreateForm"
            >
              取消编辑
            </button>
            <button
              type="submit"
              class="flex h-[52px] flex-1 items-center justify-center gap-2 rounded-2xl bg-blue-600 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:bg-blue-700 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-blue-400"
              :disabled="createLoading"
            >
              <span v-if="createLoading" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
              {{ createLoading ? '处理中...' : editingAssignmentId ? '保存作业' : '创建作业' }}
            </button>
          </div>
        </form>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
      <div class="flex flex-col gap-3 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-xl font-semibold text-slate-900">作业列表</h2>
          <p class="mt-1 text-sm text-slate-500">按班级维度展示已发布的作业。</p>
        </div>
        <div class="flex gap-3">
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
            @click="router.push(`/classes/${classId}`)"
          >
            返回班级
          </button>
          <button
            type="button"
            class="inline-flex items-center justify-center rounded-2xl bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 transition-all duration-300 hover:-translate-y-1 hover:bg-blue-100"
            @click="loadData"
          >
            刷新列表
          </button>
        </div>
      </div>

      <div v-if="loading" class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div v-for="index in 3" :key="index" class="animate-pulse rounded-[24px] border border-slate-200 bg-slate-50 p-6">
          <div class="h-5 w-32 rounded bg-slate-200"></div>
          <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
          <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
          <div class="mt-8 h-12 rounded-2xl bg-slate-200"></div>
        </div>
      </div>

      <div v-else-if="assignments.length" class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="assignment in assignments"
          :key="assignment.id"
          class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">作业</p>
              <h3 class="mt-3 text-xl font-semibold text-slate-900">{{ assignment.title }}</h3>
            </div>
            <span class="rounded-full px-3 py-1 text-xs font-medium" :class="getAssignmentBadgeClass(assignment)">
              {{ getAssignmentBadgeLabel(assignment) }}
            </span>
          </div>

          <p class="mt-4 line-clamp-3 min-h-[72px] text-sm leading-6 text-slate-500">
            {{ assignment.description || '当前作业还没有补充说明。' }}
          </p>

          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">截止时间</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ formatDateTime(assignment.due_date) }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">创建时间</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ formatDateTime(assignment.created_at) }}</p>
            </div>
          </div>

          <div v-if="!canManageAssignments" class="mt-4 text-sm text-slate-500">
            <span v-if="assignment.my_submitted">我的分数：{{ assignment.my_score ?? '待评分' }}</span>
            <span v-else>尚未提交</span>
          </div>

          <div class="mt-5 flex gap-3">
            <button
              type="button"
              class="inline-flex flex-1 items-center justify-center rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-blue-700"
              @click="router.push(`/assignments/${assignment.id}`)"
            >
              {{ canManageAssignments ? '管理作业' : '查看并作答' }}
            </button>
            <template v-if="canManageAssignments">
              <button
                type="button"
                class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                @click="startEditAssignment(assignment)"
              >
                编辑
              </button>
              <button
                type="button"
                class="inline-flex items-center justify-center rounded-2xl bg-rose-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-rose-700 disabled:cursor-not-allowed disabled:bg-rose-400"
                :disabled="deletingAssignmentId === assignment.id"
                @click="handleDeleteAssignment(assignment.id)"
              >
                {{ deletingAssignmentId === assignment.id ? '删除中...' : '删除' }}
              </button>
            </template>
          </div>
        </article>
      </div>

      <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
        <h3 class="text-lg font-semibold text-slate-900">当前班级还没有作业</h3>
        <p class="mt-2 text-sm leading-6 text-slate-500">{{ canManageAssignments ? '先创建第一份作业，学生才能进入作答流程。' : '教师发布作业后，这里会自动出现。' }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useUserStore } from '@/stores/user';
import { createAssignment, deleteAssignment, listAssignments, type Assignment, updateAssignment } from '@/services/assignments';
import { getClassroomDetail, type ClassroomDetail } from '@/services/classes';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const classId = computed(() => Number(route.params.id));
const loading = ref(false);
const createLoading = ref(false);
const editingAssignmentId = ref<number | null>(null);
const deletingAssignmentId = ref<number | null>(null);
const classroom = ref<ClassroomDetail | null>(null);
const assignments = ref<Assignment[]>([]);

const createForm = reactive({
  title: '',
  description: '',
  due_date: '',
});

const canManageAssignments = computed(() => userStore.user.role === 'teacher' || userStore.user.role === 'admin');

const formatDateTime = (value?: string | null) => {
  if (!value) {
    return '未设置';
  }

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

const getAssignmentBadgeLabel = (assignment: Assignment) => {
  if (canManageAssignments.value) {
    return '已发布';
  }

  if (assignment.my_submitted) {
    return assignment.my_score !== null && assignment.my_score !== undefined ? '已评分' : '已提交';
  }

  return '待完成';
};

const getAssignmentBadgeClass = (assignment: Assignment) => {
  if (canManageAssignments.value) {
    return 'bg-blue-100 text-blue-700';
  }

  if (assignment.my_submitted) {
    return assignment.my_score !== null && assignment.my_score !== undefined
      ? 'bg-green-100 text-green-700'
      : 'bg-amber-100 text-amber-700';
  }

  return 'bg-slate-100 text-slate-700';
};

const loadData = async () => {
  loading.value = true;
  try {
    const [classDetail, assignmentList] = await Promise.all([
      getClassroomDetail(classId.value),
      listAssignments(classId.value),
    ]);
    classroom.value = classDetail;
    assignments.value = assignmentList;
  } finally {
    loading.value = false;
  }
};

const resetCreateForm = () => {
  editingAssignmentId.value = null;
  createForm.title = '';
  createForm.description = '';
  createForm.due_date = '';
};

const startEditAssignment = (assignment: Assignment) => {
  editingAssignmentId.value = assignment.id;
  createForm.title = assignment.title;
  createForm.description = assignment.description || '';
  createForm.due_date = assignment.due_date ? new Date(assignment.due_date).toISOString().slice(0, 16) : '';
};

const handleSaveAssignment = async () => {
  if (!createForm.title.trim()) {
    ElMessage.warning('请输入作业标题');
    return;
  }

  createLoading.value = true;
  try {
    const payload = {
      title: createForm.title.trim(),
      description: createForm.description.trim() || undefined,
      due_date: createForm.due_date ? new Date(createForm.due_date).toISOString() : null,
      classroom_id: classId.value,
    };

    if (editingAssignmentId.value) {
      await updateAssignment(editingAssignmentId.value, {
        title: payload.title,
        description: payload.description,
        due_date: payload.due_date,
      });
      ElMessage.success('作业更新成功');
      await loadData();
      resetCreateForm();
      return;
    }

    const created = await createAssignment(payload);
    ElMessage.success('作业创建成功');
    resetCreateForm();
    await loadData();
    router.push(`/assignments/${created.id}`);
  } finally {
    createLoading.value = false;
  }
};

const handleDeleteAssignment = async (assignmentId: number) => {
  await ElMessageBox.confirm('删除后该作业及其题目、提交记录将一并移除，是否继续？', '确认删除', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  });

  deletingAssignmentId.value = assignmentId;
  try {
    await deleteAssignment(assignmentId);
    ElMessage.success('作业已删除');
    if (editingAssignmentId.value === assignmentId) {
      resetCreateForm();
    }
    await loadData();
  } finally {
    deletingAssignmentId.value = null;
  }
};

onMounted(() => {
  loadData();
});
</script>