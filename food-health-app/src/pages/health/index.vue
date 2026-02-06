<template>
  <view class="container">
    <view class="header">
      <view class="nav-bar">
        <text class="back" @click="goBack">←</text>
        <text class="title">健康档案</text>
      </view>
      <view class="overview">
        <view class="avatar">🙂</view>
        <view class="overview-text">
          <text class="overview-title">健康关注</text>
          <text class="overview-sub">{{ healthFocus }}</text>
        </view>
      </view>
      <view class="progress">
        <text class="progress-label">健康档案完善进度</text>
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: progress + '%' }"></view>
        </view>
        <text class="progress-value">{{ progress }}%</text>
      </view>
    </view>

    <view class="tabs">
      <text
        v-for="tab in tabs"
        :key="tab.key"
        class="tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >{{ tab.label }}</text>
    </view>

    <view class="content">
      <view v-if="activeTab === 'core'" class="card">
        <text class="card-title">核心指标</text>
        <view class="bmi-card">
          <view class="bmi-main" :class="bmiStatusClass">
            <text class="bmi-label">BMI</text>
            <text class="bmi-value">{{ bmiDisplay }}</text>
            <text class="bmi-status" v-if="bmiStatus">{{ bmiStatus }}</text>
            <text class="bmi-status muted" v-else>待完善</text>
          </view>
        <view class="bmi-advice">
          <view class="bmi-advice-header">
            <text class="bmi-advice-title">健康建议</text>
            <text v-if="adviceBadge" class="advice-badge">{{ adviceBadge }}</text>
          </view>
          <view class="advice-line">
            <text class="advice-icon">🥗</text>
            <view class="advice-content">
              <text class="advice-label">饮食建议</text>
              <text class="advice-text">{{ adviceDiet }}</text>
            </view>
          </view>
          <view class="advice-line">
            <text class="advice-icon">🏃</text>
            <view class="advice-content">
              <text class="advice-label">运动建议</text>
              <text class="advice-text">{{ adviceExercise }}</text>
            </view>
          </view>
          <text class="advice-update">最近更新：{{ adviceUpdatedLabel }}</text>
        </view>
      </view>
        <view class="form-item">
          <text class="label">体重 (kg)</text>
          <input class="input" type="number" v-model="profile.weight" placeholder="如 65" />
        </view>
        <view class="form-item">
          <text class="label">身高 (cm)</text>
          <input class="input" type="number" v-model="profile.height" placeholder="如 170" />
        </view>
        <view class="form-item">
          <text class="label">年龄</text>
          <input class="input" type="number" v-model="profile.age" placeholder="如 28" />
        </view>
        <view class="form-item">
          <text class="label">性别</text>
          <view class="tags">
            <text class="tag" :class="{ active: profile.gender === 'male' }" @click="profile.gender = 'male'">男</text>
            <text class="tag" :class="{ active: profile.gender === 'female' }" @click="profile.gender = 'female'">女</text>
          </view>
        </view>
        <view class="form-item">
          <text class="label">活动水平</text>
          <view class="tags">
            <text class="tag" :class="{ active: profile.activity === 'low' }" @click="profile.activity = 'low'">轻量</text>
            <text class="tag" :class="{ active: profile.activity === 'medium' }" @click="profile.activity = 'medium'">中等</text>
            <text class="tag" :class="{ active: profile.activity === 'high' }" @click="profile.activity = 'high'">高强度</text>
          </view>
        </view>
        <button class="save-btn" @click="saveProfile">保存</button>
      </view>

      <view v-else-if="activeTab === 'health'" class="card">
        <view class="card-header">
          <text class="card-title">健康趋势</text>
          <view class="time-filter">
            <text
              class="filter-btn"
              :class="{ active: weightDays === 7 }"
              @click="changeWeightDays(7)"
            >7天</text>
            <text
              class="filter-btn"
              :class="{ active: weightDays === 14 }"
              @click="changeWeightDays(14)"
            >14天</text>
            <text
              class="filter-btn"
              :class="{ active: weightDays === 30 }"
              @click="changeWeightDays(30)"
            >30天</text>
          </view>
        </view>
        <health-chart
          title="体重变化"
          unit="kg"
          type="line"
          :data="weightHistory"
          color="#4CAF50"
        />
        <view class="chart-tip">
          <text class="tip-icon">💡</text>
          <text class="tip-text">每日记录体重，有助于掌握身体变化趋势。</text>
        </view>
      </view>

      <view v-else-if="activeTab === 'diet'" class="card">
        <text class="card-title">营养摄入</text>
        <health-chart 
          title="近7日热量摄入" 
          unit="kcal" 
          type="bar"
          :data="nutritionHistory"
          color="#FF9800"
        />
        <view class="chart-tip">
          <text class="tip-icon">📊</text>
          <text class="tip-text">建议每日热量摄入保持在推荐范围内。</text>
        </view>
      </view>

      <view v-else class="card">
        <text class="card-title">{{ currentTabLabel }}</text>
        <text class="placeholder">模块建设中，后续会逐步补充内容</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import healthProfile from '@/utils/healthProfile'
