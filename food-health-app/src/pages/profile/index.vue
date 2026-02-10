<template>
  <view class="container">
    <view class="header">
      <view class="avatar-section" @click="user ? goEditProfile() : goLogin()">
        <!-- 头像显示 -->
        <image
          v-if="user?.avatar_url"
          class="avatar-img"
          :src="getAvatarUrl(user.avatar_url)"
          mode="aspectFill"
        />
        <text v-else class="avatar">{{ user?.nickname?.[0] || '👤' }}</text>

        <view class="user-info" v-if="user">
          <text class="nickname">{{ user.nickname || user.username }}</text>
          <text class="username">@{{ user.username }}</text>
        </view>
        <view class="user-info" v-else>
          <text class="nickname">未登录</text>
          <text class="login-tip">点击登录</text>
        </view>

        <!-- 编辑入口箭头 -->
        <text class="edit-arrow" v-if="user">›</text>
      </view>
    </view>

    <view class="content">
      <view class="summary-cards" v-if="user">
        <view class="summary-card" @click="goHealthProfile">
          <view class="card-header">
            <text class="card-title">健康档案</text>
            <text class="card-tag">{{ profileProgress }}%</text>
          </view>
          <text class="card-sub">{{ healthFocus }}</text>
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: profileProgress + '%' }"></view>
          </view>
        </view>

        <view class="summary-card" @click="goRecord">
          <view class="card-header">
            <text class="card-title">饮食管理</text>
            <text class="card-tag" v-if="todayReport">{{ todayReport.total.calories }} kcal</text>
            <text class="card-tag" v-else>--</text>
          </view>
          <text class="card-sub" v-if="todayReport">
            目标 {{ todayReport.recommended.calories }} kcal · {{ todayReport.total.calories }} 已摄入
          </text>
          <text class="card-sub" v-else>今日暂无记录</text>
          <view class="mini-bars" v-if="todayReport">
            <view class="mini-bar" :style="{ width: getMiniPercent(todayReport.total.carb, todayReport.recommended.carb) + '%' }"></view>
            <view class="mini-bar orange" :style="{ width: getMiniPercent(todayReport.total.protein, todayReport.recommended.protein) + '%' }"></view>
            <view class="mini-bar red" :style="{ width: getMiniPercent(todayReport.total.fat, todayReport.recommended.fat) + '%' }"></view>
          </view>
        </view>
      </view>

      <!-- 功能菜单 -->
      <view class="menu-section">
        <view class="menu-item" @click="goFavorites" v-if="user">
          <text class="menu-icon">❤️</text>
          <text class="menu-text">我的收藏</text>
          <text class="menu-arrow">›</text>
        </view>

        <view class="menu-item" @click="goHistory" v-if="user">
          <text class="menu-icon">📋</text>
          <text class="menu-text">识别历史</text>
          <text class="menu-arrow">›</text>
        </view>
        
        <view class="menu-item" @click="goHealthProfile" v-if="user">
          <text class="menu-icon">💚</text>
          <text class="menu-text">健康档案</text>
          <text class="menu-arrow">›</text>
        </view>

        <view class="menu-item" @click="goSettings" v-if="user">
          <text class="menu-icon">⚙️</text>
          <text class="menu-text">个人设置</text>
          <text class="menu-arrow">›</text>
        </view>
        
        <view class="menu-item" @click="goAbout">
          <text class="menu-icon">ℹ️</text>
          <text class="menu-text">关于我们</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 登录/退出按钮 -->
      <view class="action-section">
        <button v-if="!user" class="action-btn login" @click="goLogin">
          登录 / 注册
        </button>
        <button v-else class="action-btn logout" @click="handleLogout">
          退出登录
        </button>
      </view>
    </view>

    <!-- 底部导航 -->
    <view class="bottom-nav">
      <view class="nav-item" @click="goHome">
        <text class="nav-icon">📷</text>
        <text class="nav-text">识别</text>
      </view>
      <view class="nav-item" @click="goRecord">
        <text class="nav-icon">🍽️</text>
        <text class="nav-text">饮食</text>
      </view>
      <view class="nav-item" @click="goHistory">
        <text class="nav-icon">📋</text>
        <text class="nav-text">历史</text>
      </view>
      <view class="nav-item active">
        <text class="nav-icon">👤</text>
        <text class="nav-text">我的</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { API_BASE_URL } from '@/config.js'
import { request } from '@/utils/http'
import reportUtils from '@/utils/report'
import healthProfile from '@/utils/healthProfile'

const user = ref<any>(null)
const todayReport = ref<any>(null)
const profileProgress = ref(0)
const healthFocus = ref('完善健康档案，获取个性化建议')

