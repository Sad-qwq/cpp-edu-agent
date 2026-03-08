<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-r from-slate-950 via-cyan-900 to-emerald-700 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-emerald-100">
            AI 智能出题
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">{{ classroom?.name || '智能出题工作台' }}</h2>
          <p class="max-w-3xl text-sm leading-6 text-slate-300">输入主题、知识点和题型比例，系统会基于班级资料与 Qwen 模型生成题目草稿。你可以单题重生成，再一键发布到现有作业。</p>
        </div>

        <div class="grid w-full max-w-xl gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">已有作业</p>
            <p class="mt-2 text-3xl font-semibold">{{ assignments.length }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">最近草稿数</p>
            <p class="mt-2 text-3xl font-semibold">{{ jobDetail?.drafts.length ?? 0 }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">当前状态</p>
            <p class="mt-2 text-sm font-semibold">{{ statusLabel(jobDetail?.status) }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <div class="space-y-6">
        <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
          <div class="border-b border-slate-100 pb-5">
            <h3 class="text-xl font-semibold text-slate-900">生成配置</h3>
            <p class="mt-1 text-sm text-slate-500">先生成草稿，再决定是否发布到某个作业。发布目标可以不预先选择。</p>
          </div>

          <form class="mt-6 space-y-5" @submit.prevent="handleGenerate">
            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">主题</span>
              <input
                v-model.trim="form.topic"
                type="text"
                maxlength="200"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
                placeholder="例如：函数、数组与循环综合训练"
              />
            </label>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">知识点</span>
              <textarea
                v-model.trim="knowledgePointsText"
                rows="4"
                class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
                placeholder="每行一个知识点，例如：
函数定义与调用
数组遍历
for 循环"
              ></textarea>
            </label>

            <div class="grid gap-4 md:grid-cols-2">
              <label class="block space-y-2">
                <span class="text-sm font-medium text-slate-700">草稿数量</span>
                <input v-model.number="form.totalCount" type="number" min="1" max="20" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white" />
              </label>

              <label class="block space-y-2">
                <span class="text-sm font-medium text-slate-700">发布目标作业</span>
                <select v-model="form.assignmentId" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white">
                  <option :value="null">暂不指定，先只生成草稿</option>
                  <option v-for="assignment in assignments" :key="assignment.id" :value="assignment.id">{{ assignment.title }}</option>
                </select>
              </label>
            </div>

            <div class="grid gap-4 md:grid-cols-2">
              <div class="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p class="text-sm font-semibold text-slate-900">题型分布</p>
                <div class="mt-4 grid gap-3">
                  <label class="block space-y-2">
                    <span class="text-xs font-medium text-slate-500">选择题</span>
                    <input v-model.number="form.distribution.choice" type="number" min="0" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500" />
                  </label>
                  <label class="block space-y-2">
                    <span class="text-xs font-medium text-slate-500">简答题</span>
                    <input v-model.number="form.distribution.short_answer" type="number" min="0" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500" />
                  </label>
                  <label class="block space-y-2">
                    <span class="text-xs font-medium text-slate-500">编程题</span>
                    <input v-model.number="form.distribution.coding" type="number" min="0" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500" />
                  </label>
                </div>
              </div>

              <div class="rounded-3xl border border-slate-200 bg-slate-50 p-4">
                <p class="text-sm font-semibold text-slate-900">难度分布</p>
                <div class="mt-4 grid gap-3">
                  <label class="block space-y-2">
                    <span class="text-xs font-medium text-slate-500">基础</span>
                    <input v-model.number="form.difficulty.easy" type="number" min="0" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500" />
                  </label>
                  <label class="block space-y-2">
                    <span class="text-xs font-medium text-slate-500">中等</span>
                    <input v-model.number="form.difficulty.medium" type="number" min="0" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500" />
                  </label>
                  <label class="block space-y-2">
                    <span class="text-xs font-medium text-slate-500">提高</span>
                    <input v-model.number="form.difficulty.hard" type="number" min="0" class="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500" />
                  </label>
                </div>
              </div>
            </div>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">额外约束</span>
              <textarea
                v-model.trim="form.extraConstraints"
                rows="4"
                class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
                placeholder="例如：
题干语言尽量贴近 C++ 程序设计课程
编程题避免使用 STL 以外的高级技巧"
              ></textarea>
            </label>

            <div class="grid gap-3 md:grid-cols-3">
              <label class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <input v-model="form.useClassMaterials" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-emerald-600" />
                使用班级资料
              </label>
              <label class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <input v-model="form.useAdminKnowledgeBase" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-emerald-600" />
                使用公共知识库
              </label>
              <label class="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                <input v-model="form.useHistoryQuestions" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-emerald-600" />
                使用历史题目
              </label>
            </div>

            <div class="flex gap-3">
              <button
                type="submit"
                class="rounded-2xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-emerald-400"
                :disabled="generating"
              >
                {{ generating ? '生成中...' : '开始智能出题' }}
              </button>
              <button
                type="button"
                class="rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                @click="router.push(`/classes/${classId}/assignments`)"
              >
                返回作业页
              </button>
            </div>
          </form>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
          <div class="border-b border-slate-100 pb-5">
            <h3 class="text-xl font-semibold text-slate-900">检索与任务摘要</h3>
            <p class="mt-1 text-sm text-slate-500">这里展示最近一次任务的检索来源和运行状态。</p>
          </div>

          <div v-if="jobDetail" class="mt-6 space-y-4">
            <div class="grid gap-3 sm:grid-cols-3">
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-xs text-slate-400">任务状态</p>
                <p class="mt-2 text-sm font-semibold text-slate-900">{{ statusLabel(jobDetail.status) }}</p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-xs text-slate-400">草稿数量</p>
                <p class="mt-2 text-sm font-semibold text-slate-900">{{ jobDetail.drafts.length }}</p>
              </div>
              <div class="rounded-2xl bg-slate-50 p-4">
                <p class="text-xs text-slate-400">检索分块</p>
                <p class="mt-2 text-sm font-semibold text-slate-900">{{ retrievalChunkCount }}</p>
              </div>
            </div>

            <div class="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-sm font-semibold text-slate-900">蓝图</p>
              <pre class="mt-3 whitespace-pre-wrap rounded-2xl bg-white p-4 text-xs leading-6 text-slate-700">{{ JSON.stringify(jobDetail.blueprint_json, null, 2) }}</pre>
            </div>

            <div class="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-sm font-semibold text-slate-900">检索摘要</p>
              <pre class="mt-3 whitespace-pre-wrap rounded-2xl bg-white p-4 text-xs leading-6 text-slate-700">{{ JSON.stringify(jobDetail.retrieval_summary, null, 2) }}</pre>
            </div>
          </div>

          <div v-else class="mt-6 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
            <h4 class="text-lg font-semibold text-slate-900">还没有生成任务</h4>
            <p class="mt-2 text-sm leading-6 text-slate-500">填好左侧配置后即可直接测试 Qwen 出题。</p>
          </div>
        </section>
      </div>

      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">题目草稿</h3>
            <p class="mt-1 text-sm text-slate-500">可单题重生成，也可勾选后发布到选定作业。</p>
          </div>

          <div class="flex flex-wrap gap-3">
            <select v-model="publishAssignmentId" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white">
              <option :value="null">选择发布作业</option>
              <option v-for="assignment in assignments" :key="assignment.id" :value="assignment.id">{{ assignment.title }}</option>
            </select>
            <button
              type="button"
              class="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
              :disabled="publishing || !jobDetail || selectedDraftIds.length === 0 || !publishAssignmentId"
              @click="handlePublish"
            >
              {{ publishing ? '发布中...' : `发布选中题目 (${selectedDraftIds.length})` }}
            </button>
          </div>
        </div>

        <div v-if="jobLoading" class="mt-6 space-y-4">
          <div v-for="index in 3" :key="index" class="animate-pulse rounded-[24px] border border-slate-200 bg-slate-50 p-6">
            <div class="h-5 w-48 rounded bg-slate-200"></div>
            <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
            <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
          </div>
        </div>

        <div v-else-if="jobDetail?.drafts.length" class="mt-6 space-y-4">
          <article v-for="draft in orderedDrafts" :key="draft.id" class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
            <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
              <div class="space-y-3">
                <div class="flex flex-wrap items-center gap-2">
                  <label class="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                    <input :checked="selectedDraftIds.includes(draft.id)" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-emerald-600" @change="toggleDraftSelection(draft.id)" />
                    选中发布
                  </label>
                  <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">{{ problemTypeLabel(draft.type) }}</span>
                  <span class="rounded-full px-3 py-1 text-xs font-medium" :class="validationBadgeClass(draft.validation_status)">{{ validationLabel(draft.validation_status) }}</span>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">{{ difficultyLabel(draft.difficulty) }}</span>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">{{ draft.estimated_score || 0 }} 分</span>
                </div>

                <div>
                  <h4 class="text-lg font-semibold text-slate-900">第 {{ draft.draft_index + 1 }} 题</h4>
                  <p class="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-600">{{ draft.content }}</p>
                </div>

                <div v-if="draft.type === 'choice'" class="space-y-2">
                  <div v-for="(option, optionIndex) in draft.options" :key="`${draft.id}-${optionIndex}`" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                    {{ String.fromCharCode(65 + optionIndex) }}. {{ option }}
                  </div>
                  <p v-if="draft.correct_answer" class="text-xs text-emerald-600">参考答案：{{ draft.correct_answer }}</p>
                </div>

                <div v-else-if="draft.type === 'coding'" class="space-y-3">
                  <pre v-if="draft.code_template" class="overflow-x-auto rounded-2xl border border-slate-200 bg-slate-900 p-4 font-mono text-xs leading-6 text-slate-100">{{ draft.code_template }}</pre>
                  <div v-if="draft.test_cases.length" class="grid gap-3 md:grid-cols-2">
                    <div v-for="(testCase, caseIndex) in draft.test_cases" :key="`${draft.id}-case-${caseIndex}`" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">用例 {{ caseIndex + 1 }}</p>
                      <p class="mt-3 text-xs font-medium text-slate-500">输入</p>
                      <pre class="mt-1 whitespace-pre-wrap rounded-2xl bg-white p-3 font-mono text-xs text-slate-700">{{ testCase.input || '空' }}</pre>
                      <p class="mt-3 text-xs font-medium text-slate-500">输出</p>
                      <pre class="mt-1 whitespace-pre-wrap rounded-2xl bg-white p-3 font-mono text-xs text-slate-700">{{ testCase.output || '空' }}</pre>
                    </div>
                  </div>
                </div>

                <div class="rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">
                  <p><span class="font-semibold text-slate-900">命中知识点：</span>{{ draft.target_knowledge_points.join('、') || '未标注' }}</p>
                  <p v-if="draft.explanation" class="mt-2"><span class="font-semibold text-slate-900">出题说明：</span>{{ draft.explanation }}</p>
                  <p class="mt-2"><span class="font-semibold text-slate-900">来源分块：</span>{{ draft.source_chunk_ids.join(', ') || '无' }}</p>
                </div>
              </div>

              <div class="flex gap-3 xl:flex-col">
                <button
                  type="button"
                  class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-300"
                  :disabled="regeneratingDraftId === draft.id || !jobDetail"
                  @click="handleRegenerateDraft(draft.id)"
                >
                  {{ regeneratingDraftId === draft.id ? '重生成中...' : '单题重生成' }}
                </button>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
          <h4 class="text-lg font-semibold text-slate-900">暂无草稿</h4>
          <p class="mt-2 text-sm leading-6 text-slate-500">左侧点击“开始智能出题”后，这里会展示生成结果。</p>
        </div>
      </section>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { type Assignment, listAssignments } from '@/services/assignments';
import {
  createQuestionGenerationJob,
  getQuestionGenerationJobDetail,
  publishQuestionGenerationJob,
  regenerateQuestionDraft,
  type QuestionDraft,
  type QuestionGenerationJobDetail,
} from '@/services/ai-question-generation';
import { getClassroomDetail, type ClassroomDetail } from '@/services/classes';

const route = useRoute();
const router = useRouter();

const classId = computed(() => Number(route.params.id));
const classroom = ref<ClassroomDetail | null>(null);
const assignments = ref<Assignment[]>([]);
const jobDetail = ref<QuestionGenerationJobDetail | null>(null);
const jobLoading = ref(false);
const generating = ref(false);
const publishing = ref(false);
const regeneratingDraftId = ref<number | null>(null);
const selectedDraftIds = ref<number[]>([]);
const publishAssignmentId = ref<number | null>(null);

const knowledgePointsText = ref('');
const form = reactive({
  topic: '',
  totalCount: 5,
  assignmentId: null as number | null,
  extraConstraints: '',
  useClassMaterials: true,
  useAdminKnowledgeBase: true,
  useHistoryQuestions: true,
  distribution: {
    choice: 2,
    short_answer: 2,
    coding: 1,
  },
  difficulty: {
    easy: 2,
    medium: 2,
    hard: 1,
  },
});

const orderedDrafts = computed(() => [...(jobDetail.value?.drafts || [])].sort((left, right) => left.draft_index - right.draft_index));
const retrievalChunkCount = computed(() => Number((jobDetail.value?.retrieval_summary?.chunk_count as number | undefined) || 0));

const loadBaseData = async () => {
  const [classDetail, assignmentList] = await Promise.all([
    getClassroomDetail(classId.value),
    listAssignments(classId.value),
  ]);
  classroom.value = classDetail;
  assignments.value = assignmentList;
};

const loadJobDetail = async (jobId: number) => {
  jobLoading.value = true;
  try {
    jobDetail.value = await getQuestionGenerationJobDetail(jobId);
    selectedDraftIds.value = jobDetail.value.drafts.map((draft) => draft.id);
    if (!publishAssignmentId.value && jobDetail.value.assignment_id) {
      publishAssignmentId.value = jobDetail.value.assignment_id;
    }
  } finally {
    jobLoading.value = false;
  }
};

const problemTypeLabel = (type: QuestionDraft['type']) => {
  if (type === 'choice') return '选择题';
  if (type === 'coding') return '编程题';
  return '简答题';
};

const difficultyLabel = (difficulty?: string | null) => {
  const map: Record<string, string> = {
    easy: '基础',
    medium: '中等',
    hard: '提高',
  };
  return map[difficulty || ''] || '未标注';
};

const validationLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: '待校验',
    passed: '校验通过',
    warning: '有警告',
    failed: '校验失败',
  };
  return map[status] || status;
};

const validationBadgeClass = (status: string) => {
  const map: Record<string, string> = {
    pending: 'bg-slate-100 text-slate-700',
    passed: 'bg-emerald-100 text-emerald-700',
    warning: 'bg-amber-100 text-amber-700',
    failed: 'bg-rose-100 text-rose-700',
  };
  return map[status] || 'bg-slate-100 text-slate-700';
};

const statusLabel = (status?: string | null) => {
  const map: Record<string, string> = {
    pending: '等待中',
    retrieving: '检索资料中',
    blueprinting: '整理蓝图中',
    generating: '生成草稿中',
    validating: '校验中',
    reviewing: '待教师审核',
    published: '已发布',
    failed: '失败',
  };
  return map[status || ''] || '未开始';
};

const normalizeNonNegativeInt = (value: number) => Math.max(0, Number.isFinite(value) ? Math.floor(value) : 0);

const toggleDraftSelection = (draftId: number) => {
  if (selectedDraftIds.value.includes(draftId)) {
    selectedDraftIds.value = selectedDraftIds.value.filter((id) => id !== draftId);
    return;
  }
  selectedDraftIds.value = [...selectedDraftIds.value, draftId];
};

const handleGenerate = async () => {
  if (!form.topic.trim()) {
    ElMessage.warning('请输入出题主题');
    return;
  }

  const knowledgePoints = knowledgePointsText.value
    .split(/\r?\n|,|，/)
    .map((item) => item.trim())
    .filter(Boolean);

  if (!knowledgePoints.length) {
    ElMessage.warning('请至少填写一个知识点');
    return;
  }

  generating.value = true;
  try {
    const createdJob = await createQuestionGenerationJob({
      class_id: classId.value,
      assignment_id: form.assignmentId,
      topic: form.topic.trim(),
      knowledge_points: knowledgePoints,
      total_count: normalizeNonNegativeInt(form.totalCount) || 5,
      question_type_distribution: {
        choice: normalizeNonNegativeInt(form.distribution.choice),
        short_answer: normalizeNonNegativeInt(form.distribution.short_answer),
        coding: normalizeNonNegativeInt(form.distribution.coding),
      },
      difficulty_distribution: {
        easy: normalizeNonNegativeInt(form.difficulty.easy),
        medium: normalizeNonNegativeInt(form.difficulty.medium),
        hard: normalizeNonNegativeInt(form.difficulty.hard),
      },
      use_class_materials: form.useClassMaterials,
      use_admin_knowledge_base: form.useAdminKnowledgeBase,
      use_history_questions: form.useHistoryQuestions,
      extra_constraints: form.extraConstraints.trim() || undefined,
    });
    await loadJobDetail(createdJob.id);
    publishAssignmentId.value = form.assignmentId;
    ElMessage.success('智能出题完成，已生成草稿');
  } finally {
    generating.value = false;
  }
};

const handleRegenerateDraft = async (draftId: number) => {
  if (!jobDetail.value) {
    return;
  }
  regeneratingDraftId.value = draftId;
  try {
    await regenerateQuestionDraft(jobDetail.value.id, draftId);
    await loadJobDetail(jobDetail.value.id);
    ElMessage.success('题目已重生成');
  } finally {
    regeneratingDraftId.value = null;
  }
};

const handlePublish = async () => {
  if (!jobDetail.value || !publishAssignmentId.value || !selectedDraftIds.value.length) {
    ElMessage.warning('请先选择目标作业和要发布的题目');
    return;
  }

  publishing.value = true;
  try {
    const result = await publishQuestionGenerationJob(jobDetail.value.id, {
      assignment_id: publishAssignmentId.value,
      accepted_draft_ids: selectedDraftIds.value,
    });
    await Promise.all([loadJobDetail(jobDetail.value.id), loadBaseData()]);
    ElMessage.success(result.message || '题目已发布到作业');
    router.push(`/assignments/${publishAssignmentId.value}`);
  } finally {
    publishing.value = false;
  }
};

onMounted(() => {
  loadBaseData();
});
</script>