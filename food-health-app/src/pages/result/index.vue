<template>
  <view class="container">
    <!-- 顶部图片 -->
    <view class="image-section" v-if="imageUrl">
      <image :src="imageUrl" mode="aspectFill" class="food-image" />
    </view>
    <view class="image-section placeholder" v-else>
      <text class="placeholder-icon">🍽️</text>
    </view>

    <!-- 识别结果 -->
    <view class="result-section" v-if="resultData">
      <!-- 主结果 -->
      <view class="main-result" v-if="resultData.top_result">
        <view class="result-header">
          <text class="food-name">{{ resultData.top_result.name }}</text>
          <view class="badge-group">
            <view class="source-badge">
              <text>{{ getSourceLabel(resultData.top_result) }}</text>
            </view>
            <view class="confidence-badge">
              <text>{{ (resultData.top_result.confidence * 100).toFixed(0) }}% 匹配</text>
            </view>
          </view>
        </view>
        
        <view class="rating-row" v-if="resultData.top_result.health_rating">
          <text class="rating-label">健康评级：</text>
          <text :class="['rating-value', getRatingClass(resultData.top_result.health_rating)]">
            {{ resultData.top_result.health_rating }}
          </text>
        </view>

        <!-- 营养信息卡片 -->
        <view class="nutrition-card" v-if="resultData.top_result.nutrition">
          <view class="card-header">
            <text class="card-title">📊 营养成分（每100g）</text>
            <text class="ai-badge" v-if="resultData.top_result.ai_generated">🤖 AI估算</text>
          </view>
          <view class="nutrition-grid">
            <view class="nutrition-item">
              <text class="nutrition-value">{{ resultData.top_result.nutrition.calories }}</text>
              <text class="nutrition-label">热量(kcal)</text>
            </view>
            <view class="nutrition-item">
              <text class="nutrition-value">{{ resultData.top_result.nutrition.protein }}</text>
              <text class="nutrition-label">蛋白质(g)</text>
            </view>
            <view class="nutrition-item">
              <text class="nutrition-value">{{ resultData.top_result.nutrition.fat }}</text>
              <text class="nutrition-label">脂肪(g)</text>
            </view>
            <view class="nutrition-item">
              <text class="nutrition-value">{{ resultData.top_result.nutrition.carbohydrate }}</text>
              <text class="nutrition-label">碳水(g)</text>
            </view>
          </view>
          <!-- GI 值显示 -->
          <view class="gi-row" v-if="resultData.top_result.gi">
            <text class="gi-label">🩸 血糖生成指数(GI)：</text>
            <text :class="['gi-value', getGIClass(resultData.top_result.gi)]">
              {{ resultData.top_result.gi }}
              <text class="gi-level">{{ getGILevel(resultData.top_result.gi) }}</text>
            </text>
          </view>
        </view>

        <!-- 仅有百度热量时显示（DeepSeek 不可用的降级） -->
        <view class="baidu-calorie-card" v-else-if="resultData.top_result.baidu_calorie">
          <text class="card-title">🔥 热量数据</text>
          <view class="baidu-calorie-display">
            <text class="baidu-calorie-value">{{ resultData.top_result.baidu_calorie }}</text>
            <text class="baidu-calorie-unit">kcal / 100g</text>
          </view>
          <text class="baidu-calorie-note">暂时无法获取详细营养信息</text>
        </view>

        <!-- 卡路里计算（仅本地数据库有数据时显示完整选择器） -->
        <view class="calorie-card" v-if="resultData.top_result.found_in_database">
          <text class="card-title">🔥 估算你这份的热量</text>
          
          <view class="selector-group">
            <text class="selector-label">份量选择：</text>
            <view class="selector-options">
              <view 
                v-for="p in portions" 
                :key="p" 
                :class="['option-btn', selectedPortion === p ? 'active' : '']"
                @click="selectedPortion = p; calculateCalories()"
              >
                {{ p }}
              </view>
            </view>
          </view>
          
          <view class="selector-group">
            <text class="selector-label">烹饪方式：</text>
            <view class="selector-options cooking">
              <view 
                v-for="c in cookingMethods" 
                :key="c" 
                :class="['option-btn', selectedCooking === c ? 'active' : '']"
                @click="selectedCooking = c; calculateCalories()"
              >
                {{ c }}
              </view>
            </view>
          </view>
          
          <view class="calorie-result" v-if="calorieResult">
            <text class="calorie-value">{{ calorieResult.calories_display }}</text>
            <text class="calorie-note">{{ calorieResult.breakdown?.range_reason }}</text>
          </view>
        </view>

        <!-- 餐具估算（AI生成数据时使用） -->
        <view class="calorie-card" v-else-if="resultData.top_result.nutrition">
          <text class="card-title">🍽️ 估算你这份的热量</text>
          
          <view class="selector-group">
            <text class="selector-label">选择餐具：</text>
            <view class="selector-options">
              <view 
                v-for="d in dishSizes" 
                :key="d.name" 
                :class="['option-btn', selectedDish === d.name ? 'active' : '']"
                @click="selectedDish = d.name; calculateByDish()"
              >
                {{ d.name }}
              </view>
            </view>
          </view>
          
          <view class="calorie-result" v-if="dishCalories">
            <text class="calorie-value">{{ dishCalories }} kcal</text>
            <text class="calorie-note">{{ getSelectedDishWeight() }}g × {{ resultData.top_result.nutrition.calories }} kcal/100g</text>
          </view>
        </view>

        <!-- 健康提示 -->
        <view class="tips-card" v-if="resultData.top_result.health_tips">
          <text class="card-title">💡 健康建议</text>
          <text class="tips-content">{{ resultData.top_result.health_tips }}</text>
        </view>

        <!-- 禁忌人群 -->
        <view class="warning-card" v-if="resultData.top_result.contraindications?.length">
          <text class="card-title">⚠️ 不适宜人群</text>
          <view 
            v-for="(item, index) in resultData.top_result.contraindications" 
            :key="index"
            class="warning-item"
          >
            <view class="warning-header">
              <text :class="['severity-badge', getSeverityClass(item.severity)]">
                {{ item.severity }}
              </text>
              <text class="condition-type">{{ item.condition_type }}</text>
            </view>
            <text class="warning-reason">{{ item.reason }}</text>
            <text class="warning-suggestion" v-if="item.suggestion">建议：{{ item.suggestion }}</text>
          </view>
        </view>
      </view>

      <!-- 其他候选 -->
      <view class="alternatives" v-if="resultData.results?.length > 1">
        <text class="alt-title">其他可能：</text>
        <view class="alt-list">
          <text 
            v-for="(item, index) in resultData.results.slice(1, 4)" 
            :key="index"
            class="alt-item"
          >
            {{ item.name }} ({{ (item.confidence * 100).toFixed(0) }}%)
          </text>
        </view>
      </view>

      <!-- 模拟数据提示 -->
      <view class="mock-notice" v-if="resultData.is_mock">
        <text>📌 当前为测试数据，仅供开发调试</text>
      </view>
    </view>

    <!-- 底部操作 -->
    <view class="bottom-actions">
      <button class="action-btn secondary" @click="goToRecordAdd">
        记录到饮食
      </button>
      <button class="action-btn primary" @click="goBack">
        继续识别
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { API_BASE_URL } from '@/config.js'
import { request } from '@/utils/http'

