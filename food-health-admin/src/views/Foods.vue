<template>
  <div class="foods-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>食物管理</span>
          <div class="header-actions">
            <el-select v-model="filterCategory" placeholder="分类筛选" clearable style="width: 120px; margin-right: 12px;" @change="handleSearch">
              <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
            </el-select>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索食物名称"
              style="width: 200px; margin-right: 12px;"
              clearable
              @keyup.enter="handleSearch"
            />
          </div>
        </div>
      </template>

      <el-table :data="foods" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="食物名称" width="150" />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="calories" label="热量(kcal)" width="100" />
        <el-table-column prop="protein" label="蛋白质(g)" width="100" />
        <el-table-column prop="fat" label="脂肪(g)" width="100" />
        <el-table-column prop="carbohydrate" label="碳水(g)" width="100" />
        <el-table-column prop="health_rating" label="健康评级" width="100">
          <template #default="{ row }">
            <el-tag :type="getRatingType(row.health_rating)">{{ row.health_rating }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchFoods"
          @current-change="fetchFoods"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/utils/api'

const loading = ref(false)
const searchKeyword = ref('')
const filterCategory = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const foods = ref([])
const categories = ref([])

const fetchFoods = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filterCategory.value) params.category = filterCategory.value

    const res = await api.get('/admin/foods', { params })
    foods.value = res.data.items
    total.value = res.data.total
    if (res.data.categories) {
      categories.value = res.data.categories
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  fetchFoods()
}

const getRatingType = (rating) => {
  const map = { '推荐': 'success', '适量': 'warning', '少食': 'danger' }
  return map[rating] || 'info'
}

onMounted(() => {
  fetchFoods()
})
</script>

<style scoped>
.foods-page {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
