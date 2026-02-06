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
      
      <view class="date-picker">
        <text class="date-text">{{ currentDateStr }}</text>
        <text class="switch-date" @click="changeDate">切换日期</text>
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
    
    <!-- 功能入口 -->
    <view class="feature-entry" @click="goDietPlan">
      <view class="entry-content">
        <text class="entry-icon">🥗</text>
        <view class="entry-text">
          <text class="entry-title">推荐食谱</text>
          <text class="entry-desc">AI 定制专属饮食计划</text>
        </view>
      </view>
      <text class="entry-arrow">›</text>
    </view>
    
    <!-- 每日餐饮列表 -->
    <view class="meal-list" v-if="loading">
      <view class="meal-group skeleton" v-for="n in 3" :key="n">
        <view class="skeleton-title"></view>
        <view class="skeleton-line" v-for="i in 3" :key="i"></view>
      </view>
    </view>


    <view class="popup" v-if="editingRecord">
      <view class="popup-mask" @click="cancelEditRecord"></view>
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">编辑 {{ editingRecord.food_name }}</text>
          <text class="popup-close" @click="cancelEditRecord">×</text>
        </view>
        <view class="form-item">
          <text class="label">餐次</text>
          <view class="tags">
            <text
              v-for="type in mealTypes"
              :key="type.key"
              class="tag"
              :class="{ active: editMealType === type.key }"
              @click="editMealType = type.key"
            >{{ type.name }}</text>
          </view>
        </view>
        <view class="form-item">
          <text class="label">重量 (克)</text>
          <input class="weight-input" type="number" v-model="editWeight" placeholder="100" />
        </view>
        <button class="confirm-btn" @click="confirmEditRecord">保存修改</button>
      </view>
    </view>

    <view class="meal-list" v-else>
      <view class="meal-group" :id="`meal-${type.key}`" v-for="type in mealTypes" :key="type.key">
        <view class="group-header">
          <view class="title-row">
            <text class="title">{{ type.name }}</text>
            <text class="sub">{{ getMealCalories(type.key) }} 千卡</text>
          </view>
          <view class="add-btn" @click="navigateToAdd(type.key)">+ 添加</view>
        </view>
        
        <view class="food-items">
          <view class="food-item" v-for="item in getMealItems(type.key)" :key="item.id">
            <image :src="item.image_url || '/static/default_food.png'" class="food-img" mode="aspectFill"></image>
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

<script>
import { API_BASE_URL } from '@/config.js';
import nutrition from '@/utils/nutrition';
import reportUtils from '@/utils/report';

