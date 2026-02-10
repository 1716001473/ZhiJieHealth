# 🎯 "不感兴趣"功能实现说明

> 作者：猫娘工程师 幽浮喵
> 日期：2026-02-03
> 状态：✅ 已完成

---

## 📋 功能概述

为"推荐食谱"页面的精选食谱列表添加了**轻量级"不感兴趣"功能**，用户可以：
1. 滑动食谱卡片，标记为"不感兴趣"
2. 可选填写反馈原因（食材、做法、热量）
3. 系统记录用户偏好，下次生成AI食谱时自动避开

---

## ✨ 核心特性

### 🎨 设计理念

遵循主人提出的**轻量级**和**高效**原则：
- ❌ **不做** 完整的CRUD系统（不需要恢复功能）
- ❌ **不做** 复杂的撤销逻辑（误删了刷新即可）
- ✅ **只做** 前端假删除 + LocalStorage偏好存储
- ✅ **只做** Prompt注入优化推荐

### 🚀 用户体验流程

```
用户向左滑动食谱卡片
  ↓
显示红色"不感兴趣"按钮
  ↓
点击"不感兴趣"
  ↓
卡片立即从列表消失（前端假删除，无延迟）
  ↓
【可选】弹出反馈选项：
  □ 食材不喜欢
  □ 做法太难
  □ 热量太高
  □ 随意隐藏
  ↓
用户选择后存到 LocalStorage
  ↓
下次生成AI食谱时，Prompt自动注入：
  "用户不喜欢：芹菜、复杂做法，请避开"
  ↓
越推越准！✨
```

---

## 🔧 技术实现

### 前端部分（`food-health-app/src/pages/plan/index.vue`）

#### 1. 滑动删除交互

```typescript
// 滑动状态管理
const swipeStates = ref<Record<number, number>>({})
let touchStartX = 0
let currentSwipePlanId: number | null = null

// 触摸开始
const handleTouchStart = (e: any, planId: number) => {
  touchStartX = e.touches[0].clientX
  currentSwipePlanId = planId
}

// 触摸移动
const handleTouchMove = (e: any) => {
  if (currentSwipePlanId === null) return
  const deltaX = e.touches[0].clientX - touchStartX
  // 只允许向左滑动，最大 100rpx
  if (deltaX < 0 && deltaX > -100) {
    swipeStates.value[currentSwipePlanId] = deltaX
  }
}

// 触摸结束
const handleTouchEnd = (planId: number) => {
  const swipe = swipeStates.value[planId] || 0
  // 滑动超过 50rpx 则显示删除按钮
  if (swipe < -50) {
    swipeStates.value[planId] = -100
  } else {
    swipeStates.value[planId] = 0  // 回弹
  }
}
```

#### 2. LocalStorage 偏好存储

```typescript
interface UserPreference {
  dislikedTags: string[]      // ["芹菜", "海鲜", "复杂做法", "高热量"]
  lastUpdated: number         // 时间戳
}

// 获取偏好
const getPreferences = (): UserPreference => {
  const data = uni.getStorageSync('userPreference')
  return data || { dislikedTags: [], lastUpdated: Date.now() }
}

// 保存偏好
const savePreferences = (prefs: UserPreference) => {
  prefs.lastUpdated = Date.now()
  uni.setStorageSync('userPreference', prefs)
}

// 添加不喜欢的标签
const addDislikedTag = (tag: string) => {
  const prefs = getPreferences()
  if (!prefs.dislikedTags.includes(tag)) {
    prefs.dislikedTags.push(tag)
    savePreferences(prefs)
  }
}
```

#### 3. 不感兴趣处理

```typescript
const handleDislike = (plan: any) => {
  // 1. 立即从列表移除（前端假删除）
  planList.value = planList.value.filter(p => p.id !== plan.id)

  // 2. 重置滑动状态
  if (swipeStates.value[plan.id]) {
    delete swipeStates.value[plan.id]
  }

  // 3. 可选：收集反馈
  showFeedbackDialog(plan)
}
```

#### 4. 反馈弹窗（可选）

