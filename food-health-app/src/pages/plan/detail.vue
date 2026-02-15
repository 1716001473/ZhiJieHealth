<template>
  <view class="container" v-if="plan">
    <!-- Header Image -->
    <view class="banner">
      <image :src="planCover" mode="aspectFill" class="banner-img" />
      <view class="banner-overlay"></view>
      <view class="banner-content">
        <text class="plan-title">{{ plan.name }}</text>
        <view class="plan-meta">
          <text class="meta-tag">{{ plan.duration_days }}天计划</text>
          <text class="meta-tag">{{ plan.difficulty === 'easy' ? '难度: 简单' : '难度: 中等' }}</text>
        </view>
      </view>
      <view class="back-btn" :style="{ top: statusBarHeight + 'px' }" @click="goBack">
        <text class="back-icon">←</text>
      </view>
    </view>

    <!-- Description -->
    <view class="section description-section">
      <text class="section-title">简介</text>
      <text class="desc-text">{{ plan.description }}</text>
      <view class="tags">
        <text class="tag" v-for="tag in (plan.tags ? plan.tags.split(',') : [])" :key="tag">{{ tag }}</text>
      </view>
    </view>

    <!-- Daily Plan -->
    <view class="section schedule-section">
      <view class="section-header">
        <text class="section-title">每日食谱</text>
      </view>
      
      <!-- Day Selector -->
      <scroll-view scroll-x class="day-scroll" :scroll-into-view="'day-' + currentDay">
        <view class="day-list">
          <view 
            class="day-item" 
            v-for="day in plan.days" 
            :key="day.day_index"
            :id="'day-' + day.day_index"
            :class="{ active: currentDay === day.day_index }"
            @click="currentDay = day.day_index"
          >
            <text class="day-num">Day {{ day.day_index }}</text>
            <text class="day-status" v-if="day.day_index === 1">开始</text>
          </view>
        </view>
      </scroll-view>

      <!-- Meal List -->
      <view class="meal-list" v-if="currentDayData">
        <view class="mobile-summary">
          <text class="summary-text">{{ currentDayData.title || `第 ${currentDayData.day_index} 天` }}</text>
          <text class="summary-cals" v-if="currentDayData.total_calories > 0">约 {{ currentDayData.total_calories }} 千卡</text>
        </view>

        <view class="meal-card" v-for="(meal, index) in currentDayData.meals" :key="index">
          <view class="meal-header">
            <text class="meal-type">{{ getMealTypeName(meal.meal_type) }}</text>
            <text class="meal-cals">{{ meal.calories }} 千卡</text>
          </view>
          <view class="meal-content">
            <text class="food-name">{{ meal.food_name }}</text>
            <text class="food-amount">{{ meal.amount_desc }}</text>
          </view>
          
          <!-- Alternatives -->
          <view class="alternatives" v-if="meal.alternatives && meal.alternatives.length > 0">
            <view class="alt-header" @click="toggleAlt(index)">
              <text class="alt-label">🔄 可替换为：</text>
              <text class="alt-arrow">{{ meal.showAlt ? '▲' : '▼' }}</text>
            </view>
            <view class="alt-list" v-if="meal.showAlt">
              <view class="alt-item" v-for="(alt, ai) in parseAlternatives(meal.alternatives)" :key="ai">
                 <text>• {{ alt.name }} {{ alt.weight }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <!-- Action Bar -->
    <view class="bottom-bar">
      <button class="action-btn secondary" @click="saveCollection">收藏</button>
      <button class="action-btn primary" @click="applyPlan">应用此食谱</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { API_BASE_URL } from '@/config.js'
import { request } from '@/utils/http'

const plan = ref<any>(null)
const currentDay = ref(1)
const loading = ref(true)
const statusBarHeight = ref(20)

const planCover = computed(() => {
  if (!plan.value || !plan.value.cover_image) {
    return 'https://images.unsplash.com/photo-1543353071-873f17a7a088?q=80&w=800&auto=format&fit=crop'
  }
  // 修复后端返回的本地不存在的静态资源路径
  if (plan.value.cover_image.includes('/static/ai_plan.png') || 
      plan.value.cover_image.includes('/static/mock_plan.png')) {
    return 'https://images.unsplash.com/photo-1543353071-873f17a7a088?q=80&w=800&auto=format&fit=crop'
  }
  return plan.value.cover_image
})

onLoad((options) => {
  const sysInfo = uni.getSystemInfoSync()
  statusBarHeight.value = sysInfo.statusBarHeight || 20
  if (options.id) {
    loadPlanDetail(options.id)
  }
})

const currentDayData = computed(() => {
  if (!plan.value || !plan.value.days) return null
  return plan.value.days.find(d => d.day_index === currentDay.value)
})

const loadPlanDetail = async (id: string) => {
  try {
    const res: any = await request({
      url: `${API_BASE_URL}/api/v1/plans/${id}`,
      method: 'GET'
    })
    if (res.data.code === 0) {
      const data = res.data.data
      // Ensure daily structure
      data.days.forEach((d: any) => {
        d.meals.forEach((m: any) => m.showAlt = false)
      })
      plan.value = data
      // Sort days if needed
      plan.value.days.sort((a: any, b: any) => a.day_index - b.day_index)
    }
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const getMealTypeName = (type: string) => {
  const map: Record<string, string> = {
    'breakfast': '早餐',
    'lunch': '午餐',
    'dinner': '晚餐',
    'snack': '加餐'
  }
  return map[type] || type
}

const parseAlternatives = (altJson: any) => {
  if (typeof altJson === 'string') {
    try {
      return JSON.parse(altJson)
    } catch (e) {
      return []
    }
  }
  return altJson || []
}

const toggleAlt = (mealIndex: number) => {
  if (currentDayData.value && currentDayData.value.meals[mealIndex]) {
    currentDayData.value.meals[mealIndex].showAlt = !currentDayData.value.meals[mealIndex].showAlt
  }
}

const goBack = () => {
  uni.navigateBack()
}

const saveCollection = () => {
  uni.showToast({ title: '已收藏', icon: 'success' })
}

const applyPlan = () => {
  uni.showModal({
    title: '应用食谱',
    content: `确定要将第 ${currentDay.value} 天的食谱应用到今天的饮食记录吗？`,
    success: async (res) => {
      if (res.confirm) {
        uni.showLoading({ title: '应用中...' })
        try {
          const today = new Date().toISOString().split('T')[0]
          const res: any = await request({
            url: `${API_BASE_URL}/api/v1/plans/${plan.value.id}/apply`,
            method: 'POST',
            data: {
              day_index: currentDay.value,
              target_date: today
            }
          })
          
          uni.hideLoading()
          if (res.data.code === 0) {
            uni.showToast({ title: '已成功应用', icon: 'success' })
            // 可以在这里触发全局事件通知记录页刷新
            uni.$emit('meal-record-updated')
            setTimeout(() => {
                uni.navigateBack()
            }, 1000)
          } else {
            uni.showToast({ title: res.data.message || '应用失败', icon: 'none' })
          }
        } catch (e) {
          uni.hideLoading()
          uni.showToast({ title: '网络请求失败', icon: 'none' })
        }
      }
    }
  })
}
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #F8F9FA;
  padding-bottom: 120rpx;
}

.banner {
  position: relative;
  height: 400rpx;
  width: 100%;
}

.banner-img {
  width: 100%;
  height: 100%;
}

.banner-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.6));
}