export default {
  data() {
    return {
      currentDate: new Date(),
      loading: false,
      editingTarget: false,
      targetCalories: null,
      targetInput: '',
      targetDateKey: '',
      editingRecord: null,
      editWeight: '',
      editMealType: 'breakfast',
      report: {
        total: { calories: 0, protein: 0, fat: 0, carb: 0 },
        recommended: { calories: 2000, protein: 75, fat: 66, carb: 275 },
        carb_pct: 0, protein_pct: 0, fat_pct: 0,
        records: []
      },
      mealTypes: [
        { key: 'breakfast', name: '早餐' },
        { key: 'lunch', name: '午餐' },
        { key: 'dinner', name: '晚餐' },
        { key: 'snack', name: '加餐' }
      ]
    }
  },
  onLoad() {
    uni.$on('meal-record-updated', this.fetchData);
    this.loadTargetCalories();
  },
  onUnload() {
    uni.$off('meal-record-updated', this.fetchData);
  },
  computed: {
    statusBarHeight() {
        const sysInfo = uni.getSystemInfoSync();
        return sysInfo.statusBarHeight || 20;
    },
    currentDateStr() {
      return this.currentDate.toISOString().split('T')[0];
    },
    caloriePercent() {
      const total = this.report.total.calories || 0;
      const recommended = this.recommended.calories || 0;
      if (!recommended) return 0;
      const pct = (total / recommended) * 100;
      return Math.min(100, Math.max(0, Math.round(pct)));
    },
    ringStyle() {
      const color = nutrition.getRingColor(this.caloriePercent);
      return {
        background: `conic-gradient(${color} 0% ${this.caloriePercent}%, #E0E0E0 ${this.caloriePercent}% 100%)`
      };
    },
    remainingCalories() {
      let r = this.recommended.calories - this.report.total.calories;
      return r > 0 ? r.toFixed(0) : 0;
    },
    recommended() {
      if (this.targetCalories) {
        return nutrition.calculateRecommendedMacros(this.targetCalories);
      }
      return this.report.recommended;
    }
  },
  onShow() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.loading = true;
      try {
        const res = await uni.request({
          url: `${API_BASE_URL}/api/v1/meal/daily-report`,
          method: 'GET',
          data: {
            date: this.currentDateStr
          }
        });
        if(res.data && res.data.code === 0) {
          this.report = reportUtils.normalizeReport(res.data.data);
          this.scrollToLastMeal();
        }
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' });
      } finally {
        this.loading = false;
      }
    },
    loadTargetCalories() {
      const val = Number(uni.getStorageSync('targetCalories'));
      const savedDate = uni.getStorageSync('targetCaloriesDate');
      this.targetDateKey = this.currentDateStr;
      if (savedDate && savedDate !== this.currentDateStr) {
        uni.removeStorageSync('targetCalories');
        uni.removeStorageSync('targetCaloriesDate');
        this.targetCalories = null;
        return;
      }
      if (val) {
        this.targetCalories = val;
      }
    },
    startEditTarget() {
      this.targetInput = String(this.recommended.calories || 2000);
      this.editingTarget = true;
    },
    cancelEditTarget() {
      this.editingTarget = false;
      this.targetInput = '';
    },
    saveTarget() {
      const val = Number(this.targetInput);
      if (!val || val < 800 || val > 6000) {
        uni.showToast({ title: '请输入 800~6000 范围内的热量', icon: 'none' });
        return;
      }
      this.targetCalories = val;
      uni.setStorageSync('targetCalories', val);
      uni.setStorageSync('targetCaloriesDate', this.currentDateStr);
      this.editingTarget = false;
      this.targetInput = '';
    },
    resetTarget() {
      this.targetCalories = null;
      uni.removeStorageSync('targetCalories');
      uni.removeStorageSync('targetCaloriesDate');
      this.editingTarget = false;
      this.targetInput = '';
    },
    scrollToLastMeal() {
      const key = uni.getStorageSync('lastMealType');
      if (!key) return;
      uni.removeStorageSync('lastMealType');
      this.$nextTick(() => {
        const selector = `#meal-${key}`;
        uni.pageScrollTo({ selector, duration: 300 });
      });
    },
    getPercent(val, max) {
      return reportUtils.safePercent(val, max);
    },
    getMealItems(type) {
      return this.report.records.filter(r => r.meal_type === type);
    },
    getMealCalories(type) {
      const items = this.getMealItems(type);
      const sum = items.reduce((acc, cur) => acc + cur.calories, 0);
      return sum.toFixed(0);
    },
    navigateToAdd(type) {
      uni.navigateTo({
        url: `/pages/record/add?date=${this.currentDateStr}&type=${type}`
      });
    },
    changeDate() {
      // 简单实现：仅支持今天
      uni.showToast({ title: '暂时只支持查看今日', icon: 'none' });
    },
    async deleteItem(id) {
       uni.showModal({
         title: '提示',
         content: '确定删除这条记录吗？',
         success: async (res) => {
           if (res.confirm) {
             try {
                const res = await uni.request({
                  url: `${API_BASE_URL}/api/v1/meal/record/${id}`,
                  method: 'DELETE'
                });
                if(res.data.code === 0) {
                  this.fetchData();
                }
            } catch(e) {
              uni.showToast({ title: '删除失败', icon: 'none' });
            }
          }
        }
      })
   },
    startEditRecord(item) {
      this.editingRecord = item;
      this.editWeight = String(item.unit_weight || 0);
      this.editMealType = item.meal_type || 'breakfast';
    },
    cancelEditRecord() {
      this.editingRecord = null;
      this.editWeight = '';
    },
    async confirmEditRecord() {
      const weight = Number(this.editWeight);
      if (!weight || weight <= 0) {
        uni.showToast({ title: '请输入有效重量', icon: 'none' });
        return;
      }
      try {
        const res = await uni.request({
          url: `${API_BASE_URL}/api/v1/meal/record/${this.editingRecord.id}`,
          method: 'PUT',
          data: {
            unit_weight: weight,
            meal_type: this.editMealType
          }
        });
        if (res.data.code === 0) {
          uni.showToast({ title: '已更新' });
          this.editingRecord = null;
          this.fetchData();
        } else {
          uni.showToast({ title: res.data.message || '更新失败', icon: 'none' });
        }
      } catch (e) {
        uni.showToast({ title: '更新失败', icon: 'none' });
      }
    },
    goBack() {
        uni.navigateBack(); // 保留顶部返回，防止栈过深时无法退出
    },
    goHome() {
        // 使用 reLaunch 清除栈，模拟 Tab 切换，避免页面无限叠加
        uni.reLaunch({ url: '/pages/index/index' });
    },
    goHistory() {
        uni.navigateTo({ url: '/pages/history/index' });
    },
    goProfile() {
        uni.navigateTo({ url: '/pages/profile/index' });
    },
    goDietPlan() {
        uni.navigateTo({ url: '/pages/plan/index' });
    }
  }
}
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

.date-picker {
  padding: 0 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

.feature-entry {
  margin: 15px;
  background: #fff;
  border-radius: 12px;
  padding: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.entry-content {
  display: flex;
  align-items: center;
}

.entry-icon {
  font-size: 24px;
  margin-right: 15px;
}

.entry-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  display: block;
}

.entry-desc {
  font-size: 12px;
  color: #999;
}

.entry-arrow {
  color: #ccc;
  font-size: 20px;
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

.popup-title {
  font-size: 18px;
  font-weight: bold;
}

.popup-close {
  font-size: 18px;
  color: #999;
}

.form-item {
  margin-bottom: 20px;
}

.tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
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

.confirm-btn {
  background-color: #4CAF50;
  color: #fff;
  border-radius: 25px;
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
