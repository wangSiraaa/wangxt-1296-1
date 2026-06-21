<template>
  <div class="visit-record-page page-container">
    <van-nav-bar title="走访记录" fixed placeholder />

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
            class="record-item card"
            @click="goDetail(item.id)"
          >
            <div class="record-header">
              <span class="record-date">{{ formatDateTime(item.visit_date) }}</span>
              <span :class="['way-tag', `way-${item.visit_way}`]">
                {{ item.visit_way_display }}
              </span>
            </div>
            <h4 class="record-name">{{ item.correction_object_name }}</h4>
            <p class="record-summary">{{ truncateText(item.talk_summary, 80) }}</p>
            <div class="record-footer">
              <span v-if="item.risk_change" :class="['risk-tag', `risk-${item.risk_change}`]">
                风险：{{ item.risk_change_display }}
              </span>
              <span class="location-status" :class="{ valid: item.location_valid }">
                定位：{{ item.location_valid ? '有效' : '偏离' }}
              </span>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>

      <div v-if="!loading && list.length === 0" class="empty-state">
        <van-empty description="暂无走访记录" />
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
import { getVisitRecords } from '@/api/visitRecord'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const active = ref('/visit-records')

const list = ref([])
const loading = ref(false)
const refreshing = ref(false)
const finished = ref(false)
const page = ref(1)
const pageSize = 20

const formatDateTime = (datetime) => {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm')
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

const fetchList = async () => {
  try {
    const params = {
      page: page.value,
      page_size: pageSize
    }

    if (route.query.correction_object_id) {
      params.correction_object_id = route.query.correction_object_id
    }

    const res = await getVisitRecords(params)
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
    console.error('Get visit records error:', error)
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

const goDetail = (id) => {
  router.push(`/visit-records/${id}`)
}

onMounted(() => {
  loading.value = true
  fetchList()
})
</script>

<style scoped>
.visit-record-page {
  background-color: #f5f5f5;
}

.record-item {
  cursor: pointer;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.record-date {
  font-size: 13px;
  color: #666;
}

.way-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  background-color: #e8f3ff;
  color: #1989fa;
}

.record-name {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 8px 0;
}

.record-summary {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
  margin: 0 0 10px 0;
}

.record-footer {
  display: flex;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
}

.location-status {
  color: #999;
}

.location-status.valid {
  color: #07c160;
}
</style>
