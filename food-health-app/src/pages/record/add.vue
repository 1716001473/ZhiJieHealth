<template>
  <view class="container">
    <!-- 搜索栏 -->
    <view class="search-bar">
      <input 
        class="search-input" 
        placeholder="搜索食物（如：米饭、苹果）" 
        v-model="keyword"
        @confirm="doSearch" 
      />
      <text class="search-btn" @click="doSearch">搜索</text>
    </view>

    <view class="batch-panel" v-if="selectedItems.length">
      <view class="batch-header">
        <text class="batch-title">待添加清单</text>
        <text class="batch-clear" @click="clearBatch">清空</text>
      </view>
      <view class="batch-meal-types">
        <text class="batch-label">餐次</text>
        <view class="tags">
          <text 
            v-for="type in mealTypes" 
            :key="type.key"
            class="tag"
            :class="{ active: currentMealType === type.key }"
            @click="currentMealType = type.key"
          >{{ type.name }}</text>
        </view>
      </view>
      <view class="batch-item" v-for="item in selectedItems" :key="item.key">
        <view class="batch-main">
          <text class="batch-name">{{ item.name }}</text>
          <text class="batch-sub">{{ item.quantity }} {{ item.unitLabel }} ≈ {{ item.totalWeight }}g</text>
        </view>
        <text class="batch-remove" @click="removeBatchItem(item.key)">×</text>
      </view>
      <button class="batch-btn" @click="confirmBatchAdd">批量添加</button>
    </view>
    
    <!-- 搜索结果 -->
    <scroll-view scroll-y class="result-list">
      <view class="food-item" v-for="item in searchResults" :key="item.id" @click="selectFood(item)">
        <!-- 食物图片 -->
        <image
          v-if="item.image_url"
          class="food-image"
          :src="item.image_url"
          mode="aspectFill"
        />
        <view v-else class="food-image-placeholder">🍽️</view>

        <view class="left">
          <view class="name-row">
            <text class="name">{{ item.name }}</text>
            <text class="source-badge" :class="getSourceClass(item)">{{ getSourceLabel(item) }}</text>
          </view>
          <text class="info">{{ getFoodCalories(item) }}千卡/100g</text>
        </view>
        <view class="add-icon">+</view>
      </view>
      
      <view v-if="hasSearched && searchResults.length === 0" class="empty">
        <text>未找到相关食物，试试其他关键词</text>
      </view>
    </scroll-view>
    
    <!-- 统一添加弹窗 -->
    <view class="popup" v-if="selectedFood">
      <view class="popup-mask" @click="selectedFood = null"></view>
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">添加到饮食记录</text>
          <text class="close" @click="selectedFood = null">×</text>
        </view>
        <text class="popup-food-name">{{ selectedFood.name }}</text>

        <!-- 餐次选择 -->
        <view class="meal-type-section">
          <text class="popup-label">选择餐次</text>
          <view class="meal-type-options">
            <view
              v-for="type in mealTypesWithIcon" :key="type.key"
              class="meal-type-item"
              :class="{ active: currentMealType === type.key }"
              @click="currentMealType = type.key"
            >
              <text class="mt-icon">{{ type.icon }}</text>
              <text class="mt-label">{{ type.name }}</text>
            </view>
          </view>
        </view>

        <!-- 数量选择 -->
        <view class="quantity-section">
          <view class="quantity-header">
            <text class="popup-label">数量</text>
            <text class="unit-switch" @click="toggleInputMode">
              {{ useGramMode ? '切换为智能单位' : '切换为克数输入' }}
            </text>
          </view>

          <!-- 智能单位模式 -->
          <view class="quantity-row" v-if="!useGramMode">
            <view class="quantity-control">
              <view class="quantity-btn" @click="changeQuantity(-1)"><text>−</text></view>
              <text class="quantity-value">{{ quantity }}</text>
              <text class="quantity-unit">{{ unitLabel }}</text>
              <view class="quantity-btn" @click="changeQuantity(1)"><text>+</text></view>
            </view>
            <text class="quantity-weight">≈ {{ totalWeight }}g</text>
          </view>

          <!-- 克数输入模式 -->
          <view class="gram-row" v-else>
            <input class="gram-input" type="number" v-model="weight" placeholder="100" />
            <text class="gram-label">克</text>
          </view>
        </view>

        <!-- 热量预览 -->
        <view class="calorie-preview">
          <text class="calorie-text">约 {{ calculatedCalories }} 千卡</text>
        </view>

        <view class="popup-actions">
          <button class="confirm-btn ghost" @click="addToBatch">加入清单</button>
          <button class="confirm-btn" @click="confirmAdd">立即添加</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { API_BASE_URL } from '@/config.js';

