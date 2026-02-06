<template>
  <view class="container">
    <!-- Header -->
    <view class="header">
      <view class="search-bar">
        <input 
          class="search-input" 
          type="text" 
          placeholder="搜索食谱 (如: 减脂)" 
          v-model="searchQuery"
          @confirm="loadPlans"
        />
        <text class="search-icon">🔍</text>
      </view>
    </view>

    <!-- Filters -->
    <scroll-view scroll-x class="filter-scroll">
      <view class="filter-list">
        <view 
          class="filter-tag" 
          :class="{ active: currentFilter === 'all' }"
          @click="setFilter('all')"
        >全部</view>
        <view 
          class="filter-tag" 
          v-for="tag in commonTags" 
          :key="tag"
          :class="{ active: currentFilter === tag }"
          @click="setFilter(tag)"
        >{{ tag }}</view>
      </view>
    </scroll-view>

    <!-- Content -->
    <view class="content">
      <view class="section-header" v-if="recommendedPlan">
        <text class="title">今日推荐</text>
        <text class="subtitle">根据您的目标生成</text>
      </view>

      <view class="update-tip" v-if="showUpdatePrompt && !isGenerating">
        <text class="update-tip-text">检测到您数据变动，建议重新生成 AI 食谱</text>
        <button class="update-tip-btn" @click="generateAIPlan(true)">生成 AI 食谱</button>
      </view>
      
<!-- Loading Mask -->
    <view class="loading-mask" v-if="isGenerating" @touchmove.stop.prevent>
      <view class="loading-spinner"></view>
      <text class="loading-text">AI 正在根据您的目标生成食谱...</text>
    </view>

    <!-- Generate AI Plan Button -->
    <view class="generate-section" v-if="!isGenerating && !recommendedPlan">
      <view class="section-header">
        <text class="title">今日推荐</text>
        <text class="subtitle">根据您的目标生成</text>
      </view>
      <button class="generate-btn" @click="generateAIPlan()">🤖 生成推荐食谱</button>
    </view>

    <!-- AI Plan Card -->
    <view class="ai-card" v-if="recommendedPlan">
        <view class="ai-card-bg"></view>
        <view class="ai-content" @click="goDetail(recommendedPlan.id)">
          <view class="ai-header">
            <text class="ai-badge">AI 定制</text>
            <text class="ai-days">{{ recommendedPlan.duration_days }}天计划</text>
          </view>
          <text class="ai-title">{{ recommendedPlan.name }}</text>
          <text class="ai-desc">{{ recommendedPlan.description }}</text>
          
          <view class="ai-actions" style="display: flex; gap: 20rpx; margin-top: 20rpx;">
             <button class="ai-btn" @click.stop="goDetail(recommendedPlan.id)">查看详情</button>
             <button class="ai-btn regenerate-btn" @click.stop="generateAIPlan(true)">🔄 重新生成</button>
          </view>
        </view>
      </view>

      <view class="section-header">
        <text class="title">精选食谱</text>
      </view>

      <view class="plan-list">
        <view
          class="plan-card-wrapper"
          v-for="plan in planList"
          :key="plan.id"
        >
          <!-- 食谱卡片（支持滑动） -->
          <view
            class="plan-card"
            :style="{ transform: `translateX(${swipeStates[plan.id] || 0}px)` }"
            @touchstart="handleTouchStart($event, plan.id)"
            @touchmove="handleTouchMove"
            @touchend="handleTouchEnd(plan.id)"
            @click="handleCardClick(plan.id)"
          >
            <image class="plan-img" :src="plan.cover_image || '/static/default_food.png'" mode="aspectFill" />
            <view class="plan-info">
              <text class="plan-name">{{ plan.name }}</text>
              <view class="plan-tags">
                <text class="tag" v-for="tag in (plan.tags ? plan.tags.split(',') : []).slice(0, 2)" :key="tag">{{ tag }}</text>
              </view>
              <view class="plan-meta">
                <text class="difficulty">{{ plan.difficulty === 'easy' ? '简单' : '中等' }}</text>
                <text class="days">{{ plan.duration_days }}天</text>
              </view>
            </view>
          </view>

          <!-- 滑动显示的删除按钮 -->
          <view class="delete-btn" @click="handleDislike(plan)">
            不感兴趣
          </view>
        </view>
      </view>

      <view v-if="planList.length === 0 && !loading" class="empty-tip">
        暂无相关食谱
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { API_BASE_URL } from '@/config.js'
import { buildPlanSignature, buildPlanProfilePayload } from '@/utils/planSignature.js'
import { shouldShowPlanUpdatePrompt } from '@/utils/planRecommendation.js'

