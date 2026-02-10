<template>
  <view class="container">
    <view class="header">
      <text class="title">识别历史</text>
      <text class="subtitle">记录你的每一餐</text>
    </view>

    <view class="content">
      <!-- 未登录提示 -->
      <view class="empty-state" v-if="!canViewHistory">
        <text class="empty-icon">🔒</text>
        <text class="empty-title">请先登录</text>
        <text class="empty-desc">登录后可查看识别历史</text>
        <button class="go-btn" @click="goLogin">去登录</button>
      </view>

      <!-- 加载中 -->
      <view class="loading-state" v-else-if="loading">
        <text class="loading-icon">⏳</text>
        <text class="loading-text">加载中...</text>
      </view>

      <!-- 暂无数据 -->
      <view class="empty-state" v-else-if="historyList.length === 0">
        <text class="empty-icon">📝</text>
        <text class="empty-title">暂无识别记录</text>
        <text class="empty-desc">去首页拍照识别食物吧</text>
        <button class="go-btn" @click="goToIndex">去识别</button>
      </view>

      <!-- 历史列表 -->
      <view class="history-list" v-else>
        <view 
          class="history-item" 
          v-for="item in historyList" 
          :key="item.id"
          @click="viewDetail(item)"
        >
          <!-- 缩略图 -->
          <view class="item-thumb">
            <image 
              v-if="getImageUrl(item)" 
              :src="getImageUrl(item)" 
              mode="aspectFill" 
              class="thumb-image"
            />
            <view v-else class="thumb-placeholder">
              <text class="thumb-icon">🍽️</text>
            </view>
          </view>
          
          <!-- 主信息 -->
          <view class="item-main">
            <text class="food-name">{{ item.recognized_food }}</text>
            <text class="food-meta">
              {{ item.selected_portion || '中份' }} · {{ item.selected_cooking || '少油炒' }}
            </text>
            <view class="item-bottom">
              <text class="calories" v-if="item.final_calories_min">
                🔥 {{ item.final_calories_min }}~{{ item.final_calories_max }} kcal
              </text>
              <text class="meal-type-inline" v-if="item.meal_type">{{ item.meal_type }}</text>
            </view>
          </view>
          
          <!-- 右侧信息 -->
          <view class="item-side">
            <text class="item-time">{{ formatTime(item.created_at) }}</text>
            <text class="delete-btn" @click.stop="deleteItem(item.id)">🗑️</text>
          </view>
        </view>
        
        <!-- 加载更多 -->
        <view class="load-more" v-if="hasMore" @click="loadMore">
          <text>加载更多</text>
        </view>
      </view>
    </view>

    <!-- 底部导航 -->
    <view class="bottom-nav">
      <view class="nav-item" @click="goToIndex">
        <text class="nav-icon">📷</text>
        <text class="nav-text">识别</text>
      </view>
      <view class="nav-item" @click="goRecord">
        <text class="nav-icon">🍽️</text>
        <text class="nav-text">饮食</text>
      </view>
      <view class="nav-item active">
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
import { ref, onMounted, onUnmounted } from 'vue'
import { API_BASE_URL, ALLOW_GUEST_HISTORY } from '@/config.js'
import { request } from '@/utils/http'

const API_BASE = API_BASE_URL

const isLoggedIn = ref(false)
const loading = ref(false)
const historyList = ref<any[]>([])
const page = ref(1)
const pageSize = 20
const total = ref(0)
const hasMore = ref(false)
const allowGuest = ALLOW_GUEST_HISTORY
const canViewHistory = ref(true)

const syncLoginState = () => {
  const token = uni.getStorageSync('token')
  isLoggedIn.value = Boolean(token)
  canViewHistory.value = isLoggedIn.value || allowGuest
}

onMounted(() => {
  syncLoginState()
  if (canViewHistory.value) {
    loadHistory()
  }
  uni.$on('auth-unauthorized', () => {
    syncLoginState()
    historyList.value = []
    total.value = 0
    hasMore.value = false
  })
})

onUnmounted(() => {
  uni.$off('auth-unauthorized')
})

const loadHistory = async () => {
  const token = uni.getStorageSync('token')
  if (!token && !allowGuest) return
  
  loading.value = true
  
  const res: any = await request({
    url: `${API_BASE}/api/v1/history?page=${page.value}&page_size=${pageSize}`,
    method: 'GET',
    header: token ? { 'Authorization': `Bearer ${token}` } : {}
  })
  loading.value = false
  if (res.statusCode === 401) {
    return
  }
  if (res.data.code === 0) {
    const data = res.data.data
    if (page.value === 1) {
      historyList.value = data.items
    } else {
      historyList.value = [...historyList.value, ...data.items]
    }
    total.value = data.total
    hasMore.value = historyList.value.length < total.value
  }
}

const loadMore = () => {
  page.value++
  loadHistory()
}

