<template>
  <view class="chart-container" ref="chartRef">
    <!-- 标题 -->
    <view class="chart-header" v-if="title">
      <text class="chart-title">{{ title }}</text>
      <text class="chart-unit" v-if="unit">单位: {{ unit }}</text>
    </view>

    <!-- 图表区 -->
    <view class="chart-content" v-if="data && data.length > 0">
      <view class="chart-wrapper" :style="{ width: chartWidth + 'px', height: height + 'px' }">
        <!-- SVG 图形层 -->
        <svg
          :width="chartWidth"
          :height="height"
          :viewBox="`0 0 ${chartWidth} ${height}`"
          class="chart-svg"
        >
          <!-- 背景网格 (横线) -->
          <g class="grid">
            <line
              v-for="(y, index) in gridLines"
              :key="`grid-${index}`"
              :x1="padding.left"
              :y1="y"
              :x2="chartWidth - padding.right"
              :y2="y"
              stroke="#F0F0F0"
              stroke-width="1"
              stroke-dasharray="4,4"
            />
          </g>

          <!-- 数据绘制 -->
          <g class="data-layer">
            <!-- 折线图 (Line Chart) -->
            <template v-if="type === 'line'">
              <!-- 渐变填充区域 -->
              <defs>
                <linearGradient :id="`gradient-${uid}`" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" :stop-color="color" stop-opacity="0.25"/>
                  <stop offset="100%" :stop-color="color" stop-opacity="0.02"/>
                </linearGradient>
              </defs>
              <path
                :d="areaPath"
                :fill="`url(#gradient-${uid})`"
              />
              <path
                :d="linePath"
                fill="none"
                :stroke="color"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <!-- 数据点 (可点击) -->
              <circle
                v-for="(pt, index) in points"
                :key="`pt-${index}`"
                :cx="pt.x"
                :cy="pt.y"
                :r="selectedIndex === index ? 6 : 4"
                fill="#fff"
                :stroke="color"
                :stroke-width="selectedIndex === index ? 3 : 2"
                class="data-point"
                @click="handlePointClick(index)"
              />
            </template>

            <!-- 柱状图 (Bar Chart) -->
            <template v-else-if="type === 'bar'">
              <defs>
                <linearGradient v-for="(bar, index) in bars" :key="`bar-grad-${index}`" :id="`bar-gradient-${uid}-${index}`" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" :stop-color="bar.color || color" stop-opacity="1"/>
                  <stop offset="100%" :stop-color="bar.color || color" stop-opacity="0.6"/>
                </linearGradient>
              </defs>
              <rect
                v-for="(bar, index) in bars"
                :key="`bar-${index}`"
                :x="bar.x"
                :y="bar.y"
                :width="bar.width"
                :height="bar.height"
                :fill="`url(#bar-gradient-${uid}-${index})`"
                rx="4"
                class="data-bar"
                @click="handlePointClick(index)"
              />
            </template>
          </g>

          <!-- X轴线 -->
          <line
            :x1="padding.left"
            :y1="height - padding.bottom"
            :x2="chartWidth - padding.right"
            :y2="height - padding.bottom"
            stroke="#E8E8E8"
            stroke-width="1"
          />
        </svg>

        <!-- Y轴刻度标签 (使用 view 绝对定位) - 减少密度 -->
        <view
          v-for="(val, index) in yLabels"
          :key="`ylabel-${index}`"
          class="y-label"
          :style="{
            top: gridLines[index] + 'px',
            left: (padding.left - 6) + 'px'
          }"
        >
          <text class="label-text">{{ val }}</text>
        </view>

        <!-- X轴刻度标签 -->
        <view
          v-for="(pt, index) in displayXLabels"
          :key="`xlabel-${index}`"
          class="x-label"
          :style="{
            top: (height - padding.bottom + 6) + 'px',
            left: pt.x + 'px'
          }"
        >
          <text class="label-text">{{ pt.label }}</text>
        </view>

        <!-- 悬浮提示框 (点击显示) -->
        <view
          v-if="selectedIndex !== null && points[selectedIndex]"
          class="tooltip"
          :style="{
            top: (points[selectedIndex].y - 45) + 'px',
            left: Math.min(Math.max(points[selectedIndex].x, 50), chartWidth - 50) + 'px'
          }"
        >
          <view class="tooltip-content">
            <text class="tooltip-date">{{ data[selectedIndex]?.label }}</text>
            <text class="tooltip-value" :style="{ color: color }">{{ data[selectedIndex]?.value }} {{ unit }}</text>
          </view>
          <view class="tooltip-arrow" :style="{ borderTopColor: '#333' }"></view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <text class="empty-icon">📊</text>
      <text class="empty-text">暂无数据</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'

