<template>
  <view class="container">
    <!-- Content -->
    <view class="content">
      <view class="page-header">
         <text class="page-title">AI 智能食谱</text>
         <text class="page-subtitle">为您量身定制的一周饮食计划</text>
      </view>

      <view class="update-tip" v-if="showUpdatePrompt && !isGenerating">
        <text class="update-tip-text">检测到您身体数据变动，建议重新生成</text>
        <button class="update-tip-btn" @click="generateAIPlan(true)">更新食谱</button>
      </view>
      
    <!-- Loading Mask -->
    <view class="loading-mask" v-if="isGenerating" @touchmove.stop.prevent>
      <view class="loading-spinner"></view>
      <text class="loading-text">AI 正在根据您的目标生成食谱...</text>
    </view>

    <!-- Generate AI Plan Button (Empty State) -->
    <view class="empty-state" v-if="!isGenerating && !recommendedPlan">
      <!-- 临时使用默认图，稍后替换 -->
      <image :src="'https://images.unsplash.com/photo-1543353071-873f17a7a088?q=80&w=800&auto=format&fit=crop'" mode="aspectFit" class="empty-img" />
      <text class="empty-text">还没有专属食谱</text>
      <button class="generate-btn main" @click="generateAIPlan()">
        <text class="btn-icon">🤖</text> 立即生成 AI 食谱
      </button>
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
          
          <view class="ai-actions">
             <button class="ai-btn" @click.stop="goDetail(recommendedPlan.id)">查看详情</button>
             <button class="ai-btn regenerate-btn" @click.stop="generateAIPlan(true)">🔄 重新生成</button>
          </view>
        </view>
      </view>
      
      <!-- 说明区域 -->
      <view class="info-section" v-if="recommendedPlan">
        <view class="info-item">
          <text class="info-icon">🎯</text>
          <view class="info-text">
            <text class="info-title">目标导向</text>
            <text class="info-desc">根据您的减脂/增肌目标调整热量缺口</text>
          </view>
        </view>
        <view class="info-item">
          <text class="info-icon">⚖️</text>
          <view class="info-text">
            <text class="info-title">营养均衡</text>
            <text class="info-desc">合理分配碳水、蛋白质和脂肪比例</text>
          </view>
        </view>
      </view>

    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { API_BASE_URL } from '@/config.js'
import logoImg from '@/static/logo.png'
import { buildPlanSignature, buildPlanProfilePayload } from '@/utils/planSignature.js'
import { shouldShowPlanUpdatePrompt } from '@/utils/planRecommendation.js'

const isGenerating = ref(false)
const recommendedPlan = ref<any>(null)
const showUpdatePrompt = ref(false)
const currentSignature = ref('')

onMounted(() => {
  syncPlanPromptState()
  loadRecommendedPlan()
})

onShow(() => {
  syncPlanPromptState()
  loadRecommendedPlan()
})

