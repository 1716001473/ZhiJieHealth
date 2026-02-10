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
            <!-- 折线图 (Line Chart) - 平滑曲线 -->
            <template v-if="type === 'line'">
              <!-- 渐变填充区域 -->
              <defs>
                <linearGradient :id="`gradient-${uid}`" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" :stop-color="color" stop-opacity="0.3"/>
                  <stop offset="100%" :stop-color="color" stop-opacity="0.02"/>
                </linearGradient>
              </defs>
              <path
                :d="smoothAreaPath"
                :fill="`url(#gradient-${uid})`"
              />
              <path
                :d="smoothLinePath"
                fill="none"
                :stroke="color"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <!-- 智能数据点 -->
              <template v-for="(pt, index) in points" :key="`pt-${index}`">
                <!-- 最高值标记 -->
                <circle
                  v-if="index === maxIndex"
                  :cx="pt.x" :cy="pt.y" r="7"
                  fill="#fff" stroke="#FF5722" stroke-width="2.5"
                  class="data-point" @click="handlePointClick(index)"
                />
                <!-- 最低值标记 -->
                <circle
                  v-else-if="index === minIndex"
                  :cx="pt.x" :cy="pt.y" r="7"
                  fill="#fff" stroke="#2196F3" stroke-width="2.5"
                  class="data-point" @click="handlePointClick(index)"
                />
                <!-- 最新值标记 (最后一个点) -->
                <circle
                  v-else-if="index === points.length - 1"
                  :cx="pt.x" :cy="pt.y" r="6"
                  :fill="color" stroke="#fff" stroke-width="2"
                  class="data-point" @click="handlePointClick(index)"
                />
                <!-- 选中的点 -->
                <circle
                  v-else-if="selectedIndex === index"
                  :cx="pt.x" :cy="pt.y" r="6"
                  fill="#fff" :stroke="color" stroke-width="3"
                  class="data-point" @click="handlePointClick(index)"
                />
                <!-- 普通点 - 数据少时显示，数据多时隐藏 -->
                <circle
                  v-else-if="data.length <= 10"
                  :cx="pt.x" :cy="pt.y" r="3"
                  fill="#fff" :stroke="color" stroke-width="1.5"
                  class="data-point" @click="handlePointClick(index)"
                />
              </template>
            </template>

            <!-- 柱状图 (Bar Chart) + 趋势线叠加 -->
            <template v-else-if="type === 'bar'">
              <!-- 柱子渐变定义 -->
              <defs>
                <linearGradient v-for="(bar, index) in bars" :key="`bar-grad-${index}`" :id="`bar-gradient-${uid}-${index}`" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" :stop-color="bar.color || color" stop-opacity="1"/>
                  <stop offset="100%" :stop-color="bar.color || color" stop-opacity="0.5"/>
                </linearGradient>
                <!-- 趋势线渐变 -->
                <linearGradient :id="`trend-gradient-${uid}`" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" :stop-color="color" stop-opacity="0.15"/>
                  <stop offset="100%" :stop-color="color" stop-opacity="0.01"/>
                </linearGradient>
              </defs>

              <!-- 趋势线区域填充 (在柱子下面) -->
              <path
                v-if="points.length >= 2"
                :d="smoothAreaPath"
                :fill="`url(#trend-gradient-${uid})`"
              />

              <!-- 柱子 -->
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
                :opacity="highlightBar(index)"
                @click="handlePointClick(index)"
              />

              <!-- 趋势线 (在柱子上面) -->
              <path
                v-if="points.length >= 2"
                :d="smoothLinePath"
                fill="none"
                :stroke="color"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-dasharray="6,3"
                opacity="0.6"
              />

              <!-- 关键点标记 -->
              <template v-for="(pt, index) in points" :key="`bar-pt-${index}`">
                <!-- 最高值 -->
                <circle
                  v-if="index === maxIndex"
                  :cx="pt.x" :cy="pt.y" r="5"
                  fill="#FF5722" stroke="#fff" stroke-width="2"
                />
                <!-- 最低值 -->
                <circle
                  v-else-if="index === minIndex && data[index].value > 0"
                  :cx="pt.x" :cy="pt.y" r="5"
                  fill="#2196F3" stroke="#fff" stroke-width="2"
                />
                <!-- 最新值 -->
                <circle
                  v-else-if="index === points.length - 1"
                  :cx="pt.x" :cy="pt.y" r="4"
                  :fill="color" stroke="#fff" stroke-width="1.5"
                />
              </template>
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

        <!-- Y轴刻度标签 -->
        <view
          v-for="(val, index) in yLabels"
          :key="`ylabel-${index}`"
          class="y-label"
          :style="{
            top: gridLines[index] + 'px',
            left: '0px',
            width: (padding.left - 6) + 'px'
          }"
        >
          <text class="label-text">{{ val }}</text>
        </view>

        <!-- X轴刻度标签 - 智能间隔 -->
        <view
          v-for="(pt, index) in displayXLabels"
          :key="`xlabel-${index}`"
          class="x-label"
          :style="{
            top: (height - padding.bottom + 6) + 'px',
            left: pt.x + 'px'
          }"
        >
          <text class="label-text">{{ pt.displayLabel }}</text>
        </view>

        <!-- 悬浮提示框 (点击显示) -->
        <view
          v-if="selectedIndex !== null && points[selectedIndex]"
          class="tooltip"
          :style="{
            top: (points[selectedIndex].y - 55) + 'px',
            left: Math.min(Math.max(points[selectedIndex].x, 60), chartWidth - 60) + 'px'
          }"
        >
          <view class="tooltip-content">
            <text class="tooltip-date">{{ data[selectedIndex]?.label }}</text>
            <text class="tooltip-value" :style="{ color: color }">{{ data[selectedIndex]?.value }} {{ unit }}</text>
            <text class="tooltip-tag" v-if="selectedIndex === maxIndex">📈 最高</text>
            <text class="tooltip-tag" v-else-if="selectedIndex === minIndex">📉 最低</text>
            <text class="tooltip-tag" v-else-if="selectedIndex === points.length - 1">🔵 最新</text>
          </view>
          <view class="tooltip-arrow"></view>
        </view>
      </view>

      <!-- 图例 -->
      <view class="chart-legend" v-if="data.length > 1">
        <view class="legend-item">
          <view class="legend-dot" style="background: #FF5722;"></view>
          <text class="legend-text">最高 {{ maxValueDisplay }}</text>
        </view>
        <view class="legend-item">
          <view class="legend-dot" style="background: #2196F3;"></view>
          <text class="legend-text">最低 {{ minValueDisplay }}</text>
        </view>
        <view class="legend-item">
          <view class="legend-dot" :style="{ background: color }"></view>
          <text class="legend-text">最新 {{ latestValueDisplay }}</text>
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
    default: 200
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
  const query = uni.createSelectorQuery()
  query.select('.chart-container').boundingClientRect((rect: any) => {
    if (rect && rect.width > 0) {
      containerWidth.value = rect.width - 48
    }
  }).exec()
})

