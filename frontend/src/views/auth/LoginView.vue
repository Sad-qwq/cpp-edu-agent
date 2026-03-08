

<template>
  <div class="relative min-h-screen overflow-hidden bg-slate-50 text-slate-800">
    <div class="absolute inset-0">
      <div class="absolute -left-16 top-16 h-64 w-64 rounded-full bg-blue-100 blur-3xl"></div>
      <div class="absolute right-0 top-0 h-80 w-80 rounded-full bg-cyan-100 blur-3xl"></div>
      <div class="absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-slate-200 blur-3xl"></div>
    </div>

    <div class="relative mx-auto flex min-h-screen max-w-7xl items-center px-6 py-10 lg:px-10">
      <div class="grid w-full gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <section class="hidden rounded-[32px] border border-white/70 bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 p-10 text-white shadow-2xl shadow-blue-950/10 lg:flex lg:min-h-[720px] lg:flex-col lg:justify-between">
          <div class="space-y-6">
            <div class="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-medium text-blue-100 backdrop-blur">
              <span class="inline-flex h-2 w-2 rounded-full bg-emerald-400"></span>
              智能教学工作台
            </div>
            <div class="space-y-4">
              <h1 class="max-w-xl text-5xl font-semibold leading-tight tracking-tight">
                为 C++ 教学团队打造的现代化学习中枢。
              </h1>
              <p class="max-w-lg text-base leading-7 text-slate-300">
                统一管理课程、实验、提交记录与教学反馈，让教师和学生在一个界面内高效协作。
              </p>
            </div>
          </div>

          <div class="grid gap-4 md:grid-cols-3">
            <div class="rounded-2xl border border-white/10 bg-white/10 p-5 backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:bg-white/15">
              <div class="text-3xl font-semibold">18</div>
              <div class="mt-2 text-sm text-slate-300">课程工作流已上线</div>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/10 p-5 backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:bg-white/15">
              <div class="text-3xl font-semibold">96%</div>
              <div class="mt-2 text-sm text-slate-300">实验提交准时率</div>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/10 p-5 backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:bg-white/15">
              <div class="text-3xl font-semibold">24h</div>
              <div class="mt-2 text-sm text-slate-300">批改反馈闭环</div>
            </div>
          </div>
        </section>

        <section class="flex items-center justify-center">
          <div class="w-full max-w-xl rounded-[28px] border border-slate-200/70 bg-white p-8 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md sm:p-10">
            <div class="space-y-6">
              <div class="space-y-4 text-center lg:text-left">
                <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 text-2xl text-white shadow-lg shadow-blue-600/20 lg:mx-0">
                  <Promotion />
                </div>
                <div>
                  <p class="text-sm font-medium uppercase tracking-[0.24em] text-blue-600">Welcome Back</p>
                  <h2 class="mt-3 text-3xl font-semibold tracking-tight text-slate-900">欢迎回来</h2>
                  <p class="mt-2 text-sm leading-6 text-slate-500">登录 C++ 教育智能体平台，继续你的教学或学习流程。</p>
                </div>
              </div>

              <div
                v-if="infoMessage"
                class="rounded-2xl border px-4 py-3 text-sm leading-6"
                :class="infoTone === 'success' ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-amber-200 bg-amber-50 text-amber-700'"
              >
                {{ infoMessage }}
              </div>

              <form class="space-y-5" @submit.prevent="handleLogin">
                <div class="space-y-2">
                  <label class="text-sm font-medium text-slate-700">邮箱或用户名</label>
                  <div class="group relative">
                    <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400 transition-colors duration-300 group-focus-within:text-blue-600">
                      <Message class="h-5 w-5" />
                    </span>
                    <input
                      v-model="form.username"
                      type="text"
                      placeholder="请输入邮箱或用户名"
                      class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 pl-12 pr-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
                    />
                  </div>
                </div>

                <div class="space-y-2">
                  <label class="text-sm font-medium text-slate-700">密码</label>
                  <div class="group relative">
                    <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400 transition-colors duration-300 group-focus-within:text-blue-600">
                      <Lock class="h-5 w-5" />
                    </span>
                    <input
                      v-model="form.password"
                      type="password"
                      placeholder="请输入密码"
                      class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 pl-12 pr-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
                      @keyup.enter="handleLogin"
                    />
                  </div>
                </div>

                <div class="flex items-center justify-between text-xs text-slate-400">
                  <span>教师账号登录后仍需通过管理员审核才能访问业务接口</span>
                  <span>OAuth2 登录</span>
                </div>

                <button
                  type="submit"
                  class="flex h-[52px] w-full items-center justify-center gap-2 rounded-2xl bg-blue-600 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:bg-blue-700 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-blue-400"
                  :disabled="loading"
                >
                  <span v-if="loading" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
                  {{ loading ? '登录中...' : '登 录' }}
                </button>
              </form>

              <div class="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
                <span>支持邮箱或用户名登录</span>
                <div class="flex items-center gap-4">
                  <router-link to="/public-announcements" class="font-semibold text-slate-500 transition-colors duration-300 hover:text-slate-700">
                    查看公告
                  </router-link>
                  <router-link to="/register" class="font-semibold text-blue-600 transition-colors duration-300 hover:text-blue-700">
                    立即注册
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();
const loading = ref(false);

const infoMessage = computed(() => {
  if (route.query.registered === 'teacher-pending') {
    return '教师账号已创建。当前账号处于待审核状态，管理员审批通过后即可正常进入系统。';
  }

  if (route.query.registered === 'success') {
    return '账号创建成功，现在可以直接登录。';
  }

  if (route.query.session === 'expired') {
    return '登录状态已失效，请重新验证身份。';
  }

  return '';
});

const infoTone = computed(() => route.query.registered === 'success' ? 'success' : 'warning');

const form = reactive({
  username: typeof route.query.username === 'string' ? route.query.username : '',
  password: '',
});

const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入完整信息');
    return;
  }
  loading.value = true;
  const result = await userStore.login(form);
  loading.value = false;
  
  if (result.success) {
    ElMessage.success('登录成功，欢迎回来！');
    const redirectTarget = typeof route.query.redirect === 'string' ? route.query.redirect : '/';
    router.push(redirectTarget);
    return;
  }

  if (result.reason === 'teacher_pending') {
    ElMessage.warning('教师账号尚未审核，暂时无法进入系统');
    return;
  }

  if (result.reason === 'inactive') {
    ElMessage.warning('当前账号已被停用，请联系管理员');
  }
};
</script>

