<template>
  <div class="recipes-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>精品食谱管理</span>
          <div class="header-actions">
            <el-select v-model="filterCategory" placeholder="分类筛选" clearable style="width: 120px; margin-right: 12px;" @change="handleSearch">
              <el-option label="早餐" value="早餐" />
              <el-option label="午餐" value="午餐" />
              <el-option label="晚餐" value="晚餐" />
              <el-option label="汤羹" value="汤羹" />
              <el-option label="凉菜" value="凉菜" />
              <el-option label="烘焙" value="烘焙" />
              <el-option label="轻食" value="轻食" />
              <el-option label="控糖" value="控糖" />
              <el-option label="增肌" value="增肌" />
            </el-select>
            <el-input
              v-model="searchKeyword"
              placeholder="搜索食谱名称"
              style="width: 180px; margin-right: 12px;"
              clearable
              @keyup.enter="handleSearch"
            />
            <el-button type="primary" @click="handleAdd">新增食谱</el-button>
          </div>
        </div>
      </template>

      <el-table :data="recipes" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column label="食谱" width="280">
          <template #default="{ row }">
            <div class="recipe-info">
              <el-image :src="getImageUrl(row.image_url)" style="width: 60px; height: 60px; border-radius: 8px;" fit="cover" />
              <div class="recipe-text">
                <div class="recipe-name">{{ row.name }}</div>
                <div class="recipe-desc">{{ row.description }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="标签" width="180">
          <template #default="{ row }">
            <el-tag v-for="tag in parseTags(row.tags).slice(0, 3)" :key="tag" size="small" class="tag-item">
              {{ tag }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="难度" width="80" />
        <el-table-column prop="cook_time" label="烹饪时间" width="100" />
        <el-table-column prop="calories" label="热量" width="100">
          <template #default="{ row }">
            {{ row.calories || '-' }} kcal
          </template>
        </el-table-column>
        <el-table-column prop="is_featured" label="精选" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.is_featured" @change="handleToggleFeatured(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchRecipes"
          @current-change="fetchRecipes"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

const loading = ref(false)
const searchKeyword = ref('')
const filterCategory = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const recipes = ref([])

const fetchRecipes = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams({
      page: page.value,
      page_size: pageSize.value,
    })
    if (filterCategory.value) params.append('category', filterCategory.value)
    if (searchKeyword.value) params.append('keyword', searchKeyword.value)

    const res = await api.get(`/premium/recipes?${params}`)
    recipes.value = res.data.items
    total.value = res.data.total
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  fetchRecipes()
}

const handleAdd = () => {
  ElMessage.info('新增食谱功能开发中...')
}

const handleEdit = (row) => {
  ElMessage.info(`编辑食谱: ${row.name}`)
}

const handleToggleFeatured = async (row) => {
  try {
    await api.put(`/premium/recipes/${row.id}`, { is_featured: row.is_featured })
    ElMessage.success(row.is_featured ? '已设为精选' : '已取消精选')
  } catch (err) {
    row.is_featured = !row.is_featured
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确定要删除食谱 "${row.name}" 吗？`, '警告', { type: 'error' })
  try {
    await api.delete(`/premium/recipes/${row.id}`)
    ElMessage.success('删除成功')
    fetchRecipes()
  } catch (err) {
    console.error(err)
  }
}

const getImageUrl = (url) => {
  if (!url) return '/vite.svg'
  if (url.startsWith('http')) return url
  return url
}

const parseTags = (tags) => {
  if (!tags) return []
  if (Array.isArray(tags)) return tags
  try {
    if (typeof tags === 'string' && tags.startsWith('[')) {
      return JSON.parse(tags)
    }
    return tags.split(',').map(t => t.trim()).filter(Boolean)
  } catch {
    return []
  }
}

onMounted(() => {
  fetchRecipes()
})
</script>

<style scoped>
.recipes-page {
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

.recipe-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.recipe-text {
  flex: 1;
  min-width: 0;
}

.recipe-name {
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recipe-desc {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

.tag-item {
  margin-right: 4px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
