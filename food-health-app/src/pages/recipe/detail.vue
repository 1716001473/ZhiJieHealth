<template>
  <view class="container">
    <!-- Banner Image -->
    <view class="banner">
      <image 
        class="banner-img" 
        :src="getImageUrl(recipe.image_url)" 
        mode="aspectFill" 
      />
      <view class="banner-overlay"></view>
      
      <!-- Back Button -->
      <view class="back-btn" @click="goBack">
        <text class="back-icon">←</text>
      </view>
      
      <!-- Favorite Button -->
      <view class="favorite-btn" @click="toggleFavorite">
        <text class="favorite-icon">{{ isFavorited ? '❤️' : '🤍' }}</text>
      </view>
    </view>

    <!-- Content -->
    <view class="content">
      <!-- Title Section -->
      <view class="title-section">
        <text class="recipe-name">{{ recipe.name }}</text>
        <text class="recipe-desc">{{ recipe.description }}</text>
        
        <!-- Tags & Meta -->
        <view class="meta-row">
          <view class="tags-wrapper">
            <text class="tag" v-for="tag in parseTags(recipe.tags)" :key="tag">{{ tag }}</text>
          </view>
          <view class="meta-info">
            <text class="difficulty">{{ recipe.difficulty }}</text>
            <text class="cook-time">⏱ {{ recipe.cook_time }}</text>
          </view>
        </view>
      </view>

      <!-- Nutrition Section -->
      <view class="nutrition-section">
        <view class="nutrition-grid">
          <view class="nutrition-item">
            <text class="nutrition-value">{{ recipe.calories || 0 }}</text>
            <text class="nutrition-label">kcal</text>
          </view>
          <view class="nutrition-item">
            <text class="nutrition-value">{{ recipe.protein || 0 }}g</text>
            <text class="nutrition-label">蛋白质</text>
          </view>
          <view class="nutrition-item">
            <text class="nutrition-value">{{ recipe.fat || 0 }}g</text>
            <text class="nutrition-label">脂肪</text>
          </view>
          <view class="nutrition-item">
            <text class="nutrition-value">{{ recipe.carbs || 0 }}g</text>
            <text class="nutrition-label">碳水</text>
          </view>
        </view>
      </view>

      <!-- Ingredients Section -->
      <view class="section">
        <view class="section-header">
          <text class="section-icon">📋</text>
          <text class="section-title">食材清单</text>
          <text class="servings">（{{ recipe.servings || 2 }}人份）</text>
        </view>
        <view class="ingredients-list">
          <view 
            class="ingredient-item" 
            v-for="(ing, idx) in parseIngredients(recipe.ingredients)" 
            :key="idx"
          >
            <text class="ingredient-name">{{ ing.name }}</text>
            <text class="ingredient-amount">{{ ing.amount }}</text>
          </view>
        </view>
      </view>

      <!-- Steps Section -->
      <view class="section">
        <view class="section-header">
          <text class="section-icon">👨‍🍳</text>
          <text class="section-title">烹饪步骤</text>
        </view>
        <view class="steps-list">
          <view 
            class="step-item" 
            v-for="(step, idx) in parseSteps(recipe.steps)" 
            :key="idx"
          >
            <view class="step-number">{{ idx + 1 }}</view>
            <view class="step-content">
              <text class="step-text">{{ step.content || step.text }}</text>
              <image 
                v-if="step.image_url" 
                class="step-img" 
                :src="getImageUrl(step.image_url)" 
                mode="aspectFill" 
              />
            </view>
          </view>
        </view>
      </view>

      <!-- Tips Section -->
      <view class="section" v-if="recipe.tips">
        <view class="section-header">
          <text class="section-icon">💡</text>
          <text class="section-title">烹饪小贴士</text>
        </view>
        <view class="tips-content">
          <text class="tips-text">{{ recipe.tips }}</text>
        </view>
      </view>

      <!-- Suitable For Section -->
      <view class="section" v-if="recipe.suitable_for || recipe.not_suitable_for">
        <view class="section-header">
          <text class="section-icon">👥</text>
          <text class="section-title">适宜人群</text>
        </view>
        <view class="suitable-content" v-if="recipe.suitable_for">
          <text class="suitable-label">✅ 适合：</text>
          <text class="suitable-text">{{ recipe.suitable_for }}</text>
        </view>
        <view class="suitable-content not-suitable" v-if="recipe.not_suitable_for">
          <text class="suitable-label">⚠️ 不适合：</text>
          <text class="suitable-text">{{ recipe.not_suitable_for }}</text>
        </view>
      </view>
    </view>

    <!-- Loading Mask -->
    <view class="loading-mask" v-if="loading">
      <view class="loading-spinner"></view>
      <text class="loading-text">加载中...</text>
    </view>

    <!-- 底部操作栏 -->
    <view class="bottom-bar" v-if="!loading && recipe.name">
      <button class="add-meal-btn" @click="showAddMealPopup">
        🍽️ 添加到今日饮食
      </button>
    </view>

    <!-- 添加饮食弹窗 -->
    <view class="popup-mask" v-if="showMealPopup" @click="showMealPopup = false">
      <view class="popup-content" @click.stop>
        <view class="popup-header">
          <text class="popup-title">添加到饮食记录</text>
          <text class="popup-close" @click="showMealPopup = false">×</text>
        </view>
        <text class="popup-recipe-name">{{ recipe.name }}</text>

        <!-- 餐次选择 -->
        <view class="meal-type-section">
          <text class="popup-label">选择餐次</text>
          <view class="meal-type-options">
            <view
              class="meal-type-item"
              v-for="mt in mealTypes"
              :key="mt.value"
              :class="{ active: selectedMealType === mt.value }"
              @click="selectedMealType = mt.value"
            >
              <text class="mt-icon">{{ mt.icon }}</text>
              <text class="mt-label">{{ mt.label }}</text>
            </view>
          </view>
        </view>

        <!-- 数量选择（统一智能单位模式） -->
        <view class="quantity-section">
          <view class="quantity-header">
            <text class="popup-label">数量</text>
            <text class="unit-switch" @click="toggleInputMode">{{ useGramMode ? '切换为智能单位' : '切换为克数输入' }}</text>
          </view>

          <!-- 智能单位模式 -->
          <view class="quantity-row" v-if="!useGramMode">
            <view class="quantity-control">
              <view class="quantity-btn" @click="changeQuantity(-1)"><text>−</text></view>
              <text class="quantity-value">{{ popupQuantity }}</text>
              <text class="quantity-unit">{{ popupUnitLabel }}</text>
              <view class="quantity-btn" @click="changeQuantity(1)"><text>+</text></view>
            </view>
            <text class="quantity-weight">≈ {{ popupTotalWeight }}g</text>
          </view>

          <!-- 克数输入模式 -->
          <view class="gram-row" v-else>
            <input class="gram-input" type="number" v-model="popupGrams" placeholder="100" />
            <text class="gram-label">克</text>
          </view>
        </view>

        <!-- 热量预览 -->
        <view class="calorie-preview">
          <text class="calorie-preview-text">约 {{ popupCalories }} 千卡</text>
        </view>

        <!-- 确认按钮 -->
        <button class="popup-confirm-btn" @click="confirmAddMeal" :loading="submitting">
          确认添加
        </button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { API_BASE_URL } from '@/config.js'
