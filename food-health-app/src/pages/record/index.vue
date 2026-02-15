<template>
  <view class="container">
    <!-- 顶部日期与概览 -->
    <view class="header">
      <!-- 增加自定义导航栏的返回按钮 -->
      <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
        <view class="back-btn" @click="goBack">
           <text class="back-icon">←</text>
        </view>
        <view class="title">饮食记录</view>
      </view> 
      
      <view class="date-picker-row">
        <picker mode="date" :value="currentDateStr" @change="bindDateChange">
          <view class="date-picker">
            <text class="date-text">{{ currentDateStr }}</text>
            <text class="switch-date">▼</text>
          </view>
        </picker>
        <view class="today-btn" v-if="!isToday" @click="resetToToday">
          回到今天
        </view>
      </view>
      
      <view class="summary-card skeleton" v-if="loading">
        <view class="skeleton-row"></view>
        <view class="skeleton-ring"></view>
        <view class="skeleton-bar"></view>
        <view class="skeleton-bar short"></view>
      </view>

      <view class="summary-card" v-else>
        <view class="calorie-info">
          <view class="left">
            <text class="label">饮食摄入</text>
            <text class="value">{{ report.total.calories }}</text>
          </view>
          <view class="center">
            <!-- 简单的圆环进度模拟 -->
            <view class="ring" :style="ringStyle">
              <view class="ring-inner">
                <text class="small">还可吃</text>
                <text class="big">{{ remainingCalories }}</text>
              </view>
            </view>
          </view>
          <view class="right">
            <text class="label">推荐预算</text>
            <view class="target-value-row">
              <text class="value">{{ recommended.calories }}</text>
              <text class="target-edit" @click="startEditTarget">设置</text>
            </view>
          </view>
        </view>

        <view class="target-editor" v-if="editingTarget">
          <input class="target-input" type="number" v-model="targetInput" placeholder="输入目标热量" />
          <view class="target-actions">
            <text class="target-save" @click="saveTarget">保存</text>
            <text class="target-reset" @click="resetTarget">恢复默认</text>
            <text class="target-cancel" @click="cancelEditTarget">取消</text>
          </view>
        </view>
        
        <view class="macro-bars">
           <view class="macro-item">
             <view class="label-row">
               <text>碳水 {{ report.total.carb }}g</text>
               <text class="pct">{{ report.carb_pct }}%</text>
             </view>
             <progress :percent="getPercent(report.total.carb, recommended.carb)" stroke-width="4" activeColor="#4CAF50" backgroundColor="#E0E0E0" />
           </view>
           <view class="macro-item">
             <view class="label-row">
               <text>蛋白质 {{ report.total.protein }}g</text>
               <text class="pct">{{ report.protein_pct }}%</text>
             </view>
             <progress :percent="getPercent(report.total.protein, recommended.protein)" stroke-width="4" activeColor="#FF9800" backgroundColor="#E0E0E0" />
           </view>
           <view class="macro-item">
             <view class="label-row">
               <text>脂肪 {{ report.total.fat }}g</text>
               <text class="pct">{{ report.fat_pct }}%</text>
             </view>
             <progress :percent="getPercent(report.total.fat, recommended.fat)" stroke-width="4" activeColor="#F44336" backgroundColor="#E0E0E0" />
           </view>
        </view>
      </view>
    </view>
    
    <!-- 双入口功能区 -->
    <view class="feature-grid">
      <view class="feature-card ai-feature" @click="goDietPlan">
         <view class="feature-icon-box ai-icon-bg">
           <text class="feature-icon">🤖</text>
         </view>
         <view class="feature-text">
           <text class="feature-title">AI 智能食谱</text>
           <text class="feature-desc">量身定制周计划</text>
         </view>
      </view>
      
      <view class="feature-card recipe-feature" @click="goRecipeList">
         <view class="feature-icon-box recipe-icon-bg">
           <text class="feature-icon">🥗</text>
         </view>
         <view class="feature-text">
           <text class="feature-title">精选食谱</text>
           <text class="feature-desc">营养师精心推荐</text>
         </view>
      </view>
    </view>
    
    <!-- 每日餐饮列表 -->
    <view class="meal-list" v-if="loading">
      <view class="meal-group skeleton" v-for="n in 3" :key="n">
        <view class="skeleton-title"></view>
        <view class="skeleton-line" v-for="i in 3" :key="i"></view>
      </view>
    </view>




    <view class="meal-list" v-else>
      <view class="meal-group" :id="`meal-${type.key}`" v-for="type in mealTypes" :key="type.key">
        <view class="group-header">
          <view class="title-row">
            <text class="meal-icon">{{ type.icon }}</text>
            <text class="title">{{ type.name }}</text>
            <text class="sub">{{ getMealCalories(type.key) }} 千卡</text>
          </view>
          <view class="add-btn" @click="navigateToAdd(type.key)">+ 添加</view>
        </view>
        
        <view class="food-items">
          <view class="food-item" v-for="item in getMealItems(type.key)" :key="item.id">
            <image v-if="item.image_url" :src="getFoodImageUrl(item.image_url)" class="food-img" mode="aspectFill"></image>
            <view v-else class="food-img-placeholder">🍽️</view>
            <view class="food-info">
              <text class="name">{{ item.food_name }}</text>
              <text class="desc">{{ item.unit_weight }}克 · {{ item.calories }}千卡</text>
            </view>
            <view class="action">
              <text class="edit-icon" @click="startEditRecord(item)">✎</text>
              <text class="delete-icon" @click="deleteItem(item.id)">×</text>
            </view>
          </view>
          <view class="empty-tip" v-if="getMealItems(type.key).length === 0">
            <text>还没有记录哦</text>
          </view>
        </view>
      </view>
    </view>

    <FoodEntryPopup
      :visible="!!editingRecord"
      :title="'编辑 ' + (editingRecord ? editingRecord.food_name : '')"
      :foodName="editingRecord ? editingRecord.food_name : ''"
      :initialWeight="editingRecord ? editingRecord.unit_weight : ''"
      :initialMealType="editingRecord ? (editingRecord.meal_type || 'breakfast').toLowerCase() : 'breakfast'"
      @update:visible="(val) => !val && cancelEditRecord()"
      @confirm="handlePopupConfirm"
    />


    <!-- 底部导航 -->
    <view class="bottom-nav">
      <view class="nav-item" @click="goHome">
        <text class="nav-icon">📷</text>
        <text class="nav-text">识别</text>
      </view>
      <view class="nav-item active">
        <text class="nav-icon">🍽️</text>
        <text class="nav-text">饮食</text>
      </view>
      <view class="nav-item" @click="goHistory">
        <text class="nav-icon">📋</text>
        <text class="nav-text">历史</text>
      </view>
      <view class="nav-item" @click="goProfile">
        <text class="nav-icon">👤</text>
        <text class="nav-text">我的</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { onShow } from '@dcloudio/uni-app';