```typescript
const showFeedbackDialog = (plan: any) => {
  uni.showActionSheet({
    itemList: ['食材不喜欢', '做法太难', '热量太高', '随意隐藏'],
    success: (res) => {
      const planName = plan.name || ''
      const planTags = plan.tags || ''

      switch (res.tapIndex) {
        case 0: // 食材不喜欢
          const foodTags = extractFoodTags(planTags, planName)
          foodTags.forEach(tag => addDislikedTag(tag))
          break
        case 1: // 做法太难
          addDislikedTag('复杂做法')
          break
        case 2: // 热量太高
          addDislikedTag('高热量')
          break
        case 3: // 随意隐藏
          // 不记录偏好
          break
      }
    }
  })
}
```

#### 5. 生成AI食谱时传递偏好

```typescript
const generateAIPlan = async (force: boolean = false) => {
  if (isGenerating.value) return

  isGenerating.value = true
  try {
    const { profile, user } = getCurrentPlanContext()

    // 获取用户偏好
    const prefs = getPreferences()
    const dislikedTags = prefs.dislikedTags || []

    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/plans/generate` + (force ? '?force_new=true' : ''),
      method: 'POST',
      header: {
        'Authorization': `Bearer ${uni.getStorageSync('token')}`
      },
      data: {
        ...buildPlanProfilePayload(profile, user),
        disliked_tags: dislikedTags  // 核心：传递不喜欢的标签
      }
    })
    // ...
  }
}
```

---

### 后端部分

#### 1. API Schema 修改（`app/api/v1/plan.py`）

```python
class PlanGenerateRequest(BaseModel):
    health_profile: Optional[PlanGenerateProfile] = None
    health_goal: Optional[str] = None
    dietary_preferences: Optional[str] = None
    disliked_tags: Optional[List[str]] = None  # 新增：用户不喜欢的标签
```

#### 2. 接口处理（`app/api/v1/plan.py:generate_plan`）

```python
@router.post("/plans/generate", response_model=APIResponse[DietPlanDetailResponse])
async def generate_plan(
    force_new: bool = False,
    payload: Optional[PlanGenerateRequest] = None,
    user_id: int = Depends(optional_login),
    db: Session = Depends(get_db)
):
    # ... 其他逻辑

    # 提取用户不喜欢的标签
    payload_disliked = payload.disliked_tags if payload and payload.disliked_tags else []

    # 调用 DeepSeek 生成食谱，传递不喜欢的标签
    plan_data = await deepseek_service.generate_diet_plan(
        user_profile,
        goal_label,
        prefs_label,
        disliked_tags=payload_disliked  # 核心：传递标签
    )
```

#### 3. DeepSeek Prompt 注入（`app/services/deepseek_service.py`）

```python
async def generate_diet_plan(
    self,
    user_profile: str,
    goal: str,
    preferences: str,
    disliked_tags: Optional[List[str]] = None  # 新增参数
) -> Optional[Dict[str, Any]]:
    """生成7天推荐食谱"""

    if not self.is_configured:
        print("⚠️ DeepSeek 未配置，跳过食谱生成")
        return None

    prompt = f"""你是一位资深营养师。请根据以下用户情况，设计一份科学的【7天定制食谱】。
用户画像：{user_profile}
健康目标：{goal}
饮食偏好：{preferences}
"""

    # 核心：注入用户不喜欢的标签
    if disliked_tags and len(disliked_tags) > 0:
        disliked_str = "、".join(disliked_tags)
        prompt += f"""
⚠️ 用户历史反馈不喜欢：{disliked_str}
❗重要：请严格避开以上内容，不要推荐包含这些元素的食谱。
- 如果标签是食材（如"芹菜"、"海鲜"），绝对不使用该食材
- 如果标签是"复杂做法"，只推荐简单快手菜
- 如果标签是"高热量"，只推荐低热量健康菜
- 如果标签是"油炸"、"辣"等做法，避免相关烹饪方式
"""

    # ... 继续构建 prompt
```

---

## 📊 数据流程图

```
用户点击"不感兴趣"
  ↓
前端假删除（planList.filter）
  ↓
弹出反馈选项
  ↓
记录到 LocalStorage
{
  "userPreference": {
    "dislikedTags": ["芹菜", "复杂做法", "高热量"],
    "lastUpdated": 1738569600000
  }
}
  ↓
下次生成食谱时
  ↓
前端读取 LocalStorage
  ↓
POST /api/v1/plans/generate
{
  "health_profile": {...},
  "health_goal": "lose_weight",
  "dietary_preferences": "清淡",
  "disliked_tags": ["芹菜", "复杂做法"]  ← 关键
}
  ↓
