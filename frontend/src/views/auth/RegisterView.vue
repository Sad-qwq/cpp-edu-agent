

<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <div class="logo">✨</div>
        <h2>加入我们</h2>
        <p>开启您的 C++ 智能学习之旅</p>
      </div>

      <el-form :model="form" class="register-form" size="large">
        <el-form-item>
          <el-input 
            v-model="form.email" 
            placeholder="请输入邮箱" 
            prefix-icon="Message" 
          />
        </el-form-item>
        
        <el-form-item>
          <el-input 
            v-model="form.full_name" 
            placeholder="请输入真实姓名" 
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item>
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请设置密码" 
            show-password
            prefix-icon="Lock"
          />
        </el-form-item>

        <div class="role-selection">
          <span class="role-label">我是：</span>
          <el-radio-group v-model="form.role" class="custom-radio">
            <el-radio-button label="student">学生</el-radio-button>
            <el-radio-button label="teacher">教师</el-radio-button>
          </el-radio-group>
        </div>

        <el-form-item>
          <el-button 
            type="primary" 
            class="full-width register-btn" 
            @click="handleRegister" 
            :loading="loading"
            round
          >
            立即注册
          </el-button>
        </el-form-item>

        <div class="links">
          <span>已有账号？</span>
          <router-link to="/login" class="login-link">直接登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/api/request';
import { ElMessage } from 'element-plus';

const router = useRouter();
const loading = ref(false);

const form = reactive({
  email: '',
  full_name: '',
  password: '',
  role: 'student',
});

const handleRegister = async () => {
  if (!form.email || !form.full_name || !form.password) {
    ElMessage.warning('请填写所有必填信息');
    return;
  }
  loading.value = true;
  try {
    await request.post('/auth/register', form);
    ElMessage.success('注册成功，请登录');
    router.push('/login');
  } catch(e) {
    // Error is handled by interceptor, but we catch to stop loading
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
  position: relative;
  overflow: hidden;
}

.register-container::before {
  content: '';
  position: absolute;
  width: 200%;
  height: 200%;
  background: radial-gradient(#ffffff 10%, transparent 10%);
  background-size: 30px 30px;
  opacity: 0.15;
  animation: bgMove 60s linear infinite reverse;
}

@keyframes bgMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(50px, 50px); }
}

.register-box {
  background: rgba(255, 255, 255, 0.9);
  padding: 40px 50px;
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
  width: 420px;
  backdrop-filter: blur(10px);
  z-index: 10;
  transition: transform 0.3s ease;
}

.register-box:hover {
  transform: translateY(-5px);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  font-size: 48px;
  margin-bottom: 10px;
}

.register-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
  font-weight: 600;
}

.register-header p {
  margin: 5px 0 0;
  color: #666;
  font-size: 14px;
}

.register-form {
  margin-top: 20px;
}

.role-selection {
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.role-label {
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

.register-btn {
  font-size: 16px;
  font-weight: bold;
  height: 45px;
  background: linear-gradient(to right, #a18cd1, #fbc2eb);
  border: none;
  transition: all 0.3s ease;
  color: white;
}

.register-btn:hover {
  background: linear-gradient(to right, #fbc2eb, #a18cd1);
  box-shadow: 0 4px 15px rgba(161, 140, 209, 0.4);
}

.links {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 15px;
}

.login-link {
  color: #a18cd1;
  font-weight: 600;
  text-decoration: none;
  margin-left: 5px;
  transition: color 0.3s;
}

.login-link:hover {
  color: #fbc2eb;
  text-decoration: underline;
}

.full-width {
  width: 100%;
}
</style>

