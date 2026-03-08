<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-900 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-emerald-100">
            问题详情
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">{{ question?.title || '问题加载中' }}</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">围绕当前问题查看上下文、教师回答、点赞互动与最佳答案采纳状态。</p>
        </div>

        <div class="grid w-full max-w-md grid-cols-3 gap-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">点赞</p>
            <p class="mt-2 text-2xl font-semibold">{{ question?.upvote_count ?? 0 }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">回答</p>
            <p class="mt-2 text-2xl font-semibold">{{ question?.answer_count ?? 0 }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">状态</p>
            <p class="mt-2 text-sm font-semibold">{{ question?.accepted_answer_id ? '已解决' : '待跟进' }}</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="question" class="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
      <div class="space-y-4">
        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div class="flex flex-wrap items-center gap-2">
                <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                  {{ question.author?.username || '匿名用户' }}
                </span>
                <span class="text-xs text-slate-400">{{ formatDateTime(question.created_at) }}</span>
                <span v-if="question.accepted_answer_id" class="rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">已采纳答案</span>
              </div>
              <h3 class="mt-4 text-xl font-semibold text-slate-900">问题内容</h3>
              <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ question.content }}</p>
            </div>
            <div class="flex gap-3">
              <button
                type="button"
                class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-700"
                @click="handleQuestionUpvote"
              >
                <svg viewBox="0 0 24 24" fill="none" class="h-4 w-4" stroke="currentColor" stroke-width="1.8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M14 10V5.5A2.5 2.5 0 0 0 11.5 3L8 10v11h9.28a2 2 0 0 0 1.97-1.62l1.2-6.5A2 2 0 0 0 18.48 10H14ZM8 10H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h3" />
                </svg>
                <span>点赞问题</span>
                <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">{{ question.upvote_count }}</span>
              </button>
              <button
                type="button"
                class="rounded-2xl bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700 transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-100"
                @click="router.push(`/classes/${classId}/discussions`)"
              >
                返回讨论列表
              </button>
            </div>
          </div>
        </div>

        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex items-center justify-between gap-4 border-b border-slate-100 pb-5">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">回答列表</h3>
              <p class="mt-1 text-sm text-slate-500">教师和管理员的答复会在这里持续沉淀。</p>
            </div>
            <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">{{ question.answer_count }} 条回答</span>
          </div>

          <div v-if="loading" class="mt-6 space-y-4">
            <div v-for="index in 3" :key="index" class="animate-pulse rounded-2xl bg-slate-50 p-5">
              <div class="h-5 w-40 rounded bg-slate-200"></div>
              <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
              <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
            </div>
          </div>

          <div v-else-if="question.answers.length" class="mt-6 space-y-4">
            <article
              v-for="answer in question.answers"
              :key="answer.id"
              class="rounded-2xl border p-5"
              :class="answer.is_accepted ? 'border-green-200 bg-green-50/70' : 'border-slate-200 bg-slate-50'"
            >
              <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div class="flex flex-wrap items-center gap-2">
                    <span class="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700">
                      {{ answer.author?.username || '教师' }}
                    </span>
                    <span class="rounded-full px-3 py-1 text-xs font-medium" :class="answer.is_accepted ? 'bg-green-100 text-green-700' : 'bg-slate-200 text-slate-700'">
                      {{ answer.is_accepted ? '最佳答案' : '回答' }}
                    </span>
                    <span class="text-xs text-slate-400">{{ formatDateTime(answer.created_at) }}</span>
                  </div>
                  <p class="mt-4 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ answer.content }}</p>
                </div>

                <div class="flex gap-3">
                  <button
                    type="button"
                    class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:border-emerald-200 hover:bg-emerald-50 hover:text-emerald-700"
                    @click="handleAnswerUpvote(answer.id)"
                  >
                    <svg viewBox="0 0 24 24" fill="none" class="h-4 w-4" stroke="currentColor" stroke-width="1.8">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M14 10V5.5A2.5 2.5 0 0 0 11.5 3L8 10v11h9.28a2 2 0 0 0 1.97-1.62l1.2-6.5A2 2 0 0 0 18.48 10H14ZM8 10H5a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h3" />
                    </svg>
                    <span>点赞</span>
                    <span class="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">{{ answer.upvote_count }}</span>
                  </button>
                  <button
                    v-if="canAcceptAnswer && !answer.is_accepted"
                    type="button"
                    class="rounded-2xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-700"
                    @click="handleAcceptAnswer(answer.id)"
                  >
                    采纳答案
                  </button>
                </div>
              </div>
            </article>
          </div>

          <div v-else class="mt-8 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-6 py-10 text-center">
            <p class="text-sm font-medium text-slate-700">当前还没有回答</p>
            <p class="mt-2 text-sm text-slate-400">教师回复后，这里会显示完整的答疑记录。</p>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">当前问题状态</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">帮助你快速判断问题是否已经被解决。</p>
          </div>
          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">提问人</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ question.author?.username || '匿名用户' }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">当前状态</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ question.accepted_answer_id ? '已解决' : '待处理' }}</p>
            </div>
          </div>
        </div>

        <div v-if="canAnswer" class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">教师回复</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">请尽量给出可执行的解释、示例和修正建议。</p>
          </div>

          <form class="mt-5 space-y-4" @submit.prevent="handleCreateAnswer">
            <textarea
              v-model="answerForm.content"
              rows="7"
              placeholder="输入你的回复内容"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-emerald-500 focus:bg-white focus:ring-4 focus:ring-emerald-100"
            ></textarea>

            <button
              type="submit"
              class="flex h-[52px] w-full items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-700 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-emerald-400"
              :disabled="answering"
            >
              <span v-if="answering" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
              {{ answering ? '提交中...' : '发布回答' }}
            </button>
          </form>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import {
  acceptAnswer,
  createAnswer,
  getQuestionDetail,
  toggleAnswerUpvote,
  toggleQuestionUpvote,
  type DiscussionQuestionDetail,
} from '@/services/discussion';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const classId = computed(() => Number(route.params.id));
const questionId = computed(() => Number(route.params.questionId));
const loading = ref(false);
const answering = ref(false);
const question = ref<DiscussionQuestionDetail | null>(null);