const API_BASE = API_BASE_URL

const imageUrl = ref('')
const resultData = ref<any>(null)
const calorieResult = ref<any>(null)

const portions = ['小份', '中份', '大份']
const cookingMethods = ['清蒸', '水煮', '少油炒', '红烧', '油炸']
const selectedPortion = ref('中份')
const selectedCooking = ref('少油炒')

// 餐具估算（用于 AI 生成数据）
const dishSizes = [
  { name: '一小碗', weight: 150 },
  { name: '一碗', weight: 250 },
  { name: '一盘', weight: 300 },
  { name: '一大盘', weight: 450 },
]
const selectedDish = ref('一碗')
const dishCalories = ref<number | null>(null)

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.$page?.options || currentPage.options || {}
  
  if (options.data) {
    try {
      resultData.value = JSON.parse(decodeURIComponent(options.data))
      // 自动计算初始卡路里
      if (resultData.value?.top_result?.name) {
        if (resultData.value.top_result.found_in_database) {
          // 本地数据库有数据，使用份量计算
          calculateCalories()
        } else if (resultData.value.top_result.nutrition) {
          // AI生成数据，使用餐具估算
          calculateByDish()
        }
        
        // 自动保存到历史记录（已登录时，且不是从历史页跳转过来的）
        if (options.from !== 'history') {
          saveToHistory()
        }
      }
    } catch (e) {
      console.error('解析数据失败', e)
    }
  }
  
  if (options.image) {
    imageUrl.value = decodeURIComponent(options.image)
  }
})