import { API_BASE_URL } from '@/config.js';
import nutrition from '@/utils/nutrition';
import FoodEntryPopup from '@/components/FoodEntryPopup.vue';
import { useMealStore } from '@/stores/meal';
import type { MealRecord } from '@/types/meal';

// Store
const mealStore = useMealStore();

// UI State
const editingTarget = ref(false);
const targetInput = ref('');
const targetDateKey = ref('');

// Editing Record State
const editingRecord = ref<MealRecord | null>(null);
const editWeight = ref('');
const editMealType = ref('breakfast');

// Computed from Store
const loading = computed(() => mealStore.loading);
const report = computed(() => mealStore.report || {
    date: currentDateStr.value,
    total: { calories: 0, protein: 0, fat: 0, carb: 0 },
    recommended: { calories: 2000, protein: 75, fat: 66, carb: 275 },
    protein_pct: 0, fat_pct: 0, carb_pct: 0,
    records: []
});
const currentDateStr = computed(() => mealStore.currentDate);
const remainingCalories = computed(() => mealStore.remainingCalories);
const recommended = computed(() => mealStore.currentRecommended);
const caloriePercent = computed(() => mealStore.caloriePercent);

const ringStyle = computed(() => {
  const color = nutrition.getRingColor(caloriePercent.value);
  // Ensure percent doesn't break CSS if > 100
  const pct = Math.min(100, Math.max(0, caloriePercent.value));
  return {
    background: `conic-gradient(${color} 0% ${pct}%, #E0E0E0 ${pct}% 100%)`
  };
});

const mealTypes = [
  { key: 'breakfast', name: '早餐', icon: '🌅' },
  { key: 'lunch', name: '午餐', icon: '☀️' },
  { key: 'dinner', name: '晚餐', icon: '🌙' },
  { key: 'snack', name: '加餐', icon: '🍪' }
];

