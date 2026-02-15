<template>
  <view class="container">
    <PrivacyPopup />
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

    <!-- 微信登录按钮 (仅在微信小程序中显示) -->
    <!-- #ifdef MP-WEIXIN -->
    <view class="wechat-login-section">
      <view class="divider">
        <text class="divider-text">或者</text>
      </view>
      <button 
        class="wechat-btn" 
        :disabled="loading"
        @click="handleWechatLogin"
      >
        <text class="wechat-icon">💬</text>
        微信一键登录
      </button>
    </view>
    <!-- #endif -->

    <!-- 跳过登录 -->
    <view class="skip" @click="skipLogin">
      <text>暂不登录，随便看看</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { API_BASE_URL } from '@/config.js'
import { request } from '@/utils/http'
import { useUserStore } from '@/stores/user'
import PrivacyPopup from '@/components/PrivacyPopup.vue'

const API_BASE = API_BASE_URL
const userStore = useUserStore()

const isLogin = ref(true)
const loading = ref(false)

const username = ref('')
const password = ref('')
const nickname = ref('')

// 微信登录处理
const handleWechatLogin = async () => {
  loading.value = true
  
  try {
    // 1. 获取 code
    const loginRes = await uni.login({ provider: 'weixin' })
    if (!loginRes.code) {
      throw new Error('获取登录凭证失败')
    }
    
    // 2. 获取用户信息 (注：现在 getUserProfile 只能获取匿名信息，主要靠后端生成或用户后续完善)
    let userInfo = null

    // 3. 调用后端登录
    const res = await request({
      url: `${API_BASE}/api/v1/user/wechat-login`,
      method: 'POST',
      data: {
        code: loginRes.code,
        userInfo: userInfo
      }
    })
    
    const resData = res.data as any
    if (resData.code === 0) {
        const responseData = resData.data
        userStore.login(responseData.token, responseData.user)
        uni.showToast({ title: '登录成功', icon: 'success' })
        setTimeout(() => {
            uni.reLaunch({ url: '/pages/index/index' })
        }, 1000)
    } else {
        uni.showToast({ title: resData.message || '登录失败', icon: 'none' })
    }
  } catch (err) {
    console.error('微信登录失败', err)
    uni.showToast({ title: '微信登录失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

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
  
  try {
    const res = await request({
      url,
      method: 'POST',
      header: { 'Content-Type': 'application/json' },
      data,
    })

    loading.value = false
    const resData = res.data as any
    
    if (resData.code === 0) {
      const responseData = resData.data
      
      if (isLogin.value) {
        // 登录成功，保存 token 和用户信息
        userStore.login(responseData.token, responseData.user)
        uni.showToast({ title: '登录成功', icon: 'success' })
      } else {
        // 注册成功，切换到登录
        uni.showToast({ title: '注册成功，请登录', icon: 'success' })
        isLogin.value = true
        loading.value = false  // Ensure loading is reset
        return
      }
      
      // 跳转到首页
      setTimeout(() => {
        uni.reLaunch({ url: '/pages/index/index' })
      }, 1000)
    } else {
      uni.showToast({ title: resData.message || '操作失败', icon: 'none' })
    }
  } catch (err) {
    loading.value = false
    console.error('请求失败', err)
    uni.showToast({ title: '网络错误，请检查后端服务', icon: 'none' })
  }
}

// 跳过登录
const skipLogin = () => {
  uni.reLaunch({ url: '/pages/index/index' })
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background: #F5F7FA;
  padding: 0;
}

.header {
  text-align: center;
  padding: 100rpx 0 80rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
  border-bottom-left-radius: 50rpx;
  border-bottom-right-radius: 50rpx;
  margin-bottom: 40rpx;
}

.logo {
  font-size: 100rpx;
  display: block;
  margin-bottom: 20rpx;
}

.title {
  font-size: 40rpx;
  font-weight: bold;
  color: #fff;
}

.tabs {
  display: flex;
  background: #fff;
  border-radius: 16rpx;
  padding: 8rpx;
  margin: 0 40rpx 40rpx;
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
  margin: 0 40rpx;
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
  padding-bottom: 40rpx;
  
  text {
    font-size: 26rpx;
    color: #999;
    text-decoration: underline;
  }
}

.wechat-login-section {
  margin-top: 60rpx;
  padding: 0 40rpx;
}

.divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40rpx;
  
  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #e0e0e0;
  }
  
  .divider-text {
    padding: 0 20rpx;
    font-size: 24rpx;
    color: #999;
  }
}

.wechat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #07C160;
  color: #fff;
  font-size: 32rpx;
  padding: 24rpx;
  border-radius: 16rpx;
  border: none;
  
  &::after {
    border: none;
  }
  
  .wechat-icon {
    font-size: 40rpx;
    margin-right: 16rpx;
  }
  
  &:active {
    opacity: 0.9;
  }
}
</style>
