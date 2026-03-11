

<template>
  <div class="space-y-6">
    <section class="grid gap-4 xl:grid-cols-[1.6fr_1fr]">
      <div class="relative overflow-hidden rounded-[30px] bg-[radial-gradient(circle_at_top_right,_rgba(56,189,248,0.28),_transparent_24%),linear-gradient(135deg,_#0f172a,_#0f2e4f_45%,_#0f766e_100%)] p-6 text-white shadow-[0_24px_70px_rgba(15,23,42,0.16)] sm:p-7">
        <div class="app-orb right-[-3rem] top-[-2rem] h-36 w-36 bg-cyan-300/20"></div>
        <div class="app-orb bottom-[-4rem] left-[-1rem] h-44 w-44 bg-blue-400/18"></div>
        <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div class="max-w-2xl space-y-3">
            <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-blue-100">学习日程总览</div>
            <h2 class="text-2xl font-semibold tracking-tight">{{ bannerTitle }}</h2>
            <p class="text-sm leading-6 text-slate-300">{{ bannerDescription }}</p>
          </div>
          <div class="grid w-full max-w-sm grid-cols-2 gap-3">
            <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
              <p class="text-xs text-slate-300">{{ heroPrimaryMetric.label }}</p>
              <p class="mt-2 text-3xl font-semibold">{{ heroPrimaryMetric.value }}</p>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
              <p class="text-xs text-slate-300">{{ heroSecondaryMetric.label }}</p>
              <p class="mt-2 text-3xl font-semibold">{{ heroSecondaryMetric.value }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="grid gap-4 sm:grid-cols-3 xl:grid-cols-1">
        <div
          v-for="action in quickActions"
          :key="action.title"
          class="app-panel rounded-[26px] p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_22px_52px_rgba(15,23,42,0.12)]"
        >
          <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,_rgba(37,99,235,0.12),_rgba(20,184,166,0.16))] text-blue-700">
            <component :is="action.icon" class="h-5 w-5" />
          </div>
          <h3 class="mt-4 text-base font-semibold text-slate-900">{{ action.title }}</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">{{ action.description }}</p>
        </div>
      </div>
    </section>

    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="stat in statCards"
        :key="stat.title"
        class="app-panel rounded-[26px] p-6 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_22px_52px_rgba(15,23,42,0.12)]"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm font-medium text-slate-500">{{ stat.title }}</p>
            <p class="mt-4 text-4xl font-semibold tracking-tight text-slate-900">{{ stat.value }}</p>
          </div>
          <span class="rounded-full px-3 py-1 text-xs font-medium" :class="stat.badgeClass">{{ stat.badge }}</span>
        </div>
        <p class="mt-4 text-sm leading-6 text-slate-500">{{ stat.description }}</p>
      </article>
    </section>

    <section class="app-panel rounded-[30px] p-6 sm:p-7">
            <div class="flex flex-col gap-3 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 class="text-xl font-semibold text-slate-900">最近活动</h2>
                <p class="mt-1 text-sm text-slate-500">直接展示后端 /users/dashboard 返回的最近动态。</p>
              </div>
              <button
                type="button"
                class="inline-flex items-center justify-center rounded-2xl bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 transition-all duration-300 hover:-translate-y-1 hover:bg-blue-100 hover:shadow-sm"
                @click="loadDashboard"
              >
                刷新数据
              </button>
            </div>

            <div class="mt-6 overflow-x-auto">
              <table class="min-w-full divide-y divide-slate-100 text-left">
                <thead>
                  <tr class="text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
                    <th class="pb-4 pr-6">时间</th>
                    <th class="pb-4 pr-6">类型</th>
                    <th class="pb-4 pr-6">详情</th>
                    <th class="pb-4">状态</th>
                  </tr>
                </thead>
                <tbody v-if="dashboardLoading" class="divide-y divide-slate-100">
                  <tr v-for="index in 3" :key="index" class="animate-pulse">
                    <td class="py-4 pr-6"><div class="h-4 w-28 rounded bg-slate-100"></div></td>
                    <td class="py-4 pr-6"><div class="h-4 w-16 rounded bg-slate-100"></div></td>
                    <td class="py-4 pr-6"><div class="h-4 w-full max-w-md rounded bg-slate-100"></div></td>
                    <td class="py-4"><div class="h-6 w-16 rounded-full bg-slate-100"></div></td>
                  </tr>
                </tbody>
                <tbody v-else-if="activityRows.length" class="divide-y divide-slate-100">
                  <tr
                    v-for="activity in activityRows"
                    :key="activity.id"
                    class="transition-colors duration-300 hover:bg-slate-50"
                  >
                    <td class="py-4 pr-6 text-sm text-slate-500">{{ activity.time }}</td>
                    <td class="py-4 pr-6 text-sm font-medium text-slate-800">{{ activity.typeLabel }}</td>
                    <td class="py-4 pr-6 text-sm text-slate-500">{{ activity.content }}</td>
                    <td class="py-4">
                      <span class="rounded-full px-3 py-1 text-xs font-medium" :class="activity.statusClass">
                        {{ activity.statusLabel }}
                      </span>
                    </td>
                  </tr>
                </tbody>
                <tbody v-else>
                  <tr>
                    <td colspan="4" class="py-10 text-center">
                      <div class="mx-auto max-w-md space-y-2">
                        <p class="text-sm font-medium text-slate-700">{{ dashboardError || '当前还没有最近活动' }}</p>
                        <p class="text-sm text-slate-400">产生提交、发布或加入班级等动作后，这里会自动展示最新记录。</p>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { Monitor, Reading, Setting } from '@element-plus/icons-vue';