export default {
  data() {
    return {
      keyword: '',
      searchResults: [],
      hasSearched: false,
      
      // url params
      targetDate: '',
      initialType: '',
      
      // popup
      selectedFood: null,
      currentMealType: 'breakfast',
      
      // 智能单位
      quantity: 1,
      unitLabel: '份',
      unitWeight: 100,
      useGramMode: false,
      weight: 100,  // 克数模式下使用
      
      selectedItems: [],
      
      mealTypes: [
        { key: 'breakfast', name: '早餐' },
        { key: 'lunch', name: '午餐' },
        { key: 'dinner', name: '晚餐' },
        { key: 'snack', name: '加餐' }
      ],
      mealTypesWithIcon: [
        { key: 'breakfast', name: '早餐', icon: '🌅' },
        { key: 'lunch', name: '午餐', icon: '☀️' },
        { key: 'dinner', name: '晚餐', icon: '🌙' },
        { key: 'snack', name: '加餐', icon: '🍪' }
      ]
    }
  },
  onLoad(options) {
    const today = new Date().toISOString().split('T')[0];
    this.targetDate = today;
    if (options.date) this.targetDate = options.date;
    if (options.type) {
      this.initialType = options.type;
      this.currentMealType = options.type;
    }
    // 根据时间自动选择餐次
    if (!options.type) {
      const hour = new Date().getHours();
      if (hour < 10) this.currentMealType = 'breakfast';
      else if (hour < 14) this.currentMealType = 'lunch';
      else if (hour < 20) this.currentMealType = 'dinner';
      else this.currentMealType = 'snack';
    }
    if (options.keyword) {
      this.keyword = decodeURIComponent(options.keyword);
      setTimeout(() => {
        this.doSearch();
      }, 0);
    }
  },
  computed: {
    totalWeight() {
      if (this.useGramMode) return Number(this.weight) || 0;
      return Math.round(this.quantity * this.unitWeight);
    },
    calculatedCalories() {
      if (!this.selectedFood) return 0;
      const calories = this.getFoodCalories(this.selectedFood);
      const w = this.totalWeight;
      return ((calories * w) / 100).toFixed(0);
    }
  },
  methods: {
    getFoodCalories(item) {
      if (!item || !item.nutrition) return 0;
      return Number(item.nutrition.calories) || 0;
    },
    getSourceLabel(item) {
      const source = item?.data_source || 'database';
      if (source === 'deepseek_ai') return 'AI估算';
      if (source === 'baidu_ai') return '百度热量';
      if (source === 'user_custom') return '自定义';
      if (source === 'openfoodfacts') return 'OFF数据库';
      return '数据库';
    },
    getSourceClass(item) {
      const source = item?.data_source || 'database';
      if (source === 'deepseek_ai') return 'source-ai';
      if (source === 'baidu_ai') return 'source-baidu';
      if (source === 'user_custom') return 'source-user';
      if (source === 'openfoodfacts') return 'source-off';
      return 'source-db';
    },
    toggleInputMode() {
      this.useGramMode = !this.useGramMode;
      if (this.useGramMode) {
        // 切换到克数模式时，用当前计算的总重量填入
        this.weight = this.totalWeight;
      } else {
        // 切换回智能单位时，根据克数重算数量
        this.quantity = Math.max(1, Math.round(Number(this.weight) / this.unitWeight));
      }
    },
    changeQuantity(delta) {
      const next = this.quantity + delta;
      if (next >= 1 && next <= 20) this.quantity = next;
    },
    buildMealPayload(item, weightGrams) {
      const base = {
        meal_date: this.targetDate,
        meal_type: item.meal_type || this.currentMealType,
        food_name: item.name,
        unit_weight: parseFloat(weightGrams),
        image_url: item.image_url || null
      };
      const dataSource = item.data_source || 'database';
      if (item.is_temp) {
        return {
          ...base,
          data_source: dataSource,
          per_100g_calories: this.getFoodCalories(item),
          per_100g_protein: Number(item.nutrition?.protein) || 0,
          per_100g_fat: Number(item.nutrition?.fat) || 0,
          per_100g_carb: Number(item.nutrition?.carbohydrate) || 0
        };
      }
      return {
        ...base,
        food_id: item.id,
        data_source: dataSource
      };
    },
    async doSearch() {
      if (!this.keyword) return;
      
      uni.showLoading({ title: '搜索中...' });
      try {
        const res = await uni.request({
          url: `${API_BASE_URL}/api/v1/food?keyword=${this.keyword}`,
          method: 'GET'
        });
        if (res.data.code === 0) {
          this.searchResults = res.data.data;
        }
        this.hasSearched = true;
      } finally {
        uni.hideLoading();
      }
    },
    selectFood(item) {
      this.selectedFood = item;
      this.useGramMode = false;
      // 使用后端返回的智能单位
      this.unitLabel = item.default_unit || '份';
      this.unitWeight = item.unit_weight || 100;
      this.quantity = 1;
      this.weight = this.unitWeight;
    },
    addToBatch() {
      if (!this.selectedFood) return;
      const key = `${this.selectedFood.name}-${this.selectedFood.id || 'temp'}`;
      const w = this.totalWeight;
      const exists = this.selectedItems.find(item => item.key === key);
      if (exists) {
        exists.quantity = this.quantity;
        exists.totalWeight = w;
        uni.showToast({ title: '已更新清单', icon: 'none' });
      } else {
        this.selectedItems.push({
          key,
          id: this.selectedFood.id,
          name: this.selectedFood.name,
          nutrition: this.selectedFood.nutrition,
          data_source: this.selectedFood.data_source,
          is_temp: this.selectedFood.is_temp,
          image_url: this.selectedFood.image_url,
          quantity: this.quantity,
          unitLabel: this.unitLabel,
          totalWeight: w,
          weight: w,
          meal_type: this.currentMealType
        });
        uni.showToast({ title: '已加入清单', icon: 'success' });
      }
      this.selectedFood = null;
    },
    clearBatch() {
      this.selectedItems = [];
    },
    removeBatchItem(key) {
      this.selectedItems = this.selectedItems.filter(item => item.key !== key);
    },
    async confirmBatchAdd() {
      if (!this.selectedItems.length) return;
      const items = this.selectedItems.map(item => this.buildMealPayload(item, item.totalWeight));
      uni.showLoading({ title: '批量提交中' });
      try {
        const res = await uni.request({
          url: `${API_BASE_URL}/api/v1/meal/records/batch`,
          method: 'POST',
          header: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${uni.getStorageSync('token')}`
          },
          data: { items }
        });
        if (res.data.code === 0) {
          uni.showToast({ title: '批量添加成功' });
          const firstType = items[0]?.meal_type || this.currentMealType;
          uni.setStorageSync('lastMealType', firstType);
          this.selectedItems = [];
          uni.$emit('meal-record-updated');
          setTimeout(() => {
            uni.navigateBack();
          }, 1000);
        } else {
          const errorMsg = this.parseErrorMessage(res.data, res.statusCode);
          uni.showToast({ title: errorMsg, icon: 'none', duration: 3000 });
        }
      } catch (e) {
        console.error('批量添加饮食记录失败:', e);
        uni.showToast({ title: '网络请求失败，请检查网络连接', icon: 'none' });
      } finally {
        uni.hideLoading();
      }
    },
    async confirmAdd() {
      const w = this.totalWeight;
      if (!w || w <= 0) {
        uni.showToast({ title: '请输入有效数量', icon: 'none' });
        return;
      }

      uni.showLoading({ title: '提交中' });
      try {
        const res = await uni.request({
          url: `${API_BASE_URL}/api/v1/meal/record`,
          method: 'POST',
          header: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${uni.getStorageSync('token')}`
          },
          data: this.buildMealPayload(this.selectedFood, w)
        });

        if (res.data.code === 0) {
          uni.showToast({ title: '添加成功' });
          const type = this.currentMealType;
          uni.setStorageSync('lastMealType', type);
          uni.$emit('meal-record-updated');
          setTimeout(() => {
            uni.navigateBack();
          }, 1000);
        } else {
          const errorMsg = this.parseErrorMessage(res.data, res.statusCode);
          uni.showToast({ title: errorMsg, icon: 'none', duration: 3000 });
        }
      } catch (e) {
        console.error('添加饮食记录失败:', e);
        uni.showToast({ title: '网络请求失败，请检查网络连接', icon: 'none' });
      } finally {
        uni.hideLoading();
      }
    },
    parseErrorMessage(data, statusCode) {
      if (statusCode === 422) {
        if (data.detail && Array.isArray(data.detail)) {
          const firstError = data.detail[0];
          const field = firstError.loc ? firstError.loc[firstError.loc.length - 1] : '未知字段';
          const fieldNames = {
            'meal_date': '日期',
            'meal_type': '餐次',
            'unit_weight': '重量',
            'food_name': '食物名称',
            'data_source': '数据来源',
            'per_100g_calories': '热量数据'
          };
          const fieldName = fieldNames[field] || field;
          return `${fieldName}格式错误`;
        }
        return '数据格式错误，请检查输入';
      }
      if (data.message) return data.message;
      if (data.detail) return typeof data.detail === 'string' ? data.detail : '请求处理失败';
      return '添加失败，请稍后重试';
    }
  }
}
</script>