const searchQuery = ref('')
const currentFilter = ref('all')
const loading = ref(false)
const isGenerating = ref(false)
const planList = ref<any[]>([])
const recommendedPlan = ref<any>(null)
const showUpdatePrompt = ref(false)
const currentSignature = ref('')

// 滑动删除相关状态
const swipeStates = ref<Record<number, number>>({})
let touchStartX = 0
let currentSwipePlanId: number | null = null

const commonTags = ['减脂', '增肌', '低碳水', '高蛋白', '素食', '快速']

onMounted(() => {
  loadPlans()
  syncPlanPromptState()
  loadRecommendedPlan()
})

onShow(() => {
  syncPlanPromptState()
  loadRecommendedPlan()
})

const setFilter = (tag: string) => {
  currentFilter.value = tag
  loadPlans()
}

const loadPlans = async () => {
  loading.value = true
  try {
    let url = `${API_BASE_URL}/api/v1/plans`
    if (currentFilter.value !== 'all') {
      url += `?tag=${currentFilter.value}`
    }
    const res = await uni.request({
      url: url,
      method: 'GET'
    })
    if (res.data.code === 0) {
      planList.value = res.data.data
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const getCurrentPlanContext = () => {
  const profile = uni.getStorageSync('healthProfile') || {}
  const user = uni.getStorageSync('user') || {}
  return { profile, user }
}

const syncPlanPromptState = () => {
  const { profile, user } = getCurrentPlanContext()
  const signature = buildPlanSignature(profile, user)
  currentSignature.value = signature
  const savedSignature = uni.getStorageSync('planSignature') || ''
  const needsUpdate = uni.getStorageSync('planNeedsUpdate')
  showUpdatePrompt.value = shouldShowPlanUpdatePrompt(savedSignature, signature, Boolean(needsUpdate))
}

const loadRecommendedPlan = async () => {
  try {
    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/plans/recommended`,
      method: 'GET',
      header: {
        'Authorization': `Bearer ${uni.getStorageSync('token')}`
      }
    })
    if (res.data.code === 0) {
      recommendedPlan.value = res.data.data || null
    }
  } catch (e) {
    console.error('加载推荐食谱失败', e)
  }
}

const generateAIPlan = async (force: boolean = false) => {
  if (isGenerating.value) return

  isGenerating.value = true
  try {
    const { profile, user } = getCurrentPlanContext()

    // 获取用户偏好（不喜欢的标签）
    const prefs = getPreferences()
    const dislikedTags = prefs.dislikedTags || []

    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/plans/generate` + (force ? '?force_new=true' : ''),
      method: 'POST',
      header: {
          'Authorization': `Bearer ${uni.getStorageSync('token')}`
      },
      data: {
        ...buildPlanProfilePayload(profile, user),
        disliked_tags: dislikedTags  // 传递不喜欢的标签
      }
    })
    if (res.data.code === 0) {
      recommendedPlan.value = res.data.data
      uni.setStorageSync('planSignature', currentSignature.value)
      uni.setStorageSync('planNeedsUpdate', false)
      showUpdatePrompt.value = false

      // 生成成功提示
      uni.showToast({ title: force ? 'AI 食谱已更新' : '生成成功', icon: 'success' })

      // 滚动到顶部，让用户立即看到新食谱
      setTimeout(() => {
        uni.pageScrollTo({
          scrollTop: 0,
          duration: 300
        })
      }, 100)
    }
  } catch (e) {
    console.error("Failed to load AI plan", e)
    uni.showToast({ title: '生成失败，请重试', icon: 'none' })
  } finally {
    isGenerating.value = false
  }
}

const goDetail = (id: number) => {
  uni.navigateTo({ url: `/pages/plan/detail?id=${id}` })
}

// ===== 滑动删除交互 =====

const handleTouchStart = (e: any, planId: number) => {
  touchStartX = e.touches[0].clientX
  currentSwipePlanId = planId
}

const handleTouchMove = (e: any) => {
  if (currentSwipePlanId === null) return

  const deltaX = e.touches[0].clientX - touchStartX
  // 只允许向左滑动，最大滑动距离 100rpx
  if (deltaX < 0 && deltaX > -100) {
    swipeStates.value[currentSwipePlanId] = deltaX
  }
}

const handleTouchEnd = (planId: number) => {
  const swipe = swipeStates.value[planId] || 0

  // 如果滑动超过 50rpx，则显示删除按钮
  if (swipe < -50) {
    swipeStates.value[planId] = -100
  } else {
    // 否则回弹
    swipeStates.value[planId] = 0
  }

  currentSwipePlanId = null
}

const handleCardClick = (planId: number) => {
  const swipe = swipeStates.value[planId] || 0

  // 如果卡片已滑动，点击时先回弹，不进入详情
  if (swipe !== 0) {
    swipeStates.value[planId] = 0
    return
  }

  // 否则正常进入详情
  goDetail(planId)
}

// ===== 不感兴趣功能 =====

interface UserPreference {
  dislikedTags: string[]
  lastUpdated: number
}

const getPreferences = (): UserPreference => {
  const data = uni.getStorageSync('userPreference')
  return data || { dislikedTags: [], lastUpdated: Date.now() }
}

const savePreferences = (prefs: UserPreference) => {
  prefs.lastUpdated = Date.now()
  uni.setStorageSync('userPreference', prefs)
}

const addDislikedTag = (tag: string) => {
  const prefs = getPreferences()
  if (!prefs.dislikedTags.includes(tag)) {
    prefs.dislikedTags.push(tag)
    savePreferences(prefs)
  }
}

const handleDislike = (plan: any) => {
  // 1. 立即从列表移除（假删除）
  planList.value = planList.value.filter(p => p.id !== plan.id)

  // 2. 重置滑动状态
  if (swipeStates.value[plan.id]) {
    delete swipeStates.value[plan.id]
  }

  // 3. 可选：收集反馈
  showFeedbackDialog(plan)
}

const showFeedbackDialog = (plan: any) => {
  uni.showActionSheet({
    itemList: ['食材不喜欢', '做法太难', '热量太高', '随意隐藏'],
    success: (res) => {
      const planName = plan.name || ''
      const planTags = plan.tags || ''

      switch (res.tapIndex) {
        case 0: // 食材不喜欢
          // 尝试从标签中提取食材相关信息
          const foodTags = extractFoodTags(planTags, planName)
          foodTags.forEach(tag => addDislikedTag(tag))
          if (foodTags.length > 0) {
            console.log('已记录不喜欢的食材:', foodTags)
          }
          break

        case 1: // 做法太难
          addDislikedTag('复杂做法')
          console.log('已记录：不喜欢复杂做法')
          break

        case 2: // 热量太高
          addDislikedTag('高热量')
          console.log('已记录：不喜欢高热量')
          break

        case 3: // 随意隐藏
          console.log('食谱已隐藏')
          break
      }
    }
  })
}

const extractFoodTags = (tags: string, name: string): string[] => {
  const result: string[] = []
  const text = `${tags} ${name}`

  // 常见食材关键词
  const foodKeywords = [
    '素食', '海鲜', '肉类', '鸡肉', '猪肉', '牛肉', '鱼', '虾', '蟹',
    '芹菜', '香菜', '茄子', '豆腐', '辣', '油炸', '清淡'
  ]

  foodKeywords.forEach(keyword => {
    if (text.includes(keyword)) {
      result.push(keyword)
    }
  })

  return result
}
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #F8F9FA;
  padding-bottom: 40rpx;
}

