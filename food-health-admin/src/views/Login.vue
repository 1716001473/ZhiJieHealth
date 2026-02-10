<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <img src="/vite.svg" alt="Logo" class="logo" />
        <h1>食品健康管理后台</h1>
        <p>Food Health Admin System</p>
      </div>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-btn"
            native-type="submit"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-tips">
        <p>演示账号：admin / admin123</p>
      </div>
    </div>
    
    <div class="login-footer">
      © 2024 Food Health System. All rights reserved.
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  
  // 简化版登录验证（演示用）
  setTimeout(() => {
    if (form.username === 'admin' && form.password === 'admin123') {
      localStorage.setItem('admin_token', 'demo_token_' + Date.now())
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } else {
      ElMessage.error('用户名或密码错误')
    }
    loading.value = false
  }, 500)
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header .logo {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
}

.login-header h1 {
  font-size: 24px;
  color: #333;
  margin: 0 0 8px 0;
}

.login-header p {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.login-form {
  margin-top: 24px;
}

.login-btn {
  width: 100%;
  margin-top: 8px;
}

.login-tips {
  text-align: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.login-tips p {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.login-footer {
  position: fixed;
  bottom: 20px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
}
</style>
