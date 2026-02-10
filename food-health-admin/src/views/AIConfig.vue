<template>
  <div class="ai-config-page">
    <!-- 顶部提示 -->
    <el-alert
      title="配置需在服务器 .env 文件中修改后重启生效"
      type="warning"
      show-icon
      :closable="false"
      style="margin-bottom: 20px;"
    />

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🤖 豆包 AI 配置</span>
              <el-tag type="success">主要服务</el-tag>
            </div>
          </template>

          <el-form label-width="100px">
            <el-form-item label="API Key">
              <el-input :value="doubaoConfig.apiKey" disabled placeholder="未配置" />
            </el-form-item>
            <el-form-item label="Base URL">
              <el-input :value="doubaoConfig.baseUrl" disabled />
            </el-form-item>
            <el-form-item label="模型名称">
              <el-input :value="doubaoConfig.model" disabled placeholder="未配置" />
            </el-form-item>
            <el-form-item label="状态">
              <el-tag :type="doubaoConfig.status ? 'success' : 'danger'" size="large">
                {{ doubaoConfig.status ? '✅ 已配置' : '❌ 未配置' }}
              </el-tag>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🔍 百度 AI 配置</span>
              <el-tag type="info">备用服务</el-tag>
            </div>
          </template>

          <el-form label-width="100px">
            <el-form-item label="API Key">
              <el-input :value="baiduConfig.apiKey" disabled placeholder="未配置" />
            </el-form-item>
            <el-form-item label="Secret Key">
              <el-input value="********" disabled placeholder="未配置" />
            </el-form-item>
            <el-form-item label="状态">
              <el-tag :type="baiduConfig.status ? 'success' : 'warning'" size="large">
                {{ baiduConfig.status ? '✅ 待机中' : '⚠️ 未配置' }}
              </el-tag>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>🧠 DeepSeek AI 配置</span>
              <el-tag type="info">营养分析</el-tag>
            </div>
          </template>

          <el-form label-width="100px">
            <el-form-item label="API Key">
              <el-input :value="deepseekConfig.apiKey" disabled placeholder="未配置" />
            </el-form-item>
            <el-form-item label="Base URL">
              <el-input :value="deepseekConfig.baseUrl" disabled />
            </el-form-item>
            <el-form-item label="状态">
              <el-tag :type="deepseekConfig.status ? 'success' : 'danger'" size="large">
                {{ deepseekConfig.status ? '✅ 已配置' : '❌ 未配置' }}
              </el-tag>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span>📊 服务状态概览</span>
          </template>

          <div class="status-overview">
            <div class="status-item">
              <span class="status-label">API 服务</span>
              <el-tag :type="apiStatus.running ? 'success' : 'danger'">
                {{ apiStatus.running ? '运行中' : '离线' }}
              </el-tag>
            </div>
            <el-divider />
            <div class="status-item">
              <span class="status-label">API 版本</span>
              <span class="status-value">{{ apiStatus.version }}</span>
            </div>
            <el-divider />
            <div class="status-item">
              <span class="status-label">食物识别</span>
              <el-tag :type="apiStatus.recognition ? 'success' : 'danger'">
                {{ apiStatus.recognition ? '可用' : '不可用' }}
              </el-tag>
            </div>
            <el-divider />
            <div class="status-item">
              <span class="status-label">营养分析</span>
              <el-tag type="success">可用</el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const doubaoConfig = reactive({
  apiKey: '',
  baseUrl: '',
  model: '',
  status: false
})

const baiduConfig = reactive({
  apiKey: '',
  status: false
})

const deepseekConfig = reactive({
  apiKey: '',
  baseUrl: '',
  status: false
})

const apiStatus = reactive({
  running: false,
  version: '',
  recognition: false
})

const fetchStatus = async () => {
  try {
    const res = await api.get('/status')
    const data = res.data
    const features = data.features || {}
    const aiConfig = data.ai_config || {}

    // API 状态
    apiStatus.running = data.status === 'running'
    apiStatus.version = data.version || 'unknown'
    apiStatus.recognition = features.recognition

    // 豆包配置
    if (aiConfig.doubao) {
      doubaoConfig.status = aiConfig.doubao.configured
      doubaoConfig.apiKey = aiConfig.doubao.api_key || ''
      doubaoConfig.baseUrl = aiConfig.doubao.base_url || ''
      doubaoConfig.model = aiConfig.doubao.model || ''
    }

    // 百度配置
    if (aiConfig.baidu) {
      baiduConfig.status = aiConfig.baidu.configured
      baiduConfig.apiKey = aiConfig.baidu.api_key || ''
    }

    // DeepSeek 配置
    if (aiConfig.deepseek) {
      deepseekConfig.status = aiConfig.deepseek.configured
      deepseekConfig.apiKey = aiConfig.deepseek.api_key || ''
      deepseekConfig.baseUrl = aiConfig.deepseek.base_url || ''
    }

    ElMessage.success('配置信息已加载')
  } catch (err) {
    console.error('获取状态失败', err)
  }
}

onMounted(() => {
  fetchStatus()
})
</script>

<style scoped>
.ai-config-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-overview {
  padding: 10px 0;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.status-label {
  color: #666;
}

.status-value {
  font-weight: 600;
  color: #333;
}
</style>
