

<template>
  <div class="relative min-h-screen overflow-hidden bg-slate-50 text-slate-800">
    <div class="absolute inset-0">
      <div class="absolute left-0 top-0 h-80 w-80 rounded-full bg-blue-100 blur-3xl"></div>
      <div class="absolute right-8 top-24 h-72 w-72 rounded-full bg-sky-100 blur-3xl"></div>
      <div class="absolute bottom-0 left-1/2 h-80 w-80 -translate-x-1/2 rounded-full bg-slate-200 blur-3xl"></div>
    </div>

    <div class="relative mx-auto flex min-h-screen max-w-7xl items-center px-6 py-10 lg:px-10">
      <div class="grid w-full gap-8 lg:grid-cols-[0.9fr_1.1fr]">
        <section class="order-2 flex items-center justify-center lg:order-1">
          <div class="w-full max-w-xl rounded-[28px] border border-slate-200/70 bg-white p-8 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md sm:p-10">
            <div class="space-y-6">
              <div class="space-y-4 text-center lg:text-left">
                <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20 lg:mx-0">
                  <MagicStick />
                </div>
                <div>
                  <p class="text-sm font-medium uppercase tracking-[0.24em] text-blue-600">Create Account</p>
                  <h2 class="mt-3 text-3xl font-semibold tracking-tight text-slate-900">加入我们</h2>
                  <p class="mt-2 text-sm leading-6 text-slate-500">创建一个新账号，开始你的 C++ 智能学习与教学旅程。</p>
                </div>
              </div>

              <form class="space-y-5" @submit.prevent="handleRegister">
                <div class="space-y-2">
                  <label class="text-sm font-medium text-slate-700">用户名</label>
                  <div class="group relative">
                    <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400 transition-colors duration-300 group-focus-within:text-blue-600">
                      <User class="h-5 w-5" />
                    </span>
                    <input
                      v-model="form.username"
                      type="text"
                      placeholder="请输入登录用户名"
                      class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 pl-12 pr-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
                    />
                  </div>
                </div>

                <div class="space-y-2">
                  <label class="text-sm font-medium text-slate-700">邮箱</label>
                  <div class="group relative">
                    <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400 transition-colors duration-300 group-focus-within:text-blue-600">
                      <Message class="h-5 w-5" />
                    </span>
                    <input
                      v-model="form.email"
                      type="email"
                      placeholder="name@school.edu"
                      class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 pl-12 pr-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
                    />
                  </div>
                </div>

                <div class="space-y-2">
                  <label class="text-sm font-medium text-slate-700">显示名称</label>
                  <div class="group relative">
                    <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400 transition-colors duration-300 group-focus-within:text-blue-600">
                      <EditPen class="h-5 w-5" />
                    </span>
                    <input
                      v-model="form.display_name"
                      type="text"
                      placeholder="用于页面展示，可与用户名不同"
                      class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 pl-12 pr-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
                    />
                  </div>
                  <p class="text-xs leading-5 text-slate-400">当前后端用户表不保存 full_name，这个字段仅用于帮助你确认展示名称，不会提交到注册接口。</p>
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
                      placeholder="请设置密码"
                      class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 pl-12 pr-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
                    />
                  </div>
                  <p class="text-xs leading-5 text-slate-400">后端当前只要求 password 字段，但这里增加了基础强度提示，避免提交过弱密码。</p>
                </div>

                <div class="space-y-2">
                  <label class="text-sm font-medium text-slate-700">确认密码</label>
                  <div class="group relative">
                    <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400 transition-colors duration-300 group-focus-within:text-blue-600">
                      <Lock class="h-5 w-5" />
                    </span>
                    <input
                      v-model="form.confirmPassword"
                      type="password"
                      placeholder="请再次输入密码"
                      class="h-[52px] w-full rounded-2xl border border-slate-200 bg-slate-50 pl-12 pr-4 text-sm text-slate-800 outline-none transition-all duration-300 placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
                    />
                  </div>
                </div>

                <div class="space-y-3">
                  <span class="text-sm font-medium text-slate-700">我是</span>
                  <div class="grid grid-cols-2 gap-3">
                    <button
                      type="button"
                      class="rounded-2xl border px-4 py-3 text-sm font-medium transition-all duration-300"
                      :class="form.role === 'student'
                        ? 'border-blue-200 bg-blue-50 text-blue-700 shadow-sm'
                        : 'border-slate-200 bg-slate-50 text-slate-600 hover:-translate-y-1 hover:border-slate-300 hover:bg-white'"
                      @click="form.role = 'student'"
                    >
                      学生
                    </button>
                    <button
                      type="button"
                      class="rounded-2xl border px-4 py-3 text-sm font-medium transition-all duration-300"
                      :class="form.role === 'teacher'
                        ? 'border-blue-200 bg-blue-50 text-blue-700 shadow-sm'
                        : 'border-slate-200 bg-slate-50 text-slate-600 hover:-translate-y-1 hover:border-slate-300 hover:bg-white'"
                      @click="form.role = 'teacher'"
                    >
                      教师
                    </button>
                  </div>
                </div>

                <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
                  <span class="font-medium text-slate-700">注册说明：</span>
                  学生账号可直接登录；教师账号创建后默认处于待审核状态，需管理员审批。
                </div>

                <button
                  type="submit"
                  class="flex h-[52px] w-full items-center justify-center gap-2 rounded-2xl bg-blue-600 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:bg-blue-700 hover:shadow-md disabled:translate-y-0 disabled:cursor-not-allowed disabled:bg-blue-400"
                  :disabled="loading"
                >
                  <span v-if="loading" class="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
                  {{ loading ? '注册中...' : '立即注册' }}
                </button>
              </form>

              <div class="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500">
                <span>已有账号？</span>
                <div class="flex items-center gap-4">
                  <router-link to="/public-announcements" class="font-semibold text-slate-500 transition-colors duration-300 hover:text-slate-700">
                    查看公告
                  </router-link>
                  <router-link to="/login" class="font-semibold text-blue-600 transition-colors duration-300 hover:text-blue-700">
                    直接登录
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section class="order-1 rounded-[32px] border border-white/70 bg-white/70 p-8 shadow-sm backdrop-blur lg:order-2 lg:p-10">
          <div class="flex h-full flex-col justify-between gap-8">
            <div class="space-y-6">
              <div class="inline-flex items-center gap-2 rounded-full bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700">
                <span class="inline-flex h-2 w-2 rounded-full bg-blue-600"></span>
                教学协作平台
              </div>
              <div class="space-y-4">
                <h1 class="max-w-xl text-4xl font-semibold leading-tight tracking-tight text-slate-900 sm:text-5xl">
                  用一个更专业的工作台，连接课程、学生与实验反馈。
                </h1>
                <p class="max-w-lg text-base leading-7 text-slate-600">
                  从课程管理到作业批改，再到编程沙箱与互动讨论，所有教学动作都集中在一个现代化的界面内。
                </p>
              </div>
            </div>

            <div class="grid gap-4 sm:grid-cols-3">
              <div class="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition-all duration-300 hover:-translate-y-1 hover:bg-white hover:shadow-sm">
                <div class="text-sm text-slate-400">教师端</div>
                <div class="mt-3 text-2xl font-semibold text-slate-900">智能批改</div>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition-all duration-300 hover:-translate-y-1 hover:bg-white hover:shadow-sm">
                <div class="text-sm text-slate-400">学生端</div>
                <div class="mt-3 text-2xl font-semibold text-slate-900">沙箱实训</div>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition-all duration-300 hover:-translate-y-1 hover:bg-white hover:shadow-sm">
                <div class="text-sm text-slate-400">组织协作</div>
                <div class="mt-3 text-2xl font-semibold text-slate-900">消息闭环</div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { EditPen } from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import request from '@/api/request';