const props = defineProps({
  title: String,
  unit: String,
  type: {
    type: String,
    default: 'line' // line | bar
  },
  data: {
    type: Array as () => Array<{ label: string, value: number, color?: string }>,
    default: () => []
  },
  width: {
    type: Number,
    default: 0 // 0 表示自适应
  },
  height: {
    type: Number,
    default: 180
  },
  color: {
    type: String,
    default: '#4CAF50'
  }
})

// 生成唯一ID用于渐变
const uid = Math.random().toString(36).substring(2, 9)

// 选中的数据点索引
const selectedIndex = ref<number | null>(null)

// 自适应宽度
const containerWidth = ref(300)
const chartWidth = computed(() => props.width > 0 ? props.width : containerWidth.value)

// 获取容器宽度
onMounted(() => {
  // 使用 uni.createSelectorQuery 获取容器宽度
  const query = uni.createSelectorQuery()
  query.select('.chart-container').boundingClientRect((rect: any) => {
    if (rect && rect.width > 0) {
      containerWidth.value = rect.width - 48 // 减去 padding
    }
  }).exec()
})

// 点击数据点
const handlePointClick = (index: number) => {
  if (selectedIndex.value === index) {
    selectedIndex.value = null // 再次点击取消选中
  } else {
    selectedIndex.value = index
  }
}

const padding = { top: 25, right: 10, bottom: 28, left: 35 }

// 计算 Y 轴范围
const range = computed(() => {
  if (!props.data.length) return { min: 0, max: 100 }
  const values = props.data.map(d => d.value)
  let min = Math.min(...values)
  let max = Math.max(...values)

  // 增加一点缓冲
  const buffer = (max - min) * 0.12
  if (buffer === 0) {
    min = 0
    max = max * 1.2 || 100
  } else {
    min = Math.max(0, min - buffer)
    max = max + buffer
  }
  return { min, max }
})

// 计算网格线位置 (Y轴) - 减少到4条
const gridCount = 4
const gridLines = computed(() => {
  const lines = []
  const step = (props.height - padding.top - padding.bottom) / (gridCount - 1)
  for (let i = 0; i < gridCount; i++) {
    lines.push(padding.top + i * step)
  }
  return lines
})

const yLabels = computed(() => {
  const { min, max } = range.value
  const step = (max - min) / (gridCount - 1)
  const labels = []
  for (let i = 0; i < gridCount; i++) {
    const val = max - i * step
    // 格式化数值 - 更简洁
    if (val >= 1000) {
      labels.push((val / 1000).toFixed(1) + 'k')
    } else if (val >= 100) {
      labels.push(val.toFixed(0))
    } else {
      labels.push(val.toFixed(1))
    }
  }
  return labels
})

// 计算数据点坐标
const points = computed(() => {
  if (!props.data.length) return []
  const { min, max } = range.value
  const drawableHeight = props.height - padding.top - padding.bottom
  const drawableWidth = chartWidth.value - padding.left - padding.right

  // X轴步长
  const xStep = props.data.length > 1 ? drawableWidth / (props.data.length - 1) : 0

  return props.data.map((item, index) => {
    // 归一化 Y 值
    const normalizedY = (item.value - min) / (max - min || 1)
    const x = padding.left + (props.data.length > 1 ? index * xStep : drawableWidth / 2)
    const y = props.height - padding.bottom - normalizedY * drawableHeight

    return {
      x,
      y,
      value: item.value >= 1000 ? (item.value / 1000).toFixed(1) + 'k' : item.value.toFixed(0),
      label: item.label
    }
  })
})

