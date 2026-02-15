<template>
  <view class="popup" v-if="visible">
    <view class="popup-mask" @click="close"></view>
    <view class="popup-content">
      <view class="popup-header">
        <text class="popup-title">{{ title || '添加饮食记录' }}</text>
        <text class="popup-close" @click="close">×</text>
      </view>
      
      <view class="food-info" v-if="foodName">
        <text class="food-name">当前食物: {{ foodName }}</text>
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

      <!-- Unit Mode Switcher -->
      <view class="form-item" v-if="allowUnitMode">
         <view class="label-row">
            <text class="label">{{ isGramMode ? '重量 (克)' : '数量' }}</text>
            <text class="mode-switch" @click="toggleMode">
               {{ isGramMode ? `切换为${unitName || '份'}` : '切换为克' }}
            </text>
         </view>
         
         <view v-if="!isGramMode" class="quantity-row">
            <view class="stepper">
               <text class="step-btn" @click="changeQty(-0.5)">-</text>
               <input class="qty-input" type="number" v-model="quantity" />
               <text class="step-btn" @click="changeQty(0.5)">+</text>
            </view>
            <text class="approx-weight">约 {{ totalWeight }} 克</text>
         </view>
         
         <input v-else class="weight-input" type="number" v-model="currentWeight" placeholder="100" />
      </view>

      <!-- Simple Mode -->
      <view class="form-item" v-else>
        <text class="label">重量 (克)</text>
        <input class="weight-input" type="number" v-model="currentWeight" placeholder="100" />
      </view>
      
      <button class="confirm-btn" @click="confirm">确认</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';

const props = defineProps<{
  visible: boolean;
  title?: string;
  foodName?: string;
  initialWeight?: number | string;
  initialMealType?: string;
  
  // Unit mode props
  allowUnitMode?: boolean;
  unitName?: string;
  unitWeight?: number;
}>();

const emit = defineEmits(['update:visible', 'confirm', 'cancel']);

const currentWeight = ref(props.initialWeight || '');
const currentMealType = ref(props.initialMealType || 'breakfast');

// Unit mode state
const isGramMode = ref(!props.allowUnitMode); // If unit mode allowed, default to unit mode? Or grams? Let's default to unit if allowed.
// But usually result page logic defaults to unit.
// Let's default to props logic: if allowUnitMode is true, verify if we should start in gram mode.
// Actually, let's default to "Unit Mode" if allowed, unless initialWeight is provided and it doesn't match a unit?
// For simplicity: Default to Unit Mode if allowed.
const quantity = ref(1);

watch(() => props.visible, (val) => {
  if (val) {
    currentWeight.value = props.initialWeight || '';
    currentMealType.value = props.initialMealType || 'breakfast';
    
    if (props.allowUnitMode) {
        isGramMode.value = false; // Reset to unit mode
        quantity.value = 1;
        // If initialWeight is set, maybe we should calculate quantity?
        // But for now, reset.
    } else {
        isGramMode.value = true;
    }
  }
});

const mealTypes = [
  { key: 'breakfast', name: '早餐' },
  { key: 'lunch', name: '午餐' },
  { key: 'dinner', name: '晚餐' },
  { key: 'snack', name: '加餐' }
];

const totalWeight = computed(() => {
    if (isGramMode.value) return Number(currentWeight.value) || 0;
    return Math.round(Number(quantity.value) * (props.unitWeight || 100));
});

const toggleMode = () => {
    isGramMode.value = !isGramMode.value;
    if (isGramMode.value) {
        // Switch to grams: fill with calculated total weight
        currentWeight.value = String(totalWeight.value);
    } else {
        // Switch to units: estimate quantity
        const w = Number(currentWeight.value) || 0;
        const u = props.unitWeight || 100;
        quantity.value = Math.max(0.5, Math.round((w / u) * 2) / 2);
    }
};

const changeQty = (delta: number) => {
    const val = Number(quantity.value) + delta;
    if (val >= 0.5) quantity.value = val;
};

const close = () => {
  emit('update:visible', false);
  emit('cancel');
};

const confirm = () => {
  const finalWeight = totalWeight.value;
  if (!finalWeight || finalWeight <= 0) {
    uni.showToast({ title: '请输入有效重量', icon: 'none' });
    return;
  }
  emit('confirm', {
    weight: finalWeight,
    mealType: currentMealType.value
  });
};
</script>

<style lang="scss" scoped>
.popup {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.popup-mask {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}
.popup-content {
  position: relative;
  width: 80%;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  z-index: 1001;
}
.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}
.popup-title {
  font-size: 32rpx;
  font-weight: bold;
}
.popup-close {
  font-size: 40rpx;
  color: #999;
  padding: 10rpx;
}
.food-info {
  margin-bottom: 20rpx;
  padding: 16rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
  .food-name {
    font-size: 28rpx;
    font-weight: 500;
  }
}
.form-item {
  margin-bottom: 30rpx;
  .label {
    display: block;
    font-size: 28rpx;
    color: #666;
    margin-bottom: 16rpx;
  }
}
.tags {
  display: flex;
  gap: 20rpx;
  .tag {
    padding: 12rpx 24rpx;
    background: #f5f5f5;
    border-radius: 30rpx;
    font-size: 26rpx;
    color: #666;
    &.active {
      background: #4CAF50;
      color: #fff;
    }
  }
}
.weight-input {
  width: 100%;
  height: 80rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
}
.confirm-btn {
  width: 100%;
  height: 88rpx;
  background: #4CAF50;
  color: #fff;
  border-radius: 44rpx;
  font-size: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 40rpx;
}

/* Unit Mode Styles */
.label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.mode-switch {
  font-size: 26rpx;
  color: #4CAF50;
}
.quantity-row {
  display: flex;
  align-items: center;
}
.stepper {
  display: flex;
  border: 1px solid #ddd;
  border-radius: 8rpx;
  overflow: hidden;
}
.step-btn {
  padding: 10rpx 24rpx;
  background: #f9f9f9;
  font-size: 32rpx;
  font-weight: bold;
  color: #666;
  &:active {
    background: #eee;
  }
}
.qty-input {
  width: 100rpx;
  text-align: center;
  border-left: 1px solid #ddd;
  border-right: 1px solid #ddd;
  height: 100%;
  display: flex;
  align-items: center;
}
.approx-weight {
  margin-left: 20rpx;
  font-size: 26rpx;
  color: #888;
}
</style>
