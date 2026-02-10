<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <img src="/vite.svg" alt="Logo" class="logo-img" />
        <span v-if="!isCollapse" class="logo-text">健康管理后台</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
        class="menu"
        background-color="#001529"
        text-color="#ffffffa6"
        active-text-color="#1890ff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>首页看板</template>
        </el-menu-item>
        
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
        
        <el-menu-item index="/recipes">
          <el-icon><Dish /></el-icon>
          <template #title>精品食谱</template>
        </el-menu-item>
        
        <el-menu-item index="/foods">
          <el-icon><Bowl /></el-icon>
          <template #title>食物管理</template>
        </el-menu-item>
        
        <el-menu-item index="/ai-config">
          <el-icon><Setting /></el-icon>
          <template #title>AI 配置</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <!-- 顶栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-button :icon="isCollapse ? 'Expand' : 'Fold'" text @click="toggleCollapse" />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>后台管理</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRoute.meta?.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">管理员</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 内容区 -->
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  Odometer, User, Dish, Bowl, Setting, 
  ArrowDown, SwitchButton 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const isCollapse = ref(false)

const activeMenu = computed(() => route.path)
const currentRoute = computed(() => route)

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.aside {
  background: #001529;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-img {
  width: 32px;
  height: 32px;
}

.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  margin-left: 12px;
  white-space: nowrap;
}

.menu {
  border-right: none;
}

.menu:not(.el-menu--collapse) {
  width: 220px;
}

.header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  color: #333;
}

.main {
  background: #f0f2f5;
  min-height: 0;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
