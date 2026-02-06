<template>
  <view class="container">
    <!-- 头部 -->
    <view class="header">
      <text class="back" @click="goBack">&lt;</text>
      <text class="title">编辑资料</text>
      <text class="placeholder"></text>
    </view>

    <!-- 头像区域 -->
    <view class="avatar-section" @click="chooseAvatar">
      <image
        v-if="form.avatar_url"
        class="avatar-img"
        :src="getAvatarUrl(form.avatar_url)"
        mode="aspectFill"
      />
      <view v-else class="avatar-placeholder">
        <text class="avatar-text">{{ form.nickname?.[0] || '?' }}</text>
      </view>
      <text class="avatar-tip">点击更换头像</text>
    </view>

    <!-- 表单区域 -->
    <view class="form-section">
      <view class="form-item">
        <text class="label">昵称</text>
        <input
          class="input"
          v-model="form.nickname"
          placeholder="请输入昵称"
          maxlength="20"
        />
      </view>

      <view class="form-item readonly">
        <text class="label">用户名</text>
        <text class="value">@{{ user?.username || '-' }}</text>
      </view>
    </view>

    <!-- 账号安全 -->
    <view class="section-title">账号安全</view>
    <view class="menu-section">
      <view class="menu-item" @click="goChangePassword">
        <text class="menu-icon">🔐</text>
        <text class="menu-text">修改密码</text>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <!-- 保存按钮 -->
    <view class="action-section">
      <button class="save-btn" :disabled="saving" @click="saveProfile">
        {{ saving ? '保存中...' : '保存修改' }}
      </button>
    </view>

    <!-- 图片裁切弹窗 - 使用 movable 实现拖动 -->
    <view class="cropper-popup" v-if="showCropper">
      <view class="cropper-mask"></view>
      <view class="cropper-content">
        <view class="cropper-header">
          <text class="cropper-title">裁切头像</text>
          <text class="cropper-close" @click="cancelCrop">×</text>
        </view>

        <!-- 裁切区域 -->
        <view class="cropper-body">
          <view class="crop-area">
            <!-- 可移动的图片 -->
            <movable-area class="movable-area">
              <movable-view
                class="movable-view"
                :x="imageX"
                :y="imageY"
                direction="all"
                :scale="true"
                :scale-min="0.5"
                :scale-max="3"
                :scale-value="imageScale"
                @change="onImageMove"
                @scale="onImageScale"
              >
                <image
                  class="crop-image"
                  :src="tempImagePath"
                  mode="widthFix"
                  :style="{ width: imageWidth + 'px' }"
                />
              </movable-view>
            </movable-area>
            <!-- 裁切框遮罩 -->
            <view class="crop-overlay">
              <view class="crop-circle"></view>
            </view>
          </view>
          <text class="crop-tip">拖动和缩放图片调整位置</text>
        </view>

        <view class="cropper-actions">
          <button class="crop-btn cancel" @click="cancelCrop">取消</button>
          <button class="crop-btn confirm" @click="confirmCrop">确认裁切</button>
        </view>
      </view>
    </view>

    <!-- 隐藏的 canvas 用于裁切 -->
    <canvas
      v-if="showCropper"
      canvas-id="cropCanvas"
      class="hidden-canvas"
      :style="{ width: '400px', height: '400px' }"
    ></canvas>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { API_BASE_URL } from '@/config.js'

const user = ref<any>(null)
const saving = ref(false)
const showCropper = ref(false)
const tempImagePath = ref('')

// 图片位置和缩放
const imageX = ref(0)
const imageY = ref(0)
const imageScale = ref(1)
const imageWidth = ref(300)
const imageHeight = ref(300)
const originalWidth = ref(0)
const originalHeight = ref(0)

// 裁切区域大小
const cropSize = 240

const form = reactive({
  nickname: '',
  avatar_url: ''
})

onMounted(() => {
  const storedUser = uni.getStorageSync('user')
  if (storedUser) {
    user.value = storedUser
    form.nickname = storedUser.nickname || ''
    form.avatar_url = storedUser.avatar_url || ''
  }
})

const getAvatarUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  return API_BASE_URL + url
}

const goBack = () => {
  uni.navigateBack()
}

