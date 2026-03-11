<template>
  <div class="grid min-h-[calc(100vh-13rem)] gap-4 2xl:grid-cols-[320px_minmax(0,1.3fr)_360px] xl:grid-cols-[300px_minmax(0,1.2fr)_340px]">
    <aside class="flex min-h-[calc(100vh-13rem)] flex-col overflow-hidden rounded-[30px] border border-slate-200 bg-[radial-gradient(circle_at_top,_rgba(34,197,94,0.08),_transparent_40%),linear-gradient(180deg,_#0f172a_0%,_#111827_100%)] text-white shadow-[0_24px_80px_rgba(15,23,42,0.18)]">
      <div class="border-b border-white/10 p-5">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="text-xs uppercase tracking-[0.28em] text-cyan-200/80">AI Tutor</p>
            <h2 class="mt-2 text-xl font-semibold tracking-tight">{{ classroom?.name || '助学工作台' }}</h2>
            <p class="mt-2 text-sm leading-6 text-slate-300">更像 ChatGPT/Gemini 的对话式助学体验。</p>
          </div>
          <button
            type="button"
            class="inline-flex shrink-0 items-center justify-center whitespace-nowrap rounded-2xl border border-white/10 bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/15"
            @click="handleNewChat"
          >
            新建
          </button>
        </div>

        <div class="mt-5 grid gap-2">
          <button
            v-for="mode in modeOptions"
            :key="mode.value"
            type="button"
            class="flex items-center justify-between rounded-2xl px-4 py-3 text-left text-sm transition"
            :class="form.mode === mode.value ? 'bg-white text-slate-900' : 'bg-white/5 text-slate-200 hover:bg-white/10'"
            @click="switchMode(mode.value)"
          >
            <span>{{ mode.label }}</span>
            <span class="text-[11px]" :class="form.mode === mode.value ? 'text-slate-500' : 'text-slate-400'">{{ mode.short }}</span>
          </button>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto p-4">
        <div class="mb-3 flex items-center justify-between px-1">
          <p class="text-xs uppercase tracking-[0.28em] text-slate-400">会话</p>
          <span class="rounded-full bg-white/10 px-2.5 py-1 text-[11px] text-slate-200">{{ sessionList.length }}</span>
        </div>

        <div v-if="loadingSessions" class="space-y-2">
          <div v-for="index in 5" :key="index" class="h-20 animate-pulse rounded-2xl bg-white/8"></div>
        </div>

        <div v-else-if="sessionList.length" class="space-y-2">
          <button
            v-for="item in filteredSessionList"
            :key="item.id"
            type="button"
            class="group w-full rounded-2xl border px-4 py-3 text-left transition"
            :class="activeSessionId === item.id ? 'border-cyan-300 bg-cyan-50 text-slate-900' : 'border-white/10 bg-white/5 text-slate-100 hover:bg-white/10'"
            @click="openSession(item.id)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold">{{ item.title || '未命名会话' }}</p>
                <p class="mt-1 line-clamp-2 text-xs leading-5" :class="activeSessionId === item.id ? 'text-slate-500' : 'text-slate-400'">
                  {{ item.latest_summary || modeLabel(item.mode) }}
                </p>
              </div>
              <button
                type="button"
                class="shrink-0 rounded-xl px-2 py-1 text-[11px] transition"
                :class="activeSessionId === item.id ? 'text-slate-500 hover:bg-slate-100' : 'text-slate-400 hover:bg-white/10 hover:text-white'"
                @click.stop="handleDeleteSession(item.id)"
              >
                删除
              </button>
            </div>
            <div class="mt-3 flex items-center justify-between text-[11px]" :class="activeSessionId === item.id ? 'text-slate-500' : 'text-slate-400'">
              <span>{{ modeLabel(item.mode) }}</span>
              <span>{{ formatRelativeTime(item.updated_at) }}</span>
            </div>
          </button>
        </div>

        <div v-else class="rounded-2xl border border-dashed border-white/15 bg-white/5 px-4 py-8 text-center text-sm text-slate-400">
          当前还没有会话。
        </div>
      </div>

      <div class="border-t border-white/10 p-4">
        <div class="rounded-2xl bg-white/5 p-4">
          <p class="text-xs uppercase tracking-[0.24em] text-cyan-200/80">当前上下文</p>
          <p class="mt-3 text-sm text-slate-200">{{ assignmentContextLabel }}</p>
          <p class="mt-2 text-xs leading-5 text-slate-400">{{ selectedProblem ? selectedProblem.content.slice(0, 80) : '未锁定具体题目，可进行概念问答或学习建议。' }}</p>
        </div>
      </div>
    </aside>

    <section class="flex min-h-[calc(100vh-13rem)] min-w-0 flex-col overflow-hidden rounded-[34px] border border-slate-200 bg-[linear-gradient(180deg,_rgba(240,253,250,0.9)_0%,_#ffffff_16%,_#ffffff_100%)] shadow-[0_30px_80px_rgba(15,23,42,0.08)]">
      <header class="border-b border-slate-200 bg-white/80 px-6 py-5 backdrop-blur">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <div class="flex items-center gap-2 text-xs uppercase tracking-[0.26em] text-teal-700/80">
              <span>AI 助学</span>
              <span class="h-1 w-1 rounded-full bg-teal-500"></span>
              <span>{{ modeLabel(form.mode) }}</span>
            </div>
            <h3 class="mt-2 text-2xl font-semibold tracking-tight text-slate-900">{{ activeTitle }}</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">{{ modeTip }}</p>
          </div>

          <div class="flex flex-wrap gap-2">
            <button
              v-for="suggestion in visibleStarterPrompts"
              :key="suggestion"
              type="button"
              class="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm text-slate-600 transition hover:-translate-y-0.5 hover:border-teal-200 hover:text-teal-700"
              @click="applyPrompt(suggestion)"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>
      </header>

      <div ref="messageScroller" class="flex-1 overflow-y-auto px-4 py-6 sm:px-6 2xl:px-7">
        <div v-if="activeMessages.length" class="flex w-full flex-col gap-6">
          <article
            v-for="message in activeMessages"
            :key="message.id"
            class="flex"
            :class="message.role === 'assistant' ? 'justify-start' : 'justify-end'"
          >
            <div class="max-w-[92%] rounded-[28px] px-5 py-4 shadow-sm 2xl:max-w-[84%] xl:max-w-[88%]"
              :class="message.role === 'assistant'
                ? 'border border-teal-100 bg-teal-50/80 text-slate-800'
                : 'bg-slate-900 text-white'">
              <div class="flex items-center gap-2 text-xs">
                <span class="rounded-full px-2.5 py-1"
                  :class="message.role === 'assistant' ? 'bg-white text-teal-700' : 'bg-white/10 text-white'">
                  {{ message.role === 'assistant' ? 'AI 助教' : '我' }}
                </span>
                <span :class="message.role === 'assistant' ? 'text-slate-500' : 'text-white/60'">{{ formatDateTime(message.created_at) }}</span>
              </div>

              <div
                class="markdown-body mt-3 text-sm leading-7"
                :class="message.role === 'assistant' ? 'markdown-assistant' : 'markdown-user'"
                v-html="renderMarkdown(message.content)"
              ></div>

              <div v-if="message.role === 'assistant'" class="mt-4 space-y-3">
                <div class="flex flex-wrap gap-2">
                  <span v-for="tag in message.related_knowledge_points" :key="`${message.id}-${tag}`" class="rounded-full bg-white px-3 py-1 text-xs text-slate-600">
                    {{ tag }}
                  </span>
                </div>
                <div v-if="followUpQuestions(message).length" class="flex flex-wrap gap-2">
                  <button
                    v-for="question in followUpQuestions(message)"
                    :key="`${message.id}-${question}`"
                    type="button"
                    class="rounded-full border border-teal-200 bg-white px-3 py-1.5 text-xs text-teal-700 transition hover:bg-teal-50"
                    @click="applyPrompt(question)"
                  >
                    {{ question }}
                  </button>
                </div>
                <div class="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                  <span v-if="message.cited_chunk_ids.length">引用分块: {{ message.cited_chunk_ids.join(', ') }}</span>
                  <span v-if="recommendedAction(message)">建议动作: {{ recommendedAction(message) }}</span>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="flex h-full w-full flex-col items-center justify-center px-4 text-center">
          <div class="max-w-3xl">
            <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-[20px] bg-[linear-gradient(135deg,_#0f172a,_#115e59,_#06b6d4)] text-white shadow-[0_20px_50px_rgba(8,145,178,0.22)]">
              <span class="text-lg font-semibold">AI</span>
            </div>
            <h3 class="mt-6 text-3xl font-semibold tracking-tight text-slate-900">像 ChatGPT 一样和课程上下文对话</h3>
            <p class="mt-4 text-sm leading-7 text-slate-500">你可以直接提问，也可以切到提示模式、代码纠错模式或练习推荐模式。系统会自动带上当前班级资料、作业和题目上下文。</p>
          </div>

          <div class="mt-8 grid w-full max-w-5xl gap-3 sm:grid-cols-2 2xl:grid-cols-4 xl:grid-cols-3">
            <button
              v-for="suggestion in starterPrompts[form.mode]"
              :key="suggestion"
              type="button"
              class="rounded-[24px] border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:-translate-y-1 hover:border-teal-200 hover:shadow-md"
              @click="applyPrompt(suggestion)"
            >
              <p class="text-sm font-medium text-slate-800">{{ suggestion }}</p>
            </button>
          </div>
        </div>
      </div>

      <footer class="border-t border-slate-200 bg-white/90 px-4 py-4 backdrop-blur sm:px-5 2xl:px-6">
        <div class="w-full">
          <div class="mb-3 flex flex-wrap gap-2">
            <span class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">{{ modeLabel(form.mode) }}</span>
            <span class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">{{ assignmentContextLabel }}</span>
            <span v-if="selectedProblem" class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">已关联题目</span>
          </div>

          <div class="rounded-[30px] border border-slate-200 bg-slate-50 p-3 shadow-[0_16px_50px_rgba(15,23,42,0.06)]">
            <textarea
              v-model.trim="form.message"
              rows="4"
              class="w-full resize-none border-none bg-transparent px-3 py-2 text-sm leading-7 text-slate-800 outline-none placeholder:text-slate-400"
              :placeholder="messagePlaceholder"
              @keydown.enter.exact.prevent="handleSendMessage"
              @keydown.enter.shift.exact.stop
            ></textarea>

            <div v-if="showAdvancedFields" class="grid gap-3 border-t border-slate-200 px-2 pt-3 md:grid-cols-2">
              <label v-if="form.mode === 'hint'" class="block space-y-2 md:col-span-2">
                <span class="text-xs font-medium uppercase tracking-[0.22em] text-slate-400">当前作答</span>
                <textarea v-model.trim="form.studentAnswer" rows="3" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none transition focus:border-teal-400"></textarea>
              </label>

              <label v-if="form.mode === 'code_review' || selectedProblem?.type === 'coding'" class="block space-y-2 md:col-span-2">
                <span class="text-xs font-medium uppercase tracking-[0.22em] text-slate-400">代码上下文</span>
                <textarea v-model.trim="form.currentCode" rows="7" class="w-full rounded-2xl border border-slate-200 bg-slate-950 px-4 py-3 font-mono text-sm text-slate-100 outline-none transition focus:border-cyan-400"></textarea>
              </label>

              <label v-if="form.mode === 'code_review' || selectedProblem?.type === 'coding'" class="block space-y-2">
                <span class="text-xs font-medium uppercase tracking-[0.22em] text-slate-400">编译或运行输出</span>
                <textarea v-model.trim="form.compilerOutput" rows="4" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 font-mono text-sm text-slate-700 outline-none transition focus:border-teal-400"></textarea>
              </label>

              <label v-if="form.mode === 'code_review' || selectedProblem?.type === 'coding'" class="block space-y-2">
                <span class="text-xs font-medium uppercase tracking-[0.22em] text-slate-400">期望输出</span>
                <textarea v-model.trim="form.expectedOutput" rows="4" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 font-mono text-sm text-slate-700 outline-none transition focus:border-teal-400"></textarea>
              </label>
            </div>

            <div class="mt-3 flex flex-col gap-3 border-t border-slate-200 px-2 pt-3 sm:flex-row sm:items-center sm:justify-between">
              <div class="flex flex-wrap gap-2">
                <button type="button" class="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 transition hover:border-teal-200 hover:text-teal-700" @click="showAdvancedFields = !showAdvancedFields">
                  {{ showAdvancedFields ? '收起上下文' : '展开上下文' }}
                </button>
                <button v-if="form.problemId" type="button" class="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 transition hover:border-teal-200 hover:text-teal-700" :disabled="quickHinting" @click="handleQuickHint(1)">
                  一级提示
                </button>
                <button v-if="form.problemId" type="button" class="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 transition hover:border-teal-200 hover:text-teal-700" :disabled="quickHinting" @click="handleQuickHint(2)">
                  二级提示
                </button>
                <button v-if="form.mode === 'code_review'" type="button" class="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 transition hover:border-teal-200 hover:text-teal-700" :disabled="reviewingCode" @click="handleStandaloneCodeReview">
                  {{ reviewingCode ? '分析中...' : '即时分析' }}
                </button>
              </div>

              <button
                type="button"
                class="inline-flex items-center justify-center rounded-2xl bg-[linear-gradient(135deg,_#0f172a,_#0f766e,_#0891b2)] px-5 py-3 text-sm font-semibold text-white shadow-[0_16px_40px_rgba(8,145,178,0.22)] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="sending"
                @click="handleSendMessage"
              >
                {{ sending ? '发送中...' : '发送' }}
              </button>
            </div>
          </div>
        </div>
      </footer>
    </section>

    <aside class="hidden min-h-[calc(100vh-13rem)] flex-col gap-4 xl:flex">
      <section class="rounded-[30px] border border-slate-200 bg-white p-5 shadow-[0_20px_60px_rgba(15,23,42,0.06)]">
        <p class="text-xs uppercase tracking-[0.28em] text-slate-400">上下文</p>
        <div class="mt-4 space-y-4">
          <div>
            <p class="text-xs text-slate-400">班级</p>
            <p class="mt-1 text-sm font-semibold text-slate-800">{{ classroom?.name || '加载中' }}</p>
          </div>
          <div>
            <p class="text-xs text-slate-400">作业</p>
            <select v-model="form.assignmentId" class="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-teal-400">
              <option :value="null">不限定作业</option>
              <option v-for="assignment in assignments" :key="assignment.id" :value="assignment.id">{{ assignment.title }}</option>
            </select>
          </div>
          <div>
            <p class="text-xs text-slate-400">题目</p>
            <select v-model="form.problemId" class="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-teal-400" :disabled="!problems.length">
              <option :value="null">不限定题目</option>
              <option v-for="problem in problems" :key="problem.id" :value="problem.id">{{ problem.content.slice(0, 50) }}</option>
            </select>
          </div>
        </div>
      </section>

      <section class="rounded-[30px] border border-slate-200 bg-white p-5 shadow-[0_20px_60px_rgba(15,23,42,0.06)]">
        <div class="flex items-center justify-between gap-3">
          <p class="text-xs uppercase tracking-[0.28em] text-slate-400">即时结果</p>
          <span v-if="instantReply?.hint_level" class="rounded-full bg-cyan-100 px-2.5 py-1 text-[11px] text-cyan-700">提示 {{ instantReply.hint_level }}</span>
        </div>
        <div v-if="instantReply" class="mt-4 space-y-3 text-sm">
          <div class="markdown-body markdown-assistant leading-7 text-slate-700" v-html="renderMarkdown(instantReply.answer)"></div>
          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-xs text-slate-400">建议动作</p>
            <p class="mt-2 text-sm text-slate-700">{{ instantReply.recommended_action }}</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <span v-for="point in instantReply.related_knowledge_points" :key="point" class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600">{{ point }}</span>
          </div>
        </div>
        <div v-else class="mt-4 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
          快速提示和即时代码分析结果会显示在这里。
        </div>
      </section>

      <section class="rounded-[30px] border border-slate-200 bg-white p-5 shadow-[0_20px_60px_rgba(15,23,42,0.06)]">
        <div class="flex items-center justify-between gap-3">
          <p class="text-xs uppercase tracking-[0.28em] text-slate-400">练习建议</p>
          <span class="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] text-slate-600">{{ recommendations.length }}</span>
        </div>
        <div class="mt-4 space-y-3">
          <article v-for="(item, index) in recommendations" :key="`${item.title}-${index}`" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <p class="text-sm font-semibold text-slate-800">{{ item.title }}</p>
            <p class="mt-2 text-xs leading-6 text-slate-500">{{ item.reason }}</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <span v-for="point in item.target_knowledge_points" :key="`${item.title}-${point}`" class="rounded-full bg-white px-3 py-1 text-[11px] text-slate-500">{{ point }}</span>
            </div>
            <div class="mt-4 flex gap-2">
              <button v-if="item.assignment_id" type="button" class="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600 transition hover:border-teal-200 hover:text-teal-700" @click="router.push(`/assignments/${item.assignment_id}`)">
                打开作业
              </button>
              <button v-if="item.assignment_id" type="button" class="rounded-full bg-slate-900 px-3 py-1.5 text-xs text-white transition hover:bg-slate-800" @click="openRecommendation(item.assignment_id, item.problem_id)">
                跟进
              </button>
            </div>
          </article>
        </div>
      </section>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import DOMPurify from 'dompurify';
import MarkdownIt from 'markdown-it';
import { getClassroomDetail, type ClassroomDetail } from '@/services/classes';
import { getAssignment, listAssignments, listProblems, type Assignment, type Problem } from '@/services/assignments';
import {
  createTutorSession,
  deleteTutorSession,
  getPracticeRecommendations,
  getProblemHint,
  getTutorSession,
  listTutorSessions,
  reviewCodeWithTutor,
  sendTutorMessage,
  type PracticeRecommendation,
  type TutorMode,
  type TutorReplyPayload,
  type TutorSessionDetail,
} from '@/services/ai-tutor';
import { useUserStore } from '@/stores/user';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const markdown = new MarkdownIt({
  html: false,
  breaks: true,
  linkify: true,
});

const classId = computed(() => Number(route.params.id));
const classroom = ref<ClassroomDetail | null>(null);
const assignments = ref<Assignment[]>([]);
const problems = ref<Problem[]>([]);
const sessionList = ref<Array<Omit<TutorSessionDetail, 'messages'>>>([]);
const sessionDetail = ref<TutorSessionDetail | null>(null);
const recommendations = ref<PracticeRecommendation[]>([]);
const instantReply = ref<TutorReplyPayload | null>(null);
const sending = ref(false);
const quickHinting = ref(false);
const reviewingCode = ref(false);
const loadingSessions = ref(false);
const activeSessionId = ref<number | null>(null);
const showAdvancedFields = ref(false);
const messageScroller = ref<HTMLElement | null>(null);

const modeOptions = [
  { value: 'concept' as TutorMode, label: '概念讲解', short: '解释' },
  { value: 'hint' as TutorMode, label: '解题提示', short: '提示' },
  { value: 'code_review' as TutorMode, label: '代码纠错', short: '纠错' },
  { value: 'practice' as TutorMode, label: '练习推荐', short: '练习' },
];

const form = reactive({
  mode: 'concept' as TutorMode,
  assignmentId: null as number | null,
  problemId: null as number | null,
  message: '',
  studentAnswer: '',
  currentCode: '',
  compilerOutput: '',
  expectedOutput: '',
});

const starterPrompts: Record<TutorMode, string[]> = {
  concept: [
    '数组名为什么常常退化成指针？',
    'for 循环和 while 循环什么时候更合适？',
    '函数传值和传引用的区别是什么？',
  ],
  hint: [
    '请给我第一层提示，不要直接给答案。',
    '我已经写了一半，下一步该检查哪里？',
    '这道题应该先从输入输出还是逻辑拆分入手？',
  ],
  code_review: [
    '这段代码为什么会越界？',
    '请先解释编译报错，再告诉我最小修改方向。',
    '我输出不对，应该先排查哪一部分？',
  ],
  practice: [
    '根据我当前情况，下一步最值得练什么？',
    '请帮我把最近的问题拆成 3 个小练习。',
    '我适合先补概念还是先补编程题？',
  ],
};

const selectedProblem = computed(() => problems.value.find((item) => item.id === form.problemId) || null);
const activeMessages = computed(() => sessionDetail.value?.messages || []);
const filteredSessionList = computed(() => sessionList.value.filter((item) => item.mode === form.mode || !sessionList.value.some((session) => session.mode === form.mode)));
const assignmentContextLabel = computed(() => {
  const assignment = assignments.value.find((item) => item.id === form.assignmentId);
  return assignment ? assignment.title : '未限定作业';
});
const visibleStarterPrompts = computed(() => starterPrompts[form.mode].slice(0, 2));
const activeTitle = computed(() => sessionDetail.value?.title || `${modeLabel(form.mode)}会话`);
const modeTip = computed(() => {
  if (form.mode === 'hint') {
    return '提示模式会尽量只给思路和分层引导，不直接给完整标准答案。';
  }
  if (form.mode === 'code_review') {
    return '代码纠错模式适合贴上代码和报错，让 AI 解释错误类型和最小修改方向。';
  }
  if (form.mode === 'practice') {
    return '练习推荐模式会结合最近作业和题目上下文，帮你决定下一步先练什么。';
  }
  return '概念讲解模式适合问语法规则、易错点、概念差异和课堂知识点理解。';
});
const messagePlaceholder = computed(() => {
  if (form.mode === 'hint') {
    return '例如：请帮我分析这道题应该先从哪里入手';
  }
  if (form.mode === 'code_review') {
    return '例如：这段代码为什么会越界，应该先检查哪一部分';
  }
  if (form.mode === 'practice') {
    return '例如：根据我最近的作业情况，下一步最值得补哪一类题';
  }
  return '例如：数组名在表达式里为什么经常会退化为指针';
});

const modeLabel = (mode: TutorMode) => {
  if (mode === 'hint') return '解题提示';
  if (mode === 'code_review') return '代码纠错';
  if (mode === 'practice') return '练习推荐';
  return '概念讲解';
};

const followUpQuestions = (message: TutorSessionDetail['messages'][number]) => {
  const payload = (message.reply_json || {}) as { follow_up_questions?: string[] };
  return Array.isArray(payload.follow_up_questions) ? payload.follow_up_questions : [];
};

const recommendedAction = (message: TutorSessionDetail['messages'][number]) => {
  const payload = (message.reply_json || {}) as { recommended_action?: string };
  return payload.recommended_action || '';
};

const renderMarkdown = (content: string) => {
  const rendered = markdown.render(content || '');
  return DOMPurify.sanitize(rendered, {
    USE_PROFILES: { html: true },
  });
};

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

const formatRelativeTime = (value: string) => {
  const date = new Date(value);
  const diff = Date.now() - date.getTime();
  const minutes = Math.max(1, Math.floor(diff / 60000));
  if (minutes < 60) {
    return `${minutes} 分钟前`;
  }

  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return `${hours} 小时前`;
  }

  return `${Math.floor(hours / 24)} 天前`;
};

const currentSignature = () => `${classId.value}:${form.mode}:${form.assignmentId ?? 'none'}:${form.problemId ?? 'none'}`;
const sessionSignature = computed(() => {
  if (!sessionDetail.value) {
    return '';
  }
  return `${sessionDetail.value.class_id}:${sessionDetail.value.mode}:${sessionDetail.value.assignment_id ?? 'none'}:${sessionDetail.value.problem_id ?? 'none'}`;
});

const resetConversation = () => {
  activeSessionId.value = null;
  sessionDetail.value = null;
  instantReply.value = null;
  form.message = '';
  form.studentAnswer = '';
  form.currentCode = '';
  form.compilerOutput = '';
  form.expectedOutput = '';
};

const handleNewChat = () => {
  resetConversation();
};

const applyPrompt = (prompt: string) => {
  form.message = prompt;
};

const switchMode = (mode: TutorMode) => {
  form.mode = mode;
  instantReply.value = null;
  activeSessionId.value = null;
  sessionDetail.value = null;
};

const syncQueryToForm = () => {
  const assignmentId = route.query.assignmentId ? Number(route.query.assignmentId) : null;
  const problemId = route.query.problemId ? Number(route.query.problemId) : null;
  const mode = typeof route.query.mode === 'string' ? route.query.mode : null;

  form.assignmentId = Number.isFinite(assignmentId) ? assignmentId : null;
  form.problemId = Number.isFinite(problemId) ? problemId : null;
  if (mode === 'concept' || mode === 'hint' || mode === 'code_review' || mode === 'practice') {
    form.mode = mode;
  }
};

const loadAssignments = async () => {
  assignments.value = await listAssignments(classId.value);
};

const loadSessions = async () => {
  loadingSessions.value = true;
  try {
    const result = await listTutorSessions({ class_id: classId.value, limit: 100 });
    sessionList.value = result.items;
  } finally {
    loadingSessions.value = false;
  }
};

const openSession = async (sessionId: number) => {
  activeSessionId.value = sessionId;
  sessionDetail.value = await getTutorSession(sessionId);
  form.mode = sessionDetail.value.mode;
  form.assignmentId = sessionDetail.value.assignment_id ?? null;
  await loadProblems(form.assignmentId);
  form.problemId = sessionDetail.value.problem_id ?? null;
  await nextTick();
  if (messageScroller.value) {
    messageScroller.value.scrollTop = messageScroller.value.scrollHeight;
  }
};

const loadProblems = async (assignmentId: number | null) => {
  if (!assignmentId) {
    problems.value = [];
    form.problemId = null;
    return;
  }

  problems.value = await listProblems(assignmentId);
  if (form.problemId && !problems.value.some((item) => item.id === form.problemId)) {
    form.problemId = null;
  }
};

const loadRecommendations = async () => {
  if (!userStore.user.id) {
    recommendations.value = [];
    return;
  }

  const result = await getPracticeRecommendations(userStore.user.id, classId.value);
  recommendations.value = result.items;
};

const ensureSession = async () => {
  if (sessionDetail.value && sessionSignature.value === currentSignature()) {
    return sessionDetail.value;
  }

  sessionDetail.value = await createTutorSession({
    class_id: classId.value,
    assignment_id: form.assignmentId,
    problem_id: form.problemId,
    mode: form.mode,
    title: form.message.trim() ? form.message.trim().slice(0, 30) : undefined,
  });
  activeSessionId.value = sessionDetail.value.id;
  await loadSessions();
  return sessionDetail.value;
};

const resolveMessageContent = () => {
  if (form.message.trim()) {
    return form.message.trim();
  }

  if (form.mode === 'hint') {
    return '请根据当前题目和我的作答情况，给我下一步提示。';
  }
  if (form.mode === 'code_review') {
    return '请帮我解释这段代码的问题，并告诉我先检查哪里。';
  }
  if (form.mode === 'practice') {
    return '请结合我当前作业上下文，给我下一步练习建议。';
  }
  return '请帮我解释当前知识点，并指出最容易混淆的地方。';
};

const handleSendMessage = async () => {
  if (form.mode === 'code_review' && !form.currentCode.trim()) {
    ElMessage.warning('代码纠错模式下请先贴出你的代码');
    return;
  }

  sending.value = true;
  try {
    const activeSession = await ensureSession();
    sessionDetail.value = await sendTutorMessage(activeSession.id, {
      content: resolveMessageContent(),
      student_answer: form.studentAnswer.trim() || undefined,
      current_code: form.currentCode.trim() || undefined,
      compiler_output: form.compilerOutput.trim() || undefined,
      expected_output: form.expectedOutput.trim() || undefined,
    });
    activeSessionId.value = sessionDetail.value.id;
    await loadSessions();
    form.message = '';
    await nextTick();
    if (messageScroller.value) {
      messageScroller.value.scrollTop = messageScroller.value.scrollHeight;
    }
  } finally {
    sending.value = false;
  }
};

const handleQuickHint = async (hintLevel: number) => {
  if (!form.problemId) {
    ElMessage.warning('请先选择具体题目');
    return;
  }

  quickHinting.value = true;
  try {
    instantReply.value = await getProblemHint(form.problemId, {
      class_id: classId.value,
      assignment_id: form.assignmentId,
      student_answer: form.studentAnswer.trim() || undefined,
      current_code: form.currentCode.trim() || undefined,
      hint_level: hintLevel,
    });
  } finally {
    quickHinting.value = false;
  }
};

const handleStandaloneCodeReview = async () => {
  if (!form.currentCode.trim()) {
    ElMessage.warning('请先贴出你的代码');
    return;
  }

  reviewingCode.value = true;
  try {
    instantReply.value = await reviewCodeWithTutor({
      class_id: classId.value,
      assignment_id: form.assignmentId,
      problem_id: form.problemId,
      code: form.currentCode.trim(),
      compiler_output: form.compilerOutput.trim() || undefined,
      expected_output: form.expectedOutput.trim() || undefined,
      student_question: form.message.trim() || undefined,
    });
  } finally {
    reviewingCode.value = false;
  }
};

const handleDeleteSession = async (sessionId: number) => {
  await ElMessageBox.confirm('删除后该会话记录不可恢复，是否继续？', '删除会话', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  });

  await deleteTutorSession(sessionId);
  if (activeSessionId.value === sessionId) {
    handleNewChat();
  }
  await loadSessions();
  ElMessage.success('会话已删除');
};

