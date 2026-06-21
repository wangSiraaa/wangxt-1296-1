<template>
  <div class="feedback-list-page page-container">
    <van-nav-bar title="帮教反馈" fixed placeholder>
      <template #right>
        <van-icon v-if="userStore.userRole === 'family'" name="plus" size="20" @click="goCreate" />
      </template>
    </van-nav-bar>

    <van-tabs v-model:active="activeTab" @change="onTabChange">
      <van-tab title="全部" name="all" />
      <van-tab title="待审核" name="submitted" />
      <van-tab title="已审核" name="reviewed" />
    </van-tabs>

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
            class="feedback-item card"
            @click="goDetail(item.id)"
          >
            <div class="feedback-header">
              <span class="feedback-date">{{ item.feedback_date }}</span>
              <span :class="['status-tag', `status-${item.status}`]">
                {{ item.status_display }}
              </span>
            </div>
            <h4 class="feedback-object">{{ item.correction_object_name }}</h4>
            <p class="feedback-preview">{{ truncateText(item.behavior_situation, 80) }}</p>
            <div class="feedback-footer">
              <span class="feedback-author">
                <van-icon name="user-o" size="12" />
                {{ item.family_user_name }}
              </span>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>

      <div v-if="!loading && list.length === 0" class="empty-state">
        <van-empty description="暂无帮教反馈" />
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getFamilyFeedbacks } from '@/api/familyFeedback'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const active = ref('/feedbacks')

const list = ref([])
const loading = ref(false)
const refreshing = ref(false)
const finished = ref(false)
const page = ref(1)
const pageSize = ref(20)
const activeTab = ref('all')

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

const fetchList = async () => {
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }

    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }

    if (route.query.correction_object_id) {
      params.correction_object_id = route.query.correction_object_id
    }

    const res = await getFamilyFeedbacks(params)
    const results = res.results || res || []

    if (refreshing.value) {
      list.value = results
      refreshing.value = false
    } else {
      list.value = [...list.value, ...results]
    }

    loading.value = false

    if (results.length < pageSize.value) {
      finished.value = true
    }
  } catch (error) {
    console.error('Get feedbacks error:', error)
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

const onTabChange = () => {
  page.value = 1
  finished.value = false
  list.value = []
  loading.value = true
  fetchList()
}

const goDetail = (id) => {
  router.push(`/feedbacks/${id}`)
}

const goCreate = () => {
  router.push('/feedbacks/create')
}

onMounted(() => {
  loading.value = true
  fetchList()
})
</script>

<style scoped>
.feedback-list-page {
  background-color: #f5f5f5;
}

.feedback-item {
  cursor: pointer;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.feedback-date {
  font-size: 13px;
  color: #666;
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-submitted {
  background-color: #fff7e8;
  color: #ff976a;
}

.status-reviewed {
  background-color: #e8f7ee;
  color: #07c160;
}

.feedback-object {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 8px 0;
}

.feedback-preview {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin: 0 0 10px 0;
}

.feedback-footer {
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: #999;
}

.feedback-author {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