const goChangePassword = () => {
  uni.navigateTo({ url: '/pages/profile/password' })
}

const chooseAvatar = () => {
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    sourceType: ['album', 'camera'],
    success: (res) => {
      tempImagePath.value = res.tempFilePaths[0]
      // 获取图片信息
      uni.getImageInfo({
        src: res.tempFilePaths[0],
        success: (info) => {
          originalWidth.value = info.width
          originalHeight.value = info.height

          // 计算初始显示大小，让图片适应裁切区域
          const areaSize = 300
          const scale = Math.max(cropSize / info.width, cropSize / info.height)
          imageWidth.value = info.width * scale
          imageHeight.value = info.height * scale

          // 居中显示
          imageX.value = (areaSize - imageWidth.value) / 2
          imageY.value = (areaSize - imageHeight.value) / 2
          imageScale.value = 1

          showCropper.value = true
        }
      })
    }
  })
}

const onImageMove = (e: any) => {
  imageX.value = e.detail.x
  imageY.value = e.detail.y
}

const onImageScale = (e: any) => {
  imageScale.value = e.detail.scale
}

const cancelCrop = () => {
  showCropper.value = false
  tempImagePath.value = ''
}

const confirmCrop = () => {
  uni.showLoading({ title: '处理中...' })

  // 使用 canvas 进行裁切
  const ctx = uni.createCanvasContext('cropCanvas')

  // 计算裁切参数
  const areaSize = 300
  const cropOffset = (areaSize - cropSize) / 2

  // 当前图片在 movable-view 中的实际位置和大小
  const scaledWidth = imageWidth.value * imageScale.value
  const scaledHeight = imageHeight.value * imageScale.value

  // 计算裁切框相对于图片的位置
  const cropX = cropOffset - imageX.value
  const cropY = cropOffset - imageY.value

  // 计算在原图上的裁切区域
  const srcX = (cropX / scaledWidth) * originalWidth.value
  const srcY = (cropY / scaledHeight) * originalHeight.value
  const srcSize = (cropSize / scaledWidth) * originalWidth.value

  // 绘制裁切后的图片
  ctx.drawImage(
    tempImagePath.value,
    srcX, srcY, srcSize, srcSize,
    0, 0, 400, 400
  )

  ctx.draw(false, () => {
    setTimeout(() => {
      uni.canvasToTempFilePath({
        canvasId: 'cropCanvas',
        x: 0,
        y: 0,
        width: 400,
        height: 400,
        destWidth: 400,
        destHeight: 400,
        success: (res) => {
          uploadAvatar(res.tempFilePath)
        },
        fail: (err) => {
          console.error('Canvas to temp file failed:', err)
          uni.hideLoading()
          uni.showToast({ title: '裁切失败', icon: 'none' })
        }
      })
    }, 300)
  })
}

const uploadAvatar = async (filePath: string) => {
  try {
    const token = uni.getStorageSync('token')

    // 使用 uploadFile 上传文件
    const uploadRes: any = await new Promise((resolve, reject) => {
      uni.uploadFile({
        url: `${API_BASE_URL}/api/v1/user/avatar/upload`,
        filePath: filePath,
        name: 'file',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: resolve,
        fail: reject
      })
    })

    const data = JSON.parse(uploadRes.data)

    if (data?.code === 0) {
      form.avatar_url = data.data.avatar_url
      // 更新本地存储
      const updatedUser = { ...user.value, avatar_url: data.data.avatar_url }
      uni.setStorageSync('user', updatedUser)
      user.value = updatedUser
      uni.showToast({ title: '头像上传成功', icon: 'success' })
    } else {
      uni.showToast({ title: data?.message || '上传失败', icon: 'none' })
    }
  } catch (e) {
    console.error('Upload failed:', e)
    uni.showToast({ title: '上传失败', icon: 'none' })
  } finally {
    uni.hideLoading()
    showCropper.value = false
  }
}

