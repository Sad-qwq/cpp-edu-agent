<template>
  <div class="space-y-6">
    <section class="rounded-[28px] bg-gradient-to-r from-sky-900 via-cyan-800 to-teal-700 p-6 text-white shadow-sm sm:p-7">
      <div class="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-3">
          <div class="inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-cyan-100">
            个人设置
          </div>
          <h2 class="text-3xl font-semibold tracking-tight">维护你的账号资料与安全信息</h2>
          <p class="max-w-2xl text-sm leading-6 text-cyan-50/80">在这里更新昵称、个人简介、头像和密码。设置变更会即时同步到当前登录会话。</p>
        </div>

        <div class="grid w-full max-w-xl gap-3 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-cyan-50/70">账号身份</p>
            <p class="mt-2 text-xl font-semibold">{{ roleLabel }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-cyan-50/70">审批状态</p>
            <p class="mt-2 text-xl font-semibold">{{ approvalLabel }}</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
            <p class="text-xs text-cyan-50/70">账号状态</p>
            <p class="mt-2 text-xl font-semibold">{{ activeLabel }}</p>
          </div>
        </div>
      </div>
    </section>

    <div class="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
        <div class="flex items-start justify-between gap-4 border-b border-slate-100 pb-5">
          <div>
            <h3 class="text-xl font-semibold text-slate-900">头像与账户概览</h3>
            <p class="mt-1 text-sm text-slate-500">查看当前账号信息，并上传新的头像图片。</p>
          </div>
          <button
            type="button"
            class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-600 transition-all duration-300 hover:-translate-y-1 hover:bg-slate-100"
            :disabled="loadingProfile"
            @click="loadProfile"
          >
            {{ loadingProfile ? '刷新中...' : '刷新资料' }}
          </button>
        </div>

        <div class="mt-6 flex flex-col items-start gap-5 sm:flex-row sm:items-center">
          <img :src="avatarSrc" alt="avatar" class="h-24 w-24 rounded-[28px] border border-slate-200 object-cover shadow-sm" />
          <div class="space-y-3">
            <div>
              <p class="text-lg font-semibold text-slate-900">{{ userStore.user.username || '未设置用户名' }}</p>
              <p class="mt-1 text-sm text-slate-500">{{ userStore.user.email || '暂无邮箱' }}</p>
            </div>
            <label class="inline-flex cursor-pointer items-center justify-center rounded-2xl bg-cyan-600 px-4 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-cyan-700">
              {{ uploadingAvatar ? '上传中...' : '更换头像' }}
              <input class="hidden" type="file" accept="image/*" :disabled="uploadingAvatar" @change="handleAvatarUpload" />
            </label>
            <p class="text-xs leading-5 text-slate-400">支持常见图片格式。上传成功后侧栏头像会同步更新。</p>
          </div>
        </div>

        <dl class="mt-8 grid gap-4 sm:grid-cols-2">
          <div class="rounded-2xl bg-slate-50 p-4">
            <dt class="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">用户 ID</dt>
            <dd class="mt-2 text-sm font-semibold text-slate-900">{{ userStore.user.id || '-' }}</dd>
          </div>
          <div class="rounded-2xl bg-slate-50 p-4">
            <dt class="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">当前角色</dt>
            <dd class="mt-2 text-sm font-semibold text-slate-900">{{ roleLabel }}</dd>
          </div>
          <div class="rounded-2xl bg-slate-50 p-4">
            <dt class="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">激活状态</dt>
            <dd class="mt-2 text-sm font-semibold text-slate-900">{{ activeLabel }}</dd>
          </div>
          <div class="rounded-2xl bg-slate-50 p-4">
            <dt class="text-xs font-medium uppercase tracking-[0.2em] text-slate-400">审批状态</dt>
            <dd class="mt-2 text-sm font-semibold text-slate-900">{{ approvalLabel }}</dd>
          </div>
        </dl>
      </section>

      <div class="space-y-6">
        <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
          <div class="border-b border-slate-100 pb-5">
            <h3 class="text-xl font-semibold text-slate-900">个人资料</h3>
            <p class="mt-1 text-sm text-slate-500">用户名会展示在班级、讨论和作业提交记录中。</p>
          </div>

          <form class="mt-6 space-y-5" @submit.prevent="handleProfileSave">
            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">用户名</span>
              <input
                v-model.trim="profileForm.username"
                type="text"
                maxlength="50"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white"
                placeholder="请输入用户名"
              />
            </label>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">个人简介</span>
              <textarea
                v-model.trim="profileForm.bio"
                rows="5"
                maxlength="300"
                class="w-full rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white"
                placeholder="写一段简短介绍，方便班级成员认识你"
              ></textarea>
            </label>

            <div class="flex items-center justify-between gap-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-500">
              <span>邮箱地址</span>
              <span class="font-medium text-slate-700">{{ userStore.user.email || '-' }}</span>
            </div>

            <div class="flex justify-end">
              <button
                type="submit"
                class="rounded-2xl bg-cyan-600 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-cyan-700 disabled:cursor-not-allowed disabled:bg-cyan-400"
                :disabled="savingProfile"
              >
                {{ savingProfile ? '保存中...' : '保存资料' }}
              </button>
            </div>
          </form>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
          <div class="border-b border-slate-100 pb-5">
            <h3 class="text-xl font-semibold text-slate-900">密码安全</h3>
            <p class="mt-1 text-sm text-slate-500">修改密码后，当前登录状态会继续保留，但建议你重新确认其他设备的会话安全。</p>
          </div>

          <form class="mt-6 space-y-5" @submit.prevent="handlePasswordSave">
            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">当前密码</span>
              <input
                v-model="passwordForm.oldPassword"
                type="password"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white"
                placeholder="请输入当前密码"
              />
            </label>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">新密码</span>
              <input
                v-model="passwordForm.newPassword"
                type="password"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white"
                placeholder="请输入新密码"
              />
            </label>

            <label class="block space-y-2">
              <span class="text-sm font-medium text-slate-700">确认新密码</span>
              <input
                v-model="passwordForm.confirmPassword"
                type="password"
                class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-cyan-500 focus:bg-white"
                placeholder="请再次输入新密码"
              />
            </label>

            <div class="rounded-2xl border border-cyan-100 bg-cyan-50 px-4 py-3 text-sm leading-6 text-cyan-900">
              建议使用长度不少于 8 位的密码，并混合字母、数字与符号。
            </div>

            <div class="flex justify-end">
              <button
                type="submit"
                class="rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition-all duration-300 hover:-translate-y-1 hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
                :disabled="savingPassword"
              >
                {{ savingPassword ? '提交中...' : '更新密码' }}
              </button>
            </div>
          </form>
        </section>

        <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm sm:p-7">
          <div class="flex items-start justify-between gap-4 border-b border-slate-100 pb-5">
            <div>
              <h3 class="text-xl font-semibold text-slate-900">界面主题</h3>
              <p class="mt-1 text-sm text-slate-500">切换白天或黑夜主题，当前选择会保存在本机浏览器中。</p>
            </div>
            <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{{ themeLabel }}</span>
          </div>

          <div class="mt-6 grid gap-4 md:grid-cols-2">
            <button
              type="button"
              class="rounded-[24px] border p-5 text-left transition-all duration-300"
              :class="theme === 'light' ? 'border-cyan-300 bg-cyan-50 shadow-sm' : 'border-slate-200 bg-white hover:-translate-y-1 hover:shadow-md'"
              @click="setTheme('light')"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-base font-semibold text-slate-900">白天模式</p>
                  <p class="mt-2 text-sm leading-6 text-slate-500">浅色界面更清爽，适合白天办公和高频操作。</p>
                </div>
                <span class="rounded-full px-3 py-1 text-xs font-medium" :class="theme === 'light' ? 'bg-cyan-100 text-cyan-700' : 'bg-slate-100 text-slate-500'">
                  {{ theme === 'light' ? '当前使用' : '点击切换' }}
                </span>
              </div>
            </button>

            <button
              type="button"
              class="rounded-[24px] border p-5 text-left transition-all duration-300"
              :class="theme === 'dark' ? 'border-slate-700 bg-slate-900 text-white shadow-sm' : 'border-slate-200 bg-white hover:-translate-y-1 hover:shadow-md'"
              @click="setTheme('dark')"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="text-base font-semibold" :class="theme === 'dark' ? 'text-white' : 'text-slate-900'">黑夜模式</p>
                  <p class="mt-2 text-sm leading-6" :class="theme === 'dark' ? 'text-slate-300' : 'text-slate-500'">暗色界面更沉浸，适合晚间学习和长时间阅读。</p>
                </div>
                <span class="rounded-full px-3 py-1 text-xs font-medium" :class="theme === 'dark' ? 'bg-white/10 text-white' : 'bg-slate-100 text-slate-500'">
                  {{ theme === 'dark' ? '当前使用' : '点击切换' }}
                </span>
              </div>
            </button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { API_ORIGIN } from '@/api/request';
import { useUserStore } from '@/stores/user';
import { applyTheme, getStoredTheme, type AppTheme } from '@/utils/theme';
import { changeMyPassword, getMyProfile, updateMyProfile, uploadMyAvatar } from '@/services/users';

const userStore = useUserStore();

const loadingProfile = ref(false);
const savingProfile = ref(false);
const savingPassword = ref(false);
const uploadingAvatar = ref(false);
const theme = ref<AppTheme>(getStoredTheme());

const profileForm = reactive({
  username: '',
  bio: '',
});

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
});