const openRecommendation = async (assignmentId: number, problemId?: number | null) => {
  form.assignmentId = assignmentId;
  await loadProblems(assignmentId);
  form.problemId = problemId || null;
  form.mode = problemId ? 'hint' : 'practice';
  form.message = problemId ? '请根据这道题给我下一步最值得尝试的提示。' : '请根据这个作业给我下一步练习建议。';
  instantReply.value = null;
  sessionDetail.value = null;
};

onMounted(async () => {
  syncQueryToForm();
  classroom.value = await getClassroomDetail(classId.value);
  await loadAssignments();
  await loadProblems(form.assignmentId);
  await loadRecommendations();
  await loadSessions();

  if (form.assignmentId && !assignments.value.some((item) => item.id === form.assignmentId)) {
    const assignment = await getAssignment(form.assignmentId);
    assignments.value = [assignment, ...assignments.value];
  }
});

watch(
  () => form.assignmentId,
  async (nextAssignmentId, previousAssignmentId) => {
    if (nextAssignmentId === previousAssignmentId) {
      return;
    }
    await loadProblems(nextAssignmentId);
    instantReply.value = null;
  },
);

watch(
  () => [form.mode, form.problemId],
  () => {
    instantReply.value = null;
  },
);
</script>

<style scoped>
.markdown-body :deep(p) {
  margin: 0.55rem 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0.7rem 0;
  padding-left: 1.35rem;
}