.banner-content {
  position: absolute;
  bottom: 30rpx;
  left: 30rpx;
  right: 30rpx;
  color: #fff;
}

.plan-title {
  font-size: 44rpx;
  font-weight: bold;
  margin-bottom: 16rpx;
  display: block;
}

.plan-meta {
  display: flex;
  gap: 20rpx;
}

.meta-tag {
  font-size: 24rpx;
  background: rgba(255,255,255,0.2);
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
  backdrop-filter: blur(4px);
}

.back-btn {
  position: absolute;
  left: 30rpx;
  width: 60rpx;
  height: 60rpx;
  background: rgba(0,0,0,0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 32rpx;
  z-index: 10;
}

.section {
  background: #fff;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.description-section {
  border-bottom-left-radius: 24rpx;
  border-bottom-right-radius: 24rpx;
  margin-top: -20rpx;
  position: relative;
  z-index: 5;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
  display: block;
  border-left: 8rpx solid #4CAF50;
  padding-left: 20rpx;
}

.desc-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  margin-bottom: 20rpx;
  display: block;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.tag {
  font-size: 24rpx;
  color: #4CAF50;
  background: #E8F5E9;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
}

.day-scroll {
  white-space: nowrap;
  margin: 0 -30rpx 30rpx;
  width: calc(100% + 60rpx);
}

.day-list {
  display: flex;
  padding: 0 30rpx;
  gap: 20rpx;
}

.day-item {
  width: 120rpx;
  height: 120rpx;
  background: #F5F5F5;
  border-radius: 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 2rpx solid transparent;
  
  &.active {
    background: #E8F5E9;
    border-color: #4CAF50;
    
    .day-num { color: #4CAF50; font-weight: bold; }
  }
}

.day-num {
  font-size: 28rpx;
  color: #666;
}

.day-status {
  font-size: 20rpx;
  color: #999;
  margin-top: 4rpx;
}

.mobile-summary {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20rpx;
  border-bottom: 1rpx solid #eee;
  padding-bottom: 10rpx;
}

.summary-text {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
}

.summary-cals {
  font-size: 24rpx;
  color: #999;
}

.meal-card {
  background: #FFF;
  border: 1rpx solid #eee;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
}

.meal-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.meal-type {
  font-size: 26rpx;
  font-weight: bold;
  color: #333;
  background: #F0F0F0;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.meal-cals {
  font-size: 24rpx;
  color: #999;
}

.meal-content {
  margin-bottom: 12rpx;
}

.food-name {
  font-size: 30rpx;
  color: #333;
  margin-right: 16rpx;
}

.food-amount {
  font-size: 26rpx;
  color: #666;
}

.alternatives {
  border-top: 1rpx dashed #eee;
  padding-top: 12rpx;
  margin-top: 12rpx;
}

.alt-header {
  display: flex;
  justify-content: space-between;
  font-size: 24rpx;
  color: #4CAF50;
}

.alt-list {
  margin-top: 10rpx;
  background: #FAFAFA;
  padding: 12rpx;
  border-radius: 8rpx;
}

.alt-item {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 4rpx;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  display: flex;
  gap: 20rpx;
  box-shadow: 0 -4rpx 12rpx rgba(0,0,0,0.05);
}

.action-btn {
  flex: 1;
  font-size: 28rpx;
  border-radius: 40rpx;
  border: none;
  
  &.secondary {
    background: #F5F5F5;
    color: #666;
  }
  
  &.primary {
    background: #4CAF50;
    color: #fff;
  }
}
</style>