// 保存到历史记录
const saveToHistory = () => {
  const token = uni.getStorageSync('token')
  if (!token || !resultData.value?.top_result) return
  
  const topResult = resultData.value.top_result
  const calories = topResult.nutrition?.calories || parseInt(topResult.baidu_calorie) || 0
  
  // 保存完整识别结果 JSON
  const resultJson = JSON.stringify(resultData.value)
  
  request({
    url: `${API_BASE}/api/v1/history`,
    method: 'POST',
    header: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    data: {
      recognized_food: topResult.name,
      confidence: topResult.confidence,
      selected_portion: selectedPortion.value,
      selected_cooking: selectedCooking.value,
      final_calories_min: Math.round(calories * 0.8),
      final_calories_max: Math.round(calories * 1.2),
      result_data: resultJson,
    },
    silentAuth: true
  }).then((res: any) => {
    if (res.statusCode === 401) return
    console.log('✅ 历史记录已保存', res.data)
  }).catch((err) => {
    console.log('⚠️ 保存历史记录失败', err)
  })
}

const calculateCalories = () => {
  if (!resultData.value?.top_result?.name) return
  
  uni.request({
    url: `${API_BASE}/api/v1/calculate/calories`,
    method: 'POST',
    header: {
      'Content-Type': 'application/json'
    },
    data: {
      food_name: resultData.value.top_result.name,
      portion: selectedPortion.value,
      cooking_method: selectedCooking.value
    },
    success: (res: any) => {
      if (res.data.code === 0) {
        calorieResult.value = res.data.data
      }
    }
  })
}

// 餐具估算计算
const calculateByDish = () => {
  const dish = dishSizes.find(d => d.name === selectedDish.value)
  const calories = resultData.value?.top_result?.nutrition?.calories
  if (dish && calories) {
    dishCalories.value = Math.round((dish.weight / 100) * calories)
  }
}

const getSelectedDishWeight = () => {
  const dish = dishSizes.find(d => d.name === selectedDish.value)
  return dish?.weight || 0
}

const getRatingClass = (rating: string) => {
  switch (rating) {
    case '推荐': return 'rating-good'
    case '适量': return 'rating-normal'
    case '少食': return 'rating-warning'
    default: return ''
  }
}

const getSeverityClass = (severity: string) => {
  switch (severity) {
    case '禁食': return 'severity-danger'
    case '慎食': return 'severity-warning'
    case '少食': return 'severity-caution'
    default: return ''
  }
}

// GI 值分类
const getGIClass = (gi: number) => {
  if (gi <= 55) return 'gi-low'
  if (gi <= 70) return 'gi-medium'
  return 'gi-high'
}

const getGILevel = (gi: number) => {
  if (gi <= 55) return '(低GI)'
  if (gi <= 70) return '(中GI)'
  return '(高GI)'
}

const goBack = () => {
  uni.navigateBack()
}

const getSourceLabel = (item: any) => {
  if (item.found_in_database) return '数据库'
  if (item.ai_generated) return 'AI估算'
  if (item.baidu_calorie) return '百度热量'
  return '未知来源'
}

const goToRecordAdd = () => {
  const name = resultData.value?.top_result?.name
  const keyword = name ? encodeURIComponent(name) : ''
  const date = new Date().toISOString().split('T')[0]
  const params = []
  if (keyword) params.push(`keyword=${keyword}`)
  params.push(`date=${date}`)
  const query = params.length ? `?${params.join('&')}` : ''
  uni.navigateTo({ url: `/pages/record/add${query}` })
}
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #F5F5F5;
  padding-bottom: 160rpx;
}