// 点击数据点
const handlePointClick = (index: number) => {
  if (selectedIndex.value === index) {
    selectedIndex.value = null
  } else {
    selectedIndex.value = index
  }
}

// 根据容器宽度动态计算左边距，给Y轴标签留出空间
const dynamicLeftPadding = computed(() => {
  const w = containerWidth.value
  if (w < 200) return 60  // 极小屏
  if (w < 300) return 55  // 小屏设备
  return 50                // 正常屏幕
})

const padding = computed(() => ({
  top: 25,
  right: 15,
  bottom: 28,
  left: dynamicLeftPadding.value
}))

// 计算最高/最低值索引
const maxIndex = computed(() => {
  if (!props.data.length) return -1
  let idx = 0
  for (let i = 1; i < props.data.length; i++) {
    if (props.data[i].value > props.data[idx].value) idx = i
  }
  return idx
})

const minIndex = computed(() => {
  if (!props.data.length) return -1
  let idx = 0
  for (let i = 1; i < props.data.length; i++) {
    if (props.data[i].value < props.data[idx].value) idx = i
  }
  return idx
})

// 图例显示值
const formatVal = (v: number) => {
  if (v >= 1000) return (v / 1000).toFixed(1) + 'k'
  if (v >= 100) return v.toFixed(0)
  return v.toFixed(1)
}

