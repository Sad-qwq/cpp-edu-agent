<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-r from-slate-950 via-emerald-900 to-teal-700 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-emerald-100">
            模型配置
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">维护模型参数与调用额度</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">管理员可以在这里更新默认模型供应商、温度、输出长度限制，并查看最近的模型调用日志。</p>
        </div>

        <div class="grid w-full max-w-lg gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">当前供应商</p>
            <p class="mt-2 text-xl font-semibold">{{ config.provider || '--' }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">日志条数</p>
            <p class="mt-2 text-3xl font-semibold">{{ logsTotal }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">累计 Tokens</p>
            <p class="mt-2 text-3xl font-semibold">{{ visibleTokenTotal }}</p>
          </div>
        </div>
      </div>
    </section>

    <div class="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div class="flex items-center justify-between gap-4 border-b border-slate-100 pb-5">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">基础配置</h3>
            <p class="mt-1 text-sm text-slate-500">这些参数会影响平台默认的模型调用行为。</p>
          </div>
          <button
            type="button"
            class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
            :disabled="configLoading"
            @click="loadConfig"
          >
            {{ configLoading ? '刷新中...' : '刷新配置' }}
          </button>
        </div>

        <form class="mt-6 space-y-5" @submit.prevent="handleSaveConfig">
          <label class="block space-y-2">
            <span class="text-sm font-medium text-slate-700">模型供应商</span>
            <select
              v-model="form.provider"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
            >
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="azure">Azure OpenAI</option>
              <option value="custom">Custom</option>
            </select>
          </label>

          <label class="block space-y-2">
            <span class="text-sm font-medium text-slate-700">模型名称</span>
            <input
              v-model.trim="form.model_name"
              type="text"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
              placeholder="例如：gpt-4o-mini"
            />
          </label>

          <div class="grid gap-4 md:grid-cols-2">
            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">Temperature</span>
              <input
                v-model.number="form.temperature"
                type="number"
                min="0"
                max="2"
                step="0.1"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
              />
            </label>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">最大输出 Tokens</span>
              <input
                v-model.number="form.max_tokens"
                type="number"
                min="1"
                step="1"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
              />
            </label>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">每分钟速率限制</span>
              <input
                v-model.number="form.rate_limit_per_minute"
                type="number"
                min="1"
                step="1"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
              />
            </label>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">每日额度</span>
              <input
                v-model.trim="form.daily_quota"
                type="text"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
                placeholder="留空表示不限制"
              />
            </label>
          </div>

          <div class="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm leading-6 text-emerald-900">
            最近更新时间：{{ formatDateTime(config.updated_at) }}
          </div>

          <div class="flex justify-end">
            <button
              type="submit"
              class="rounded-2xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-emerald-400"
              :disabled="savingConfig"
            >
              {{ savingConfig ? '保存中...' : '保存配置' }}
            </button>
          </div>
        </form>
      </section>

      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div class="flex flex-col gap-4 border-b border-slate-100 pb-5">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">调用日志</h3>
              <p class="mt-1 text-sm text-slate-500">按用户和模型名称筛选最近调用记录。</p>
            </div>
            <button
              type="button"
              class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
              :disabled="logsLoading"
              @click="loadLogs"
            >
              {{ logsLoading ? '刷新中...' : '刷新日志' }}
            </button>
          </div>

          <div class="grid gap-3 md:grid-cols-[0.8fr_1fr_auto]">
            <input
              v-model.trim="filters.userId"
              type="text"
              class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
              placeholder="按用户 ID 筛选"
            />
            <input
              v-model.trim="filters.modelName"
              type="text"
              class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-500 focus:bg-white"
              placeholder="按模型名称筛选"
            />
            <button
              type="button"
              class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-slate-800"
              @click="handleSearch"
            >
              应用筛选
            </button>
          </div>
        </div>

        <div class="mt-6 grid gap-3 sm:grid-cols-3">
          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-xs text-slate-400">当前页成本</p>
            <p class="mt-2 text-xl font-semibold text-slate-900">{{ visibleCostTotal }}</p>
          </div>
          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-xs text-slate-400">当前页记录</p>
            <p class="mt-2 text-xl font-semibold text-slate-900">{{ logs.length }}</p>
          </div>
          <div class="rounded-2xl bg-slate-50 p-4">
            <p class="text-xs text-slate-400">当前页码</p>
            <p class="mt-2 text-xl font-semibold text-slate-900">{{ currentPage }}</p>
          </div>
        </div>

        <div v-if="logsLoading" class="mt-6 space-y-4">
          <div v-for="index in 4" :key="index" class="animate-pulse rounded-[24px] border border-slate-200 bg-slate-50 p-5">
            <div class="h-5 w-40 rounded bg-slate-200"></div>
            <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
            <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
          </div>
        </div>

        <div v-else-if="logs.length" class="mt-6 space-y-4">
          <article
            v-for="log in logs"
            :key="log.id"
            class="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
          >
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">用户 {{ log.user_id }}</span>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{{ log.model_name }}</span>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{{ formatDateTime(log.created_at) }}</span>
                </div>
                <div class="mt-4 grid gap-3 sm:grid-cols-4">
                  <div class="rounded-2xl bg-slate-50 p-3">
                    <p class="text-xs text-slate-400">Prompt</p>
                    <p class="mt-2 text-sm font-semibold text-slate-900">{{ log.prompt_tokens }}</p>
                  </div>
                  <div class="rounded-2xl bg-slate-50 p-3">
                    <p class="text-xs text-slate-400">Completion</p>
                    <p class="mt-2 text-sm font-semibold text-slate-900">{{ log.completion_tokens }}</p>
                  </div>
                  <div class="rounded-2xl bg-slate-50 p-3">
                    <p class="text-xs text-slate-400">Total</p>
                    <p class="mt-2 text-sm font-semibold text-slate-900">{{ log.total_tokens }}</p>
                  </div>
                  <div class="rounded-2xl bg-slate-50 p-3">
                    <p class="text-xs text-slate-400">Cost</p>
                    <p class="mt-2 text-sm font-semibold text-slate-900">{{ formatCost(log.cost) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
          <h4 class="text-lg font-semibold text-slate-900">暂无调用日志</h4>
          <p class="mt-2 text-sm leading-6 text-slate-500">当后端记录模型调用后，这里会展示最新数据。</p>
        </div>

        <div class="mt-6 flex items-center justify-between gap-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          <span>共 {{ logsTotal }} 条记录</span>
          <div class="flex gap-3">
            <button
              type="button"
              class="rounded-2xl border border-slate-200 bg-white px-4 py-2 font-medium transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-300"
              :disabled="currentPage <= 1 || logsLoading"
              @click="goToPage(currentPage - 1)"
            >
              上一页
            </button>
            <button
              type="button"
              class="rounded-2xl border border-slate-200 bg-white px-4 py-2 font-medium transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-300"
              :disabled="!hasNextPage || logsLoading"
              @click="goToPage(currentPage + 1)"
            >
              下一页
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import {
  getModelConfig,
  listModelUsageLogs,
  type ModelConfigItem,
  type ModelUsageLogItem,
  updateModelConfig,
} from '@/services/model-config';

const pageSize = 10;

const configLoading = ref(false);
const savingConfig = ref(false);
const logsLoading = ref(false);
const logsTotal = ref(0);
const currentPage = ref(1);
const logs = ref<ModelUsageLogItem[]>([]);

const config = reactive<ModelConfigItem>({
  id: 1,
  provider: '',
  model_name: '',
  temperature: 0,
  max_tokens: 0,
  rate_limit_per_minute: 0,
  daily_quota: null,
  updated_at: '',
});

const form = reactive({
  provider: 'openai',
  model_name: '',
  temperature: 0.2,
  max_tokens: 2048,
  rate_limit_per_minute: 60,
  daily_quota: '',
});

const filters = reactive({
  userId: '',
  modelName: '',
});

const hasNextPage = computed(() => currentPage.value * pageSize < logsTotal.value);
const visibleTokenTotal = computed(() => logs.value.reduce((sum, item) => sum + item.total_tokens, 0));
const visibleCostTotal = computed(() => {
  const total = logs.value.reduce((sum, item) => sum + (item.cost || 0), 0);
  return total ? total.toFixed(4) : '0.0000';
});

const formatDateTime = (value?: string) => {
  if (!value) {
    return '--';
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

const formatCost = (value?: number | null) => {
  if (value === null || value === undefined) {
    return '--';
  }

  return value.toFixed(4);
};

const syncFormFromConfig = () => {
  form.provider = config.provider;
  form.model_name = config.model_name;
  form.temperature = config.temperature;
  form.max_tokens = config.max_tokens;
  form.rate_limit_per_minute = config.rate_limit_per_minute;
  form.daily_quota = config.daily_quota === null || config.daily_quota === undefined ? '' : String(config.daily_quota);
};

const loadConfig = async () => {
  configLoading.value = true;
  try {
    const result = await getModelConfig();
    Object.assign(config, result);
    syncFormFromConfig();
  } finally {
    configLoading.value = false;
  }
};

const loadLogs = async () => {
  logsLoading.value = true;
  try {
    const result = await listModelUsageLogs({
      user_id: filters.userId ? Number(filters.userId) : undefined,
      model_name: filters.modelName || undefined,
      skip: (currentPage.value - 1) * pageSize,
      limit: pageSize,
    });
    logs.value = result.items;
    logsTotal.value = result.total;
  } finally {
    logsLoading.value = false;
  }
};

const handleSaveConfig = async () => {
  if (!form.model_name.trim()) {
    ElMessage.warning('模型名称不能为空');
    return;
  }

  if (form.temperature < 0 || form.temperature > 2) {
    ElMessage.warning('Temperature 需要在 0 到 2 之间');
    return;
  }

  const dailyQuotaValue = form.daily_quota.trim() ? Number(form.daily_quota.trim()) : null;
  if (dailyQuotaValue !== null && (!Number.isFinite(dailyQuotaValue) || dailyQuotaValue <= 0)) {
    ElMessage.warning('每日额度需要是正整数，或留空表示不限');
    return;
  }

  savingConfig.value = true;
  try {
    const updated = await updateModelConfig({
      provider: form.provider,
      model_name: form.model_name.trim(),
      temperature: Number(form.temperature),
      max_tokens: Number(form.max_tokens),
      rate_limit_per_minute: Number(form.rate_limit_per_minute),
      daily_quota: dailyQuotaValue,
    });
    Object.assign(config, updated);
    syncFormFromConfig();
    ElMessage.success('模型配置已更新');
  } finally {
    savingConfig.value = false;
  }
};

const handleSearch = () => {
  if (filters.userId && !/^\d+$/.test(filters.userId)) {
    ElMessage.warning('用户 ID 必须是数字');
    return;
  }

  currentPage.value = 1;
  loadLogs();
};

const goToPage = (page: number) => {
  currentPage.value = page;
  loadLogs();
};

onMounted(async () => {
  await Promise.all([loadConfig(), loadLogs()]);
});
</script>