onShow(() => {
  // 从本地存储获取用户信息
  const storedUser = uni.getStorageSync('user')
  if (storedUser) {
    user.value = storedUser
  } else {
    user.value = null
  }
  const storedProfile = uni.getStorageSync('healthProfile') || {}
  profileProgress.value = healthProfile.calcProfileCompletion(storedProfile)
  healthFocus.value = healthProfile.getHealthFocusMessage(storedProfile)
  loadTodayReport()
})

const loadTodayReport = async () => {
  const token = uni.getStorageSync('token')
  if (!token) {
    todayReport.value = null
    return
  }

  try {
    const date = new Date().toISOString().split('T')[0]
    const res = await request({
      url: `${API_BASE_URL}/api/v1/meal/daily-report?date=${date}`,
      method: 'GET',
      silentAuth: true
    })
    if (res.statusCode === 200 && (res.data as any)?.code === 0) {
      todayReport.value = reportUtils.normalizeReport((res.data as any).data)
    }
  } catch (e) {
    todayReport.value = null
  }
}

const getAvatarUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return API_BASE_URL + url
}

const goLogin = () => {
  uni.navigateTo({ url: '/pages/login/index' })
}

const goEditProfile = () => {
  uni.navigateTo({ url: '/pages/profile/edit' })
}

const goHistory = () => {
  if (!user.value) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    return
  }
  uni.navigateTo({ url: '/pages/history/index' })
}

const goFavorites = () => {
  if (!user.value) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    return
  }
  uni.navigateTo({ url: '/pages/favorite/index' })
}

const goHealthProfile = () => {
  uni.navigateTo({ url: '/pages/health/index' })
}

const goSettings = () => {
  uni.navigateTo({ url: '/pages/profile/settings' })
}

const goAbout = () => {
  uni.showModal({
    title: '智能食物识别助手',
    content: '版本 1.0.0\n\n通过 AI 识别食物，获取营养信息和健康建议。',
    showCancel: false
  })
}

const goHome = () => {
  uni.reLaunch({ url: '/pages/index/index' })
}

const goRecord = () => {
  uni.reLaunch({ url: '/pages/record/index' })
}

const getMiniPercent = (val: number, max: number) => {
  return reportUtils.safePercent(val, max)
}

const handleLogout = () => {
  uni.showModal({
    title: '确认退出',
    content: '确定要退出登录吗？',
    success: (res) => {
      if (res.confirm) {
        uni.removeStorageSync('token')
        uni.removeStorageSync('user')
        user.value = null
        uni.showToast({ title: '已退出登录', icon: 'success' })
      }
    }
  })
}
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #F5F5F5;
  padding-bottom: 140rpx;
}

.header {
  padding: 60rpx 40rpx 40rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
}

.avatar-section {
  display: flex;
  align-items: center;
}

.avatar-img {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  margin-right: 30rpx;
  background: rgba(255, 255, 255, 0.3);
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 50rpx;
  color: #fff;
  margin-right: 30rpx;
  text-align: center;
  line-height: 120rpx;
}

.edit-arrow {
  font-size: 40rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-left: 10rpx;
}

.user-info {
  flex: 1;
}

.nickname {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 8rpx;
}

.username {
  display: block;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}

.login-tip {
  display: block;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: underline;
}

.content {
  padding: 30rpx;
}

.summary-cards {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.summary-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 6rpx 20rpx rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.card-tag {
  font-size: 22rpx;
  color: #4CAF50;
  background: #E8F5E9;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}

.card-sub {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 16rpx;
}

.progress-bar {
  height: 10rpx;
  background: #F1F1F1;
  border-radius: 10rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #81C784);
}

.mini-bars {
  display: flex;
  gap: 10rpx;
}

.mini-bar {
  height: 10rpx;
  background: #4CAF50;
  border-radius: 10rpx;
  flex: 1;
}

.mini-bar.orange {
  background: #FF9800;
}

.mini-bar.red {
  background: #F44336;
}

.menu-section {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 30rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 32rpx 30rpx;
  border-bottom: 1rpx solid #F0F0F0;
  
  &:last-child {
    border-bottom: none;
  }
  
  &:active {
    background: #F9F9F9;
  }
}

.menu-icon {
  font-size: 40rpx;
  margin-right: 24rpx;
}

.menu-text {
  flex: 1;
  font-size: 30rpx;
  color: #333;
}

.menu-arrow {
  font-size: 36rpx;
  color: #CCC;
}

.action-section {
  margin-top: 60rpx;
}

.action-btn {
  width: 100%;
  padding: 28rpx;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 500;
  border: none;
  
  &.login {
    background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
    color: #fff;
  }
  
  &.logout {
    background: #fff;
    color: #F44336;
    border: 2rpx solid #F44336;
  }
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: #fff;
  padding: 20rpx 0;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  
  &.active {
    .nav-icon, .nav-text {
      color: #4CAF50;
    }
  }
}

.nav-icon {
  font-size: 44rpx;
  margin-bottom: 6rpx;
}

.nav-text {
  font-size: 22rpx;
  color: #999;
}
</style>