const maxValueDisplay = computed(() => {
  if (maxIndex.value < 0) return '--'
  return formatVal(props.data[maxIndex.value].value)
})

const minValueDisplay = computed(() => {
  if (minIndex.value < 0) return '--'
  return formatVal(props.data[minIndex.value].value)
})

const latestValueDisplay = computed(() => {
  if (!props.data.length) return '--'
  return formatVal(props.data[props.data.length - 1].value)
})

// 柱子高亮：最高/最低/最新 不透明度更高
const highlightBar = (index: number) => {
  if (index === maxIndex.value || index === minIndex.value || index === props.data.length - 1) {
    return 1
  }
  return 0.8
}

// 计算 Y 轴范围
const range = computed(() => {
  if (!props.data.length) return { min: 0, max: 100 }
  const values = props.data.map(d => d.value)
  let min = Math.min(...values)
  let max = Math.max(...values)

  const buffer = (max - min) * 0.15
  if (buffer === 0) {
    min = 0
    max = max * 1.2 || 100
  } else {
    min = Math.max(0, min - buffer)
    max = max + buffer
  }
  return { min, max }
})

// 计算网格线位置 (Y轴)
const gridCount = 4
const gridLines = computed(() => {
  const lines = []
  const step = (props.height - padding.value.top - padding.value.bottom) / (gridCount - 1)
  for (let i = 0; i < gridCount; i++) {
    lines.push(padding.value.top + i * step)
  }
  return lines
})