const getCurrentPlanContext = () => {
  // 使用本地缓存的健康档案（由 health/index.vue 和 profile/index.vue 同步更新）
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
    const data = res.data as any
    if (data.code === 0) {
      recommendedPlan.value = data.data || null
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

    // 获取用户偏好
    const prefs = uni.getStorageSync('userPreference') || { dislikedTags: [] }
    const dislikedTags = prefs.dislikedTags || []

    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/plans/generate` + (force ? '?force_new=true' : ''),
      method: 'POST',
      header: {
          'Authorization': `Bearer ${uni.getStorageSync('token')}`
      },
      data: {
        ...buildPlanProfilePayload(profile, user),
        disliked_tags: dislikedTags
      }
    })
    const data = res.data as any
    if (data.code === 0) {
      recommendedPlan.value = data.data
      uni.setStorageSync('planSignature', currentSignature.value)
      uni.setStorageSync('planNeedsUpdate', false)
      showUpdatePrompt.value = false

      uni.showToast({ title: force ? 'AI 食谱已更新' : '生成成功', icon: 'success' })
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
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #F8F9FA;
  padding-bottom: 40rpx;
}

.content {
  padding: 30rpx;
}

.page-header {
  margin: 20rpx 0 40rpx;
}

.page-title {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  display: block;
  margin-bottom: 10rpx;
}

.page-subtitle {
  font-size: 26rpx;
  color: #888;
}

/* Loading Mask */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  z-index: 999;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 80rpx;
  height: 80rpx;
  border: 4rpx solid #E8F5E9;
  border-top: 4rpx solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 30rpx;
}

.loading-text {
  font-size: 28rpx;
  color: #4CAF50;
  font-weight: 500;
}

/* Update Tip */
.update-tip {
  background: #FFF8E1;
  border: 1rpx solid #FFE0B2;
  border-radius: 16rpx;
  padding: 24rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 30rpx;
  box-shadow: 0 2rpx 8rpx rgba(255, 160, 0, 0.1);
}

.update-tip-text {
  font-size: 26rpx;
  color: #8D6E63;
  flex: 1;
}

.update-tip-btn {
  background: #FF9800;
  color: #fff;
  font-size: 24rpx;
  padding: 10rpx 24rpx;
  border-radius: 30rpx;
  line-height: normal;
  border: none;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
}

.empty-img {
  width: 240rpx;
  height: 240rpx;
  margin-bottom: 30rpx;
  opacity: 0.8;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 40rpx;
}

.generate-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 24rpx 60rpx;
  border-radius: 50rpx;
  font-size: 32rpx;
  box-shadow: 0 8rpx 20rpx rgba(76, 175, 80, 0.3);
  display: flex;
  align-items: center;
}

.generate-btn:active {
  transform: scale(0.98);
  background: #43A047;
}

.btn-icon {
  margin-right: 12rpx;
  font-size: 36rpx;
}

/* AI Card */
.ai-card {
  min-height: 340rpx;
  border-radius: 30rpx;
  overflow: hidden;
  position: relative;
  box-shadow: 0 10rpx 30rpx rgba(76, 175, 80, 0.25);
  margin-bottom: 40rpx;
}

.ai-card-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
  /* 可选：增加一些纹理或图案 */
}

.ai-content {
  position: relative;
  height: 100%;
  padding: 40rpx 40rpx 50rpx; /* 增加底部内间距 */
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 上下分布 */
  z-index: 2;
}

.ai-header {
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}

.ai-badge {
  background: rgba(255,255,255,0.25);
  backdrop-filter: blur(4px);
  color: #fff;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 12rpx;
  margin-right: 16rpx;
  font-weight: 500;
}

.ai-days {
  color: rgba(255,255,255,0.9);
  font-size: 26rpx;
}

.ai-title {
  color: #fff;
  font-size: 44rpx;
  font-weight: bold;
  margin-bottom: 16rpx;
  text-shadow: 0 2rpx 4rpx rgba(0,0,0,0.1);
}

.ai-desc {
  color: rgba(255,255,255,0.9);
  font-size: 28rpx;
  margin-bottom: 30rpx;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
}

.ai-actions {
  display: flex;
  gap: 24rpx;
}

.ai-btn {
  background: #fff;
  color: #2E7D32;
  font-size: 26rpx;
  padding: 12rpx 32rpx;
  border-radius: 30rpx;
  font-weight: 600;
  border: none;
  line-height: normal;
  margin: 0; /* reset uni-app defaults */
}

.regenerate-btn {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #fff !important;
  border: 1px solid rgba(255, 255, 255, 0.4) !important;
}

/* Info Section */
.info-section {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.info-item {
  background: #fff;
  padding: 24rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.03);
}

.info-icon {
  font-size: 40rpx;
  margin-right: 24rpx;
}

.info-text {
  flex: 1;
}

.info-title {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 4rpx;
}

.info-desc {
  font-size: 24rpx;
  color: #888;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