import request from '@/api/request';
import { useUserStore } from '@/stores/user';

interface DashboardActivity {
  id: number;
  content: string;
  time: string;
  type: string;
}

interface DashboardStats {
  role: string;
  class_count: number;
  assignment_count: number;
  submission_count: number;
  recent_activities: DashboardActivity[];
}

const userStore = useUserStore();
const dashboardLoading = ref(false);
const dashboardError = ref('');
const dashboard = ref<DashboardStats | null>(null);

const currentRole = computed(() => dashboard.value?.role || userStore.user.role || 'student');

const isTeachingRole = computed(() => currentRole.value === 'teacher' || currentRole.value === 'admin');

const bannerTitle = computed(() => {
  if (isTeachingRole.value) {
    return '今天适合回顾班级节奏、检查提交情况，并推进教学反馈闭环。';
  }

  return '今天适合完成班级任务、提交实验，并回顾最近的学习进展。';
});

const bannerDescription = computed(() => {
  if (isTeachingRole.value) {
    return '首页数据已直接接入后端统计接口，你现在看到的是当前教师或管理员身份下的真实班级、作业与提交总览。';
  }

  return '首页数据已直接接入后端统计接口，你现在看到的是当前学生身份下的班级数量、待完成作业与个人提交记录。';
});

const heroMetrics = computed(() => {
  if (isTeachingRole.value) {
    return [
      { label: '班级总数', value: String(dashboard.value?.class_count ?? 0) },
      { label: '最近动态', value: String(dashboard.value?.recent_activities.length ?? 0) },
    ];
  }

  return [
    { label: '待完成作业', value: String(dashboard.value?.assignment_count ?? 0) },
    { label: '我的提交', value: String(dashboard.value?.submission_count ?? 0) },
  ];
});

const heroPrimaryMetric = computed(() => heroMetrics.value[0] ?? { label: '主指标', value: '0' });
const heroSecondaryMetric = computed(() => heroMetrics.value[1] ?? { label: '次指标', value: '0' });

const quickActions = [
  { title: '班级视图', description: '快速查看当前班级与成员、公告的整体状态。', icon: Reading },
  { title: '沙箱实验', description: '进入编程环境，继续当前的 C++ 训练任务。', icon: Monitor },
  { title: '系统配置', description: '调整教学偏好、通知与个人账户设置。', icon: Setting },
];

const statCards = computed(() => {
  if (isTeachingRole.value) {
    return [
      {
        title: '班级总数',
        value: String(dashboard.value?.class_count ?? 0),
        badge: '管理中',
        badgeClass: 'bg-green-100 text-green-700',
        description: '教师显示本人管理班级数，管理员显示平台班级总量。',
      },
      {
        title: '作业总数',
        value: String(dashboard.value?.assignment_count ?? 0),
        badge: '已发布',
        badgeClass: 'bg-blue-100 text-blue-700',
        description: '来自后端统计接口，反映当前身份下可管理的作业规模。',
      },
      {
        title: '收到提交',
        value: String(dashboard.value?.submission_count ?? 0),
        badge: '累计',
        badgeClass: 'bg-amber-100 text-amber-700',
        description: '用于观察近期学生提交密度，辅助安排批改节奏。',
      },
    ];
  }

  return [
    {
      title: '加入班级',
      value: String(dashboard.value?.class_count ?? 0),
      badge: '进行中',
      badgeClass: 'bg-green-100 text-green-700',
      description: '统计当前已加入且仍处于激活状态的班级数量。',
    },
    {
      title: '待完成作业',
      value: String(dashboard.value?.assignment_count ?? 0),
      badge: '待处理',
      badgeClass: 'bg-blue-100 text-blue-700',
      description: '仅统计当前课程中尚未过期或未设置截止时间的作业。',
    },
    {
      title: '我的提交',
      value: String(dashboard.value?.submission_count ?? 0),
      badge: '累计',
      badgeClass: 'bg-amber-100 text-amber-700',
      description: '来自后端真实提交记录，可用于判断近期学习投入度。',
    },
  ];
});

const activityRows = computed(() => {
  const typeMap: Record<string, { label: string; status: string; classes: string }> = {
    submission: { label: '提交', status: '已记录', classes: 'bg-green-100 text-green-700' },
    assignment: { label: '作业', status: '已发布', classes: 'bg-blue-100 text-blue-700' },
    join: { label: '加入', status: '已同步', classes: 'bg-amber-100 text-amber-700' },
  };

  return (dashboard.value?.recent_activities ?? []).map((activity) => {
    const meta = typeMap[activity.type] || { label: activity.type, status: '已同步', classes: 'bg-slate-100 text-slate-700' };
    return {
      id: activity.id,
      time: formatDateTime(activity.time),
      typeLabel: meta.label,
      content: activity.content,
      statusLabel: meta.status,
      statusClass: meta.classes,
    };
  });
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

const loadDashboard = async () => {
  dashboardLoading.value = true;
  dashboardError.value = '';

  try {
    if (!userStore.user.username && !userStore.user.email && userStore.token) {
      await userStore.fetchUserInfo();
    }

    dashboard.value = await request.get('/users/dashboard') as DashboardStats;
  } catch (error) {
    dashboardError.value = '仪表盘数据加载失败，请稍后重试';
  } finally {
    dashboardLoading.value = false;
  }
};

onMounted(() => {
  loadDashboard();
});
</script>

