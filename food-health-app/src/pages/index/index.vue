<template>
  <view class="container">
    <!-- 顶部渐变背景 -->
    <view class="header">
      <view class="header-content">
        <text class="title">🍎 智能食物识别</text>
        <text class="subtitle">拍照即可获取营养信息</text>
      </view>
    </view>

    <!-- 主要功能区 -->
    <view class="main-area">
      <!-- 拍照按钮 -->
      <view class="camera-section">
        <view class="camera-btn" @click="takePhoto">
          <text class="camera-icon">📷</text>
          <text class="camera-text">拍照识别</text>
        </view>
        <view class="album-btn" @click="chooseFromAlbum">
          <text class="album-icon">🖼️</text>
          <text class="album-text">从相册选择</text>
        </view>
      </view>

      <!-- 功能介绍 -->
      <view class="features">
        <view class="feature-item">
          <text class="feature-icon">🔍</text>
          <text class="feature-title">智能识别</text>
          <text class="feature-desc">AI识别菜品名称</text>
        </view>
        <view class="feature-item" @click="goRecord">
          <text class="feature-icon">📊</text>
          <text class="feature-title">营养分析</text>
          <text class="feature-desc">查看热量和营养</text>
        </view>
        <view class="feature-item">
          <text class="feature-icon">⚠️</text>
          <text class="feature-title">健康提醒</text>
          <text class="feature-desc">禁忌人群提示</text>
        </view>
      </view>

      <!-- 今日饮食摘要 -->
      <view class="diet-card" @click="goRecord">
        <view class="diet-header">
          <text class="diet-title">🍽️ 今日饮食</text>
          <text class="diet-link">详情 ></text>
        </view>
        <template v-if="dietReport.total.calories > 0">
          <view class="calorie-row">
            <text class="calorie-label">已摄入</text>
            <text class="calorie-value">{{ dietReport.total.calories.toFixed(0) }}</text>
            <text class="calorie-unit">/ {{ dietReport.recommended.calories.toFixed(0) }} kcal</text>
          </view>
          <view class="calorie-bar">
            <view class="calorie-fill" :style="{ width: caloriePercent + '%', background: caloriePercent > 100 ? '#F44336' : '#4CAF50' }"></view>
          </view>
          <view class="macro-row">
            <view class="macro-item">
              <text class="macro-label">碳水</text>
              <view class="macro-bar"><view class="macro-fill" :style="{ width: carbPercent + '%', background: '#4CAF50' }"></view></view>
              <text class="macro-val">{{ dietReport.total.carb.toFixed(0) }}g</text>
            </view>
            <view class="macro-item">
              <text class="macro-label">蛋白质</text>
              <view class="macro-bar"><view class="macro-fill" :style="{ width: proteinPercent + '%', background: '#FF9800' }"></view></view>
              <text class="macro-val">{{ dietReport.total.protein.toFixed(0) }}g</text>
            </view>
            <view class="macro-item">
              <text class="macro-label">脂肪</text>
              <view class="macro-bar"><view class="macro-fill" :style="{ width: fatPercent + '%', background: '#F44336' }"></view></view>
              <text class="macro-val">{{ dietReport.total.fat.toFixed(0) }}g</text>
            </view>
          </view>
        </template>
        <view v-else class="diet-empty">
          <text class="diet-empty-icon">🥗</text>
          <text class="diet-empty-text">今天还没有饮食记录，去记录一下吧～</text>
        </view>
      </view>

    </view>

    <!-- 加载提示 -->
    <view v-if="loading" class="loading-mask">
      <view class="loading-content">
        <text class="loading-icon">🔄</text>
        <text class="loading-text">正在识别中...</text>
      </view>
    </view>

    <!-- 底部导航 -->
    <view class="bottom-nav">
      <view class="nav-item active">
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
      <view class="nav-item" @click="goProfile">
        <text class="nav-icon">👤</text>
        <text class="nav-text">我的</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { API_BASE_URL } from '@/config.js'
import { buildChooseImageOptions } from '@/utils/imageSelect.js'
import { request } from '@/utils/http'
import reportUtils from '@/utils/report.js'

// API 地址配置
const API_BASE = API_BASE_URL

const loading = ref(false)

// 今日饮食数据
const dietReport = ref(reportUtils.normalizeReport(null))

const caloriePercent = computed(() => reportUtils.safePercent(dietReport.value.total.calories, dietReport.value.recommended.calories))
const carbPercent = computed(() => reportUtils.safePercent(dietReport.value.total.carb, dietReport.value.recommended.carb))
const proteinPercent = computed(() => reportUtils.safePercent(dietReport.value.total.protein, dietReport.value.recommended.protein))
const fatPercent = computed(() => reportUtils.safePercent(dietReport.value.total.fat, dietReport.value.recommended.fat))

// 获取今日饮食摘要
const fetchDailyReport = async () => {
  // Check for token first to avoid 401 on guest visit
  const token = uni.getStorageSync('token')
  if (!token) {
    dietReport.value = reportUtils.normalizeReport(null)
    return
  }

  try {
    const today = new Date().toISOString().slice(0, 10)
    const res = await request({
      url: `${API_BASE}/api/v1/meal/daily-report?date=${today}`,
      method: 'GET',
      silentAuth: true
    })
    if (res.statusCode === 200 && (res.data as any)?.code === 0) {
      dietReport.value = reportUtils.normalizeReport((res.data as any).data)
    }
  } catch (e) {
    // 静默处理
  }
}