import defaultImg from '@/static/logo.png'

const recipe = ref<any>({})
const loading = ref(true)
const isFavorited = ref(false)
const recipeId = ref<number>(0)

onMounted(() => {
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1] as any
  const options = currentPage.options || currentPage.$page?.options || {}
  
  recipeId.value = parseInt(options.id) || 0
  if (recipeId.value) {
    loadRecipeDetail()
  }
})

const loadRecipeDetail = async () => {
  loading.value = true
  try {
    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/premium/recipes/${recipeId.value}`,
      method: 'GET'
    })

    const data = res.data as any
    if (data.code === 0 && data.data) {
      recipe.value = data.data
      // 加载收藏状态
      loadFavoriteStatus()
    } else {
      uni.showToast({ title: '食谱不存在', icon: 'none' })
      setTimeout(() => goBack(), 1500)
    }
  } catch (e) {
    console.error('加载详情失败', e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  } finally {
    loading.value = false
  }
}

const loadFavoriteStatus = async () => {
  const token = uni.getStorageSync('token')
  if (!token) return
  try {
    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/favorites/${recipeId.value}/status`,
      method: 'GET',
      header: { Authorization: `Bearer ${token}` },
    })
    const data = res.data as any
    if (data.code === 0 && data.data) {
      isFavorited.value = data.data.is_favorited
    }
  } catch (e) {
    // 未登录或查询失败，保持默认 false
  }
}