<style>
.container {
  padding: 15px;
  background-color: #F8F8F8;
  min-height: 100vh;
}

.search-bar {
  display: flex;
  background-color: #fff;
  padding: 10px;
  border-radius: 8px;
  align-items: center;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  font-size: 14px;
}

.search-btn {
  color: #4CAF50;
  margin-left: 10px;
  font-weight: bold;
}

.result-list {
  height: calc(100vh - 100px);
}

.food-item {
  background-color: #fff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.food-image {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  flex-shrink: 0;
  background-color: #f5f5f5;
}

.food-image-placeholder {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  flex-shrink: 0;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.left {
  flex: 1;
  min-width: 0;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 5px;
}

.name {
  font-size: 16px;
  font-weight: bold;
}

.info {
  font-size: 12px;
  color: #888;
}

.source-badge {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  background: #f0f0f0;
  color: #666;
}

.source-ai { background: #EEF2FF; color: #4F46E5; }
.source-baidu { background: #FFF7ED; color: #EA580C; }
.source-user { background: #ECFDF3; color: #16A34A; }
.source-db { background: #F1F5F9; color: #64748B; }
.source-off { background: #FEF3C7; color: #D97706; }

.add-icon {
  font-size: 20px;
  color: #4CAF50;
  font-weight: bold;
}

.empty {
  text-align: center;
  color: #999;
  margin-top: 50px;
}

/* 清单面板 */
.batch-panel {
  background: #fff;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 15px;
}

.batch-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.batch-title { font-size: 14px; font-weight: bold; }
.batch-clear { font-size: 12px; color: #999; }

.batch-meal-types { margin-bottom: 10px; }
.batch-label { display: block; font-size: 12px; color: #666; margin-bottom: 6px; }

.batch-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
.batch-item:last-child { border-bottom: none; }

.batch-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.batch-name { font-size: 14px; font-weight: 500; }
.batch-sub { font-size: 12px; color: #999; }
.batch-remove { font-size: 18px; color: #ccc; padding: 0 8px; }

.batch-btn {
  margin-top: 10px;
  background-color: #4CAF50;
  color: #fff;
  border-radius: 20px;
}

/* 弹窗 */
.popup {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 999;
}

.popup-mask {
  width: 100%; height: 100%;
  background-color: rgba(0,0,0,0.5);
}

.popup-content {
  position: absolute;
  bottom: 0; left: 0; width: 100%;
  background-color: #fff;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  padding: 24px 20px;
  padding-bottom: calc(24px + env(safe-area-inset-bottom));
  box-sizing: border-box;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.popup-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.close {
  font-size: 22px;
  color: #999;
  padding: 4px 8px;
}

.popup-food-name {
  display: block;
  font-size: 14px;
  color: #999;
  margin-top: 4px;
  margin-bottom: 20px;
}

.popup-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 10px;
}

/* 餐次选择 */
.meal-type-section { margin-bottom: 20px; }

.meal-type-options {
  display: flex;
  gap: 10px;
}

.meal-type-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 0;
  background: #F5F5F5;
  border-radius: 10px;
  border: 1px solid transparent;
}

.meal-type-item.active {
  background: #E8F5E9;
  border-color: #4CAF50;
}

.mt-icon { font-size: 18px; }
.mt-label { font-size: 12px; color: #666; }
.meal-type-item.active .mt-label { color: #4CAF50; font-weight: 500; }

/* 数量选择 */
.quantity-section { margin-bottom: 16px; }

.quantity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.unit-switch {
  font-size: 12px;
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
  gap: 16px;
}

.quantity-btn {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: #F5F5F5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #333;
}

.quantity-value {
  font-size: 22px;
  font-weight: 600;
  color: #333;
  min-width: 30px;
  text-align: center;
}

.quantity-unit {
  font-size: 14px;
  color: #666;
}

.quantity-weight {
  font-size: 13px;
  color: #999;
}

.gram-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.gram-input {
  flex: 1;
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 8px;
  font-size: 16px;
}

.gram-label {
  font-size: 14px;
  color: #666;
}

/* 热量预览 */
.calorie-preview {
  text-align: right;
  margin-bottom: 16px;
}

.calorie-text {
  font-size: 16px;
  font-weight: 600;
  color: #4CAF50;
}

/* 底部按钮 */
.popup-actions {
  display: flex;
  gap: 10px;
}

.confirm-btn {
  flex: 1;
  background-color: #4CAF50;
  color: #fff;
  border-radius: 25px;
  font-size: 14px;
  padding: 10px 0;
}

.confirm-btn.ghost {
  background-color: #fff;
  color: #4CAF50;
  border: 1px solid #4CAF50;
}

.tags {
  display: flex;
  gap: 10px;
}

.tag {
  padding: 6px 12px;
  background-color: #f0f0f0;
  border-radius: 15px;
  font-size: 12px;
  color: #666;
}

.tag.active {
  background-color: #E8F5E9;
  color: #4CAF50;
  border: 1px solid #4CAF50;
}
</style>
