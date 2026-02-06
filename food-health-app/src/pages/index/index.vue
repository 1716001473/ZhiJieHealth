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

      <!-- 快速测试（开发用） -->
      <view class="test-section">
        <button class="test-btn" @click="testRecognize">
          🧪 快速测试（模拟数据）
        </button>
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
import { ref } from 'vue'
import { API_BASE_URL } from '@/config.js'
import { buildChooseImageOptions } from '@/utils/imageSelect.js'

// API 地址配置
const API_BASE = API_BASE_URL

const loading = ref(false)

// 拍照
const takePhoto = () => {
  const options = buildChooseImageOptions('camera')
  uni.chooseImage({
    ...options,
    success: (res) => {
      uploadAndRecognize(res.tempFilePaths[0])
    },
    fail: (err) => {
      console.log('拍照取消', err)
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
    fail: (err) => {
      console.log('选择取消', err)
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

// 快速测试（使用模拟数据）
const testRecognize = () => {
  loading.value = true
  
  uni.request({
    url: `${API_BASE}/api/v1/recognize/test`,
    method: 'GET',
    success: (res: any) => {
      loading.value = false
      if (res.data.code === 0 && res.data.data) {
        uni.navigateTo({
          url: `/pages/result/index?data=${encodeURIComponent(JSON.stringify(res.data.data))}`
        })
      } else {
        uni.showToast({
          title: '测试失败',
          icon: 'none'
        })
      }
    },
    fail: (err) => {
      loading.value = false
      console.error('请求失败', err)
      uni.showToast({
        title: '请确保后端服务已启动\nhttp://127.0.0.1:8000',
        icon: 'none',
        duration: 3000
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

.test-section {
  margin-top: 40rpx;
}

.test-btn {
  width: 100%;
  padding: 28rpx;
  background: #fff;
  border: 2rpx dashed #4CAF50;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #4CAF50;
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