const toggleFavorite = async () => {
  const token = uni.getStorageSync('token')
  if (!token) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    return
  }
  try {
    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/favorites/${recipeId.value}`,
      method: 'POST',
      header: { Authorization: `Bearer ${token}` },
    })
    const data = res.data as any
    if (data.code === 0 && data.data) {
      isFavorited.value = data.data.is_favorited
      uni.showToast({
        title: isFavorited.value ? '收藏成功' : '取消收藏',
        icon: 'success'
      })
    }
  } catch (e) {
    console.error('收藏操作失败', e)
    uni.showToast({ title: '操作失败', icon: 'none' })
  }
}

const getImageUrl = (url: string | null) => {
  if (!url) return defaultImg
  if (url.startsWith('http')) return url
  return `${API_BASE_URL}${url}`
}

const parseTags = (tags: any): string[] => {
  if (!tags) return []
  if (Array.isArray(tags)) return tags
  try {
    if (typeof tags === 'string' && tags.startsWith('[')) {
      return JSON.parse(tags)
    }
    if (typeof tags === 'string') {
      return tags.split(',').map(t => t.trim()).filter(Boolean)
    }
    return []
  } catch {
    return []
  }
}

const parseIngredients = (ingredients: any): any[] => {
  if (!ingredients) return []
  if (Array.isArray(ingredients)) return ingredients
  try {
    if (typeof ingredients === 'string' && ingredients.startsWith('[')) {
      return JSON.parse(ingredients)
    }
    return []
  } catch {
    return []
  }
}

const parseSteps = (steps: any): any[] => {
  if (!steps) return []
  if (Array.isArray(steps)) return steps
  try {
    if (typeof steps === 'string' && steps.startsWith('[')) {
      return JSON.parse(steps)
    }
    return []
  } catch {
    return []
  }
}

const goBack = () => {
  uni.navigateBack()
}

// ========== 添加到饮食记录 ==========
const showMealPopup = ref(false)
const selectedMealType = ref('lunch')
const submitting = ref(false)

// 智能单位相关状态
const popupQuantity = ref(1)
const popupUnitLabel = ref('份')
const popupUnitWeight = ref(100)
const useGramMode = ref(false)
const popupGrams = ref('100')

const mealTypes = [
  { value: 'breakfast', label: '早餐', icon: '🌅' },
  { value: 'lunch', label: '午餐', icon: '☀️' },
  { value: 'dinner', label: '晚餐', icon: '🌙' },
  { value: 'snack', label: '加餐', icon: '🍪' },
]

// 食谱名称关键词 -> 智能单位推断
const RECIPE_UNIT_MAP: Record<string, [string, number]> = {
  '米饭': ['碗', 200], '面条': ['碗', 250], '粥': ['碗', 300],
  '汤': ['碗', 300], '羚': ['碗', 300],
  '馒头': ['个', 100], '包子': ['个', 100], '饺子': ['个', 20],
  '饼': ['张', 80], '粽子': ['个', 150],
  '沙拉': ['份', 200], '三明治': ['个', 150],
  '牛排': ['块', 200], '鸡胸': ['块', 150],
  '蛋': ['个', 60], '鸡蛋': ['个', 60],
  '牛奶': ['杯', 250], '豆浆': ['杯', 250], '果汁': ['杯', 250],
}

const inferRecipeUnit = (foodName: string): [string, number] => {
  for (const [keyword, unitInfo] of Object.entries(RECIPE_UNIT_MAP)) {
    if (foodName.includes(keyword)) return unitInfo
  }
  return ['份', 100]
}

// 计算属性
const popupTotalWeight = computed(() => {
  if (useGramMode.value) return Number(popupGrams.value) || 0
  return Math.round(popupQuantity.value * popupUnitWeight.value)
})

const popupCalories = computed(() => {
  const cal = recipe.value.calories || 0
  return ((cal * popupTotalWeight.value) / 100).toFixed(0)
})

const showAddMealPopup = () => {
  const token = uni.getStorageSync('token')
  if (!token) {
    uni.showToast({ title: '请先登录', icon: 'none' })
    return
  }
  // 根据当前时间自动推荐餐次
  const hour = new Date().getHours()
  if (hour < 10) selectedMealType.value = 'breakfast'
  else if (hour < 14) selectedMealType.value = 'lunch'
  else if (hour < 20) selectedMealType.value = 'dinner'
  else selectedMealType.value = 'snack'

  // 推断智能单位
  const foodName = recipe.value.name || ''
  const [unit, weight] = inferRecipeUnit(foodName)
  popupUnitLabel.value = unit
  popupUnitWeight.value = weight
  popupQuantity.value = 1
  popupGrams.value = String(weight)
  useGramMode.value = false
  showMealPopup.value = true
}

const changeQuantity = (delta: number) => {
  const next = popupQuantity.value + delta
  if (next >= 1 && next <= 20) popupQuantity.value = next
}

const toggleInputMode = () => {
  useGramMode.value = !useGramMode.value
  if (useGramMode.value) {
    popupGrams.value = String(popupTotalWeight.value)
  } else {
    popupQuantity.value = Math.max(1, Math.round(Number(popupGrams.value) / popupUnitWeight.value))
  }
}

const confirmAddMeal = async () => {
  submitting.value = true
  try {
    const token = uni.getStorageSync('token')
    const today = new Date().toISOString().split('T')[0]

    const payload = {
      meal_date: today,
      meal_type: selectedMealType.value,
      food_name: recipe.value.name,
      unit_weight: popupTotalWeight.value,
      image_url: recipe.value.image_url || null,
      data_source: 'user_custom',
      per_100g_calories: recipe.value.calories || 0,
      per_100g_protein: recipe.value.protein || 0,
      per_100g_fat: recipe.value.fat || 0,
      per_100g_carb: recipe.value.carbs || 0,
    }

    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/meal/record`,
      method: 'POST',
      header: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      data: payload,
    })

    const data = res.data as any
    if (data.code === 0) {
      showMealPopup.value = false
      uni.showToast({ title: '添加成功', icon: 'success' })
      uni.$emit('meal-record-updated')
      setTimeout(() => {
        uni.reLaunch({ url: '/pages/record/index' })
      }, 1000)
    } else {
      uni.showToast({ title: data.message || '添加失败', icon: 'none' })
    }
  } catch (e) {
    console.error('添加饮食记录失败', e)
    uni.showToast({ title: '添加失败', icon: 'none' })
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #F8F9FA;
  padding-bottom: 140rpx;
}