.image-section {
  width: 100%;
  height: 400rpx;
  background: #E8F5E9;
  
  &.placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.food-image {
  width: 100%;
  height: 100%;
}

.placeholder-icon {
  font-size: 120rpx;
}

.result-section {
  padding: 30rpx;
}

.main-result {
  background: #fff;
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.badge-group {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.source-badge {
  padding: 6rpx 16rpx;
  background: #F1F5F9;
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #64748B;
}

.food-name {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
}

.confidence-badge {
  padding: 8rpx 20rpx;
  background: #E8F5E9;
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #4CAF50;
}

.rating-row {
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}

.rating-label {
  font-size: 28rpx;
  color: #666;
}

.rating-value {
  font-size: 28rpx;
  font-weight: 500;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  margin-left: 12rpx;
  
  &.rating-good {
    background: #E8F5E9;
    color: #4CAF50;
  }
  &.rating-normal {
    background: #FFF3E0;
    color: #FF9800;
  }
  &.rating-warning {
    background: #FFEBEE;
    color: #F44336;
  }
}

.card-title {
  display: block;
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
  margin-bottom: 20rpx;
}

.nutrition-card, .calorie-card, .tips-card, .warning-card, .baidu-calorie-card {
  background: #FAFAFA;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-top: 24rpx;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.ai-badge {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 20rpx;
}

.gi-row {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #E0E0E0;
  display: flex;
  align-items: center;
}

.gi-label {
  font-size: 26rpx;
  color: #666;
}

.gi-value {
  font-size: 28rpx;
  font-weight: 500;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  margin-left: 8rpx;
  
  &.gi-low {
    background: #E8F5E9;
    color: #4CAF50;
  }
  &.gi-medium {
    background: #FFF3E0;
    color: #FF9800;
  }
  &.gi-high {
    background: #FFEBEE;
    color: #F44336;
  }
}

.gi-level {
  font-size: 22rpx;
  margin-left: 8rpx;
}

.baidu-calorie-card {
  background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
  text-align: center;
}

.baidu-calorie-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin: 20rpx 0;
}

.baidu-calorie-value {
  font-size: 56rpx;
  font-weight: bold;
  color: #1976D2;
}

.baidu-calorie-unit {
  font-size: 26rpx;
  color: #1976D2;
  margin-left: 12rpx;
}

.baidu-calorie-note {
  font-size: 22rpx;
  color: #64B5F6;
}

.nutrition-grid {
  display: flex;
  justify-content: space-between;
}

.nutrition-item {
  text-align: center;
}

.nutrition-value {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #4CAF50;
}

.nutrition-label {
  display: block;
  font-size: 22rpx;
  color: #999;
  margin-top: 8rpx;
}

.selector-group {
  margin-bottom: 20rpx;
}

.selector-label {
  display: block;
  font-size: 26rpx;
  color: #666;
  margin-bottom: 12rpx;
}

.selector-options {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
  
  &.cooking {
    .option-btn {
      font-size: 24rpx;
      padding: 12rpx 20rpx;
    }
  }
}

.option-btn {
  padding: 16rpx 28rpx;
  background: #fff;
  border: 2rpx solid #E0E0E0;
  border-radius: 12rpx;
  font-size: 26rpx;
  color: #666;
  
  &.active {
    background: #4CAF50;
    border-color: #4CAF50;
    color: #fff;
  }
}

.calorie-result {
  margin-top: 24rpx;
  padding: 24rpx;
  background: linear-gradient(135deg, #FF9800 0%, #FFB74D 100%);
  border-radius: 16rpx;
  text-align: center;
}

.calorie-value {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
}

.calorie-note {
  display: block;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 12rpx;
}

.tips-content {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
}

.warning-item {
  padding: 20rpx;
  background: #fff;
  border-radius: 12rpx;
  margin-bottom: 16rpx;
  border-left: 6rpx solid #FF9800;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.warning-header {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.severity-badge {
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
  font-weight: 500;
  margin-right: 12rpx;
  
  &.severity-danger {
    background: #FFEBEE;
    color: #F44336;
  }
  &.severity-warning {
    background: #FFF3E0;
    color: #FF9800;
  }
  &.severity-caution {
    background: #FFF8E1;
    color: #FFC107;
  }
}

.condition-type {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
}

.warning-reason {
  display: block;
  font-size: 26rpx;
  color: #666;
  margin-bottom: 8rpx;
}

.warning-suggestion {
  display: block;
  font-size: 24rpx;
  color: #4CAF50;
}

.alternatives {
  padding: 20rpx;
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 24rpx;
}

.alt-title {
  font-size: 26rpx;
  color: #999;
}

.alt-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 12rpx;
}

.alt-item {
  padding: 8rpx 20rpx;
  background: #F5F5F5;
  border-radius: 20rpx;
  font-size: 24rpx;
  color: #666;
}

.mock-notice {
  padding: 20rpx;
  background: #FFF3E0;
  border-radius: 12rpx;
  text-align: center;
  font-size: 24rpx;
  color: #FF9800;
}

.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.action-btn {
  width: 100%;
  padding: 28rpx;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 500;
  
  &.secondary {
    background: #fff;
    color: #4CAF50;
    border: 2rpx solid #4CAF50;
    margin-bottom: 16rpx;
  }

  &.primary {
    background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
    color: #fff;
  }
}
</style>