/* Loading Mask */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  z-index: 999;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid #E8F5E9;
  border-top: 4rpx solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20rpx;
}

.loading-text {
  font-size: 28rpx;
  color: #4CAF50;
  font-weight: 500;
}

/* Generate Button */
.generate-section {
  padding: 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.generate-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 24rpx 40rpx;
  border-radius: 30rpx;
  font-size: 32rpx;
  margin-top: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(76, 175, 80, 0.3);
}

.generate-btn:active {
  background: #45a049;
  transform: scale(0.98);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.header {
  background: #fff;
  padding: 20rpx 30rpx;
  position: sticky;
  top: 0;
  z-index: 100;
}

.search-bar {
  background: #F5F5F5;
  border-radius: 40rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  padding: 0 30rpx;
}

.search-icon {
  font-size: 32rpx;
  color: #999;
  margin-left: 20rpx;
}

.search-input {
  flex: 1;
  height: 100%;
  font-size: 28rpx;
}

.filter-scroll {
  background: #fff;
  white-space: nowrap;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #EEE;
}

.filter-list {
  padding: 0 30rpx;
  display: flex;
  gap: 20rpx;
}

.filter-tag {
  padding: 10rpx 30rpx;
  background: #F5F5F5;
  border-radius: 30rpx;
  font-size: 26rpx;
  color: #666;
  
  &.active {
    background: #E8F5E9;
    color: #4CAF50;
    font-weight: 500;
  }
}

.content {
  padding: 30rpx;
}

.section-header {
  margin: 40rpx 0 20rpx;
  display: flex;
  align-items: baseline;
  &:first-child { margin-top: 10rpx; }
}

.update-tip {
  background: #FFF8E1;
  border: 1rpx solid #FFE0B2;
  border-radius: 16rpx;
  padding: 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.update-tip-text {
  font-size: 24rpx;
  color: #8D6E63;
  flex: 1;
}

.update-tip-btn {
  background: #FFB74D;
  color: #fff;
  font-size: 24rpx;
  padding: 12rpx 24rpx;
  border-radius: 30rpx;
  line-height: normal;
}

.title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  margin-right: 16rpx;
}

.subtitle {
  font-size: 24rpx;
  color: #999;
}

/* AI Card */
.ai-card {
  height: 300rpx;
  border-radius: 24rpx;
  overflow: hidden;
  position: relative;
  box-shadow: 0 8rpx 24rpx rgba(76, 175, 80, 0.2);
  margin-bottom: 30rpx;
}

.ai-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
}

