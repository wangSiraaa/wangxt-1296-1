<template>
  <div class="profile-page page-container">
    <van-nav-bar title="个人中心" fixed placeholder />

    <div class="page-content">
      <div class="user-card card">
        <div class="user-avatar">
          <van-image
            round
            width="64"
            height="64"
            :src="userStore.user?.avatar || ''"
          >
            <template #default>
              <van-icon name="user-o" size="40" color="#ccc" />
            </template>
          </van-image>
        </div>
        <div class="user-info">
          <h3>{{ userStore.userName || '用户' }}</h3>
          <p class="user-role">{{ roleText }}</p>
          <p class="user-dept">{{ userStore.user?.department || '-' }}</p>
        </div>
      </div>

      <van-cell-group inset>
        <van-cell title="用户名" :value="userStore.user?.username" />
        <van-cell title="真实姓名" :value="userStore.user?.real_name" />
        <van-cell title="手机号" :value="userStore.user?.phone || '-' " />
        <van-cell title="邮箱" :value="userStore.user?.email || '-' " />
      </van-cell-group>

      <van-cell-group inset style="margin-top: 12px;">
        <van-cell title="修改密码" is-link @click="showChangePassword = true" />
        <van-cell title="关于系统" is-link @click="showAbout = true" />
      </van-cell-group>

      <div style="margin: 24px 16px;">
        <van-button round block type="danger" @click="handleLogout">
          退出登录
        </van-button>
      </div>
    </div>

    <van-tabbar v-model="active" route>
      <van-tabbar-item to="/home" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item
        v-if="userStore.userRole === 'judicial' || userStore.userRole === 'social_worker'"
        to="/objects"
        icon="friends-o"
      >
        对象
      </van-tabbar-item>
      <van-tabbar-item to="/visit-plans" icon="calendar-o">走访</van-tabbar-item>
      <van-tabbar-item
        v-if="userStore.userRole === 'family' || userStore.userRole === 'judicial'"
        to="/feedbacks"
        icon="comment-o"
      >
        反馈
      </van-tabbar-item>
      <van-tabbar-item to="/profile" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>

    <van-dialog v-model:show="showAbout" title="关于系统" show-cancel-button>
      <div style="padding: 20px; text-align: center;">
        <h3>社区矫正走访系统</h3>
        <p>版本 1.0.0</p>
        <p class="text-muted" style="margin-top: 12px; font-size: 12px;">
          服务司法所、社工和矫正对象家属的智慧走访管理平台
        </p>
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { showConfirmDialog, showToast } from 'vant'

const router = useRouter()
const userStore = useUserStore()
const active = ref('/profile')

const showChangePassword = ref(false)
const showAbout = ref(false)

const roleText = computed(() => {
  const roleMap = {
    judicial: '司法所',
    social_worker: '社工',
    family: '家属'
  }
  return roleMap[userStore.userRole] || ''
})

const handleLogout = async () => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '确定要退出登录吗？'
    })
    userStore.logout()
    showToast('已退出登录')
    router.replace('/login')
  } catch (error) {
    // 用户取消
  }
}
</script>

<style scoped>
.profile-page {
  background-color: #f5f5f5;
}

.user-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 16px;
  background: linear-gradient(135deg, #1989fa 0%, #00b4ff 100%);
  color: #fff;
}

.user-avatar {
  flex-shrink: 0;
}

.user-info h3 {
  color: #fff;
  font-size: 20px;
  margin-bottom: 4px;
}

.user-role {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2px;
}

.user-dept {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}
</style>
