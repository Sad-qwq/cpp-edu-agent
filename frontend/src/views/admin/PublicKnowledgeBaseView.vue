<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-r from-slate-950 via-cyan-900 to-blue-700 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-cyan-100">
            公共知识库
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">维护跨班级复用的教学资料</h2>
          <p class="max-w-3xl text-sm leading-6 text-slate-300">管理员可在这里上传课程规范、章节讲义、标准样题和术语说明。启用“公共知识库”后，这些文档会参与 AI 出题检索。</p>
        </div>

        <div class="grid w-full max-w-lg gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">文档总数</p>
            <p class="mt-2 text-3xl font-semibold">{{ total }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">已完成入库</p>
            <p class="mt-2 text-3xl font-semibold">{{ completedCount }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">当前筛选</p>
            <p class="mt-2 text-sm font-semibold">{{ filters.keyword.trim() || '全部文档' }}</p>
          </div>
        </div>
      </div>
    </section>

    <div class="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div>
          <p class="text-sm font-medium uppercase tracking-[0.22em] text-cyan-600">Upload Document</p>
          <h3 class="mt-2 text-xl font-semibold text-slate-900">上传公共知识库文档</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">推荐上传课程规范、章节知识点说明、样题库或术语文档。Markdown、TXT、PDF、PPTX 都可以自动入库。</p>
        </div>

        <form class="mt-5 space-y-4" @submit.prevent="handleUpload">
          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">文档标题</label>
            <input
              v-model="uploadForm.title"
              type="text"
              placeholder="例如：C++ 出题规范文档"
              class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
            />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">文档说明</label>
            <textarea
              v-model="uploadForm.description"
              rows="3"
              placeholder="说明该文档适用的章节、目标或使用约束"
              class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
            ></textarea>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">上传文件</label>
            <input
              type="file"
              class="block w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 file:mr-4 file:rounded-xl file:border-0 file:bg-cyan-600 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-cyan-700"
              @change="handleFileChange"
            />
            <p class="text-xs text-slate-400">{{ uploadForm.file?.name || '尚未选择文件' }}</p>
          </div>

          <button
            type="submit"
            class="flex h-[52px] w-full items-center justify-center gap-2 rounded-2xl bg-cyan-600 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:bg-cyan-700 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-cyan-400"
            :disabled="uploading"
          >
            <span v-if="uploading" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
            {{ uploading ? '上传中...' : '上传并入库' }}
          </button>
        </form>
      </section>

      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">文档列表</h3>
            <p class="mt-1 text-sm text-slate-500">已上传的公共知识库文档会在这里展示，并参与管理员启用的公共检索。</p>
          </div>

          <div class="flex gap-3">
            <input
              v-model="filters.keyword"
              type="text"
              placeholder="按标题筛选"
              class="h-[48px] rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
            />
            <button
              type="button"
              class="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-slate-800"
              @click="loadDocuments"
            >
              搜索
            </button>
          </div>
        </div>

        <div v-if="loading" class="mt-6 space-y-4">
          <div v-for="index in 3" :key="index" class="animate-pulse rounded-[24px] border border-slate-200 bg-slate-50 p-5">
            <div class="h-5 w-40 rounded bg-slate-200"></div>
            <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
            <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
          </div>
        </div>

        <div v-else-if="documents.length" class="mt-6 space-y-4">
          <article
            v-for="document in documents"
            :key="document.id"
            class="rounded-[24px] border border-slate-200 bg-white p-5 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
          >
            <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div class="space-y-3">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded-full bg-cyan-100 px-3 py-1 text-xs font-medium text-cyan-700">公共知识库</span>
                  <span class="rounded-full px-3 py-1 text-xs font-medium" :class="statusBadgeClass(document.parse_status)">{{ statusLabel(document.parse_status) }}</span>
                  <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">{{ displayMimeType(document.mime_type) }}</span>
                </div>

                <div>
                  <h4 class="text-lg font-semibold text-slate-900">{{ document.title }}</h4>
                  <p class="mt-2 text-sm leading-6 text-slate-600">{{ descriptionOf(document) || '暂无补充说明。' }}</p>
                </div>

                <div class="rounded-2xl bg-slate-50 p-4 text-sm leading-6 text-slate-600">
                  <p><span class="font-semibold text-slate-900">原始文件：</span>{{ originalFilenameOf(document) || '未知文件名' }}</p>
                  <p class="mt-2"><span class="font-semibold text-slate-900">分块数量：</span>{{ chunkCountOf(document) }}</p>
                  <p class="mt-2"><span class="font-semibold text-slate-900">更新时间：</span>{{ formatDateTime(document.updated_at) }}</p>
                  <p v-if="document.parse_error" class="mt-2 text-rose-600"><span class="font-semibold">解析错误：</span>{{ document.parse_error }}</p>
                </div>
              </div>

              <div class="flex gap-3 sm:flex-col">
                <a
                  v-if="fileUrlOf(document)"
                  :href="resolveAssetUrl(fileUrlOf(document) || '')"
                  target="_blank"
                  rel="noreferrer"
                  class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-center text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
                >
                  查看文件
                </a>
                <button
                  type="button"
                  class="rounded-2xl bg-rose-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-rose-700 disabled:cursor-not-allowed disabled:bg-rose-400"
                  :disabled="deletingDocumentId === document.id"
                  @click="handleDelete(document.id)"
                >
                  {{ deletingDocumentId === document.id ? '删除中...' : '删除文档' }}
                </button>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
          <h4 class="text-lg font-semibold text-slate-900">暂无公共知识库文档</h4>
          <p class="mt-2 text-sm leading-6 text-slate-500">上传一份课程规范、样题库或章节讲义后，这里会立即展示。</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { API_ORIGIN } from '@/api/request';
import {
  deleteAdminKnowledgeDocument,
  listAdminKnowledgeDocuments,
  uploadAdminKnowledgeDocument,
  type KnowledgeDocumentItem,
} from '@/services/knowledge-base';

const loading = ref(false);
const uploading = ref(false);
const deletingDocumentId = ref<number | null>(null);
const total = ref(0);
const documents = ref<KnowledgeDocumentItem[]>([]);
const filters = reactive({ keyword: '' });
const uploadForm = reactive<{ title: string; description: string; file: File | null }>({
  title: '',
  description: '',
  file: null,
});

const completedCount = computed(() => documents.value.filter((item) => item.parse_status === 'completed').length);

const resolveAssetUrl = (url: string) => `${API_ORIGIN}${url}`;

const descriptionOf = (document: KnowledgeDocumentItem) => String(document.metadata_json.description || '');
const fileUrlOf = (document: KnowledgeDocumentItem) => String(document.metadata_json.file_url || '');
const originalFilenameOf = (document: KnowledgeDocumentItem) => String(document.metadata_json.original_filename || '');
const chunkCountOf = (document: KnowledgeDocumentItem) => Number(document.metadata_json.chunk_count || 0);

const statusLabel = (status: KnowledgeDocumentItem['parse_status']) => {
  const map = {
    pending: '等待中',
    processing: '处理中',
    completed: '入库完成',
    failed: '入库失败',
  };
  return map[status] || status;
};

const statusBadgeClass = (status: KnowledgeDocumentItem['parse_status']) => {
  const map = {
    pending: 'bg-slate-100 text-slate-700',
    processing: 'bg-amber-100 text-amber-700',
    completed: 'bg-emerald-100 text-emerald-700',
    failed: 'bg-rose-100 text-rose-700',
  };
  return map[status] || 'bg-slate-100 text-slate-700';
};

const displayMimeType = (value?: string | null) => (value || 'unknown').toUpperCase();

const formatDateTime = (value?: string | null) => {
  if (!value) {
    return '--';
  }
  return new Date(value).toLocaleString('zh-CN', { hour12: false });
};

const loadDocuments = async () => {
  loading.value = true;
  try {
    const response = await listAdminKnowledgeDocuments({ keyword: filters.keyword.trim() || undefined, limit: 50 });
    documents.value = response.items;
    total.value = response.total;
  } finally {
    loading.value = false;
  }
};

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  uploadForm.file = input.files?.[0] || null;
};

const handleUpload = async () => {
  if (!uploadForm.title.trim()) {
    ElMessage.warning('请输入文档标题');
    return;
  }
  if (!uploadForm.file) {
    ElMessage.warning('请选择要上传的文件');
    return;
  }

  uploading.value = true;
  try {
    await uploadAdminKnowledgeDocument({
      title: uploadForm.title.trim(),
      description: uploadForm.description.trim(),
      file: uploadForm.file,
    });
    uploadForm.title = '';
    uploadForm.description = '';
    uploadForm.file = null;
    ElMessage.success('公共知识库文档上传并入库成功');
    await loadDocuments();
  } finally {
    uploading.value = false;
  }
};

const handleDelete = async (documentId: number) => {
  await ElMessageBox.confirm('确认删除这份公共知识库文档吗？删除后将不会再参与 AI 出题检索。', '删除确认', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  });

  deletingDocumentId.value = documentId;
  try {
    await deleteAdminKnowledgeDocument(documentId);
    ElMessage.success('公共知识库文档已删除');
    await loadDocuments();
  } finally {
    deletingDocumentId.value = null;
  }
};

onMounted(() => {
  loadDocuments();
});
</script>