import { hasPlanProfileChanged } from '@/utils/planSignature.js'
import { API_BASE_URL } from '@/config.js'
import { request } from '@/utils/http'
import HealthChart from '@/components/HealthChart.vue'

const tabs = [
  { key: 'core', label: '核心指标' },
  { key: 'health', label: '健康数据' },
  { key: 'diet', label: '饮食管理' },
  { key: 'sport', label: '运动燃脂' }
]

const activeTab = ref('core')
const weightDays = ref(7) // 默认显示7天
const profile = ref<any>(uni.getStorageSync('healthProfile') || {})
const progress = ref(healthProfile.calcProfileCompletion(profile.value))
const healthFocus = ref(healthProfile.getHealthFocusMessage(profile.value))
const advice = ref<any>(uni.getStorageSync('healthAdvice') || {})
const adviceUpdatedAt = ref(advice.value?.updatedAt || '')

// 图表数据类型
interface ChartDataItem {
  label: string
  value: number
  color?: string
}

// 图表数据
const weightHistory = ref<ChartDataItem[]>([])
const nutritionHistory = ref<ChartDataItem[]>([])

const bmiValue = computed(() => healthProfile.calcBmiValue(profile.value))
const bmiStatus = computed(() => healthProfile.getBmiStatus(bmiValue.value))
const localAdvice = computed(() => healthProfile.getLocalAdvice(profile.value))
const bmiDisplay = computed(() => {
  if (!bmiValue.value) return '--'
  return bmiValue.value.toFixed(1)
})
const adviceDiet = computed(() => advice.value?.diet || localAdvice.value.diet)
const adviceExercise = computed(() => advice.value?.exercise || localAdvice.value.exercise)
const adviceBadge = computed(() => (advice.value?.source === 'deepseek_ai' ? 'AI建议' : ''))
const adviceUpdatedLabel = computed(() => {
  if (!adviceUpdatedAt.value) return '暂无'
  const date = new Date(adviceUpdatedAt.value)
  if (Number.isNaN(date.getTime())) return '暂无'
  const pad = (value: number) => value.toString().padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
})
const bmiStatusClass = computed(() => {
  if (!bmiStatus.value) return ''
  if (bmiStatus.value === '正常') return 'status-normal'
  if (bmiStatus.value === '偏低') return 'status-low'
  if (bmiStatus.value === '超重') return 'status-high'
  return 'status-obese'
})

const currentTabLabel = computed(() => {
  return tabs.find((tab) => tab.key === activeTab.value)?.label || ''
})

const persistAdvice = (nextAdvice: any) => {
  const updatedAt = new Date().toISOString()
  const payload = {
    diet: nextAdvice.diet,
    exercise: nextAdvice.exercise,
    source: nextAdvice.source || 'local',
    updatedAt
  }
  advice.value = payload
  adviceUpdatedAt.value = updatedAt
  uni.setStorageSync('healthAdvice', payload)
}

const fetchAdvice = async () => {
  try {
    const res = await request({
      url: `${API_BASE_URL}/api/v1/health/advice`,
      method: 'POST',
      data: profile.value
    })
    if (res.statusCode === 200 && res.data?.code === 0 && res.data?.data) {
      const data = res.data.data
      persistAdvice({
        diet: data.diet_advice,
        exercise: data.exercise_advice,
        source: data.source || (data.ai_generated ? 'deepseek_ai' : 'local')
      })
      return
    }
  } catch (error) {
    // 忽略请求失败
  }
  persistAdvice({
    diet: localAdvice.value.diet,
    exercise: localAdvice.value.exercise,
    source: 'local'
  })
}