/* Banner */
.banner {
  position: relative;
  height: 500rpx;
}

.banner-img {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
}

.banner-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 200rpx;
  background: linear-gradient(transparent, rgba(0,0,0,0.3));
}

.back-btn {
  position: absolute;
  top: 80rpx;
  left: 30rpx;
  width: 72rpx;
  height: 72rpx;
  background: rgba(255,255,255,0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.15);
}

.back-icon {
  font-size: 36rpx;
  color: #333;
}

.favorite-btn {
  position: absolute;
  top: 80rpx;
  right: 30rpx;
  width: 72rpx;
  height: 72rpx;
  background: rgba(255,255,255,0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.15);
}

.favorite-icon {
  font-size: 36rpx;
}

/* Content */
.content {
  margin-top: -60rpx;
  position: relative;
  z-index: 10;
  background: #fff;
  border-radius: 40rpx 40rpx 0 0;
  padding: 40rpx 30rpx;
}

/* Title Section */
.title-section {
  margin-bottom: 30rpx;
}

.recipe-name {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 16rpx;
  display: block;
}

.recipe-desc {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  margin-bottom: 20rpx;
  display: block;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tags-wrapper {
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.tag {
  font-size: 22rpx;
  color: #4CAF50;
  background: #E8F5E9;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}

.meta-info {
  display: flex;
  gap: 20rpx;
  font-size: 24rpx;
  color: #999;
}

.difficulty {
  color: #FF9800;
}

/* Nutrition Section */
.nutrition-section {
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
  border-radius: 24rpx;
  padding: 30rpx;
  margin-bottom: 30rpx;
}

.nutrition-grid {
  display: flex;
  justify-content: space-around;
}

.nutrition-item {
  text-align: center;
}

.nutrition-value {
  font-size: 36rpx;
  font-weight: bold;
  color: #2E7D32;
  display: block;
}

.nutrition-label {
  font-size: 24rpx;
  color: #4CAF50;
  margin-top: 8rpx;
  display: block;
}

/* Section */
.section {
  margin-bottom: 40rpx;
}

.section-header {
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}

.section-icon {
  font-size: 36rpx;
  margin-right: 12rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.servings {
  font-size: 24rpx;
  color: #999;
  margin-left: 8rpx;
}

/* Ingredients */
.ingredients-list {
  background: #FAFAFA;
  border-radius: 20rpx;
  padding: 20rpx;
}

.ingredient-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #EEE;
  
  &:last-child {
    border-bottom: none;
  }
}

.ingredient-name {
  font-size: 28rpx;
  color: #333;
}

.ingredient-amount {
  font-size: 28rpx;
  color: #4CAF50;
  font-weight: 500;
}

/* Steps */
.steps-list {
  padding-left: 10rpx;
}

.step-item {
  display: flex;
  margin-bottom: 30rpx;
}

.step-number {
  width: 56rpx;
  height: 56rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28rpx;
  font-weight: bold;
  flex-shrink: 0;
  margin-right: 20rpx;
}

.step-content {
  flex: 1;
}

.step-text {
  font-size: 28rpx;
  color: #333;
  line-height: 1.7;
  display: block;
}

.step-img {
  width: 100%;
  height: 300rpx;
  border-radius: 16rpx;
  margin-top: 16rpx;
  background: #EEE;
}

/* Tips */
.tips-content {
  background: #FFF8E1;
  border-radius: 16rpx;
  padding: 24rpx;
  border-left: 6rpx solid #FFB300;
}

.tips-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.7;
}

/* Suitable */
.suitable-content {
  padding: 16rpx 0;
  display: flex;
  align-items: flex-start;
}

.suitable-label {
  font-size: 26rpx;
  font-weight: 500;
  color: #4CAF50;
  margin-right: 8rpx;
}

.suitable-text {
  font-size: 26rpx;
  color: #666;
  flex: 1;
}

.not-suitable .suitable-label {
  color: #FF9800;
}

/* Loading */
.loading-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255,255,255,0.95);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 6rpx solid #E8F5E9;
  border-top-color: #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  margin-top: 20rpx;
  font-size: 28rpx;
  color: #666;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 底部操作栏 */
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: #fff;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.08);
  z-index: 100;
}

