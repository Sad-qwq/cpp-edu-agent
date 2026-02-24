

<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <div class="logo">🚀</div>
        <h2>欢迎回来</h2>
        <p>C++ 教育智能体平台</p>
      </div>

      <el-form :model="form" class="login-form" size="large">
        <el-form-item>
          <el-input 
            v-model="form.username" 
            placeholder="请输入邮箱" 
            prefix-icon="Message" 
          />
        </el-form-item>
        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码" 
            show-password 
            prefix-icon="Lock" 
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            class="full-width login-btn" 
            @click="handleLogin" 
            :loading="loading" 
            round
          >
            登 录
          </el-button>
        </el-form-item>
        
        <div class="links">
          <span>还没有账号？</span>
          <router-link to="/register" class="register-link">立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';

const userStore = useUserStore();
const router = useRouter();
const loading = ref(false);

const form = reactive({
  username: '', // Still using 'username' as field name for compatibility with store, but placeholder says 'Email'
  password: '',
});

const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入完整信息');
    return;
  }
  loading.value = true;
  const success = await userStore.login(form);
  loading.value = false;
  
  if (success) {
    ElMessage.success('登录成功，欢迎回来！');
    router.push('/');
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

/* Optional: Add some background shapes */
.login-container::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 200%;
  background: radial-gradient(#ffffff 10%, transparent 10%);
  background-size: 20px 20px;
  opacity: 0.1;
  animation: bgMove 60s linear infinite;
}

@keyframes bgMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(-50px, -50px); }
}

.login-box {
  background: rgba(255, 255, 255, 0.95);
  padding: 40px 50px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 400px;
  backdrop-filter: blur(10px);
  z-index: 10;
  transition: transform 0.3s ease;
}

.login-box:hover {
  transform: translateY(-5px);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  font-size: 48px;
  margin-bottom: 10px;
}

.login-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
  font-weight: 600;
}

.login-header p {
  margin: 5px 0 0;
  color: #666;
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.login-btn {
  font-size: 16px;
  font-weight: bold;
  height: 45px;
  background: linear-gradient(to right, #667eea, #764ba2);
  border: none;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: linear-gradient(to right, #764ba2, #667eea);
  box-shadow: 0 4px 15px rgba(118, 75, 162, 0.4);
}

.links {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 15px;
}

.register-link {
  color: #764ba2;
  font-weight: 600;
  text-decoration: none;
  margin-left: 5px;
  transition: color 0.3s;
}

.register-link:hover {
  color: #667eea;
  text-decoration: underline;
}

.full-width {
  width: 100%;
}
</style>