// X轴标签 - 智能显示（避免重叠）
const displayXLabels = computed(() => {
  if (points.value.length <= 5) return points.value
  // 数据点多时，只显示首、中、尾
  const result = []
  const len = points.value.length
  result.push(points.value[0])
  if (len > 2) {
    result.push(points.value[Math.floor(len / 2)])
  }
  result.push(points.value[len - 1])
  return result
})

// 折线路径
const linePath = computed(() => {
  if (points.value.length < 2) return ''
  return 'M ' + points.value.map(p => `${p.x},${p.y}`).join(' L ')
})

// 区域填充路径
const areaPath = computed(() => {
  if (points.value.length < 2) return ''
  const baseline = props.height - padding.bottom
  const start = `M ${points.value[0].x},${baseline}`
  const line = points.value.map(p => `L ${p.x},${p.y}`).join(' ')
  const end = `L ${points.value[points.value.length - 1].x},${baseline} Z`
  return `${start} ${line} ${end}`
})

// 柱状图数据
const bars = computed(() => {
  if (props.type !== 'bar' || !points.value.length) return []
  const { max } = range.value
  const drawableHeight = props.height - padding.top - padding.bottom
  const drawableWidth = chartWidth.value - padding.left - padding.right
  const barWidth = Math.min(24, (drawableWidth / props.data.length) * 0.65)

  return points.value.map((pt, index) => {
    const originalValue = props.data[index].value
    const barHeight = Math.max(2, (originalValue / max) * drawableHeight)
    const zeroY = props.height - padding.bottom
    const topY = zeroY - barHeight

    return {
      x: pt.x - barWidth / 2,
      y: topY,
      width: barWidth,
      height: barHeight,
      color: props.data[index].color
    }
  })
})
</script>

<style lang="scss" scoped>
.chart-container {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  width: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.chart-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.chart-unit {
  font-size: 22rpx;
  color: #999;
}

.chart-content {
  width: 100%;
  overflow: hidden;
}

.chart-wrapper {
  position: relative;
  margin: 0 auto;
}

.chart-svg {
  display: block;
}

/* 数据点可点击样式 */
.data-point,
.data-bar {
  cursor: pointer;
}

/* Y轴标签 */
.y-label {
  position: absolute;
  transform: translateY(-50%);
  text-align: right;
}

.y-label .label-text {
  font-size: 18rpx;
  color: #AAAAAA;
  white-space: nowrap;
}

/* X轴标签 */
.x-label {
  position: absolute;
  transform: translateX(-50%);
  text-align: center;
}

.x-label .label-text {
  font-size: 18rpx;
  color: #AAAAAA;
  white-space: nowrap;
}

/* 悬浮提示框 */
.tooltip {
  position: absolute;
  transform: translateX(-50%);
  z-index: 100;
  pointer-events: none;
}

.tooltip-content {
  background: #333;
  border-radius: 8rpx;
  padding: 10rpx 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.15);
}

.tooltip-date {
  font-size: 20rpx;
  color: #ccc;
}

.tooltip-value {
  font-size: 24rpx;
  font-weight: 600;
}

.tooltip-arrow {
  width: 0;
  height: 0;
  border-left: 8rpx solid transparent;
  border-right: 8rpx solid transparent;
  border-top: 8rpx solid #333;
  margin: 0 auto;
}

.empty-state {
  width: 100%;
  height: 200rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
}

.empty-icon {
  font-size: 64rpx;
  opacity: 0.5;
}

.empty-text {
  font-size: 24rpx;
  color: #999;
}
</style>