.add-meal-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border-radius: 44rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 弹窗遮罩 */
.popup-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.popup-content {
  width: 100%;
  background: #fff;
  border-radius: 40rpx 40rpx 0 0;
  padding: 40rpx 30rpx;
  padding-bottom: calc(40rpx + env(safe-area-inset-bottom));
}

.popup-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  display: block;
  text-align: center;
  margin-bottom: 8rpx;
}

.popup-recipe-name {
  font-size: 26rpx;
  color: #999;
  display: block;
  text-align: center;
  margin-bottom: 36rpx;
}

.popup-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 20rpx;
}

/* 餐次选择 */
.meal-type-section {
  margin-bottom: 36rpx;
}

.meal-type-options {
  display: flex;
  gap: 16rpx;
}

.meal-type-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0;
  border-radius: 20rpx;
  background: #F5F5F5;
  border: 3rpx solid transparent;
  transition: all 0.2s;

  &.active {
    background: #E8F5E9;
    border-color: #4CAF50;
  }
}

.mt-icon {
  font-size: 40rpx;
  margin-bottom: 8rpx;
}

.mt-label {
  font-size: 24rpx;
  color: #666;
}

.meal-type-item.active .mt-label {
  color: #2E7D32;
  font-weight: 600;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.popup-close {
  font-size: 44rpx;
  color: #999;
  padding: 0 8rpx;
  line-height: 1;
}

/* 数量选择（统一智能单位模式） */
.quantity-section {
  margin-bottom: 24rpx;
}

.quantity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.unit-switch {
  font-size: 24rpx;
  color: #4CAF50;
}

.quantity-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.quantity-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #F0F0F0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  color: #333;

  &:active {
    background: #E0E0E0;
  }
}

.quantity-value {
  font-size: 44rpx;
  font-weight: bold;
  color: #333;
  min-width: 40rpx;
  text-align: center;
}

.quantity-unit {
  font-size: 28rpx;
  color: #666;
}

.quantity-weight {
  font-size: 26rpx;
  color: #999;
}

.gram-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.gram-input {
  flex: 1;
  background: #f9f9f9;
  padding: 20rpx;
  border-radius: 12rpx;
  font-size: 32rpx;
}

.gram-label {
  font-size: 28rpx;
  color: #666;
}

.calorie-preview {
  text-align: right;
  margin-bottom: 24rpx;
}

.calorie-preview-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #4CAF50;
}

/* 确认按钮 */
.popup-confirm-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border-radius: 44rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 8rpx;
}
</style>
