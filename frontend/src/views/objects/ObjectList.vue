<template>
  <div class="object-list-page page-container">
    <van-nav-bar title="矫正对象" fixed placeholder>
      <template #right>
        <van-icon v-if="userStore.userRole === 'judicial'" name="plus" size="20" @click="goCreate" />
      </template>
    </van-nav-bar>

    <van-search
      v-model="searchValue"
      placeholder="搜索姓名/身份证/电话"
      @search="onSearch"
      @clear="onSearch"
      shape="round"
    />

    <van-tabs v-model:active="activeTab" @change="onTabChange">
      <van-tab title="全部" name="all" />
      <van-tab title="低风险" name="low" />
      <van-tab title="中风险" name="medium" />
      <van-tab title="高风险" name="high" />
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
            class="object-item card"
            @click="goDetail(item.id)"
          >
            <div class="object-header">
              <div class="object-info">
              <h4 class="object-name">{{ item.name }}</h4>
              <span :class="['risk-tag', `risk-${item.risk_level}`]">
                {{ item.risk_level_display }}
              </span>
            </div>
            <span :class="['status-tag', `status-${item.status}`]">
              {{ item.status_display }}
            </span>
          </div>
          <div class="object-meta">
            <span class="meta-item">
              <van-icon name="idcard-o" size="12" />
              {{ maskIdCard(item.id_card) }}
            </span>
            <span class="meta-item">
              <van-icon name="phone-o" size="12" />
              {{ item.phone || '-' }}
            </span>
          </div>
          <div class="object-footer">
            <span class="meta-item">
              {{ item.correction_type }}
            </span>
            <span class="meta-item">
              {{ item.correction_start }} ~ {{ item.correction_end }}
            </span>
          </div>
        </div>
        </van-list>
      </van-pull-refresh>

      <div v-if="!loading && list.length === 0" class="empty-state">
        <van-empty description="暂无矫正对象" />
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
import { getCorrectionObjects } from '@/api/correctionObject'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const active = ref('/objects')

const list = ref([])
const loading = ref(false)
const refreshing = ref(false)
const finished = ref(false)
const page = ref(1)
const pageSize = 20
const searchValue = ref('')
const activeTab = ref('all')

const maskIdCard = (idCard) => {
  if (!idCard) return '-'
  if (idCard.length < 8) return idCard
  return idCard.slice(0, 6) + '********' + idCard.slice(-4)
}

const fetchList = async () => {
  try {
    const params = {
      page: page.value,
      page_size: pageSize,
      search: searchValue.value
    }

    if (activeTab.value !== 'all') {
      params.risk_level = activeTab.value
    }

    const res = await getCorrectionObjects(params)
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
    console.error('Get objects error:', error)
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

const onSearch = () => {
  page.value = 1
  finished.value = false
  list.value = []
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
  router.push(`/objects/${id}`)
}

const goCreate = () => {
  router.push('/objects/create')
}

onMounted(() => {
  if (route.query.risk_level) {
    activeTab.value = route.query.risk_level
  }
  loading.value = true
  fetchList()
})
</script>

<style scoped>
.object-list-page {
  background-color: #f5f5f5;
}

.object-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.object-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.object-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.object-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-active {
  background-color: #e8f7ee;
  color: #07c160;
}

.status-completed {
  background-color: #f0f0f0;
  color: #969799;
}

.status-suspended {
  background-color: #fff7e8;
  color: #ff976a;
}

.object-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #666;
}

.object-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: #999;
}
</style>