const resolveAssetUrl = (url?: string | null) => {
  if (!url) {
    return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';
  }

  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  return `${API_ORIGIN}${url}`;
};

const avatarSrc = computed(() => resolveAssetUrl(userStore.user.avatar_url));
const roleLabel = computed(() => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生',
  };

  return roleMap[userStore.user.role || ''] || '平台用户';
});
const activeLabel = computed(() => userStore.user.is_active ? '已启用' : '已停用');
const approvalLabel = computed(() => {
  if (userStore.user.role !== 'teacher') {
    return '无需审批';
  }

  return userStore.user.is_approved ? '已通过' : '待审核';
});
const themeLabel = computed(() => theme.value === 'dark' ? '黑夜模式' : '白天模式');

const syncProfileForm = () => {
  profileForm.username = userStore.user.username || '';
  profileForm.bio = userStore.user.bio || '';
};

const loadProfile = async () => {
  loadingProfile.value = true;
  try {
    const profile = await getMyProfile();
    userStore.setUserProfile(profile);
    syncProfileForm();
  } finally {
    loadingProfile.value = false;
  }
};

const handleProfileSave = async () => {
  if (!profileForm.username.trim()) {
    ElMessage.warning('用户名不能为空');
    return;
  }

  savingProfile.value = true;
  try {
    const updated = await updateMyProfile({
      username: profileForm.username.trim(),
      bio: profileForm.bio.trim(),
    });
    userStore.setUserProfile(updated);
    syncProfileForm();
    ElMessage.success('个人资料已更新');
  } finally {
    savingProfile.value = false;
  }
};

const handlePasswordSave = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    ElMessage.warning('请完整填写密码信息');
    return;
  }

  if (passwordForm.newPassword.length < 8) {
    ElMessage.warning('新密码长度不能少于 8 位');
    return;
  }

  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致');
    return;
  }

  savingPassword.value = true;
  try {
    const result = await changeMyPassword({
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword,
    });
    passwordForm.oldPassword = '';
    passwordForm.newPassword = '';
    passwordForm.confirmPassword = '';
    ElMessage.success(result.msg || '密码修改成功');
  } finally {
    savingPassword.value = false;
  }
};

const handleAvatarUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) {
    return;
  }

  uploadingAvatar.value = true;
  try {
    await uploadMyAvatar(file);
    await loadProfile();
    ElMessage.success('头像上传成功');
  } finally {
    uploadingAvatar.value = false;
    input.value = '';
  }
};

const setTheme = (nextTheme: AppTheme) => {
  if (theme.value === nextTheme) {
    return;
  }

  theme.value = nextTheme;
  applyTheme(nextTheme);
  ElMessage.success(`已切换为${nextTheme === 'dark' ? '黑夜' : '白天'}模式`);
};

onMounted(() => {
  syncProfileForm();
  loadProfile();
});
</script>