<template>
  <view class="container">
    <!-- 头部 -->
    <view class="header">
      <text class="back" @click="goBack">&lt;</text>
      <text class="title">修改密码</text>
      <text class="placeholder"></text>
    </view>

    <!-- 表单区域 -->
    <view class="form-section">
      <view class="form-item">
        <text class="label">旧密码</text>
        <input
          class="input"
          type="password"
          v-model="form.oldPassword"
          placeholder="请输入旧密码"
          maxlength="50"
        />
      </view>

      <view class="form-item">
        <text class="label">新密码</text>
        <input
          class="input"
          type="password"
          v-model="form.newPassword"
          placeholder="请输入新密码（至少6位）"
          maxlength="50"
        />
      </view>

      <view class="form-item">
        <text class="label">确认密码</text>
        <input
          class="input"
          type="password"
          v-model="form.confirmPassword"
          placeholder="请再次输入新密码"
          maxlength="50"
        />
      </view>
    </view>

    <!-- 提示信息 -->
    <view class="tips">
      <text class="tip-item">• 密码长度至少 6 位</text>
      <text class="tip-item">• 建议使用字母、数字组合</text>
    </view>

    <!-- 提交按钮 -->
    <view class="action-section">
      <button class="submit-btn" :disabled="submitting" @click="submitChange">
        {{ submitting ? '提交中...' : '确认修改' }}
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { API_BASE_URL } from '@/config.js'

const submitting = ref(false)

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const goBack = () => {
  uni.navigateBack()
}

const validateForm = () => {
  if (!form.oldPassword) {
    uni.showToast({ title: '请输入旧密码', icon: 'none' })
    return false
  }
  if (!form.newPassword) {
    uni.showToast({ title: '请输入新密码', icon: 'none' })
    return false
  }
  if (form.newPassword.length < 6) {
    uni.showToast({ title: '新密码至少6位', icon: 'none' })
    return false
  }
  if (form.newPassword !== form.confirmPassword) {
    uni.showToast({ title: '两次密码输入不一致', icon: 'none' })
    return false
  }
  if (form.oldPassword === form.newPassword) {
    uni.showToast({ title: '新密码不能与旧密码相同', icon: 'none' })
    return false
  }
  return true
}

const submitChange = async () => {
  if (!validateForm()) return

  submitting.value = true
  try {
    const token = uni.getStorageSync('token')
    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/user/password`,
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        old_password: form.oldPassword,
        new_password: form.newPassword
      }
    })

    if (res.data?.code === 0) {
      uni.showToast({ title: '密码修改成功', icon: 'success' })
      setTimeout(() => {
        // 清除登录状态，要求重新登录
        uni.removeStorageSync('token')
        uni.removeStorageSync('user')
        uni.reLaunch({ url: '/pages/login/index' })
      }, 1500)
    } else {
      uni.showToast({ title: res.data?.message || '修改失败', icon: 'none' })
    }
  } catch (e) {
    uni.showToast({ title: '请求失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40rpx 30rpx 30rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
}

.back {
  font-size: 40rpx;
  color: #fff;
  padding: 10rpx 20rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #fff;
}

.placeholder {
  width: 60rpx;
}

.form-section {
  background: #fff;
  margin: 20rpx 0;
}

.form-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;

  &:last-child {
    border-bottom: none;
  }
}

.label {
  width: 160rpx;
  font-size: 30rpx;
  color: #333;
}

.input {
  flex: 1;
  font-size: 30rpx;
  text-align: right;
}

.tips {
  padding: 20rpx 30rpx;
}

.tip-item {
  display: block;
  font-size: 24rpx;
  color: #999;
  line-height: 1.8;
}

.action-section {
  padding: 60rpx 30rpx;
}

.submit-btn {
  width: 100%;
  padding: 28rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  color: #fff;
  font-size: 32rpx;
  font-weight: 500;
  border-radius: 50rpx;
  border: none;

  &[disabled] {
    opacity: 0.6;
  }
}
</style>
