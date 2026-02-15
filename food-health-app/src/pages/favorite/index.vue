<template>
  <view class="container">
    <!-- 顶部标题栏 -->
    <view class="header">
      <view class="header-inner">
        <view class="back-btn" @click="goBack">
          <text class="back-icon">←</text>
        </view>
        <text class="header-title">我的收藏</text>
        <view class="header-right"></view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-if="!loading && list.length === 0">
      <text class="empty-icon">🤍</text>
      <text class="empty-title">还没有收藏喵～</text>
      <text class="empty-desc">去精选食谱看看，收藏喜欢的食谱吧</text>
      <button class="explore-btn" @click="goRecipeList">去逛逛</button>
    </view>

    <!-- 收藏列表 -->
    <view class="list-wrapper" v-else>
      <view
        class="recipe-card"
        v-for="item in list"
        :key="item.id"
        @click="goDetail(item.id)"
      >
        <image
          class="recipe-img"
          :src="getImageUrl(item.image_url)"
          mode="aspectFill"
        />
        <view class="recipe-info">
          <text class="recipe-name">{{ item.name }}</text>
          <text class="recipe-desc">{{ item.description || '' }}</text>
          <view class="recipe-meta">
            <text class="meta-tag" v-if="item.category">{{ item.category }}</text>
            <text class="meta-cal" v-if="item.calories">{{ item.calories }} kcal</text>
            <text class="meta-time" v-if="item.cook_time">⏱ {{ item.cook_time }}</text>
          </view>
        </view>
        <view class="unfav-btn" @click.stop="handleUnfavorite(item)">
          <text class="unfav-icon">❤️</text>
        </view>
      </view>

      <!-- 加载更多 -->
      <view class="load-more" v-if="hasMore" @click="loadMore">
        <text class="load-more-text">{{ loadingMore ? '加载中...' : '加载更多' }}</text>
      </view>

      <!-- 没有更多 -->
      <view class="no-more" v-if="!hasMore && list.length > 0">
        <text class="no-more-text">— 已经到底了 —</text>
      </view>
    </view>

    <!-- 加载中 -->
    <view class="loading-mask" v-if="loading">
      <view class="loading-spinner"></view>
      <text class="loading-text">加载中...</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { API_BASE_URL } from '@/config.js'
import { request } from '@/utils/http'
import defaultImg from '@/static/logo.png'

const list = ref<any[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const page = ref(1)
const pageSize = 10
const total = ref(0)
const hasMore = ref(false)

onMounted(() => {
  loadFavorites()
})



const loadFavorites = async () => {
  loading.value = true
  page.value = 1
  try {
    const res = await request({
      url: `${API_BASE_URL}/api/v1/favorites?page=${page.value}&page_size=${pageSize}`,
      method: 'GET',
    })
    const data = res.data as any
    if (data.code === 0 && data.data) {
      list.value = data.data.items || []
      total.value = data.data.total || 0
      hasMore.value = page.value < (data.data.total_pages || 0)
    }
  } catch (e) {
    console.error('加载收藏失败', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const loadMore = async () => {
  if (loadingMore.value || !hasMore.value) return
  loadingMore.value = true
  page.value++
  try {
    const res = await request({
      url: `${API_BASE_URL}/api/v1/favorites?page=${page.value}&page_size=${pageSize}`,
      method: 'GET',
    })
    const data = res.data as any
    if (data.code === 0 && data.data) {
      list.value.push(...(data.data.items || []))
      hasMore.value = page.value < (data.data.total_pages || 0)
    }
  } catch (e) {
    console.error('加载更多失败', e)
    page.value--
  } finally {
    loadingMore.value = false
  }
}

const handleUnfavorite = async (item: any) => {
  uni.showModal({
    title: '取消收藏',
    content: `确定取消收藏「${item.name}」吗？`,
    success: async (res) => {
      if (!res.confirm) return
      try {
        await request({
          url: `${API_BASE_URL}/api/v1/favorites/${item.id}`,
          method: 'POST',
        })
        // 从列表中移除
        list.value = list.value.filter((i) => i.id !== item.id)
        total.value--
        uni.showToast({ title: '已取消收藏', icon: 'success' })
      } catch (e) {
        console.error('取消收藏失败', e)
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
  })
}

const getImageUrl = (url: string | null) => {
  if (!url) return defaultImg
  if (url.startsWith('http')) return url
  return `${API_BASE_URL}${url}`
}

const goDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/recipe/detail?id=${id}` })
}

const goBack = () => {
  uni.navigateBack()
}

const goRecipeList = () => {
  uni.navigateTo({ url: '/pages/recipe/list' })
}
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
}

/* 顶部标题栏 */
.header {
  background: linear-gradient(135deg, #4caf50 0%, #81c784 100%);
  padding-top: var(--status-bar-height, 44px);
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 30rpx;
}

.back-btn {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-icon {
  font-size: 40rpx;
  color: #fff;
}

.header-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #fff;
}

.header-right {
  width: 60rpx;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 200rpx;
}

.empty-icon {
  font-size: 120rpx;
  margin-bottom: 30rpx;
}

.empty-title {
  font-size: 32rpx;
  color: #333;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: #999;
  margin-bottom: 40rpx;
}

.explore-btn {
  background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
  color: #fff;
  font-size: 28rpx;
  padding: 20rpx 60rpx;
  border-radius: 40rpx;
  border: none;
}

/* 收藏列表 */
.list-wrapper {
  padding: 20rpx 24rpx;
}

.recipe-card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 20rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);

  &:active {
    background: #fafafa;
  }
}

.recipe-img {
  width: 160rpx;
  height: 160rpx;
  border-radius: 16rpx;
  flex-shrink: 0;
  background: #e8f5e9;
}

.recipe-info {
  flex: 1;
  margin-left: 20rpx;
  overflow: hidden;
}

.recipe-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recipe-desc {
  font-size: 24rpx;
  color: #999;
  display: block;
  margin-bottom: 12rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recipe-meta {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex-wrap: wrap;
}

.meta-tag {
  font-size: 20rpx;
  color: #4caf50;
  background: #e8f5e9;
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}

.meta-cal {
  font-size: 22rpx;
  color: #ff9800;
  font-weight: 500;
}

.meta-time {
  font-size: 22rpx;
  color: #999;
}

.unfav-btn {
  width: 72rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.unfav-icon {
  font-size: 40rpx;
}

/* 加载更多 */
.load-more {
  text-align: center;
  padding: 30rpx;
}

.load-more-text {
  font-size: 26rpx;
  color: #4caf50;
}

.no-more {
  text-align: center;
  padding: 30rpx;
}

.no-more-text {
  font-size: 24rpx;
  color: #ccc;
}

/* 加载中 */
.loading-mask {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 300rpx;
}

.loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 6rpx solid #e8f5e9;
  border-top-color: #4caf50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 20rpx;
  font-size: 28rpx;
  color: #666;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