const answerForm = reactive({
  content: '',
});

const canAnswer = computed(() => userStore.user.role === 'teacher' || userStore.user.role === 'admin');
const canAcceptAnswer = computed(() => {
  if (!question.value) {
    return false;
  }
  return userStore.isAdmin || userStore.user.id === question.value.user_id || userStore.user.role === 'teacher';
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

const loadQuestion = async () => {
  loading.value = true;
  try {
    question.value = await getQuestionDetail(classId.value, questionId.value);
  } finally {
    loading.value = false;
  }
};

const handleCreateAnswer = async () => {
  if (!answerForm.content.trim()) {
    ElMessage.warning('请输入回答内容');
    return;
  }

  answering.value = true;
  try {
    const created = await createAnswer(classId.value, questionId.value, {
      content: answerForm.content.trim(),
    });
    ElMessage.success('回答发布成功');
    answerForm.content = '';
    if (question.value) {
      question.value = {
        ...question.value,
        answer_count: question.value.answer_count + 1,
        answers: [created, ...question.value.answers],
      };
    }
  } finally {
    answering.value = false;
  }
};

const handleQuestionUpvote = async () => {
  if (!question.value) {
    return;
  }
  const result = await toggleQuestionUpvote(classId.value, question.value.id);
  question.value = {
    ...question.value,
    upvote_count: result.upvote_count,
  };
};

const handleAnswerUpvote = async (answerId: number) => {
  const result = await toggleAnswerUpvote(classId.value, questionId.value, answerId);
  if (!question.value) {
    return;
  }
  question.value = {
    ...question.value,
    answers: question.value.answers.map((answer) => {
      if (answer.id !== answerId) {
        return answer;
      }
      return {
        ...answer,
        upvote_count: result.upvote_count,
      };
    }),
  };
};

const handleAcceptAnswer = async (answerId: number) => {
  question.value = await acceptAnswer(classId.value, questionId.value, answerId);
  ElMessage.success('已采纳该回答');
};

onMounted(() => {
  loadQuestion();
});
</script>