.ai-content {
  position: relative;
  height: 100%;
  padding: 30rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.ai-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.ai-badge {
  background: rgba(255,255,255,0.2);
  color: #fff;
  font-size: 20rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  margin-right: 16rpx;
}

.ai-days {
  color: rgba(255,255,255,0.8);
  font-size: 24rpx;
}

.ai-title {
  color: #fff;
  font-size: 40rpx;
  font-weight: bold;
  margin-bottom: 12rpx;
}

.ai-desc {
  color: rgba(255,255,255,0.8);
  font-size: 26rpx;
  margin-bottom: 30rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.regenerate-btn {
  background: rgba(255, 255, 255, 0.2) !important;
  color: #fff !important;
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.ai-btn {
  background: #fff;
  color: #4CAF50;
  font-size: 26rpx;
  padding: 10rpx 30rpx;
  border-radius: 30rpx;
  align-self: flex-start;
  line-height: normal;
}

/* Plan List */
.plan-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}

.plan-card-wrapper {
  width: 48%;
  position: relative;
  margin-bottom: 30rpx;
  overflow: hidden;
  border-radius: 20rpx;
}

.plan-card {
  width: 100%;
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.05);
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  z-index: 2;
}

.delete-btn {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 100rpx;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  font-size: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  font-weight: 500;
}

.plan-img {
  width: 100%;
  height: 200rpx;
  background: #eee;
}

.plan-info {
  padding: 20rpx;
}

.plan-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 12rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
}

.plan-tags {
  display: flex;
  gap: 10rpx;
  margin-bottom: 16rpx;
}

.tag {
  font-size: 20rpx;
  color: #999;
  background: #F5F5F5;
  padding: 4rpx 10rpx;
  border-radius: 8rpx;
}

.plan-meta {
  display: flex;
  justify-content: space-between;
  font-size: 22rpx;
  color: #999;
}

.empty-tip {
  text-align: center;
  padding: 60rpx;
  color: #999;
  font-size: 26rpx;
}
</style>
