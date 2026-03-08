<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-r from-slate-950 via-blue-900 to-cyan-700 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-cyan-100">
            班级成员管理
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">{{ classroom?.name || '班级成员' }}</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">查看当前班级成员列表，支持按姓名或邮箱过滤，并将学生移出班级。</p>
        </div>

        <div class="grid w-full max-w-md gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">学生人数</p>
            <p class="mt-2 text-3xl font-semibold">{{ filteredStudents.length }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">邀请码</p>
            <p class="mt-2 text-xl font-semibold tracking-[0.12em]">{{ classroom?.invite_code || '--' }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">教师</p>
            <p class="mt-2 text-xl font-semibold">{{ classroom?.teacher_name || '--' }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
      <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 class="text-xl font-semibold text-slate-900">成员列表</h3>
          <p class="mt-1 text-sm text-slate-500">教师和管理员可在这里维护班级学生名单。</p>
        </div>

        <div class="flex flex-wrap gap-3">
          <input
            v-model.trim="keyword"
            type="text"
            class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white"
            placeholder="搜索用户名或邮箱"
          />
          <button
            type="button"
            class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
            :disabled="loading"
            @click="loadData"
          >
            {{ loading ? '刷新中...' : '刷新列表' }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="mt-6 space-y-4">
        <div v-for="index in 4" :key="index" class="animate-pulse rounded-[24px] border border-slate-200 bg-slate-50 p-5">
          <div class="h-5 w-36 rounded bg-slate-200"></div>
          <div class="mt-3 h-4 w-48 rounded bg-slate-200"></div>
        </div>
      </div>

      <div v-else-if="filteredStudents.length" class="mt-6 space-y-4">
        <article
          v-for="student in filteredStudents"
          :key="student.id"
          class="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
        >
          <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span class="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">学生</span>
                <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">ID {{ student.id }}</span>
              </div>
              <h4 class="mt-3 text-lg font-semibold text-slate-900">{{ student.username || '未命名用户' }}</h4>
              <p class="mt-1 text-sm text-slate-500">{{ student.email || '未提供邮箱' }}</p>
            </div>

            <button
              type="button"
              class="rounded-2xl bg-rose-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-rose-700 disabled:cursor-not-allowed disabled:bg-rose-400"
              :disabled="removingId === student.id"
              @click="handleRemove(student.id!)"
            >
              {{ removingId === student.id ? '移除中...' : '移出班级' }}
            </button>
          </div>
        </article>
      </div>

      <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
        <h4 class="text-lg font-semibold text-slate-900">没有匹配的学生</h4>
        <p class="mt-2 text-sm leading-6 text-slate-500">调整筛选条件后再试一次，或等待学生加入班级。</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { type UserProfile } from '@/stores/user';
import { getClassroomDetail, listClassStudents, removeClassStudent, type ClassroomDetail } from '@/services/classes';

const route = useRoute();

const classId = computed(() => Number(route.params.id));
const loading = ref(false);
const removingId = ref<number | null>(null);
const keyword = ref('');
const classroom = ref<ClassroomDetail | null>(null);
const students = ref<UserProfile[]>([]);

const filteredStudents = computed(() => {
  const query = keyword.value.trim().toLowerCase();
  if (!query) {
    return students.value;
  }

  return students.value.filter((student) => {
    return [student.username, student.email]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query));
  });
});

const loadData = async () => {
  loading.value = true;
  try {
    const [detail, members] = await Promise.all([
      getClassroomDetail(classId.value),
      listClassStudents(classId.value),
    ]);
    classroom.value = detail;
    students.value = members;
  } finally {
    loading.value = false;
  }
};

const handleRemove = async (studentId: number) => {
  await ElMessageBox.confirm('移出后该学生将失去当前班级访问权限，是否继续？', '确认移出', {
    type: 'warning',
    confirmButtonText: '移出',
    cancelButtonText: '取消',
  });

  removingId.value = studentId;
  try {
    await removeClassStudent(classId.value, studentId);
    students.value = students.value.filter((student) => student.id !== studentId);
    ElMessage.success('学生已移出班级');
  } finally {
    removingId.value = null;
  }
};

onMounted(() => {
  loadData();
});
</script>