import { ElMessage } from 'element-plus';
import type { UserProfile } from '@/stores/user';

const router = useRouter();
const loading = ref(false);

const form = reactive({
  username: '',
  email: '',
  display_name: '',
  password: '',
  confirmPassword: '',
  role: 'student',
});

const handleRegister = async () => {
  if (!form.username || !form.email || !form.password) {
    ElMessage.warning('请填写所有必填信息');
    return;
  }

  if (!/^[a-zA-Z0-9_]{3,20}$/.test(form.username.trim())) {
    ElMessage.warning('用户名需为 3 到 20 位字母、数字或下划线');
    return;
  }

  if (form.password.length < 6) {
    ElMessage.warning('密码长度至少为 6 位');
    return;
  }

  if (form.password !== form.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致');
    return;
  }

  const normalizedEmail = form.email.trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
    ElMessage.warning('请输入有效的邮箱地址');
    return;
  }

  loading.value = true;
  try {
    const payload = {
      username: form.username.trim(),
      email: normalizedEmail,
      password: form.password,
      role: form.role,
    };

    const user = await request.post('/auth/register', payload) as UserProfile;

    if (user.role === 'teacher' && user.is_approved === false) {
      ElMessage.success('教师账号已创建，等待管理员审核后即可完整使用');
      router.push({ path: '/login', query: { registered: 'teacher-pending', username: payload.username } });
    } else {
      ElMessage.success('注册成功，请登录');
      router.push({ path: '/login', query: { registered: 'success', username: payload.username } });
    }
  } catch(e) {
    // Error is handled by interceptor, but we catch to stop loading
  } finally {
    loading.value = false;
  }
};
</script>