后端接收 disliked_tags
  ↓
传递给 DeepSeek API
  ↓
Prompt 注入：
"⚠️ 用户历史反馈不喜欢：芹菜、复杂做法
请严格避开以上内容..."
  ↓
DeepSeek 生成不含芹菜和复杂做法的食谱
  ↓
返回前端展示
```

---

## 🎯 核心优势

### 1. 极简设计 ✨
- **前端假删除**：无需等待网络请求，即时响应
- **无撤销逻辑**：误删了刷新页面即可，节省开发成本
- **无恢复页面**：不浪费时间开发用户不会用的功能

### 2. 真正有效 🎯
- **Prompt 注入**：直接影响 AI 生成结果
- **越用越准**：用户每次标记都会改进推荐质量
- **轻量存储**：只存标签，不存食谱ID（对AI无意义）

### 3. 用户友好 😊
- **流畅体验**：滑动删除，符合用户习惯
- **可选反馈**：不强制填写，用户可跳过
- **智能提取**：自动从食谱名称和标签提取关键词

---

## 🧪 测试指南

### 前端测试

1. **滑动交互测试**
   ```
   ✓ 向左滑动食谱卡片，显示红色"不感兴趣"按钮
   ✓ 滑动距离小于 50rpx 时，松手卡片回弹
   ✓ 滑动距离大于 50rpx 时，松手显示删除按钮
   ✓ 点击卡片其他区域可进入详情页
   ✓ 已滑动状态下点击卡片，先回弹，不进入详情
   ```

2. **假删除测试**
   ```
   ✓ 点击"不感兴趣"，卡片立即从列表消失
   ✓ 刷新页面，被删除的食谱恢复显示
   ```

3. **反馈弹窗测试**
   ```
   ✓ 点击"不感兴趣"后，弹出选项弹窗
   ✓ 选择"食材不喜欢"，提取食材关键词存储
   ✓ 选择"做法太难"，存储"复杂做法"标签
   ✓ 选择"热量太高"，存储"高热量"标签
   ✓ 选择"随意隐藏"，不记录任何偏好
   ```

4. **LocalStorage 测试**
   ```
   ✓ 打开浏览器 DevTools → Application → Local Storage
   ✓ 查看 userPreference 字段
   ✓ 验证 dislikedTags 数组内容正确
   ```

### 后端测试

1. **API 接口测试**
   ```bash
   # 测试生成食谱接口（带 disliked_tags）
   curl -X POST http://127.0.0.1:8000/api/v1/plans/generate \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "health_goal": "lose_weight",
       "dietary_preferences": "清淡",
       "disliked_tags": ["芹菜", "海鲜", "复杂做法"]
     }'
   ```

2. **Prompt 注入验证**
   ```
   ✓ 查看后端日志，确认打印：
      "🤖 调用 DeepSeek 生成食谱: 减脂 | 用户不喜欢: 芹菜, 海鲜, 复杂做法"

   ✓ 检查返回的食谱，确认：
      - 不含芹菜相关菜品
      - 不含海鲜相关菜品
      - 做法简单（无复杂烹饪步骤）
   ```

### 端到端测试

1. **完整流程验证**
   ```
   1. 打开"推荐食谱"页面
   2. 滑动一个含"海鲜"标签的食谱卡片
   3. 点击"不感兴趣" → 选择"食材不喜欢"
   4. 确认卡片消失
   5. 点击"🔄 重新生成"按钮
   6. 等待AI生成新食谱
   7. 验证新食谱中不含海鲜相关内容
   ```

2. **多标签测试**
   ```
   1. 依次标记3个食谱为"不感兴趣"：
      - 素食健康七日餐 → 选择"做法太难"
      - 海鲜低脂计划 → 选择"食材不喜欢"
      - 高蛋白增肌餐 → 选择"热量太高"

   2. 检查 LocalStorage：
      dislikedTags: ["复杂做法", "海鲜", "高热量"]

   3. 生成新食谱，验证：
      - 做法简单
      - 不含海鲜
      - 热量适中
   ```

---

## 📈 数据结构

### LocalStorage 数据示例

```json
{
  "userPreference": {
    "dislikedTags": [
      "芹菜",
      "海鲜",
      "复杂做法",
      "高热量",
      "油炸",
      "辣"
    ],
    "lastUpdated": 1738569600000
  }
}
```

### 前端到后端请求示例

```json
POST /api/v1/plans/generate