const deleteItem = (id: number) => {
  uni.showModal({
    title: '确认删除',
    content: '确定要删除这条记录吗？',
    success: (res) => {
      if (res.confirm) {
        const token = uni.getStorageSync('token')
        if (!token) {
          uni.showToast({ title: '请先登录', icon: 'none' })
          return
        }
        request({
          url: `${API_BASE}/api/v1/history/${id}`,
          method: 'DELETE',
          header: {
            'Authorization': `Bearer ${token}`
          }
        }).then((res: any) => {
          if (res.statusCode === 401) return
          if (res.data.code === 0) {
            historyList.value = historyList.value.filter(item => item.id !== id)
            uni.showToast({ title: '已删除', icon: 'success' })
          }
        })
      }
    }
  })
}

const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours().toString().padStart(2, '0')
  const minute = date.getMinutes().toString().padStart(2, '0')
  return `${month}/${day} ${hour}:${minute}`
}

const goToIndex = () => {
  uni.reLaunch({ url: '/pages/index/index' })
}

const goRecord = () => {
  uni.reLaunch({ url: '/pages/record/index' })
}

const goProfile = () => {
  uni.navigateTo({ url: '/pages/profile/index' })
}

const goLogin = () => {
  uni.navigateTo({ url: '/pages/login/index' })
}

// 查看历史详情（使用缓存数据，无需重新请求）
const viewDetail = (item: any) => {
  if (!item.result_data) {
    uni.showToast({ title: '无缓存数据', icon: 'none' })
    return
  }
  
  // 跳转到结果页，传递缓存的数据和图片URL
  const data = encodeURIComponent(item.result_data)
  // 获取图片链接并编码，注意处理 relative Url
  const imgUrl = getImageUrl(item)
  const image = encodeURIComponent(imgUrl)
  
  uni.navigateTo({
    url: `/pages/result/index?data=${data}&image=${image}&from=history`
  })
}

// 获取识别历史项的图片 URL
const getImageUrl = (item: any): string => {
  // 优先使用直接存储的 image_url
  if (item.image_url) {
    // 如果是相对路径，拼接 API 地址
    if (item.image_url.startsWith('/static/')) {
      return `${API_BASE}${item.image_url}`
    }
    return item.image_url
  }
  
  // 其次尝试从 result_data 中提取
  if (item.result_data) {
    try {
      const resultData = JSON.parse(item.result_data)
      if (resultData.image_url) {
        if (resultData.image_url.startsWith('/static/')) {
          return `${API_BASE}${resultData.image_url}`
        }
        return resultData.image_url
      }
    } catch (e) {
      // 解析失败忽略
    }
  }
  
  return ''
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

.title {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #fff;
}

.subtitle {
  display: block;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 8rpx;
}

.content {
  padding: 30rpx;
}

.empty-state, .loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 40rpx;
  background: #fff;
  border-radius: 24rpx;
  margin-top: 40rpx;
}

.empty-icon, .loading-icon {
  font-size: 100rpx;
  margin-bottom: 24rpx;
}

.empty-title {
  font-size: 32rpx;
  font-weight: 500;
  color: #333;
  margin-bottom: 12rpx;
}

.empty-desc, .loading-text {
  font-size: 26rpx;
  color: #999;
  margin-bottom: 40rpx;
}

.go-btn {
  padding: 20rpx 60rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  border-radius: 40rpx;
  font-size: 28rpx;
  color: #fff;
}

.history-list {
  margin-top: 20rpx;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.04);
}

// 缩略图
.item-thumb {
  width: 120rpx;
  height: 120rpx;
  border-radius: 12rpx;
  overflow: hidden;
  margin-right: 24rpx;
  flex-shrink: 0;
  
  .thumb-image {
    width: 100%;
    height: 100%;
  }
}

.thumb-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumb-icon {
  font-size: 48rpx;
}

.item-main {
  flex: 1;
  min-width: 0;
}

.item-bottom {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex-wrap: wrap;
}

.meal-type-inline {
  font-size: 22rpx;
  color: #4CAF50;
  background: #E8F5E9;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.food-name {
  display: block;
  font-size: 32rpx;
  font-weight: 500;
  color: #333;
  margin-bottom: 8rpx;
}

.food-meta {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-bottom: 8rpx;
}

.calories {
  display: inline-block;
  font-size: 24rpx;
  color: #FF9800;
  background: #FFF3E0;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.item-side {
  text-align: right;
  margin-right: 20rpx;
}

.meal-type {
  display: block;
  font-size: 24rpx;
  color: #4CAF50;
  background: #E8F5E9;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  margin-bottom: 8rpx;
}

.item-time {
  display: block;
  font-size: 22rpx;
  color: #999;
}

.item-actions {
  .delete-btn {
    font-size: 36rpx;
    opacity: 0.6;
  }
}

.load-more {
  text-align: center;
  padding: 30rpx;
  color: #4CAF50;
  font-size: 26rpx;
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