const yLabels = computed(() => {
  const { min, max } = range.value
  const step = (max - min) / (gridCount - 1)
  const labels = []
  for (let i = 0; i < gridCount; i++) {
    const val = max - i * step
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
  const drawableHeight = props.height - padding.value.top - padding.value.bottom
  const drawableWidth = chartWidth.value - padding.value.left - padding.value.right

  const xStep = props.data.length > 1 ? drawableWidth / (props.data.length - 1) : 0

  return props.data.map((item, index) => {
    const normalizedY = (item.value - min) / (max - min || 1)
    const x = padding.value.left + (props.data.length > 1 ? index * xStep : drawableWidth / 2)
    const y = props.height - padding.value.bottom - normalizedY * drawableHeight

    return {
      x,
      y,
      value: item.value >= 1000 ? (item.value / 1000).toFixed(1) + 'k' : item.value.toFixed(0),
      label: item.label
    }
  })
})

// X轴标签 - 智能均匀间隔显示
const displayXLabels = computed(() => {
  if (!points.value.length) return []
  const len = points.value.length

  // 数据点 <= 7 个，全部显示
  if (len <= 7) {
    return points.value.map(pt => ({
      ...pt,
      displayLabel: formatXLabel(pt.label)
    }))
  }

  // 数据点多时，均匀选取 5~7 个标签
  const maxLabels = len <= 14 ? 5 : 6
  const result = []
  const step = (len - 1) / (maxLabels - 1)

  for (let i = 0; i < maxLabels; i++) {
    const idx = Math.round(i * step)
    const pt = points.value[idx]
    result.push({
      ...pt,
      displayLabel: formatXLabel(pt.label)
    })
  }

  return result
})

// X轴日期格式化 - 更简洁
const formatXLabel = (label: string) => {
  // label 格式为 "MM-DD"，如 "02-09"
  if (!label) return ''
  const parts = label.split('-')
  if (parts.length === 2) {
    const month = parseInt(parts[0])
    const day = parseInt(parts[1])
    // 1号显示月份，其他显示日
    if (day === 1) return `${month}月`
    return `${month}/${day}`
  }
  return label
}

// 贝塞尔曲线平滑路径生成
const smoothLinePath = computed(() => {
  if (points.value.length < 2) return ''
  return generateSmoothPath(points.value, false)
})

// 贝塞尔曲线平滑区域填充路径
const smoothAreaPath = computed(() => {
  if (points.value.length < 2) return ''
  return generateSmoothPath(points.value, true)
})

// 生成平滑贝塞尔曲线路径
const generateSmoothPath = (pts: Array<{ x: number, y: number }>, closed: boolean) => {
  if (pts.length < 2) return ''

  const baseline = props.height - padding.value.bottom
  let path = `M ${pts[0].x},${pts[0].y}`

  if (pts.length === 2) {
    // 只有两个点，直线连接
    path += ` L ${pts[1].x},${pts[1].y}`
  } else {
    // 使用 Catmull-Rom 样条转贝塞尔曲线
    const tension = 0.3 // 张力系数，越小越平滑

    for (let i = 0; i < pts.length - 1; i++) {
      const p0 = pts[Math.max(0, i - 1)]
      const p1 = pts[i]
      const p2 = pts[i + 1]
      const p3 = pts[Math.min(pts.length - 1, i + 2)]

      // 控制点
      const cp1x = p1.x + (p2.x - p0.x) * tension
      const cp1y = p1.y + (p2.y - p0.y) * tension
      const cp2x = p2.x - (p3.x - p1.x) * tension
      const cp2y = p2.y - (p3.y - p1.y) * tension

      path += ` C ${cp1x},${cp1y} ${cp2x},${cp2y} ${p2.x},${p2.y}`
    }
  }

  if (closed) {
    // 闭合区域填充
    path += ` L ${pts[pts.length - 1].x},${baseline}`
    path += ` L ${pts[0].x},${baseline} Z`
  }

  return path
}

// 柱状图数据
const bars = computed(() => {
  if (props.type !== 'bar' || !points.value.length) return []
  const { max } = range.value
  const drawableHeight = props.height - padding.value.top - padding.value.bottom
  const drawableWidth = chartWidth.value - padding.value.left - padding.value.right
  const barWidth = Math.min(28, (drawableWidth / props.data.length) * 0.6)

  return points.value.map((pt, index) => {
    const originalValue = props.data[index].value
    const barHeight = Math.max(2, (originalValue / max) * drawableHeight)
    const zeroY = props.height - padding.value.bottom
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
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.y-label .label-text {
  font-size: 18rpx;
  color: #AAAAAA;
  white-space: nowrap;
  padding-right: 4px;
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
  border-radius: 10rpx;
  padding: 12rpx 18rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.2);
}

.tooltip-date {
  font-size: 20rpx;
  color: #ccc;
}

.tooltip-value {
  font-size: 26rpx;
  font-weight: 600;
}

.tooltip-tag {
  font-size: 18rpx;
  color: #FFD54F;
  margin-top: 2rpx;
}

.tooltip-arrow {
  width: 0;
  height: 0;
  border-left: 8rpx solid transparent;
  border-right: 8rpx solid transparent;
  border-top: 8rpx solid #333;
  margin: 0 auto;
}

/* 图例 */
.chart-legend {
  display: flex;
  justify-content: center;
  gap: 24rpx;
  margin-top: 16rpx;
  padding-top: 12rpx;
  border-top: 1rpx solid #F5F5F5;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.legend-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
}

.legend-text {
  font-size: 20rpx;
  color: #999;
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
