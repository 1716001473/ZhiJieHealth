<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-users">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-title">注册用户</p>
              <h3 class="stat-value">{{ stats.totalUsers }}</h3>
              <p class="stat-sub">累计注册</p>
            </div>
            <div class="stat-icon">
              <el-icon><User /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-recipes">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-title">精品食谱</p>
              <h3 class="stat-value">{{ stats.totalRecipes }}</h3>
              <p class="stat-sub">本周新增 {{ stats.weekRecipes }} 条</p>
            </div>
            <div class="stat-icon">
              <el-icon><Dish /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-foods">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-title">食物库</p>
              <h3 class="stat-value">{{ stats.totalFoods }}</h3>
              <p class="stat-sub">覆盖 {{ stats.foodCategories }} 个分类</p>
            </div>
            <div class="stat-icon">
              <el-icon><Bowl /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card-requests">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-title">今日识别</p>
              <h3 class="stat-value">{{ stats.todayRequests }}</h3>
              <p class="stat-sub">AI 识别次数</p>
            </div>
            <div class="stat-icon">
              <el-icon><Camera /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-section">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>近7日请求趋势</span>
            </div>
          </template>
          <div ref="requestChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>食物分类占比</span>
            </div>
          </template>
          <div ref="categoryChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最新动态 -->
    <el-row :gutter="20" class="activity-section">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最新精品食谱</span>
              <el-button type="primary" text @click="$router.push('/recipes')">
                查看更多
              </el-button>
            </div>
          </template>
          <el-table :data="latestRecipes" style="width: 100%">
            <el-table-column prop="name" label="食谱名称" />
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="calories" label="热量" width="100">
              <template #default="{ row }">
                {{ row.calories }} kcal
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>AI 服务状态</span>
            </div>
          </template>
          <div class="service-status">
            <div class="service-item">
              <div class="service-info">
                <span class="service-name">豆包 AI</span>
                <span class="service-desc">主要识别服务</span>
              </div>
              <el-tag :type="aiStatus.doubao ? 'success' : 'danger'">
                {{ aiStatus.doubao ? '已配置' : '未配置' }}
              </el-tag>
            </div>
            <el-divider />
            <div class="service-item">
              <div class="service-info">
                <span class="service-name">百度 AI</span>
                <span class="service-desc">备用识别服务</span>
              </div>
              <el-tag :type="aiStatus.baidu ? 'success' : 'warning'">
                {{ aiStatus.baidu ? '待机中' : '未配置' }}
              </el-tag>
            </div>
            <el-divider />
            <div class="service-item">
              <div class="service-info">
                <span class="service-name">DeepSeek AI</span>
                <span class="service-desc">营养分析补充</span>
              </div>
              <el-tag :type="aiStatus.deepseek ? 'success' : 'danger'">
                {{ aiStatus.deepseek ? '已配置' : '未配置' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { User, Dish, Bowl, Camera } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/utils/api'

// 统计数据
const stats = reactive({
  totalUsers: 0,
  totalRecipes: 0,
  weekRecipes: 0,
  totalFoods: 0,
  foodCategories: 0,
  todayRequests: 0,
})

// AI 服务状态
const aiStatus = reactive({
  doubao: false,
  baidu: false,
  deepseek: false,
})

// 最新食谱
const latestRecipes = ref([])

// 分类统计数据（饼图）
const categoryStats = ref([])

// 图表引用
const requestChartRef = ref(null)
const categoryChartRef = ref(null)
let requestChart = null
let categoryChart = null

// 获取看板数据
const fetchDashboardData = async () => {
  try {
    const res = await api.get('/admin/dashboard/stats')
    const data = res.data

    stats.totalUsers = data.total_users || 0
    stats.totalRecipes = data.total_recipes || 0
    stats.weekRecipes = data.week_recipes || 0
    stats.totalFoods = data.total_foods || 0
    stats.foodCategories = data.food_categories || 0
    stats.todayRequests = data.today_requests || 0

    latestRecipes.value = data.latest_recipes || []
    categoryStats.value = data.category_stats || []

    // 数据加载后更新饼图
    await nextTick()
    updateCategoryChart()
  } catch (err) {
    console.error('获取看板数据失败', err)
  }
}

// 获取 AI 服务状态
const fetchAIStatus = async () => {
  try {
    const res = await api.get('/status')
    const data = res.data
    const features = data.features || {}
    aiStatus.doubao = features.doubao_configured || false
    aiStatus.baidu = features.baidu_configured || false
    aiStatus.deepseek = features.deepseek_configured || false
  } catch (err) {
    console.error('获取AI状态失败', err)
  }
}

// 初始化请求趋势图（保留演示数据，因为暂无按日统计 API）
const initRequestChart = () => {
  if (requestChartRef.value) {
    requestChart = echarts.init(requestChartRef.value)
    requestChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '识别请求',
          type: 'line',
          smooth: true,
          data: [0, 0, 0, 0, 0, 0, stats.todayRequests || 0],
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(102, 126, 234, 0.4)' },
              { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
            ])
          },
          lineStyle: { color: '#667eea' },
          itemStyle: { color: '#667eea' }
        }
      ]
    })
  }
}

// 更新分类占比饼图（使用真实数据）
const updateCategoryChart = () => {
  if (categoryChartRef.value) {
    if (!categoryChart) {
      categoryChart = echarts.init(categoryChartRef.value)
    }
    const chartData = categoryStats.value.length > 0
      ? categoryStats.value
      : [{ name: '暂无数据', value: 1 }]

    categoryChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          label: { show: true, position: 'outside' },
          data: chartData,
          color: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#43e97b', '#ffa726', '#ef5350']
        }
      ]
    })
  }
}

const handleResize = () => {
  requestChart?.resize()
  categoryChart?.resize()
}

onMounted(async () => {
  initRequestChart()
  updateCategoryChart()
  window.addEventListener('resize', handleResize)
  // 并行获取数据
  await Promise.all([fetchDashboardData(), fetchAIStatus()])
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  requestChart?.dispose()
  categoryChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 8px;
  overflow: hidden;
}

.stat-card .el-card__body {
  padding: 20px;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-title {
  font-size: 14px;
  color: #666;
  margin: 0 0 8px 0;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #333;
}

.stat-change,
.stat-sub {
  font-size: 12px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-change.up {
  color: #52c41a;
}

.stat-sub {
  color: #999;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.stat-card-users .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-card-recipes .stat-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-card-foods .stat-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.stat-card-requests .stat-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }

.chart-section,
.activity-section {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
}

.service-status {
  padding: 10px 0;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.service-info {
  display: flex;
  flex-direction: column;
}

.service-name {
  font-weight: 500;
  color: #333;
}

.service-desc {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
</style>
