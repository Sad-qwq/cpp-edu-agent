<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-r from-slate-950 via-slate-800 to-emerald-800 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-emerald-100">
            管理员面板
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">统一处理教师审核与账号状态</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">查看平台用户列表，按角色筛选，并快速完成教师审核、启停用等后台管理动作。</p>
        </div>

        <div class="grid w-full max-w-xl gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">用户总数</p>
            <p class="mt-2 text-3xl font-semibold">{{ users.length }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">待审核教师</p>
            <p class="mt-2 text-3xl font-semibold">{{ pendingTeachers.length }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">停用账号</p>
            <p class="mt-2 text-3xl font-semibold">{{ inactiveCount }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
      <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <h3 class="text-xl font-semibold text-slate-900">筛选用户</h3>
          <p class="mt-1 text-sm text-slate-500">支持按角色和账号状态过滤，便于快速定位目标用户。</p>
        </div>

        <div class="flex flex-wrap gap-3">
          <select v-model="filters.role" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-emerald-500 focus:bg-white">
            <option value="">全部角色</option>
            <option value="student">学生</option>
            <option value="teacher">教师</option>
            <option value="admin">管理员</option>
          </select>

          <select v-model="filters.status" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-emerald-500 focus:bg-white">
            <option value="all">全部状态</option>
            <option value="active">仅启用</option>
            <option value="inactive">仅停用</option>
            <option value="pending">待审核教师</option>
          </select>

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

      <div class="mt-6 grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-lg font-semibold text-slate-900">教师审核</h4>
              <p class="mt-1 text-sm text-slate-500">这里集中处理新注册教师账号。</p>
            </div>
            <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">{{ pendingTeachers.length }} 条待处理</span>
          </div>

          <div v-if="pendingTeachers.length" class="space-y-3">
            <article
              v-for="teacher in pendingTeachers"
              :key="teacher.id"
              class="rounded-[24px] border border-emerald-100 bg-emerald-50/60 p-5 shadow-sm"
            >
              <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div class="flex flex-wrap items-center gap-2">
                    <span class="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-600">{{ teacher.email }}</span>
                    <span class="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-700">待审核</span>
                  </div>
                  <h5 class="mt-3 text-lg font-semibold text-slate-900">{{ teacher.username }}</h5>
                  <p class="mt-2 text-sm leading-6 text-slate-600">{{ teacher.bio || '该教师尚未填写个人简介。' }}</p>
                </div>

                <div class="flex gap-3">
                  <button
                    type="button"
                    class="rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-700"
                    :disabled="actionUserId === teacher.id"
                    @click="handleApprove(teacher.id)"
                  >
                    通过
                  </button>
                  <button
                    type="button"
                    class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                    :disabled="actionUserId === teacher.id"
                    @click="handleReject(teacher.id)"
                  >
                    拒绝
                  </button>
                </div>
              </div>
            </article>
          </div>

          <div v-else class="rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-5 py-10 text-center">
            <h5 class="text-base font-semibold text-slate-900">当前没有待审核教师</h5>
            <p class="mt-2 text-sm leading-6 text-slate-500">新的教师注册申请会自动出现在这里。</p>
          </div>
        </div>

        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-lg font-semibold text-slate-900">用户列表</h4>
              <p class="mt-1 text-sm text-slate-500">当前显示 {{ filteredUsers.length }} 个用户。</p>
            </div>
          </div>

          <div v-if="filteredUsers.length" class="space-y-3">
            <article
              v-for="account in filteredUsers"
              :key="account.id"
              class="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
            >
              <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                <div class="space-y-3">
                  <div class="flex flex-wrap items-center gap-2">
                    <span class="rounded-full px-3 py-1 text-xs font-medium" :class="roleClassMap[account.role] || 'bg-slate-100 text-slate-700'">
                      {{ roleTextMap[account.role] || account.role }}
                    </span>
                    <span class="rounded-full px-3 py-1 text-xs font-medium" :class="account.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'">
                      {{ account.is_active ? '已启用' : '已停用' }}
                    </span>
                    <span class="rounded-full px-3 py-1 text-xs font-medium" :class="approvalClass(account)">
                      {{ approvalText(account) }}
                    </span>
                  </div>

                  <div>
                    <h5 class="text-lg font-semibold text-slate-900">{{ account.username }}</h5>
                    <p class="mt-1 text-sm text-slate-500">{{ account.email }}</p>
                  </div>

                  <p class="text-sm leading-6 text-slate-600">{{ account.bio || '暂无个人简介。' }}</p>
                </div>

                <div class="flex flex-wrap gap-3 xl:max-w-[320px] xl:justify-end">
                  <button
                    v-if="account.role !== 'admin'"
                    type="button"
                    class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                    :disabled="actionUserId === account.id"
                    @click="handleToggleActive(account)"
                  >
                    {{ account.is_active ? '停用账号' : '启用账号' }}
                  </button>

                  <button
                    v-if="account.role === 'teacher' && !account.is_approved"
                    type="button"
                    class="rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-700"
                    :disabled="actionUserId === account.id"
                    @click="handleApprove(account.id)"
                  >
                    审核通过
                  </button>
                </div>
              </div>
            </article>
          </div>

          <div v-else class="rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-5 py-10 text-center">
            <h5 class="text-base font-semibold text-slate-900">没有匹配的用户</h5>
            <p class="mt-2 text-sm leading-6 text-slate-500">调整筛选条件后再试一次。</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import {
  adminUpdateUser,
  approveTeacher,
  listPendingTeachers,
  listUsers,
  rejectTeacher,
  type UserProfileResponse,
} from '@/services/users';

const loading = ref(false);
const actionUserId = ref<number | null>(null);
const users = ref<UserProfileResponse[]>([]);
const pendingTeachers = ref<UserProfileResponse[]>([]);

const filters = reactive({
  role: '',
  status: 'all',
});

const roleTextMap: Record<string, string> = {
  admin: '管理员',
  teacher: '教师',
  student: '学生',
};

const roleClassMap: Record<string, string> = {
  admin: 'bg-amber-100 text-amber-700',
  teacher: 'bg-sky-100 text-sky-700',
  student: 'bg-slate-100 text-slate-700',
};

const inactiveCount = computed(() => users.value.filter((item) => !item.is_active).length);

const approvalText = (account: UserProfileResponse) => {
  if (account.role !== 'teacher') {
    return '无需审批';
  }

  return account.is_approved ? '已审核' : '待审核';
};

const approvalClass = (account: UserProfileResponse) => {
  if (account.role !== 'teacher') {
    return 'bg-slate-100 text-slate-600';
  }

  return account.is_approved ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700';
};

const filteredUsers = computed(() => {
  return users.value.filter((account) => {
    if (filters.role && account.role !== filters.role) {
      return false;
    }

    if (filters.status === 'active' && !account.is_active) {
      return false;
    }

    if (filters.status === 'inactive' && account.is_active) {
      return false;
    }

    if (filters.status === 'pending' && !(account.role === 'teacher' && !account.is_approved)) {
      return false;
    }

    return true;
  });
});

const loadData = async () => {
  loading.value = true;
  try {
    const [userList, teacherList] = await Promise.all([
      listUsers({ limit: 200 }),
      listPendingTeachers(),
    ]);
    users.value = userList;
    pendingTeachers.value = teacherList;
  } finally {
    loading.value = false;
  }
};

const handleApprove = async (userId: number) => {
  actionUserId.value = userId;
  try {
    await approveTeacher(userId);
    ElMessage.success('教师账号已审核通过');
    await loadData();
  } finally {
    actionUserId.value = null;
  }
};

const handleReject = async (userId: number) => {
  actionUserId.value = userId;
  try {
    await rejectTeacher(userId);
    ElMessage.success('教师账号已拒绝并停用');
    await loadData();
  } finally {
    actionUserId.value = null;
  }
};

const handleToggleActive = async (account: UserProfileResponse) => {
  actionUserId.value = account.id;
  try {
    const updated = await adminUpdateUser(account.id, {
      is_active: !account.is_active,
    });
    users.value = users.value.map((item) => item.id === account.id ? updated : item);
    pendingTeachers.value = pendingTeachers.value.filter((item) => item.id !== account.id || !updated.is_approved);
    ElMessage.success(updated.is_active ? '账号已启用' : '账号已停用');
  } finally {
    actionUserId.value = null;
  }
};

onMounted(() => {
  loadData();
});
</script>