// 拍照
const takePhoto = () => {
  const options = buildChooseImageOptions('camera')
  uni.chooseImage({
    ...options,
    success: (res) => {
      uploadAndRecognize(res.tempFilePaths[0])
    },
    fail: () => {
    }
  })
}

// 从相册选择
const chooseFromAlbum = () => {
  const options = buildChooseImageOptions('album')
  uni.chooseImage({
    ...options,
    success: (res) => {
      uploadAndRecognize(res.tempFilePaths[0])
    },
    fail: () => {
    }
  })
}

// 上传图片并识别
const uploadAndRecognize = (filePath: string) => {
  loading.value = true
  
  uni.uploadFile({
    url: `${API_BASE}/api/v1/recognize`,
    filePath: filePath,
    name: 'image',
    success: (res) => {
      loading.value = false
      try {
        const data = JSON.parse(res.data)
        if (data.code === 0 && data.data) {
          // 跳转到结果页
          uni.navigateTo({
            url: `/pages/result/index?data=${encodeURIComponent(JSON.stringify(data.data))}&image=${encodeURIComponent(filePath)}`
          })
        } else {
          uni.showToast({
            title: data.message || '识别失败',
            icon: 'none'
          })
        }
      } catch (e) {
        uni.showToast({
          title: '解析结果失败',
          icon: 'none'
        })
      }
    },
    fail: (err) => {
      loading.value = false
      console.error('上传失败', err)
      uni.showToast({
        title: '网络错误，请检查后端服务',
        icon: 'none'
      })
    }
  })
}

// 导航方法
const goHistory = () => {
  uni.navigateTo({ url: '/pages/history/index' })
}

const goRecord = () => {
  uni.navigateTo({ url: '/pages/record/index' })
}

const goProfile = () => {
  uni.navigateTo({ url: '/pages/profile/index' })
}

onShow(() => {
  fetchDailyReport()
})
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: linear-gradient(180deg, #E8F5E9 0%, #F5F5F5 30%);
}

.header {
  padding: 120rpx 40rpx 60rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
  border-radius: 0 0 60rpx 60rpx;
}

.header-content {
  text-align: center;
}

.title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 16rpx;
}

.subtitle {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
}

.main-area {
  padding: 40rpx;
  padding-bottom: 160rpx;
  margin-top: -30rpx;
}

.camera-section {
  display: flex;
  gap: 30rpx;
  margin-bottom: 50rpx;
}

.camera-btn, .album-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 50rpx 20rpx;
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
  
  &:active {
    transform: scale(0.98);
  }
}

.camera-btn {
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
}

.camera-icon, .album-icon {
  font-size: 64rpx;
  margin-bottom: 16rpx;
}

.camera-text {
  font-size: 30rpx;
  font-weight: 500;
  color: #fff;
}

.album-text {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
}

.features {
  display: flex;
  gap: 20rpx;
  margin-bottom: 50rpx;
}

.feature-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30rpx 16rpx;
  background: #fff;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.feature-icon {
  font-size: 48rpx;
  margin-bottom: 12rpx;
}

.feature-title {
  font-size: 26rpx;
  font-weight: 500;
  color: #333;
  margin-bottom: 8rpx;
}

.feature-desc {
  font-size: 22rpx;
  color: #999;
}

/* 今日饮食摘要卡片 */
.diet-card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  box-shadow: 0 6rpx 24rpx rgba(0, 0, 0, 0.06);
}

.diet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.diet-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.diet-link {
  font-size: 24rpx;
  color: #4CAF50;
}

.calorie-row {
  display: flex;
  align-items: baseline;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.calorie-label {
  font-size: 24rpx;
  color: #999;
}

.calorie-value {
  font-size: 48rpx;
  font-weight: 700;
  color: #333;
}

.calorie-unit {
  font-size: 22rpx;
  color: #999;
}

.calorie-bar {
  height: 16rpx;
  background: #F0F0F0;
  border-radius: 8rpx;
  overflow: hidden;
  margin-bottom: 28rpx;
}

.calorie-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width 0.5s ease;
}

.macro-row {
  display: flex;
  gap: 20rpx;
}

.macro-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.macro-label {
  font-size: 22rpx;
  color: #999;
}

.macro-bar {
  height: 8rpx;
  background: #F0F0F0;
  border-radius: 4rpx;
  overflow: hidden;
}

.macro-fill {
  height: 100%;
  border-radius: 4rpx;
  transition: width 0.5s ease;
}

.macro-val {
  font-size: 22rpx;
  color: #666;
  font-weight: 500;
}

.diet-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 0 20rpx;
  gap: 16rpx;
}

.diet-empty-icon {
  font-size: 64rpx;
}

.diet-empty-text {
  font-size: 24rpx;
  color: #999;
}

.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 80rpx;
  background: #fff;
  border-radius: 24rpx;
}

.loading-icon {
  font-size: 80rpx;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 24rpx;
  font-size: 28rpx;
  color: #666;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