.markdown-body :deep(li) {
  margin: 0.3rem 0;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin: 0.9rem 0 0.55rem;
  font-weight: 700;
  line-height: 1.4;
}

.markdown-body :deep(h1) {
  font-size: 1.25rem;
}

.markdown-body :deep(h2) {
  font-size: 1.1rem;
}

.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  font-size: 1rem;
}

.markdown-body :deep(pre) {
  overflow-x: auto;
  border-radius: 18px;
  padding: 1rem 1.1rem;
  margin: 0.85rem 0;
  background: #0f172a;
  color: #e2e8f0;
}

.markdown-body :deep(code) {
  border-radius: 0.45rem;
  padding: 0.15rem 0.4rem;
  font-family: Consolas, 'Courier New', monospace;
  font-size: 0.92em;
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: transparent;
  color: inherit;
}

.markdown-body :deep(:not(pre) > code) {
  background: rgba(15, 23, 42, 0.08);
  color: #0f172a;
}

.markdown-body :deep(blockquote) {
  margin: 0.8rem 0;
  border-left: 3px solid rgba(13, 148, 136, 0.45);
  padding-left: 0.9rem;
  color: #475569;
}

.markdown-body :deep(a) {
  color: #0f766e;
  text-decoration: underline;
  text-underline-offset: 0.18rem;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.9rem 0;
  overflow: hidden;
  border-radius: 0.9rem;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid rgba(148, 163, 184, 0.28);
  padding: 0.65rem 0.8rem;
  text-align: left;
}

.markdown-body :deep(th) {
  background: rgba(148, 163, 184, 0.08);
}

.markdown-assistant :deep(strong) {
  color: #0f172a;
}

.markdown-user :deep(a),
.markdown-user :deep(strong),
.markdown-user :deep(code) {
  color: inherit;
}

.markdown-user :deep(:not(pre) > code) {
  background: rgba(255, 255, 255, 0.14);
}

.markdown-user :deep(blockquote) {
  color: rgba(255, 255, 255, 0.78);
  border-left-color: rgba(255, 255, 255, 0.28);
}
</style>
