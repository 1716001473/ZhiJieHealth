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
          <view class="batch-meal-tags">
            <text
              v-for="type in mealTypes"
              :key="type.key"
              class="tag"
              :class="{ active: item.meal_type === type.key }"
              @click="item.meal_type = type.key"
            >{{ type.name }}</text>
          </view>
        </view>
        <input class="batch-weight" type="number" v-model="item.weight" placeholder="克数" />
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
    
    <!-- 添加弹窗 -->
    <view class="popup" v-if="selectedFood">
      <view class="popup-mask" @click="selectedFood = null"></view>
      <view class="popup-content">
        <view class="popup-header">
          <text class="title">添加 {{ selectedFood.name }}</text>
          <text class="close" @click="selectedFood = null">×</text>
        </view>
        
        <view class="form-item">
          <text class="label">餐次</text>
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
        
        <view class="form-item">
          <text class="label">重量 (克)</text>
          <input class="weight-input" type="number" v-model="weight" placeholder="100" />
        </view>

        <view class="form-item">
          <text class="label">餐具估算</text>
          <view class="tags">
            <text 
              v-for="dish in dishSizes"
              :key="dish.name"
              class="tag"
              :class="{ active: selectedDish === dish.name }"
              @click="applyDishWeight(dish)"
            >{{ dish.name }}</text>
          </view>
        </view>
        
        <view class="calc-preview">
          <text>预计热量: {{ calculatedCalories }} 千卡</text>
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
      weight: 100,
      selectedDish: '',
      selectedItems: [],
      
      mealTypes: [
        { key: 'breakfast', name: '早餐' },
        { key: 'lunch', name: '午餐' },
        { key: 'dinner', name: '晚餐' },
        { key: 'snack', name: '加餐' }
      ],
      dishSizes: [
        { name: '一小碗', weight: 150 },
        { name: '一碗', weight: 250 },
        { name: '一盘', weight: 300 },
        { name: '一大盘', weight: 450 }
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
    if (options.keyword) {
      this.keyword = decodeURIComponent(options.keyword);
      setTimeout(() => {
        this.doSearch();
      }, 0);
    }
  },
  computed: {
    calculatedCalories() {
      if (!this.selectedFood) return 0;
      const calories = this.getFoodCalories(this.selectedFood);
      const weight = Number(this.weight) || 0;
      return ((calories * weight) / 100).toFixed(0);
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
    applyDishWeight(dish) {
      this.selectedDish = dish.name;
      this.weight = dish.weight;
    },
    buildMealPayload(item, weight) {
      const base = {
        meal_date: this.targetDate,
        meal_type: item.meal_type || this.currentMealType,
        food_name: item.name,
        unit_weight: parseFloat(weight)
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
      this.weight = 100; // reset
      this.selectedDish = '';
    },
    addToBatch() {
      if (!this.selectedFood) return;
      const key = `${this.selectedFood.name}-${this.selectedFood.id || 'temp'}`;
      const exists = this.selectedItems.find(item => item.key === key);
      if (exists) {
        exists.weight = this.weight;
        uni.showToast({ title: '已更新清单', icon: 'none' });
      } else {
        this.selectedItems.push({
          key,
          id: this.selectedFood.id,
          name: this.selectedFood.name,
          nutrition: this.selectedFood.nutrition,
          data_source: this.selectedFood.data_source,
          is_temp: this.selectedFood.is_temp,
          weight: this.weight,
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
      const items = this.selectedItems.map(item => this.buildMealPayload(item, item.weight));
      uni.showLoading({ title: '批量提交中' });
      try {
        const res = await uni.request({
          url: `${API_BASE_URL}/api/v1/meal/records/batch`,
          method: 'POST',
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
          uni.showToast({ title: res.data.message || '批量添加失败', icon: 'none' });
        }
      } catch (e) {
        uni.showToast({ title: '请求出错', icon: 'none' });
      } finally {
        uni.hideLoading();
      }
    },
    async confirmAdd() {
      if (!this.weight || this.weight <= 0) {
        uni.showToast({ title: '请输入有效重量', icon: 'none' });
        return;
      }
      
      uni.showLoading({ title: '提交中' });
      try {
        const res = await uni.request({
          url: `${API_BASE_URL}/api/v1/meal/record`,
          method: 'POST',
          data: this.buildMealPayload(this.selectedFood, this.weight)
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
          uni.showToast({ title: res.data.message || '添加失败', icon: 'none' });
        }
      } catch (e) {
        uni.showToast({ title: '请求出错', icon: 'none' });
      } finally {
        uni.hideLoading();
      }
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

.source-ai {
  background: #EEF2FF;
  color: #4F46E5;
}

.source-baidu {
  background: #FFF7ED;
  color: #EA580C;
}

.source-user {
  background: #ECFDF3;
  color: #16A34A;
}

.source-db {
  background: #F1F5F9;
  color: #64748B;
}

.source-off {
  background: #FEF3C7;
  color: #D97706;
}

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

.batch-title {
  font-size: 14px;
  font-weight: bold;
}

.batch-clear {
  font-size: 12px;
  color: #999;
}

.batch-meal-types {
  margin-bottom: 10px;
}

.batch-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 6px;
}

.batch-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.batch-item:last-child {
  border-bottom: none;
}

.batch-name {
  flex: 1;
  font-size: 13px;
}

.batch-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-right: 8px;
}

.batch-meal-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.batch-weight {
  width: 80px;
  text-align: right;
  background: #f9f9f9;
  padding: 6px 8px;
  border-radius: 6px;
  margin-right: 8px;
}

.batch-remove {
  font-size: 16px;
  color: #ccc;
}

.batch-btn {
  margin-top: 10px;
  background-color: #4CAF50;
  color: #fff;
  border-radius: 20px;
}

/* Popup */
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
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  padding: 20px;
  box-sizing: border-box;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.popup-header .title {
  font-size: 18px;
  font-weight: bold;
}

.form-item {
  margin-bottom: 20px;
}

.label {
  display: block;
  margin-bottom: 10px;
  color: #666;
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

.weight-input {
  background-color: #f9f9f9;
  padding: 10px;
  border-radius: 6px;
  font-size: 16px;
}

.calc-preview {
  margin-bottom: 20px;
  text-align: right;
  color: #ff9800;
  font-size: 14px;
}

.confirm-btn {
  background-color: #4CAF50;
  color: #fff;
  border-radius: 25px;
}

.popup-actions {
  display: flex;
  gap: 10px;
}

.confirm-btn.ghost {
  background-color: #fff;
  color: #4CAF50;
  border: 1px solid #4CAF50;
}
</style>
