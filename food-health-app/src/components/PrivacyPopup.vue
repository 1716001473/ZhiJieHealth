<template>
  <view v-if="show" class="privacy-popup">
    <view class="mask"></view>
    <view class="content">
      <view class="title">用户隐私保护提示</view>
      <view class="desc">
        感谢您使用本服务。在使用前，请您仔细阅读<text class="link" @click="openPrivacyContract">{{ privacyContractName }}</text>。当您点击同意并开始使用产品服务时，即表示您已理解并同意该条款内容，该条款将对您产生法律约束力。如您拒绝，将无法使用本小程序的相关功能。
      </view>
      <view class="btns">
        <button class="btn refuse" @click="handleDisagree">拒绝</button>
        <button 
          class="btn agree" 
          open-type="agreePrivacyAuthorization" 
          @agreePrivacyAuthorization="handleAgree"
        >同意并继续</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const show = ref(false)
const privacyContractName = ref('《用户隐私保护指引》')

// 用于存储授权回调
let resolvePrivacyAuthorization: ((value: any) => void) | null = null

// 打开隐私协议详情
const openPrivacyContract = () => {
  // #ifdef MP-WEIXIN
  uni.openPrivacyContract({
    success: () => {},
    fail: (err) => {
      console.error('打开隐私协议失败', err)
    }
  })
  // #endif
}

// 拒绝
const handleDisagree = () => {
  show.value = false
  // 通知微信用户拒绝了隐私协议
  if (resolvePrivacyAuthorization) {
    resolvePrivacyAuthorization({ event: 'disagree' })
    resolvePrivacyAuthorization = null
  }
}

// 同意
const handleAgree = () => {
  show.value = false
  // 模拟同意回调
  if (resolvePrivacyAuthorization) {
    resolvePrivacyAuthorization({ buttonId: 'agree-btn', event: 'agree' })
    resolvePrivacyAuthorization = null
  }
}

// 初始化监听
onMounted(() => {
  // #ifdef MP-WEIXIN
  if (uni.onNeedPrivacyAuthorization) {
    uni.onNeedPrivacyAuthorization((resolve) => {
      console.log('触发隐私协议授权')
      show.value = true
      resolvePrivacyAuthorization = resolve
    })
  }

  if (uni.getPrivacySetting) {
    uni.getPrivacySetting({
      success: (res) => {
        if (res.needAuthorization) {
          show.value = true
          privacyContractName.value = res.privacyContractName || '《用户隐私保护指引》'
        }
      }
    })
  }
  // #endif
})
</script>

<style lang="scss" scoped>
.privacy-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .mask {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
  }
  
  .content {
    position: relative;
    width: 600rpx;
    background: #fff;
    border-radius: 24rpx;
    padding: 40rpx;
    z-index: 10000;
  }
  
  .title {
    font-size: 34rpx;
    font-weight: bold;
    text-align: center;
    margin-bottom: 30rpx;
    color: #333;
  }
  
  .desc {
    font-size: 28rpx;
    color: #666;
    line-height: 1.6;
    margin-bottom: 40rpx;
    text-align: justify;
    
    .link {
      color: #07C160;
      display: inline;
    }
  }
  
  .btns {
    display: flex;
    justify-content: space-between;
    
    .btn {
      width: 240rpx;
      height: 80rpx;
      line-height: 80rpx;
      text-align: center;
      border-radius: 12rpx;
      font-size: 30rpx;
      margin: 0;
      
      &::after {
        border: none;
      }
      
      &.refuse {
        background: #f5f5f5;
        color: #666;
      }
      
      &.agree {
        background: #07C160;
        color: #fff;
      }
    }
  }
}
</style>