// 保存个人档案并同步体重
const saveProfile = async () => {
  const prevProfile = uni.getStorageSync('healthProfile') || {}
  const prevUser = uni.getStorageSync('user') || {}
  const nextProfile = { ...profile.value }
  const hasChanged = hasPlanProfileChanged(prevProfile, prevUser, nextProfile, prevUser)

  uni.setStorageSync('healthProfile', profile.value)
  if (hasChanged) {
    uni.setStorageSync('planNeedsUpdate', true)
  }
  progress.value = healthProfile.calcProfileCompletion(profile.value)
  healthFocus.value = healthProfile.getHealthFocusMessage(profile.value)
  fetchAdvice()
  
  // 同步体重到后端
  if (profile.value.weight) {
    try {
      const weightRes = await request({
        url: `${API_BASE_URL}/api/v1/health/weight`,
        method: 'POST',
        data: profile.value
      })

      // 检查保存结果
      if (weightRes.statusCode === 200 && weightRes.data?.code === 0) {
        console.log('✅ 体重记录已保存到数据库')

        // 刷新图表数据（如果在健康数据tab）
        if (activeTab.value === 'health') {
          await fetchChartsData()
        }
      } else {
        console.warn('⚠️ 体重保存失败:', weightRes.data?.message || '未知错误')
      }
    } catch (e) {
      console.error('❌ 同步体重异常:', e)
      // 用户可能未登录或网络错误
      // 不影响本地保存，静默处理
    }
  }

  uni.showToast({ title: '已保存', icon: 'success' })
}

const goBack = () => {
  uni.navigateBack()
}

// 切换体重显示天数
const changeWeightDays = (days: number) => {
  weightDays.value = days
  fetchWeightData()
}

// 数据采样函数 - 等间隔选取关键数据点
const sampleData = (data: any[], maxPoints: number = 8) => {
  if (data.length <= maxPoints) return data

  const result = []
  const step = (data.length - 1) / (maxPoints - 1)

  for (let i = 0; i < maxPoints; i++) {
    const index = Math.round(i * step)
    result.push(data[index])
  }

  return result
}

// 获取体重数据
const fetchWeightData = async () => {
  try {
    const res = await request({ url: `${API_BASE_URL}/api/v1/health/weight/history?days=${weightDays.value}`, method: 'GET' })
    if (res.data?.code === 0) {
      const rawData = res.data.data.map((item: any) => ({
        label: item.date.slice(5), // MD格式
        value: item.weight
      }))
      // 采样：最多显示8个数据点
      weightHistory.value = sampleData(rawData, 8)
    }
  } catch (e) {}
}

// 获取图表数据
const fetchChartsData = async () => {
  // 1. 获取体重历史
  await fetchWeightData()

  // 2. 获取营养历史
  try {
    const res = await request({ url: `${API_BASE_URL}/api/v1/health/nutrition/history?days=7`, method: 'GET' })
    if (res.data?.code === 0) {
      nutritionHistory.value = res.data.data.map((item: any) => ({
        label: item.date.slice(5),
        value: item.calories,
        color: item.calories > 2500 ? '#FF5722' : '#FF9800' // 高热量标红
      }))
    }
  } catch (e) {}
}

onMounted(() => {
  if (!advice.value?.diet) {
    persistAdvice({
      diet: localAdvice.value.diet,
      exercise: localAdvice.value.exercise,
      source: 'local'
    })
  }
  // if (profile.value?.weight && profile.value?.height) {
  //   fetchAdvice()
  // }
  
  // 加载报表数据
  fetchChartsData()
})

// 监听 tab 切换，如果是数据页则刷新数据
watch(activeTab, (newVal) => {
  if (newVal === 'health' || newVal === 'diet') {
    fetchChartsData()
  }
})
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #F5F7FA;
}

.header {
  padding: 40rpx 30rpx 30rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
  color: #fff;
}