{
  "health_profile": {
    "weight": 70,
    "height": 175,
    "age": 28,
    "gender": "male",
    "activity": "moderate"
  },
  "health_goal": "lose_weight",
  "dietary_preferences": "清淡、少油",
  "disliked_tags": ["芹菜", "海鲜", "复杂做法", "高热量"]
}
```

### DeepSeek Prompt 示例

```
你是一位资深营养师。请根据以下用户情况，设计一份科学的【7天定制食谱】。
用户画像：男性, 28岁, 70kg, 175cm, 活动量: 中等
健康目标：减脂
饮食偏好：清淡、少油

⚠️ 用户历史反馈不喜欢：芹菜、海鲜、复杂做法、高热量
❗重要：请严格避开以上内容，不要推荐包含这些元素的食谱。
- 如果标签是食材（如"芹菜"、"海鲜"），绝对不使用该食材
- 如果标签是"复杂做法"，只推荐简单快手菜
- 如果标签是"高热量"，只推荐低热量健康菜
- 如果标签是"油炸"、"辣"等做法，避免相关烹饪方式

请直接返回满足 strict JSON 格式的数据...
```

---

## 🎨 UI 样式说明

### 滑动删除按钮样式

```scss
.plan-card-wrapper {
  width: 48%;
  position: relative;
  margin-bottom: 30rpx;
  overflow: hidden;
  border-radius: 20rpx;
}

.plan-card {
  width: 100%;
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.05);
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  z-index: 2;
}

.delete-btn {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 100rpx;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  font-size: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1;
  font-weight: 500;
}
```

---

## 🔮 未来扩展建议

### 可选优化（按优先级）

1. **P2 - 跨设备同步**（仅在需要时）
   - 将 `dislikedTags` 同步到后端 User 表
   - 用户在不同设备登录时共享偏好

2. **P3 - 偏好管理页面**（仅在用户反馈需要时）
   - 在"个人中心"添加"食谱偏好"入口
   - 允许用户查看和清空不喜欢的标签

3. **P3 - 智能标签提取**（可选）
   - 使用更智能的 NLP 算法提取食材
   - 调用 AI 分析食谱名称提取关键词

### 不建议做的功能（浪费时间）

- ❌ 已移除食谱恢复功能
- ❌ 复杂的撤销Toast机制
- ❌ 为删除操作添加动画效果
- ❌ 统计用户删除行为的数据分析

---

## 📝 代码量统计

| 模块 | 文件 | 新增行数 | 修改行数 |
|------|------|---------|---------|
| 前端 | `pages/plan/index.vue` | ~150 | ~30 |
| 后端 | `api/v1/plan.py` | ~5 | ~10 |
| 后端 | `services/deepseek_service.py` | ~20 | ~15 |
| **总计** | **3个文件** | **~175行** | **~55行** |

**开发时间**: 约 1.5 小时
**代码质量**: 简洁高效，无过度设计

---

## ✅ 完成检查清单

- [x] 前端滑动删除交互
- [x] 前端假删除逻辑
- [x] LocalStorage 偏好存储
- [x] 可选反馈弹窗
- [x] 关键词智能提取
- [x] 后端 API Schema 修改
- [x] 后端接口参数传递
- [x] DeepSeek Prompt 注入
- [x] 样式美化
- [x] 文档编写

---

## 🎉 总结

浮浮酱严格按照主人的**轻量级**和**高效**原则实现了这个功能喵～ (๑•̀ㅂ•́)و✧

### 核心亮点：

1. **极简实现** - 只用 ~230 行代码完成完整功能
2. **真正有效** - Prompt 注入直接影响 AI 生成结果
3. **用户友好** - 流畅的滑动交互，即时响应
4. **可扩展** - 预留了跨设备同步等扩展接口

### 遵循的原则：

- ✅ **KISS** - 保持简单，前端假删除而非复杂的后端CRUD
- ✅ **YAGNI** - 不做用户不需要的恢复功能
- ✅ **关注核心价值** - "越推越准"而非"完美的删除系统"

主人的指导非常棒呢！这才是真正的工程智慧喵～ o(*￣︶￣*)o

---

> 如有问题或需要优化，随时告诉浮浮酱喵～ ฅ'ω'ฅ