const statusBarHeight = computed(() => {
    const sysInfo = uni.getSystemInfoSync();
    return sysInfo.statusBarHeight || 20;
});

// Lifecycle
onShow(() => {
  mealStore.fetchDailyReport();
});

// Methods
const getFoodImageUrl = (url: string | null | undefined) => {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  return API_BASE_URL + url;
};

const getPercent = (val: number | undefined, max: number | undefined) => {
    // Basic calculation, or use util if needed. Store has safe logic for ring but bars need it too.
    const v = val || 0;
    const m = max || 0;
    if (!m) return 0;
    const pct = (v / m) * 100;
    return Math.min(100, Math.max(0, Math.round(pct)));
};

// Store wrappers
const getMealItems = (type: string) => mealStore.getMealItems(type);
const getMealCalories = (type: string) => mealStore.getMealCalories(type);

const navigateToAdd = (type: string) => {
  uni.navigateTo({
    url: `/pages/record/add?date=${currentDateStr.value}&type=${type}`
  });
};

const bindDateChange = (e: any) => {
    mealStore.setDate(e.detail.value);
};

const isToday = computed(() => {
    const today = new Date().toISOString().split('T')[0];
    return currentDateStr.value === today;
});

const resetToToday = () => {
    const today = new Date().toISOString().split('T')[0];
    mealStore.setDate(today);
};

// Target Calories Logic
const startEditTarget = () => {
  targetInput.value = String(recommended.value.calories || 2000);
  editingTarget.value = true;
};

const cancelEditTarget = () => {
  editingTarget.value = false;
  targetInput.value = '';
};

const saveTarget = () => {
  const val = Number(targetInput.value);
  if (!val || val < 800 || val > 6000) {
    uni.showToast({ title: '请输入 800~6000 范围内的热量', icon: 'none' });
    return;
  }
  mealStore.setTargetCalories(val);
  editingTarget.value = false;
  targetInput.value = '';
};

const resetTarget = () => {
  mealStore.setTargetCalories(null);
  editingTarget.value = false;
  targetInput.value = '';
};

// Edit Record Logic
const startEditRecord = (item: MealRecord) => {
  editingRecord.value = item;
  editWeight.value = String(item.unit_weight || 0);
  editMealType.value = (item.meal_type || 'breakfast').toLowerCase();
};

const cancelEditRecord = () => {
  editingRecord.value = null;
  editWeight.value = '';
};

const handlePopupConfirm = async ({ weight, mealType }: { weight: string, mealType: string }) => {
  const numWeight = Number(weight);
  if (!numWeight || numWeight <= 0) {
    uni.showToast({ title: '请输入有效重量', icon: 'none' });
    return;
  }
  
  if (editingRecord.value) {
      const success = await mealStore.updateRecord(editingRecord.value.id, {
        unit_weight: numWeight,
        meal_type: mealType
      });
      if (success) {
          editingRecord.value = null;
      }
  }
};

const deleteItem = (id: number) => {
   uni.showModal({
     title: '提示',
     content: '确定删除这条记录吗？',
     success: async (res) => {
       if (res.confirm) {
         await mealStore.deleteRecord(id);
       }
    }
  })
};

// Navigation
const goBack = () => uni.navigateBack();
const goHome = () => uni.reLaunch({ url: '/pages/index/index' });
const goHistory = () => uni.navigateTo({ url: '/pages/history/index' });
const goProfile = () => uni.navigateTo({ url: '/pages/profile/index' });
const goDietPlan = () => uni.navigateTo({ url: '/pages/plan/index' });
const goRecipeList = () => uni.navigateTo({ url: '/pages/recipe/list' });
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #F5F7FA;
  padding-bottom: 40px;
}

.header {
  background-color: #4CAF50;
  /* padding: 20px 15px; Remove fixed padding to accommodate status bar */
  padding-bottom: 20px;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  color: #fff;
}

.nav-bar {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  margin-bottom: 10px;
}

.back-btn {
  font-size: 24px;
  margin-right: 15px;
  padding: 5px;
}

.nav-bar .title {
  font-size: 18px;
  font-weight: bold;
}

.date-picker-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
  margin-bottom: 20px;
}

.date-picker {
  display: flex;
  align-items: center;
}

