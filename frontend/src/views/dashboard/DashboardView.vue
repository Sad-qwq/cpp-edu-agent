

<template>
  <el-container class="dashboard-layout">
    <!-- Sidebar -->
    <el-aside width="240px" class="aside">
      <div class="logo-area">
        <el-icon :size="30" color="#409EFF"><element-plus /></el-icon>
        <span class="logo-text">EduPilot</span>
      </div>
      <el-menu
        default-active="1"
        class="el-menu-vertical"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="1">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="2">
          <el-icon><Reading /></el-icon>
          <span>我的课程</span>
        </el-menu-item>
        <el-menu-item index="3">
          <el-icon><Monitor /></el-icon>
          <span>C++ 实训沙箱</span>
        </el-menu-item>
        <el-menu-item index="4" v-if="userStore.isAdmin">
          <el-icon><UserFilled /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="5">
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- Header -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>仪表盘</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown trigger="click">
            <span class="el-dropdown-link">
              <el-avatar :size="32" :src="defaultAvatar" style="margin-right: 8px"></el-avatar>
              {{ userStore.user.full_name }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Main Content -->
      <el-main class="main">
        <div class="welcome-banner">
          <h2>👋 欢迎回来, {{ userStore.user.full_name }}!</h2>
          <p>今天是学习 C++ 的好日子。准备好接受挑战了吗？</p>
        </div>

        <el-row :gutter="20" class="stat-cards">
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header">
                  <span>已修课程</span>
                  <el-tag type="success">进行中</el-tag>
                </div>
              </template>
              <div class="stat-value">3</div>
              <div class="stat-desc">算法基础, 面向对象编程...</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header">
                  <span>完成实验</span>
                  <el-tag>累计</el-tag>
                </div>
              </template>
              <div class="stat-value">12</div>
              <div class="stat-desc">超过 85% 的同学</div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card shadow="hover" class="stat-card">
              <template #header>
                <div class="card-header">
                  <span>代码提交</span>
                  <el-tag type="warning">本周</el-tag>
                </div>
              </template>
              <div class="stat-value">45</div>
              <div class="stat-desc">上次提交: 2小时前</div>
            </el-card>
          </el-col>
        </el-row>

        <el-card class="recent-list" shadow="never">
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
              <el-button type="primary" link>查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentActivities" stripe style="width: 100%">
            <el-table-column prop="date" label="时间" width="180" />
            <el-table-column prop="action" label="操作" width="180" />
            <el-table-column prop="detail" label="详情" />
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'Success' ? 'success' : 'warning'">{{ scope.row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router'; // 引入 useRouter import

const userStore = useUserStore();
const router = useRouter(); // 获取 router 实例
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';

const recentActivities = [
  { date: '2023-10-24 10:00', action: '登录系统', detail: 'IP: 192.168.1.1', status: 'Success' },
  { date: '2023-10-23 15:30', action: '提交代码', detail: 'Lab 3: Pointers', status: 'Success' },
  { date: '2023-10-22 09:15', action: '查看课程', detail: 'C++ Advanced Topics', status: 'Active' },
];

const handleLogout = () => {
  userStore.logout();
  router.push('/login'); // 确保登出后跳转
}
</script>

<style scoped>
.dashboard-layout {
  height: 100vh;
}

.aside {
  background-color: #304156;
  color: white;
  display: flex;
  flex-direction: column;
}

.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4d;
  color: white;
  gap: 10px;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  letter-spacing: 1px;
}

.el-menu-vertical {
  border-right: none;
  flex: 1;
}

.header {
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #333;
}

.main {
  background-color: #f0f2f5;
  padding: 20px;
}

.welcome-banner {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.05);
}

.welcome-banner h2 {
  margin: 0 0 10px 0;
  color: #303133;
}
.welcome-banner p {
  margin: 0;
  color: #909399;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin: 10px 0;
}

.stat-desc {
  font-size: 12px;
  color: #909399;
}

.recent-list {
  border-radius: 8px;
}
</style>