.nav-bar {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.back {
  font-size: 36rpx;
}

.title {
  font-size: 32rpx;
  font-weight: 600;
}

.overview {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: rgba(255,255,255,0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}

.overview-title {
  font-size: 28rpx;
  font-weight: 600;
}

.overview-sub {
  font-size: 22rpx;
  opacity: 0.9;
}

.progress {
  background: #fff;
  color: #333;
  border-radius: 16rpx;
  padding: 20rpx;
}

.progress-label {
  font-size: 24rpx;
  margin-bottom: 12rpx;
}

.progress-bar {
  height: 12rpx;
  background: #E6F4EA;
  border-radius: 10rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #81C784);
}

.progress-value {
  font-size: 22rpx;
  margin-top: 8rpx;
  text-align: right;
}

.tabs {
  display: flex;
  gap: 16rpx;
  padding: 20rpx 30rpx 0;
  flex-wrap: wrap;
}

.tab {
  padding: 10rpx 22rpx;
  background: #fff;
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #666;
}

.tab.active {
  background: #E8F5E9;
  color: #4CAF50;
  border: 1rpx solid #4CAF50;
}

.content {
  padding: 20rpx 30rpx;
}

.card {
  background: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 6rpx 20rpx rgba(0,0,0,0.05);
  margin-bottom: 20rpx;
}

.card-title {
  font-size: 28rpx;
  font-weight: 600;
  margin-bottom: 20rpx;
}

.bmi-card {
  display: flex;
  gap: 24rpx;
  padding: 20rpx;
  background: #F6FBF7;
  border-radius: 18rpx;
  margin-bottom: 24rpx;
}

.bmi-main {
  width: 180rpx;
  background: #E8F5E9;
  border-radius: 16rpx;
  padding: 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
}

.bmi-main.status-normal {
  background: #E8F5E9;
}

.bmi-main.status-low {
  background: #E3F2FD;
}

.bmi-main.status-high {
  background: #FFF3E0;
}

.bmi-main.status-obese {
  background: #FFEBEE;
}

.bmi-label {
  font-size: 22rpx;
  color: #66BB6A;
}

.bmi-value {
  font-size: 36rpx;
  font-weight: 600;
  color: #2E7D32;
}

.bmi-status {
  font-size: 22rpx;
  color: #4CAF50;
}

.bmi-status.muted {
  color: #9E9E9E;
}

.bmi-main.status-low .bmi-label,
.bmi-main.status-low .bmi-status {
  color: #1E88E5;
}

.bmi-main.status-low .bmi-value {
  color: #1565C0;
}

.bmi-main.status-high .bmi-label,
.bmi-main.status-high .bmi-status {
  color: #F57C00;
}

.bmi-main.status-high .bmi-value {
  color: #EF6C00;
}

.bmi-main.status-obese .bmi-label,
.bmi-main.status-obese .bmi-status {
  color: #D32F2F;
}

.bmi-main.status-obese .bmi-value {
  color: #C62828;
}

.bmi-advice {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  justify-content: center;
}

.bmi-advice-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.bmi-advice-title {
  font-size: 24rpx;
  color: #4CAF50;
  font-weight: 600;
}

.advice-badge {
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  background: #FFECB3;
  color: #8D6E63;
  font-size: 20rpx;
}

.advice-line {
  display: flex;
  gap: 14rpx;
  align-items: flex-start;
}

.advice-icon {
  font-size: 28rpx;
  line-height: 1.2;
}

.advice-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6rpx;
}

.advice-label {
  font-size: 22rpx;
  color: #4CAF50;
  font-weight: 500;
}

.advice-text {
  font-size: 22rpx;
  color: #5F6C6F;
  line-height: 1.6;
}

.advice-update {
  font-size: 20rpx;
  color: #9E9E9E;
}

.form-item {
  margin-bottom: 20rpx;
}

.label {
  display: block;
  font-size: 24rpx;
  color: #666;
  margin-bottom: 10rpx;
}

.input {
  background: #F7F7F7;
  padding: 16rpx;
  border-radius: 12rpx;
  font-size: 26rpx;
}

.tags {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.tag {
  padding: 10rpx 20rpx;
  background: #F0F0F0;
  border-radius: 16rpx;
  font-size: 24rpx;
  color: #666;
}

.tag.active {
  background: #E8F5E9;
  color: #4CAF50;
  border: 1rpx solid #4CAF50;
}

.save-btn {
  width: 100%;
  padding: 24rpx;
  background: linear-gradient(135deg, #4CAF50, #66BB6A);
  border-radius: 16rpx;
  color: #fff;
  font-size: 28rpx;
}

.placeholder {
  font-size: 24rpx;
  color: #999;
}

.chart-tip {
  margin-top: 24rpx;
  display: flex;
  gap: 12rpx;
  background: #F5F7FA;
  padding: 16rpx;
  border-radius: 12rpx;
}

.tip-icon {
  font-size: 28rpx;
}

.tip-text {
  font-size: 22rpx;
  color: #666;
  line-height: 1.5;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

/* 时间筛选器 */
.time-filter {
  display: flex;
  gap: 8rpx;
}

.filter-btn {
  padding: 8rpx 16rpx;
  font-size: 22rpx;
  color: #999;
  background: #F5F5F5;
  border-radius: 12rpx;
}

.filter-btn.active {
  color: #fff;
  background: #4CAF50;
}
</style>
