<template>
  <div class="space-y-6">
    <section class="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
      <div class="rounded-[28px] bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900 p-6 text-white shadow-sm sm:p-7">
        <div class="space-y-4">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-emerald-100">
            班级讨论
          </div>
          <h2 class="text-2xl font-semibold tracking-tight">{{ classroom?.name || '讨论中心' }}</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">围绕当前班级中的 C++ 学习问题发起讨论。学生可以提问，教师和管理员可以回答并标记最佳答案。</p>
        </div>

        <div class="mt-6 grid gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">问题总数</p>
            <p class="mt-2 text-3xl font-semibold">{{ total }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">当前筛选</p>
            <p class="mt-2 text-xl font-semibold">{{ statusLabel(filters.status) }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">回答权限</p>
            <p class="mt-2 text-xl font-semibold">{{ canAnswer ? '教师可回答' : '学生提问中' }}</p>
          </div>
        </div>
      </div>

      <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div>
          <p class="text-sm font-medium uppercase tracking-[0.22em] text-emerald-600">Ask Question</p>
          <h3 class="mt-2 text-xl font-semibold text-slate-900">发起一个问题</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">描述你在语法、算法、题目或实验中的具体问题，便于教师更快给出有效答复。</p>
        </div>

        <form class="mt-5 space-y-4" @submit.prevent="handleCreateQuestion">
          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">问题标题</label>
            <input
              v-model="createForm.title"
              type="text"
              placeholder="例如：模板特化和偏特化有什么本质区别？"
              class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
            />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">问题描述</label>
            <textarea
              v-model="createForm.content"
              rows="5"
              placeholder="补充你的代码背景、报错信息或当前理解，帮助定位问题。"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
            ></textarea>
          </div>

          <button
            type="submit"
            class="flex h-[52px] w-full items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-700 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-emerald-400"
            :disabled="creating"
          >
            <span v-if="creating" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
            {{ creating ? '发布中...' : '发布问题' }}
          </button>
        </form>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
      <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <h2 class="text-xl font-semibold text-slate-900">问题列表</h2>
          <p class="mt-1 text-sm text-slate-500">可按状态、排序和关键词快速筛选当前班级中的讨论问题。</p>
        </div>

        <div class="grid gap-3 sm:grid-cols-4 xl:min-w-[880px]">
          <input
            v-model="filters.keyword"
            type="text"
            placeholder="搜索标题或内容"
            class="h-[48px] rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
          />
          <select
            v-model="filters.status"
            class="h-[48px] rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
          >
            <option value="">全部状态</option>
            <option value="answered">已有回答</option>
            <option value="unanswered">待回答</option>
            <option value="accepted">已采纳</option>
          </select>
          <select
            v-model="filters.sortBy"
            class="h-[48px] rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
          >
            <option value="latest">最新发布</option>
            <option value="votes">最多点赞</option>
            <option value="answers">最多回答</option>
          </select>
          <div class="flex gap-3">
            <button
              type="button"
              class="flex-1 rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700 transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-100"
              @click="loadQuestions"
            >
              刷新
            </button>
            <button
              type="button"
              class="flex-1 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
              @click="router.push(`/classes/${classId}`)"
            >
              返回班级
            </button>
          </div>
        </div>
      </div>

      <div v-if="loading" class="mt-6 space-y-4">
        <div v-for="index in 3" :key="index" class="animate-pulse rounded-[24px] border border-slate-200 bg-slate-50 p-6">
          <div class="h-5 w-48 rounded bg-slate-200"></div>
          <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
          <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
        </div>
      </div>

      <div v-else-if="questions.length" class="mt-6 space-y-4">
        <article
          v-for="question in questions"
          :key="question.id"
          class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
        >
          <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div class="space-y-3">
              <div class="flex flex-wrap items-center gap-2">
                <span class="rounded-full px-3 py-1 text-xs font-medium" :class="question.accepted_answer_id ? 'bg-green-100 text-green-700' : question.answer_count ? 'bg-blue-100 text-blue-700' : 'bg-amber-100 text-amber-700'">
                  {{ question.accepted_answer_id ? '已采纳' : question.answer_count ? '已有回答' : '待回答' }}
                </span>
                <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                  {{ question.author?.username || '匿名用户' }}
                </span>
                <span class="text-xs text-slate-400">{{ formatDateTime(question.created_at) }}</span>
              </div>

              <div>
                <h3 class="text-xl font-semibold text-slate-900">{{ question.title }}</h3>
                <p class="mt-2 line-clamp-3 text-sm leading-6 text-slate-500">{{ question.content }}</p>
              </div>
            </div>

            <div class="grid grid-cols-3 gap-3 lg:min-w-[260px]">
              <div class="rounded-2xl bg-slate-50 p-4 text-center">
                <p class="text-xs text-slate-400">点赞</p>
                <p class="mt-2 text-lg font-semibold text-slate-900">{{ question.upvote_count }}</p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4 text-center">
                <p class="text-xs text-slate-400">回答</p>
                <p class="mt-2 text-lg font-semibold text-slate-900">{{ question.answer_count }}</p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4 text-center">
                <p class="text-xs text-slate-400">状态</p>
                <p class="mt-2 text-sm font-semibold text-slate-900">{{ question.accepted_answer_id ? '已解决' : '处理中' }}</p>
              </div>
            </div>
          </div>

          <div class="mt-5 flex gap-3">
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-700"
              @click="handleQuestionUpvote(question)"
            >
              <svg viewBox="0 0 24 24" fill="none" class="h-4 w-4" stroke="currentColor" stroke-width="1.8">
                <path stroke-linecap="round" stroke-linejoin="round" d="M14 10V5.5A2.5 2.5 0 0 0 11.5 3L8 10v11h9.28a2 2 0 0 0 1.97-1.62l1.2-6.5A2 2 0 0 0 18.48 10H14ZM8 10H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h3" />
              </svg>
              <span>点赞问题</span>
              <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700 transition-colors duration-300 group-hover:bg-emerald-100 group-hover:text-emerald-700">{{ question.upvote_count }}</span>
            </button>
            <button
              type="button"
              class="flex-1 rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-700"
              @click="router.push(`/classes/${classId}/discussions/${question.id}`)"
            >
              查看详情
            </button>
          </div>
        </article>
      </div>

      <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
        <h3 class="text-lg font-semibold text-slate-900">当前班级还没有讨论问题</h3>
        <p class="mt-2 text-sm leading-6 text-slate-500">你可以发布第一个问题，教师会在这里持续跟进答疑。</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '@/api/request';
import { createQuestion, listQuestions, toggleQuestionUpvote, type DiscussionQuestion } from '@/services/discussion';
import { useUserStore } from '@/stores/user';

interface ClassroomDetail {
  id: number;
  name: string;
}

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const classId = computed(() => Number(route.params.id));
const loading = ref(false);
const creating = ref(false);
const total = ref(0);
const questions = ref<DiscussionQuestion[]>([]);
const classroom = ref<ClassroomDetail | null>(null);

const filters = reactive({
  keyword: '',
  status: '',
  sortBy: 'latest',
});

const createForm = reactive({
  title: '',
  content: '',
});

const canAnswer = computed(() => userStore.user.role === 'teacher' || userStore.user.role === 'admin');

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

const statusLabel = (status: string) => {
  const map: Record<string, string> = {
    answered: '已有回答',
    unanswered: '待回答',
    accepted: '已采纳',
  };
  return map[status] || '全部状态';
};

const loadQuestions = async () => {
  loading.value = true;
  try {
    const [classroomDetail, response] = await Promise.all([
      request.get(`/classes/${classId.value}`) as Promise<ClassroomDetail>,
      listQuestions(classId.value, {
        status: filters.status || undefined,
        keyword: filters.keyword.trim() || undefined,
        sort_by: filters.sortBy,
      }),
    ]);
    classroom.value = classroomDetail;
    questions.value = response.items;
    total.value = response.total;
  } finally {
    loading.value = false;
  }
};

const handleCreateQuestion = async () => {
  if (!createForm.title.trim() || !createForm.content.trim()) {
    ElMessage.warning('请填写完整的问题标题和描述');
    return;
  }

  creating.value = true;
  try {
    const created = await createQuestion(classId.value, {
      title: createForm.title.trim(),
      content: createForm.content.trim(),
    });
    ElMessage.success('问题发布成功');
    createForm.title = '';
    createForm.content = '';
    await loadQuestions();
    router.push(`/classes/${classId.value}/discussions/${created.id}`);
  } finally {
    creating.value = false;
  }
};

const handleQuestionUpvote = async (question: DiscussionQuestion) => {
  const result = await toggleQuestionUpvote(classId.value, question.id);
  questions.value = questions.value.map((item) => {
    if (item.id !== question.id) {
      return item;
    }
    return {
      ...item,
      upvote_count: result.upvote_count,
    };
  });
};

onMounted(() => {
  loadQuestions();
});
</script>