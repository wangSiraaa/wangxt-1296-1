<template>
  <div class="tabbar-container">
    <div class="page-content">
      <router-view v-slot="{ Component }">
        <keep-alive>
          <component :is="Component" />
        </keep-alive>
      </router-view>
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
      <van-tabbar-item to="/notifications" icon="bell-o">
        通知
        <template #icon>
          <van-badge :content="unreadCount" :show="unreadCount > 0" max="99">
            <van-icon name="bell-o" size="20" />
          </van-badge>
        </template>
      </van-tabbar-item>
      <van-tabbar-item to="/profile" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getUnreadCount } from '@/api/notification'

const userStore = useUserStore()
const route = useRoute()
const unreadCount = ref(0)

const active = computed(() => route.path)

const fetchUnreadCount = async () => {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.unread_count
  } catch (error) {
    console.error('Get unread count error:', error)
  }
}

onMounted(() => {
  if (userStore.isLoggedIn) {
    fetchUnreadCount()
  }
})

onActivated(() => {
  if (userStore.isLoggedIn) {
    fetchUnreadCount()
  }
})
</script>

<style scoped>
.tabbar-container {
  min-height: 100vh;
  padding-bottom: 50px;
}

.page-content {
  min-height: calc(100vh - 50px);
}
</style>
