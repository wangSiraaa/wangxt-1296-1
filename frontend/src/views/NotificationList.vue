<template>
  <div class="notification-page page-container">
    <van-nav-bar title="通知中心" fixed placeholder>
      <template #right>
        <van-button size="small" type="primary" plain @click="handleMarkAllRead">
          全部已读
        </van-button>
      </template>
    </van-nav-bar>

    <div class="page-content">
      <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
        <van-list
          v-model:loading="loading"
          :finished="finished"
          finished-text="没有更多了"
          @load="onLoad"
        >
          <div
            v-for="item in list"
            :key="item.id"
            class="notification-item card"
            :class="{ unread: !item.is_read }"
            @click="handleClick(item)"
          >
            <div class="notification-header">
              <div class="notification-type">
                <span :class="['type-tag', `type-${item.type}`]">
                  {{ getTypeText(item.type) }}
                </span>
                <span :class="['level-tag', `level-${item.level}`]">
                  {{ getLevelText(item.level) }}
                </span>
              </div>
              <span class="notification-time">{{ formatTime(item.created_at) }}</span>
            </div>
            <h4 class="notification-title">{{ item.title }}</h4>
            <p class="notification-content">{{ item.content }}</p>
            <div v-if="item.correction_object_name" class="notification-object">
              关联对象：{{ item.correction_object_name }}
            </div>
          </div>
        </van-list>
      </van-pull-refresh>

      <div v-if="!loading && list.length === 0" class="empty-state">
        <van-empty description="暂无通知" />
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
      <van-tabbar-item to="/notifications" icon="bell-o">通知</van-tabbar-item>
      <van-tabbar-item to="/profile" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getNotifications, markNotificationRead, markAllRead } from '@/api/notification'
import { showToast } from 'vant'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()
const active = ref('/notifications')

const list = ref([])
const loading = ref(false)
const refreshing = ref(false)
const finished = ref(false)
const page = ref(1)
const pageSize = 20

const getTypeText = (type) => {
  const map = {
    missed_visit: '漏访提醒',
    location_deviation: '定位偏离',
    risk_change: '风险变更',
    system: '系统通知'
  }
  return map[type] || '系统通知'
}

const getLevelText = (level) => {
  const map = {
    normal: '普通',
    warning: '警告',
    urgent: '紧急'
  }
  return map[level] || '普通'
}

const formatTime = (time) => {
  return dayjs(time).format('MM-DD HH:mm')
}

const fetchList = async () => {
  try {
    const res = await getNotifications({
      page: page.value,
      page_size: pageSize
    })
    const results = res.results || res || []

    if (refreshing.value) {
      list.value = results
      refreshing.value = false
    } else {
      list.value = [...list.value, ...results]
    }

    loading.value = false

    if (results.length < pageSize) {
      finished.value = true
    }
  } catch (error) {
    console.error('Get notifications error:', error)
    loading.value = false
    refreshing.value = false
  }
}

const onLoad = () => {
  if (!refreshing.value) {
    page.value = 1
    finished.value = false
  }
  fetchList()
}

const onRefresh = () => {
  page.value = 1
  finished.value = false
  loading.value = true
  fetchList()
}

const handleClick = async (item) => {
  if (!item.is_read) {
    try {
      await markNotificationRead(item.id)
      item.is_read = true
    } catch (error) {
      console.error('Mark read error:', error)
    }
  }

  if (item.type === 'missed_visit' && item.related_id) {
    router.push(`/visit-plans/${item.related_id}`)
  } else if (item.type === 'risk_change' && item.correction_object) {
    router.push(`/objects/${item.correction_object}`)
  }
}

const handleMarkAllRead = async () => {
  try {
    await markAllRead()
    list.value.forEach(item => {
      item.is_read = true
    })
    showToast('已全部标记为已读')
  } catch (error) {
    console.error('Mark all read error:', error)
  }
}
</script>

<style scoped>
.notification-page {
  background-color: #f5f5f5;
}

.notification-item {
  margin-bottom: 10px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.notification-item.unread {
  border-left: 3px solid #1989fa;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.notification-type {
  display: flex;
  gap: 6px;
}

.type-tag,
.level-tag {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.type-missed_visit {
  background-color: #ffede8;
  color: #ee0a24;
}

.type-location_deviation {
  background-color: #fff7e8;
  color: #ff976a;
}

.type-risk_change {
  background-color: #e8f3ff;
  color: #1989fa;
}

.type-system {
  background-color: #f0f0f0;
  color: #666;
}

.level-normal {
  background-color: #e8f7ee;
  color: #07c160;
}

.level-warning {
  background-color: #fff7e8;
  color: #ff976a;
}

.level-urgent {
  background-color: #ffede8;
  color: #ee0a24;
}

.notification-time {
  font-size: 12px;
  color: #999;
}

.notification-title {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #333;
}

.notification-content {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 8px;
}

.notification-object {
  font-size: 12px;
  color: #999;
}
</style>
