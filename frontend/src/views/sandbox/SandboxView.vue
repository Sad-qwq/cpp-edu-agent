<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-900 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-indigo-100">
            C++ 沙箱
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">在线编译与运行 C++ 代码</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">在浏览器内快速验证语法、调试输入输出，并对课堂代码片段做即时实验。当前版本直接调用后端编译执行接口。</p>
        </div>

        <div class="grid w-full max-w-xl grid-cols-3 gap-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">语言</p>
            <p class="mt-2 text-xl font-semibold">C++</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">运行状态</p>
            <p class="mt-2 text-sm font-semibold">{{ statusLabel }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">最近结果</p>
            <p class="mt-2 text-sm font-semibold">{{ result.status ? result.status : '未执行' }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="grid gap-4 xl:grid-cols-[1.45fr_0.55fr] xl:items-start">
      <div class="space-y-4">
        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">代码编辑区</h3>
              <p class="mt-1 text-sm text-slate-500">支持自由粘贴或基于模板快速开始，左侧专注写代码，右侧统一查看输入和结果。</p>
            </div>
            <div class="flex gap-3">
              <button
                type="button"
                class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                @click="loadTemplate('hello')"
              >
                Hello World
              </button>
              <button
                type="button"
                class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                @click="loadTemplate('input')"
              >
                输入模板
              </button>
              <button
                type="button"
                class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                @click="formatCodeSample"
              >
                恢复示例
              </button>
            </div>
          </div>

          <div class="mt-5 rounded-[24px] border border-slate-800 bg-[#08111f] shadow-inner shadow-slate-950/40">
            <div class="flex items-center justify-between border-b border-slate-800 px-5 py-3">
              <div class="flex items-center gap-2">
                <span class="h-3 w-3 rounded-full bg-rose-400"></span>
                <span class="h-3 w-3 rounded-full bg-amber-400"></span>
                <span class="h-3 w-3 rounded-full bg-emerald-400"></span>
              </div>
              <div class="rounded-full bg-white/5 px-3 py-1 text-xs font-medium text-slate-300">
                main.cpp
              </div>
            </div>

            <div class="relative min-h-[620px] overflow-hidden rounded-b-[24px]">
              <pre
                ref="codePreviewRef"
                class="pointer-events-none min-h-[620px] overflow-auto px-5 py-4 font-mono text-sm leading-7 text-slate-100"
              ><code v-html="highlightedCode"></code></pre>
              <textarea
                ref="codeInputRef"
                v-model="code"
                rows="22"
                spellcheck="false"
                class="absolute inset-0 min-h-[620px] w-full resize-none overflow-auto bg-transparent px-5 py-4 font-mono text-sm leading-7 text-transparent caret-slate-100 outline-none selection:bg-indigo-500/30"
                @scroll="syncCodeScroll"
              ></textarea>
            </div>
          </div>

          <div class="mt-5 flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-slate-50 px-4 py-4">
            <div class="flex flex-wrap items-center gap-3 text-sm text-slate-500">
              <span class="rounded-full bg-white px-3 py-1 font-medium text-slate-700">main.cpp</span>
              <span>{{ codeLineCount }} 行代码</span>
              <span>{{ codeCharCount }} 个字符</span>
            </div>
            <button
              type="button"
              class="flex items-center justify-center gap-2 rounded-2xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-indigo-400"
              :disabled="running"
              @click="handleRun"
            >
              <span v-if="running" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
              {{ running ? '执行中...' : '运行代码' }}
            </button>
          </div>
        </div>

        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">使用建议</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">当前沙箱适合课堂练习、语法验证和短程序调试，不适合长时间或高资源任务。</p>
          </div>
          <div class="mt-5 grid gap-3 lg:grid-cols-3">
            <div class="rounded-2xl bg-slate-50 px-4 py-4 text-sm leading-6 text-slate-600">编译失败时，错误信息会显示在右侧 Error 面板。</div>
            <div class="rounded-2xl bg-slate-50 px-4 py-4 text-sm leading-6 text-slate-600">运行超时会被后端终止，并返回超时提示。</div>
            <div class="rounded-2xl bg-slate-50 px-4 py-4 text-sm leading-6 text-slate-600">建议优先写标准输入输出风格代码，方便和作业题联动。</div>
          </div>
        </div>
      </div>

      <div class="space-y-4 xl:sticky xl:top-6">
        <div class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">运行面板</h3>
              <p class="mt-1 text-sm text-slate-500">输入、输出和错误信息集中在这里查看。</p>
            </div>
            <span class="rounded-full px-3 py-1 text-xs font-medium" :class="statusBadgeClass">
              {{ statusLabel }}
            </span>
          </div>

          <div class="mt-5 space-y-5">
            <div>
              <div class="flex items-center justify-between gap-3">
                <h4 class="text-sm font-semibold uppercase tracking-[0.18em] text-slate-500">标准输入</h4>
                <span class="text-xs text-slate-400">stdin</span>
              </div>
              <textarea
                v-model="inputData"
                rows="8"
                spellcheck="false"
                placeholder="例如：
5
1 2 3 4 5"
                class="mt-3 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 font-mono text-sm leading-6 text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-indigo-500 focus:bg-white focus:ring-4 focus:ring-indigo-100"
              ></textarea>
            </div>

            <div>
              <div class="flex items-center gap-2 rounded-2xl bg-slate-100 p-1">
                <button
                  type="button"
                  class="flex-1 rounded-xl px-4 py-2 text-sm font-medium transition-all duration-300"
                  :class="activePanel === 'output' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                  @click="activePanel = 'output'"
                >
                  标准输出
                </button>
                <button
                  type="button"
                  class="flex-1 rounded-xl px-4 py-2 text-sm font-medium transition-all duration-300"
                  :class="activePanel === 'error' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
                  @click="activePanel = 'error'"
                >
                  错误信息
                </button>
              </div>

              <pre
                v-if="activePanel === 'output'"
                class="mt-3 min-h-[260px] whitespace-pre-wrap rounded-2xl bg-slate-950 p-4 font-mono text-sm leading-6 text-emerald-300"
              >{{ result.output || '暂无输出' }}</pre>
              <pre
                v-else
                class="mt-3 min-h-[260px] whitespace-pre-wrap rounded-2xl bg-slate-950 p-4 font-mono text-sm leading-6 text-rose-300"
              >{{ result.error || '暂无错误信息' }}</pre>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { executeCode } from '@/services/sandbox';

const helloWorldTemplate = `#include <iostream>
using namespace std;

int main() {
    cout << "Hello, C++ Edu Platform!" << endl;
    return 0;
}
`;

const inputTemplate = `#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    cin >> n;

    vector<int> nums(n);
    int sum = 0;
    for (int i = 0; i < n; ++i) {
        cin >> nums[i];
        sum += nums[i];
    }

    cout << "sum = " << sum << endl;
    return 0;
}
`;

const code = ref(helloWorldTemplate);
const inputData = ref('');
const running = ref(false);
const activePanel = ref<'output' | 'error'>('output');
const codeInputRef = ref<HTMLTextAreaElement | null>(null);
const codePreviewRef = ref<HTMLElement | null>(null);
const result = ref({
  output: '',
  error: '',
  status: '',
});

const escapeHtml = (value: string) => value
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;');

const highlightCpp = (source: string) => {
  const tokenPattern = new RegExp(
    [
      '#[^\\n]*',
      '"(?:\\\\.|[^"\\\\])*"',
      "'(?:\\\\.|[^'\\\\])*'",
      '\\/\\/[^\\n]*',
      '\\/\\*[\\s\\S]*?\\*\\/',
      '\\b(?:include|using|namespace|int|long|short|float|double|char|bool|void|return|for|while|if|else|switch|case|break|continue|class|struct|template|typename|const|auto|new|delete|nullptr|true|false|main)\\b',
      '\\b(?:std|cout|cin|endl|vector|string)\\b',
      '\\b\\d+(?:\\.\\d+)?\\b',
    ].join('|'),
    'g',
  );
  let resultHtml = '';
  let lastIndex = 0;

  for (const match of source.matchAll(tokenPattern)) {
    const matchIndex = match.index ?? 0;
    const token = match[0];
    resultHtml += escapeHtml(source.slice(lastIndex, matchIndex));

    let className = 'text-slate-100';
    if (token.startsWith('#')) {
      className = 'text-sky-300';
    } else if (token.startsWith('//') || token.startsWith('/*')) {
      className = 'text-slate-500';
    } else if (token.startsWith('"') || token.startsWith('\'')) {
      className = 'text-amber-300';
    } else if (/^\d/.test(token)) {
      className = 'text-rose-300';
    } else if (/^(std|cout|cin|endl|vector|string)$/.test(token)) {
      className = 'text-emerald-300';
    } else {
      className = 'text-violet-300';
    }

    resultHtml += `<span class="${className}">${escapeHtml(token)}</span>`;
    lastIndex = matchIndex + token.length;
  }

  resultHtml += escapeHtml(source.slice(lastIndex));
  return resultHtml || '<span class="text-slate-500">// 在这里输入 C++ 代码</span>';
};

const highlightedCode = computed(() => highlightCpp(code.value));

const statusLabel = computed(() => {
  if (running.value) {
    return '执行中';
  }
  if (result.value.status === 'success') {
    return '运行成功';
  }
  if (result.value.status === 'compile_error') {
    return '编译失败';
  }
  if (result.value.status === 'runtime_error') {
    return '运行错误';
  }
  return '未开始';
});

const statusBadgeClass = computed(() => {
  if (running.value) {
    return 'bg-amber-100 text-amber-700';
  }
  if (result.value.status === 'success') {
    return 'bg-emerald-100 text-emerald-700';
  }
  if (result.value.status === 'compile_error' || result.value.status === 'runtime_error') {
    return 'bg-rose-100 text-rose-700';
  }
  return 'bg-slate-100 text-slate-700';
});

const codeLineCount = computed(() => code.value.split('\n').length);
const codeCharCount = computed(() => code.value.length);

const loadTemplate = (type: 'hello' | 'input') => {
  code.value = type === 'hello' ? helloWorldTemplate : inputTemplate;
  if (type === 'hello') {
    inputData.value = '';
  }
};

const formatCodeSample = () => {
  code.value = helloWorldTemplate;
  inputData.value = '';
  activePanel.value = 'output';
  result.value = {
    output: '',
    error: '',
    status: '',
  };
};

const syncCodeScroll = () => {
  if (!codeInputRef.value || !codePreviewRef.value) {
    return;
  }

  codePreviewRef.value.scrollTop = codeInputRef.value.scrollTop;
  codePreviewRef.value.scrollLeft = codeInputRef.value.scrollLeft;
};

const handleRun = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请输入要执行的 C++ 代码');
    return;
  }

  running.value = true;
  try {
    result.value = await executeCode({
      code: code.value,
      input_data: inputData.value,
    });

    activePanel.value = result.value.status === 'success' ? 'output' : 'error';

    if (result.value.status === 'success') {
      ElMessage.success('代码运行成功');
    } else if (result.value.status === 'compile_error') {
      ElMessage.error('代码编译失败');
    } else {
      ElMessage.warning('代码运行完成，但存在错误');
    }
  } finally {
    running.value = false;
  }
};
</script>