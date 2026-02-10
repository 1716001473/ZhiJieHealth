<template>
  <div class="users-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <div>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索用户名/昵称"
              style="width: 200px; margin-right: 12px;"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </template>

      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :size="36" :src="row.avatar_url || ''" />
          </template>
        </el-table-column>
        <el-table-column prop="health_goal" label="健康目标" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="getGoalType(row.health_goal)">
              {{ getGoalLabel(row.health_goal) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="health_conditions" label="健康状况" width="150">
          <template #default="{ row }">
            <span class="text-muted">{{ row.health_conditions || '无' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180" />
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchUsers"
          @current-change="fetchUsers"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

const loading = ref(false)
const searchKeyword = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const users = ref([])

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (searchKeyword.value) params.keyword = searchKeyword.value

    const res = await api.get('/admin/users', { params })
    users.value = res.data.items
    total.value = res.data.total
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  fetchUsers()
}

const getGoalLabel = (goal) => {
  const map = { lose_weight: '减重', gain_muscle: '增肌', maintain: '保持' }
  return map[goal] || '保持'
}

const getGoalType = (goal) => {
  const map = { lose_weight: 'warning', gain_muscle: 'success', maintain: '' }
  return map[goal] || ''
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.text-muted {
  color: #999;
  font-size: 13px;
}
</style>