.today-btn {
  font-size: 12px;
  color: #fff;
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.date-text {
  font-size: 18px;
  font-weight: bold;
}

.switch-date {
  font-size: 14px;
  opacity: 0.8;
}

.summary-card {
  background-color: #fff;
  border-radius: 12px;
  padding: 15px;
  color: #333;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.target-value-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.target-edit {
  font-size: 12px;
  color: #4CAF50;
}

.target-editor {
  margin-top: 12px;
  padding: 10px;
  background: #F6FFF6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.target-input {
  flex: 1;
  background: #fff;
  border-radius: 6px;
  padding: 8px;
  font-size: 14px;
}

.target-actions {
  display: flex;
  gap: 10px;
}

.target-save {
  font-size: 12px;
  color: #4CAF50;
}

.target-reset {
  font-size: 12px;
  color: #FF9800;
}

.target-cancel {
  font-size: 12px;
  color: #999;
}

.summary-card.skeleton {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-row,
.skeleton-ring,
.skeleton-bar,
.skeleton-title,
.skeleton-line {
  background: linear-gradient(90deg, #f0f0f0 0%, #f7f7f7 50%, #f0f0f0 100%);
  border-radius: 8px;
  animation: shimmer 1.2s infinite;
}

.skeleton-row {
  height: 16px;
  width: 60%;
}

.skeleton-ring {
  height: 80px;
  width: 80px;
  border-radius: 50%;
  align-self: center;
}

.skeleton-bar {
  height: 10px;
  width: 100%;
}

.skeleton-bar.short {
  width: 70%;
}

.meal-group.skeleton {
  padding: 15px;
  border-radius: 12px;
}

.skeleton-title {
  height: 14px;
  width: 40%;
  margin-bottom: 12px;
}

.skeleton-line {
  height: 10px;
  width: 100%;
  margin-bottom: 10px;
}

@keyframes shimmer {
  0% { background-position: -200px 0; }
  100% { background-position: 200px 0; }
}

.calorie-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.value {
  font-size: 18px;
  font-weight: bold;
  display: block;
}

.label {
  font-size: 12px;
  color: #888;
}

.center {
  text-align: center;
}

.ring {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ring-inner {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.ring-inner .big {
  font-size: 24px;
  color: #4CAF50;
  font-weight: bold;
  display: block;
}
.ring-inner .small {
  font-size: 12px;
  color: #888;
}

.macro-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.feature-grid {
  margin: 15px;
  display: flex;
  gap: 15px;
}

.feature-card {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transition: transform 0.2s;
}

.feature-card:active {
  transform: scale(0.98);
}

.feature-icon-box {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
}

.ai-icon-bg {
  background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
}

.recipe-icon-bg {
  background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
}

.feature-icon {
  font-size: 28rpx;
}

.feature-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 4px;
}

.feature-desc {
  font-size: 12px;
  color: #888;
}

.ai-feature .feature-title {
  color: #2E7D32;
}

.recipe-feature .feature-title {
  color: #EF6C00;
}

.macro-item {
  margin-bottom: 8px;
}

.label-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 4px;
  color: #666;
}

.meal-list {
  padding: 15px;
}

.meal-group {
  background-color: #fff;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 15px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.title {
  font-size: 16px;
  font-weight: bold;
  margin-right: 10px;
}

.meal-icon {
  font-size: 20px;
  margin-right: 6px;
}

.sub {
  font-size: 12px;
  color: #888;
}

.add-btn {
  font-size: 14px;
  color: #4CAF50;
}

.food-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.food-img {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  background-color: #eee;
  margin-right: 10px;
}

.food-img-placeholder {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  background-color: #f5f5f5;
  margin-right: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.food-info {
  flex: 1;
}

.name {
  font-size: 14px;
  display: block;
}

.desc {
  font-size: 12px;
  color: #888;
}

.action {
  display: flex;
  align-items: center;
  gap: 8px;
}

.edit-icon {
  color: #4CAF50;
  font-size: 16px;
  padding: 5px;
}

.delete-icon {
  color: #ccc;
  font-size: 18px;
  padding: 5px;
}

.empty-tip {
  text-align: center;
  font-size: 12px;
  color: #ccc;
  padding: 10px 0;
}



.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  background: #fff;
  padding: 20rpx 0;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.nav-item.active .nav-icon,
.nav-item.active .nav-text {
  color: #4CAF50;
}

.nav-icon {
  font-size: 44rpx;
  margin-bottom: 6rpx;
}

.nav-text {
  font-size: 22rpx;
  color: #999;
}
</style>
