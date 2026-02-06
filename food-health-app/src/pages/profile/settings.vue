<template>
  <view class="container">
    <view class="section">
      <text class="section-title">我的健康目标</text>
      <view class="radio-group">
        <view 
          class="radio-item" 
          :class="{ active: form.health_goal === 'loss_weight' }"
          @click="form.health_goal = 'loss_weight'"
        >
          <text class="icon">🔥</text>
          <text class="label">减脂塑形</text>
        </view>
        <view 
          class="radio-item" 
          :class="{ active: form.health_goal === 'maintain' }"
          @click="form.health_goal = 'maintain'"
        >
          <text class="icon">⚖️</text>
          <text class="label">保持健康</text>
        </view>
        <view 
          class="radio-item" 
          :class="{ active: form.health_goal === 'gain_muscle' }"
          @click="form.health_goal = 'gain_muscle'"
        >
          <text class="icon">💪</text>
          <text class="label">增肌增重</text>
        </view>
      </view>
    </view>

    <view class="section">
      <text class="section-title">饮食偏好 (多选)</text>
      <view class="check-group">
        <view 
          class="check-item" 
          v-for="pref in preferences"
          :key="pref.key"
          :class="{ active: form.dietary_preferences.includes(pref.key) }"
          @click="togglePref(pref.key)"
        >
          <text>{{ pref.label }}</text>
        </view>
      </view>
    </view>

    <button class="save-btn" @click="handleSave" :loading="loading">保存设置</button>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { API_BASE_URL } from '@/config.js'
import { hasPlanProfileChanged } from '@/utils/planSignature.js'

const loading = ref(false)
const form = ref({
  health_goal: 'maintain',
  dietary_preferences: [] as string[]
})

const preferences = [
  { key: 'vegetarian', label: '🥬 素食主义' },
  { key: 'no_spicy', label: '🌶️ 不吃辣' },
  { key: 'low_sugar', label: '🍬 抗糖/低糖' },
  { key: 'high_protein', label: '🥚 高蛋白' },
  { key: 'lactose_free', label: '🥛 乳糖不耐受' }
]

onMounted(() => {
  const user = uni.getStorageSync('user')
  if (user) {
    form.value.health_goal = user.health_goal || 'maintain'
    if (user.dietary_preferences) {
      form.value.dietary_preferences = user.dietary_preferences.split(',').filter(Boolean)
    }
  }
})

const togglePref = (key: string) => {
  const index = form.value.dietary_preferences.indexOf(key)
  if (index > -1) {
    form.value.dietary_preferences.splice(index, 1)
  } else {
    form.value.dietary_preferences.push(key)
  }
}

const handleSave = async () => {
  loading.value = true
  try {
    const prevProfile = uni.getStorageSync('healthProfile') || {}
    const prevUser = uni.getStorageSync('user') || {}
    const nextUser = {
      ...prevUser,
      health_goal: form.value.health_goal,
      dietary_preferences: form.value.dietary_preferences.join(',')
    }
    const hasChanged = hasPlanProfileChanged(prevProfile, prevUser, prevProfile, nextUser)

    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/user/profile`,
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${uni.getStorageSync('token')}`
      },
      data: {
        health_goal: form.value.health_goal,
        dietary_preferences: form.value.dietary_preferences.join(',')
      }
    })

    if (res.data.code === 0) {
      uni.showToast({ title: '保存成功' })
      // Update local storage
      const user = uni.getStorageSync('user')
      if (user) {
        user.health_goal = form.value.health_goal
        user.dietary_preferences = form.value.dietary_preferences.join(',')
        uni.setStorageSync('user', user)
      }
      if (hasChanged) {
        uni.setStorageSync('planNeedsUpdate', true)
      }
      setTimeout(() => uni.navigateBack(), 1000)
    } else {
      uni.showToast({ title: res.data.message || '保存失败', icon: 'none' })
    }
  } catch (e) {
    uni.showToast({ title: '网络错误', icon: 'none' })
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss">
.container {
  padding: 30rpx;
  background: #F5F7FA;
  min-height: 100vh;
}

.section {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 30rpx;
  display: block;
  color: #333;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.radio-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border: 2rpx solid #EEE;
  border-radius: 16rpx;
  transition: all 0.2s;

  &.active {
    border-color: #4CAF50;
    background: #E8F5E9;
    .label { color: #4CAF50; font-weight: bold; }
  }
}

.icon {
  font-size: 40rpx;
  margin-right: 20rpx;
}

.label {
  font-size: 30rpx;
  color: #666;
}

.check-group {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.check-item {
  padding: 16rpx 30rpx;
  background: #F5F5F5;
  border-radius: 40rpx;
  font-size: 28rpx;
  color: #666;
  border: 2rpx solid transparent;

  &.active {
    background: #E8F5E9;
    color: #4CAF50;
    border-color: #4CAF50;
  }
}

.save-btn {
  background: #4CAF50;
  color: #fff;
  border-radius: 50rpx;
  margin-top: 60rpx;
  font-size: 32rpx;
  
  &:active {
    opacity: 0.9;
  }
}
</style>
