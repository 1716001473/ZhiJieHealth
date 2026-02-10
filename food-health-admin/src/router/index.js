import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/Login.vue'),
        meta: { title: '登录', hideLayout: true }
    },
    {
        path: '/',
        redirect: '/dashboard',
        component: () => import('@/layouts/MainLayout.vue'),
        children: [
            {
                path: 'dashboard',
                name: 'Dashboard',
                component: () => import('@/views/Dashboard.vue'),
                meta: { title: '首页看板', icon: 'Odometer' }
            },
            {
                path: 'users',
                name: 'Users',
                component: () => import('@/views/Users.vue'),
                meta: { title: '用户管理', icon: 'User' }
            },
            {
                path: 'recipes',
                name: 'Recipes',
                component: () => import('@/views/Recipes.vue'),
                meta: { title: '精品食谱', icon: 'Dish' }
            },
            {
                path: 'foods',
                name: 'Foods',
                component: () => import('@/views/Foods.vue'),
                meta: { title: '食物管理', icon: 'Bowl' }
            },
            {
                path: 'ai-config',
                name: 'AIConfig',
                component: () => import('@/views/AIConfig.vue'),
                meta: { title: 'AI 配置', icon: 'Setting' }
            }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
    // 设置页面标题
    document.title = to.meta.title ? `${to.meta.title} - 食品健康管理后台` : '食品健康管理后台'

    // 检查登录状态（简化版，后续可接入真实认证）
    const token = localStorage.getItem('admin_token')

    if (to.path === '/login') {
        next()
    } else if (!token) {
        next('/login')
    } else {
        next()
    }
})

export default router
