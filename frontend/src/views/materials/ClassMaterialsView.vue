<template>
  <div class="space-y-6">
    <section class="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
      <div class="rounded-[28px] bg-gradient-to-br from-slate-900 via-slate-800 to-cyan-900 p-6 text-white shadow-sm sm:p-7">
        <div class="space-y-4">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-cyan-100">
            班级资料
          </div>
          <h2 class="text-2xl font-semibold tracking-tight">{{ classroom?.name || '资料中心' }}</h2>
          <p class="max-w-2xl text-sm leading-6 text-slate-300">集中管理当前班级的课件、PDF、视频与补充讲义。学生可快速检索下载，教师可持续更新资料。</p>
        </div>

        <div class="mt-6 grid gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">资料总数</p>
            <p class="mt-2 text-3xl font-semibold">{{ total }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">当前筛选</p>
            <p class="mt-2 text-xl font-semibold">{{ fileTypeLabel(filters.fileType) }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-slate-300">上传权限</p>
            <p class="mt-2 text-xl font-semibold">{{ canManageMaterials ? '教师可用' : '仅浏览' }}</p>
          </div>
        </div>
      </div>

      <div v-if="canManageMaterials" class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div>
          <p class="text-sm font-medium uppercase tracking-[0.22em] text-cyan-600">Upload Material</p>
          <h3 class="mt-2 text-xl font-semibold text-slate-900">上传班级资料</h3>
          <p class="mt-2 text-sm leading-6 text-slate-500">支持 PDF、PPTX、视频及其他补充文件，上传成功后会自动完成知识入库并出现在资料列表中。旧版 .ppt 请先转换为 .pptx 或 PDF。</p>
        </div>

        <form class="mt-5 space-y-4" @submit.prevent="handleUpload">
          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">资料标题</label>
            <input
              v-model="uploadForm.title"
              type="text"
              placeholder="例如：模板元编程讲义"
              class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
            />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium text-slate-700">资料说明</label>
            <textarea
              v-model="uploadForm.description"
              rows="3"
              placeholder="简要说明适用章节、阅读建议或使用场景"
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
            {{ uploading ? '上传中...' : '上传资料' }}
          </button>
        </form>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
      <div class="flex flex-col gap-4 border-b border-slate-100 pb-5 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <h2 class="text-xl font-semibold text-slate-900">资料列表</h2>
          <p class="mt-1 text-sm text-slate-500">按文件类型与关键字检索当前班级资料。</p>
        </div>

        <div class="grid gap-3 sm:grid-cols-3 xl:min-w-[720px]">
          <input
            v-model="filters.keyword"
            type="text"
            placeholder="搜索标题或说明"
            class="h-[48px] rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
          />
          <select
            v-model="filters.fileType"
            class="h-[48px] rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm text-slate-800 outline-none transition-all duration-300 focus:border-cyan-500 focus:bg-white focus:ring-4 focus:ring-cyan-100"
          >
            <option value="">全部类型</option>
            <option value="pdf">PDF</option>
            <option value="ppt">PPT</option>
            <option value="video">视频</option>
            <option value="other">其他</option>
          </select>
          <div class="flex gap-3">
            <button
              type="button"
              class="flex-1 rounded-2xl bg-cyan-50 px-4 py-3 text-sm font-medium text-cyan-700 transition-all duration-300 hover:-translate-y-1 hover:bg-cyan-100"
              @click="loadMaterials"
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

      <div v-if="loading" class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div v-for="index in 3" :key="index" class="animate-pulse rounded-[24px] border border-slate-200 bg-slate-50 p-6">
          <div class="h-5 w-40 rounded bg-slate-200"></div>
          <div class="mt-4 h-4 w-full rounded bg-slate-200"></div>
          <div class="mt-2 h-4 w-2/3 rounded bg-slate-200"></div>
          <div class="mt-6 h-11 rounded-2xl bg-slate-200"></div>
        </div>
      </div>

      <div v-else-if="materials.length" class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="material in materials"
          :key="material.id"
          class="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <span class="rounded-full px-3 py-1 text-xs font-medium" :class="fileTypeBadgeClass(material.file_type)">
                {{ fileTypeLabel(material.file_type) }}
              </span>
              <h3 class="mt-4 text-xl font-semibold text-slate-900">{{ material.title }}</h3>
            </div>
            <span class="text-xs text-slate-400">{{ formatDateTime(material.created_at) }}</span>
          </div>

          <p class="mt-4 min-h-[72px] text-sm leading-6 text-slate-500">
            {{ material.description || '当前资料还没有补充说明。' }}
          </p>

          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">文件大小</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ formatSize(material.size) }}</p>
            </div>
            <div class="rounded-2xl bg-slate-50 p-4">
              <p class="text-xs text-slate-400">资料类型</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ fileTypeLabel(material.file_type) }}</p>
            </div>
          </div>

          <div class="mt-5 flex gap-3">
            <a
              class="flex-1 rounded-2xl bg-cyan-600 px-4 py-3 text-center text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-cyan-700"
              :href="resolveFileUrl(material.file_url)"
              target="_blank"
              rel="noreferrer"
            >
              打开资料
            </a>
            <button
              v-if="canManageMaterials"
              type="button"
              class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-600 transition-all duration-300 hover:-translate-y-1 hover:bg-red-100"
              @click="handleDelete(material.id)"
            >
              删除
            </button>
          </div>
        </article>
      </div>

      <div v-else class="mt-10 rounded-[24px] border border-dashed border-slate-200 bg-slate-50 px-6 py-12 text-center">
        <h3 class="text-lg font-semibold text-slate-900">当前班级还没有资料</h3>
        <p class="mt-2 text-sm leading-6 text-slate-500">{{ canManageMaterials ? '上传第一份讲义或课件后，这里会立即展示。' : '教师上传资料后，你可以在这里查看和下载。' }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import request, { API_ORIGIN } from '@/api/request';
import { useUserStore } from '@/stores/user';
import { deleteMaterial, listMaterials, uploadMaterial, type MaterialItem } from '@/services/materials';

interface ClassroomDetail {
  id: number;
  name: string;
  teacher_name?: string | null;
}

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const classId = computed(() => Number(route.params.id));
const loading = ref(false);
const uploading = ref(false);
const materials = ref<MaterialItem[]>([]);
const total = ref(0);
const classroom = ref<ClassroomDetail | null>(null);

const filters = reactive({
  keyword: '',
  fileType: '',
});

const uploadForm = reactive<{
  title: string;
  description: string;
  file: File | null;
}>({
  title: '',
  description: '',
  file: null,
});

const canManageMaterials = computed(() => userStore.user.role === 'teacher' || userStore.user.role === 'admin');

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

const formatSize = (size?: number | null) => {
  if (!size) {
    return '未知';
  }
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
};

const fileTypeLabel = (type?: string) => {
  const map: Record<string, string> = {
    pdf: 'PDF',
    ppt: 'PPT',
    video: '视频',
    other: '其他',
  };

  return map[type || ''] || '全部类型';
};

const fileTypeBadgeClass = (type: string) => {
  const map: Record<string, string> = {
    pdf: 'bg-red-100 text-red-700',
    ppt: 'bg-amber-100 text-amber-700',
    video: 'bg-blue-100 text-blue-700',
    other: 'bg-slate-100 text-slate-700',
  };

  return map[type] || 'bg-slate-100 text-slate-700';
};

const resolveFileUrl = (fileUrl: string) => {
  if (fileUrl.startsWith('http://') || fileUrl.startsWith('https://')) {
    return fileUrl;
  }
  return `${API_ORIGIN}${fileUrl}`;
};

const loadMaterials = async () => {
  loading.value = true;
  try {
    const [classroomDetail, response] = await Promise.all([
      request.get(`/classes/${classId.value}`) as Promise<ClassroomDetail>,
      listMaterials({
        class_id: classId.value,
        keyword: filters.keyword.trim() || undefined,
        file_type: filters.fileType || undefined,
      }),
    ]);
    classroom.value = classroomDetail;
    materials.value = response.items;
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
    ElMessage.warning('请输入资料标题');
    return;
  }
  if (!uploadForm.file) {
    ElMessage.warning('请选择要上传的文件');
    return;
  }

  uploading.value = true;
  try {
    await uploadMaterial({
      class_id: classId.value,
      title: uploadForm.title.trim(),
      description: uploadForm.description.trim(),
      file: uploadForm.file,
    });
    ElMessage.success('资料上传并入库成功');
    uploadForm.title = '';
    uploadForm.description = '';
    uploadForm.file = null;
    await loadMaterials();
  } finally {
    uploading.value = false;
  }
};

const handleDelete = async (materialId: number) => {
  try {
    await ElMessageBox.confirm('确认删除这份资料吗？删除后无法恢复。', '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    });
  } catch {
    return;
  }

  await deleteMaterial(materialId);
  ElMessage.success('资料已删除');
  await loadMaterials();
};

watch(() => [filters.keyword, filters.fileType], () => {
  loadMaterials();
});

onMounted(() => {
  loadMaterials();
});
</script>