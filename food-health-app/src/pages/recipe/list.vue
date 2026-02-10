<template>
  <view class="container">
    <!-- Header with Search -->
    <view class="header">
      <view class="search-bar">
        <text class="search-icon-left">🔍</text>
        <input
          class="search-input"
          type="text"
          placeholder="搜索食谱..."
          v-model="searchQuery"
          @confirm="loadRecipes"
        />
      </view>
    </view>

    <!-- Main Content: Left Tags + Right Recipes -->
    <view class="main-layout">
      <!-- Left Sidebar: Vertical Tags -->
      <scroll-view scroll-y class="sidebar">
        <view
          class="sidebar-item"
          :class="{ active: currentTag === '' }"
          @click="setFilter('')"
        >
          <text class="sidebar-text">全部</text>
        </view>
        <view
          class="sidebar-item"
          v-for="tag in tagList"
          :key="tag"
          :class="{ active: currentTag === tag }"
          @click="setFilter(tag)"
        >
          <text class="sidebar-text">{{ tag }}</text>
        </view>
      </scroll-view>

      <!-- Right Content: Recipe Grid -->
      <scroll-view
        scroll-y
        class="recipe-area"
        @scrolltolower="loadMore"
      >
        <view class="recipe-grid">
          <view
            class="recipe-card"
            v-for="recipe in recipeList"
            :key="recipe.id"
            @click="goDetail(recipe.id)"
          >
            <image
              class="recipe-img"
              :src="getImageUrl(recipe.image_url)"
              mode="aspectFill"
            />
            <view class="recipe-info">
              <text class="recipe-name">{{ recipe.name }}</text>
              <view class="recipe-meta">
                <text class="calories">{{ recipe.calories }} kcal</text>
                <text class="cook-time">{{ recipe.cook_time }}</text>
              </view>
            </view>
          </view>
        </view>

        <view v-if="recipeList.length === 0 && !loading" class="empty-tip">
          暂无相关食谱
        </view>

        <view v-if="loading" class="loading-tip">
          加载中...
        </view>

        <view v-if="!hasMore && recipeList.length > 0" class="no-more-tip">
          没有更多了
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { API_BASE_URL } from '@/config.js'
import defaultImg from '@/static/logo.png'

const searchQuery = ref('')
const currentTag = ref('')
const loading = ref(false)
const recipeList = ref<any[]>([])
const tagList = ref<string[]>([])
const page = ref(1)
const pageSize = 10
const hasMore = ref(true)

onMounted(() => {
  loadTags()
  loadRecipes()
})

// 获取所有标签
const loadTags = async () => {
  try {
    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/premium/recipes/tags`,
      method: 'GET'
    })
    const data = res.data as any
    if (data.code === 0) {
      tagList.value = data.data || []
    }
  } catch (e) {
    console.error('加载标签失败', e)
    tagList.value = ['早餐', '午餐', '晚餐', '汤羹', '凉菜', '烘焙', '轻食', '控糖', '增肌']
  }
}

const setFilter = (tag: string) => {
  currentTag.value = tag
  page.value = 1
  recipeList.value = []
  hasMore.value = true
  loadRecipes()
}

const loadRecipes = async () => {
  if (loading.value) return
  loading.value = true
  try {
    let url = `${API_BASE_URL}/api/v1/premium/recipes?page=${page.value}&page_size=${pageSize}`

    if (currentTag.value) {
      url += `&tag=${encodeURIComponent(currentTag.value)}`
    }
    if (searchQuery.value) {
      url += `&keyword=${encodeURIComponent(searchQuery.value)}`
    }

    const res = await uni.request({
      url: url,
      method: 'GET'
    })

    const data = res.data as any
    if (data.code === 0 && data.data) {
      const items = data.data.items || []
      if (page.value === 1) {
        recipeList.value = items
      } else {
        recipeList.value = [...recipeList.value, ...items]
      }
      hasMore.value = page.value < data.data.total_pages
    }
  } catch (e) {
    console.error('加载食谱失败', e)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  if (!hasMore.value || loading.value) return
  page.value++
  loadRecipes()
}

const getImageUrl = (url: string | null) => {
  if (!url) return defaultImg
  if (url.startsWith('http')) return url
  return `${API_BASE_URL}${url}`
}

const goDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/recipe/detail?id=${id}` })
}
</script>

<style lang="scss">
.container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #F5F5F5;
}

/* Header */
.header {
  background: #fff;
  padding: 16rpx 24rpx;
  border-bottom: 1rpx solid #EEEEEE;
  flex-shrink: 0;
}

.search-bar {
  background: #F5F5F5;
  border-radius: 36rpx;
  height: 72rpx;
  display: flex;
  align-items: center;
  padding: 0 24rpx;
}

.search-icon-left {
  font-size: 28rpx;
  margin-right: 16rpx;
  color: #999;
}

.search-input {
  flex: 1;
  height: 100%;
  font-size: 28rpx;
  color: #333;
}

/* Main Layout */
.main-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Left Sidebar */
.sidebar {
  width: 140rpx;
  flex-shrink: 0;
  background: #FAFAFA;
  height: 100%;
  border-right: 1rpx solid #EEEEEE;
}

.sidebar-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 28rpx 12rpx;
  position: relative;
  transition: all 0.2s;

  &.active {
    background: #fff;

    .sidebar-text {
      color: #4CAF50;
      font-weight: 600;
    }

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 20%;
      height: 60%;
      width: 6rpx;
      background: #4CAF50;
      border-radius: 0 6rpx 6rpx 0;
    }
  }
}

.sidebar-text {
  font-size: 26rpx;
  color: #666;
  text-align: center;
  line-height: 1.3;
}

/* Right Recipe Area */
.recipe-area {
  flex: 1;
  height: 100%;
  padding: 20rpx;
  box-sizing: border-box;
}

.recipe-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.recipe-card {
  width: 48.5%;
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.recipe-img {
  width: 100%;
  height: 220rpx;
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
}

.recipe-info {
  padding: 16rpx 18rpx;
}

.recipe-name {
  font-size: 26rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 10rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
}

.recipe-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.calories {
  font-size: 24rpx;
  color: #4CAF50;
  font-weight: 600;
}

.cook-time {
  font-size: 22rpx;
  color: #999;
}

/* Status Tips */
.empty-tip,
.loading-tip,
.no-more-tip {
  text-align: center;
  padding: 60rpx 0;
  color: #999;
  font-size: 26rpx;
}

.no-more-tip {
  padding: 40rpx 0;
}
</style>
