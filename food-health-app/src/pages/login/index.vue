<template>
  <view class="container">
    <!-- 顶部装饰 -->
    <view class="header">
      <text class="logo">🍎</text>
      <text class="title">智能食物识别</text>
    </view>

    <!-- 切换标签 -->
    <view class="tabs">
      <view 
        :class="['tab', isLogin ? 'active' : '']"
        @click="isLogin = true"
      >登录</view>
      <view 
        :class="['tab', !isLogin ? 'active' : '']"
        @click="isLogin = false"
      >注册</view>
    </view>

    <!-- 表单区域 -->
    <view class="form">
      <view class="input-group">
        <text class="input-icon">👤</text>
        <input 
          v-model="username" 
          type="text" 
          placeholder="请输入用户名" 
          class="input"
        />
      </view>
      
      <view class="input-group">
        <text class="input-icon">🔒</text>
        <input 
          v-model="password" 
          type="password" 
          placeholder="请输入密码" 
          class="input"
        />
      </view>
      
      <view class="input-group" v-if="!isLogin">
        <text class="input-icon">😊</text>
        <input 
          v-model="nickname" 
          type="text" 
          placeholder="请输入昵称（可选）" 
          class="input"
        />
      </view>

      <button 
        class="submit-btn" 
        :disabled="loading"
        @click="handleSubmit"
      >
        {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
      </button>
    </view>

    <!-- 跳过登录 -->
    <view class="skip" @click="skipLogin">
      <text>暂不登录，随便看看</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { API_BASE_URL } from '@/config.js'

const API_BASE = API_BASE_URL

const isLogin = ref(true)
const loading = ref(false)

const username = ref('')
const password = ref('')
const nickname = ref('')

// 处理提交
const handleSubmit = async () => {
  if (!username.value || !password.value) {
    uni.showToast({ title: '请填写完整信息', icon: 'none' })
    return
  }
  
  if (password.value.length < 6) {
    uni.showToast({ title: '密码至少6位', icon: 'none' })
    return
  }
  
  loading.value = true
  
  const url = isLogin.value 
    ? `${API_BASE}/api/v1/user/login`
    : `${API_BASE}/api/v1/user/register`
  
  const data = isLogin.value
    ? { username: username.value, password: password.value }
    : { username: username.value, password: password.value, nickname: nickname.value || username.value }
  
  uni.request({
    url,
    method: 'POST',
    header: { 'Content-Type': 'application/json' },
    data,
    success: (res: any) => {
      loading.value = false
      
      if (res.data.code === 0) {
        const responseData = res.data.data
        
        if (isLogin.value) {
          // 登录成功，保存 token 和用户信息
          uni.setStorageSync('token', responseData.token)
          uni.setStorageSync('user', responseData.user)
          uni.showToast({ title: '登录成功', icon: 'success' })
        } else {
          // 注册成功，切换到登录
          uni.showToast({ title: '注册成功，请登录', icon: 'success' })
          isLogin.value = true
          return
        }
        
        // 跳转到首页
        setTimeout(() => {
          uni.reLaunch({ url: '/pages/index/index' })
        }, 1000)
      } else {
        uni.showToast({ title: res.data.message || '操作失败', icon: 'none' })
      }
    },
    fail: (err) => {
      loading.value = false
      console.error('请求失败', err)
      uni.showToast({ title: '网络错误，请检查后端服务', icon: 'none' })
    }
  })
}

// 跳过登录
const skipLogin = () => {
  uni.reLaunch({ url: '/pages/index/index' })
}
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #E8F5E9 0%, #FFFFFF 100%);
  padding: 60rpx 40rpx;
}

.header {
  text-align: center;
  padding: 60rpx 0 80rpx;
}

.logo {
  font-size: 100rpx;
  display: block;
  margin-bottom: 20rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
}

.tabs {
  display: flex;
  background: #fff;
  border-radius: 16rpx;
  padding: 8rpx;
  margin-bottom: 50rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.tab {
  flex: 1;
  text-align: center;
  padding: 24rpx;
  font-size: 30rpx;
  color: #666;
  border-radius: 12rpx;
  transition: all 0.3s;
  
  &.active {
    background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
    color: #fff;
    font-weight: 500;
  }
}

.form {
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.08);
}

.input-group {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #F5F5F5;
  border-radius: 12rpx;
  margin-bottom: 24rpx;
}

.input-icon {
  font-size: 36rpx;
  margin-right: 20rpx;
}

.input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.submit-btn {
  width: 100%;
  margin-top: 20rpx;
  padding: 28rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 500;
  color: #fff;
  border: none;
  
  &:disabled {
    opacity: 0.6;
  }
}

.skip {
  text-align: center;
  margin-top: 50rpx;
  
  text {
    font-size: 26rpx;
    color: #999;
    text-decoration: underline;
  }
}
</style>
