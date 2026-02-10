# 体重图表调试指南

## 🔍 数据库检查结果

数据库中已有 **32 条体重记录**，包括：
- 用户 `test_user_history_fix` (ID:1): 16 条记录
- 用户 `11111` (ID:2): 16 条记录

**所以问题不在数据库，而在于前端请求！**

## ⚠️ 可能的问题原因

1. **用户未登录或 Token 失效**
2. **登录的用户不是上述两个测试用户**
3. **CORS 跨域问题导致请求失败**

## 在浏览器控制台执行以下代码测试：

### 0. 🔍 首先检查当前登录状态

```javascript
// 检查当前 Token 和用户信息
const token = uni.getStorageSync('token')
const user = uni.getStorageSync('user')

console.log('=== 登录状态检查 ===')
console.log('Token:', token ? `已登录 (长度: ${token.length})` : '❌ 未登录')
console.log('用户信息:', user)
console.log('用户ID:', user?.id)
console.log('用户名:', user?.username)
```

### 1. 测试获取体重历史接口

```javascript
// 获取 Token
const token = uni.getStorageSync('token')
console.log('Token:', token ? '已登录' : '未登录')

// 测试体重历史接口
uni.request({
  url: 'http://127.0.0.1:8000/api/v1/health/weight/history?days=30',
  method: 'GET',
  header: {
    'Authorization': `Bearer ${token}`
  },
  success: (res) => {
    console.log('体重历史数据:', res.data)
    if (res.data.code === 0) {
      console.log('记录条数:', res.data.data.length)
      console.log('详细数据:', res.data.data)
    } else {
      console.error('接口返回错误:', res.data.message)
    }
  },
  fail: (err) => {
    console.error('请求失败:', err)
  }
})
```

### 2. 测试保存体重接口

```javascript
const token = uni.getStorageSync('token')

uni.request({
  url: 'http://127.0.0.1:8000/api/v1/health/weight',
  method: 'POST',
  header: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  data: {
    weight: 69
  },
  success: (res) => {
    console.log('保存结果:', res.data)
  },
  fail: (err) => {
    console.error('保存失败:', err)
  }
})
```

## 预期结果

### 成功情况：

```json
// GET /health/weight/history 返回
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "date": "2026-02-03",
      "weight": 69.0
    }
  ]
}
```

### 失败情况：

1. **未登录**
```json
{
  "code": -1,
  "message": "请先登录",
  "data": null
}
```

2. **Token 过期**
```json
{
  "code": 401,
  "message": "Unauthorized",
  "data": null
}
```

## 如何查看数据库

如果有 SQLite 工具，可以直接查看数据：

```sql
-- 查看体重记录表
SELECT * FROM weight_records;

-- 查看用户表
SELECT id, username FROM users;
```

数据库路径：`food-health-api/health.db`