const saveProfile = async () => {
  if (!form.nickname.trim()) {
    uni.showToast({ title: '请输入昵称', icon: 'none' })
    return
  }

  saving.value = true
  try {
    const token = uni.getStorageSync('token')
    const res = await uni.request({
      url: `${API_BASE_URL}/api/v1/user/profile`,
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${token}`
      },
      data: {
        nickname: form.nickname,
        avatar_url: form.avatar_url
      }
    })

    if (res.data?.code === 0) {
      // 更新本地存储
      const updatedUser = { ...user.value, ...res.data.data }
      uni.setStorageSync('user', updatedUser)
      user.value = updatedUser

      uni.showToast({ title: '保存成功', icon: 'success' })
      setTimeout(() => {
        uni.navigateBack()
      }, 1000)
    } else {
      uni.showToast({ title: res.data?.message || '保存失败', icon: 'none' })
    }
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    saving.value = false
  }
}
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 40rpx 30rpx 30rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
}

.back {
  font-size: 40rpx;
  color: #fff;
  padding: 10rpx 20rpx;
}

.title {
  font-size: 36rpx;
  font-weight: bold;
  color: #fff;
}

.placeholder {
  width: 60rpx;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50rpx 0;
  background: #fff;
  margin-bottom: 20rpx;
}

.avatar-img {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: #f0f0f0;
}

.avatar-placeholder {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 60rpx;
  color: #fff;
  font-weight: bold;
}

.avatar-tip {
  margin-top: 16rpx;
  font-size: 26rpx;
  color: #4CAF50;
}

.form-section {
  background: #fff;
  margin-bottom: 20rpx;
}

.form-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;

  &:last-child {
    border-bottom: none;
  }

  &.readonly {
    .value {
      color: #999;
    }
  }
}

.label {
  width: 140rpx;
  font-size: 30rpx;
  color: #333;
}

.input {
  flex: 1;
  font-size: 30rpx;
  text-align: right;
}

.value {
  flex: 1;
  font-size: 30rpx;
  text-align: right;
  color: #333;
}

.section-title {
  padding: 30rpx;
  font-size: 26rpx;
  color: #999;
}

.menu-section {
  background: #fff;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 32rpx 30rpx;

  &:active {
    background: #f9f9f9;
  }
}

.menu-icon {
  font-size: 40rpx;
  margin-right: 20rpx;
}

.menu-text {
  flex: 1;
  font-size: 30rpx;
  color: #333;
}

.menu-arrow {
  font-size: 36rpx;
  color: #ccc;
}

.action-section {
  padding: 60rpx 30rpx;
}

.save-btn {
  width: 100%;
  padding: 28rpx;
  background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
  color: #fff;
  font-size: 32rpx;
  font-weight: 500;
  border-radius: 50rpx;
  border: none;

  &[disabled] {
    opacity: 0.6;
  }
}

/* 裁切弹窗 */
.cropper-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

.cropper-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
}

.cropper-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 400px;
  background: #fff;
  border-radius: 24rpx;
  overflow: hidden;
}

.cropper-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.cropper-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.cropper-close {
  font-size: 48rpx;
  color: #999;
  padding: 10rpx;
  line-height: 1;
}

.cropper-body {
  padding: 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.crop-area {
  width: 300px;
  height: 300px;
  position: relative;
  overflow: hidden;
  border-radius: 16rpx;
  background: #000;
}

.movable-area {
  width: 300px;
  height: 300px;
}

.movable-view {
  width: auto;
  height: auto;
}

.crop-image {
  display: block;
}

.crop-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.crop-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 240px;
  height: 240px;
  border: 3px solid #4CAF50;
  border-radius: 50%;
  box-shadow: 0 0 0 1000px rgba(0, 0, 0, 0.5);
}

.crop-tip {
  margin-top: 20rpx;
  font-size: 24rpx;
  color: #999;
}

.cropper-actions {
  display: flex;
  gap: 20rpx;
  padding: 30rpx;
  border-top: 1rpx solid #f0f0f0;
}

.crop-btn {
  flex: 1;
  padding: 24rpx;
  font-size: 30rpx;
  border-radius: 50rpx;
  border: none;

  &.cancel {
    background: #f5f5f5;
    color: #666;
  }

  &.confirm {
    background: linear-gradient(135deg, #4CAF50 0%, #66BB6A 100%);
    color: #fff;
  }
}

/* 隐藏的 canvas */
.hidden-canvas {
  position: fixed;
  left: -9999px;
  top: -9999px;
}
</style>
