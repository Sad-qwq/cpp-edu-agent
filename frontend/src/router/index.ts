
import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/stores/user';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
    },
    {
      path: '/public-announcements',
      name: 'public-announcements',
      component: () => import('@/views/announcements/PublicAnnouncementsView.vue'),
    },
    {
      path: '/',
      component: () => import('@/layouts/AppShell.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
          meta: {
            title: '仪表盘',
            description: '查看班级、作业与最近动态的全局概览。',
          },
        },
        {
          path: 'classes',
          name: 'classes',
          component: () => import('@/views/classes/ClassListView.vue'),
          meta: {
            title: '班级',
            description: '管理班级、加入班级，并查看与你相关的班级列表。',
          },
        },
        {
          path: 'notifications',
          name: 'notifications',
          component: () => import('@/views/notifications/NotificationsView.vue'),
          meta: {
            title: '通知中心',
            description: '统一查看平台提醒、班级动态和待处理通知。',
          },
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/settings/SettingsView.vue'),
          meta: {
            title: '个人设置',
            description: '更新个人资料、头像和密码，并查看当前账号状态。',
          },
        },
        {
          path: 'admin/users',
          name: 'admin-users',
          component: () => import('@/views/admin/UserManagementView.vue'),
          meta: {
            requiresAuth: true,
            adminOnly: true,
            title: '用户管理',
            description: '审核教师账号、筛选平台用户，并维护用户启停用状态。',
          },
        },
        {
          path: 'admin/announcements',
          name: 'admin-announcements',
          component: () => import('@/views/admin/AnnouncementManagementView.vue'),
          meta: {
            requiresAuth: true,
            adminOnly: true,
            title: '平台公告',
            description: '维护全局公告、置顶提醒与停用状态。',
          },
        },
        {
          path: 'admin/model-config',
          name: 'admin-model-config',
          component: () => import('@/views/admin/ModelConfigView.vue'),
          meta: {
            requiresAuth: true,
            adminOnly: true,
            title: '模型配置',
            description: '维护模型参数、调用额度，并查看模型使用日志。',
          },
        },
        {
          path: 'admin/knowledge-base',
          name: 'admin-knowledge-base',
          component: () => import('@/views/admin/PublicKnowledgeBaseView.vue'),
          meta: {
            requiresAuth: true,
            adminOnly: true,
            title: '公共知识库',
            description: '维护跨班级复用的课程规范、样题库与公共教学资料。',
          },
        },
        {
          path: 'sandbox',
          name: 'sandbox',
          component: () => import('@/views/sandbox/SandboxView.vue'),
          meta: {
            title: 'C++ 沙箱',
            description: '在线编译、运行并调试 C++ 代码片段。',
          },
        },
        {
          path: 'classes/:id',
          name: 'class-detail',
          component: () => import('@/views/classes/ClassDetailView.vue'),
          meta: {
            title: '班级详情',
            description: '查看班级概览、公告与成员信息。',
          },
        },
        {
          path: 'classes/:id/assignments',
          name: 'class-assignments',
          component: () => import('@/views/assignments/AssignmentListView.vue'),
          meta: {
            title: '班级作业',
            description: '查看当前班级的作业列表，并按身份进入创建或作答流程。',
          },
        },
        {
          path: 'classes/:id/ai-question-generation',
          name: 'ai-question-generation',
          component: () => import('@/views/assignments/AiQuestionGenerationView.vue'),
          meta: {
            title: 'AI 智能出题',
            description: '基于班级资料与模型生成题目草稿，并发布到现有作业。',
          },
        },
        {
          path: 'classes/:id/materials',
          name: 'class-materials',
          component: () => import('@/views/materials/ClassMaterialsView.vue'),
          meta: {
            title: '班级资料',
            description: '查看、检索并维护当前班级的课件、讲义和视频资料。',
          },
        },
        {
          path: 'classes/:id/members',
          name: 'class-members',
          component: () => import('@/views/classes/ClassMembersView.vue'),
          meta: {
            title: '班级成员',
            description: '查看并维护当前班级的学生成员列表。',
          },
        },
        {
          path: 'classes/:id/announcements',
          name: 'class-announcements',
          component: () => import('@/views/announcements/ClassAnnouncementsView.vue'),
          meta: {
            title: '班级公告',
            description: '查看、发布和维护当前班级的公告信息。',
          },
        },
        {
          path: 'classes/:id/discussions',
          name: 'class-discussions',
          component: () => import('@/views/discussion/DiscussionListView.vue'),
          meta: {
            title: '班级讨论',
            description: '围绕当前班级中的问题发起讨论、查看回复并持续答疑。',
          },
        },
        {
          path: 'classes/:id/discussions/:questionId',
          name: 'discussion-detail',
          component: () => import('@/views/discussion/DiscussionDetailView.vue'),
          meta: {
            title: '讨论详情',
            description: '查看问题上下文、教师回答、点赞互动与最佳答案采纳状态。',
          },
        },
        {
          path: 'assignments/:id',
          name: 'assignment-detail',
          component: () => import('@/views/assignments/AssignmentDetailView.vue'),
          meta: {
            title: '作业详情',
            description: '查看题目、提交答案并完成教师评分。',
          },
        },
      ],
    },
  ],
});

router.beforeEach(async (to) => {
  const userStore = useUserStore();
  await userStore.initializeAuth();

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    };
  }

  if (to.meta.adminOnly && !userStore.isAdmin) {
    return { path: '/' };
  }

  if ((to.name === 'login' || to.name === 'register') && userStore.isLoggedIn) {
    return { path: '/' };
  }

  return true;
});

export default router;
