<template>
  <div class="home-page page-container">
    <van-nav-bar title="社区矫正走访系统" fixed placeholder>
      <template #right>
        <van-icon name="bell-o" size="20" @click="goNotifications" />
      </template>
    </van-nav-bar>

    <div class="page-content">
      <div class="welcome-card card">
        <div class="welcome-header">
          <div class="user-info">
            <h3>{{ userStore.userName || '用户' }}</h3>
            <p class="user-role">{{ roleText }}</p>
          </div>
          <van-image
            round
            width="48"
            height="48"
            :src="avatarUrl"
          >
            <template #default>
              <van-icon name="user-o" size="32" color="#ccc" />
            </template>
          </van-image>
        </div>
      </div>

      <div class="stats-grid">
        <div v-for="stat in stats" :key="stat.label" class="stat-item card" @click="handleStatClick(stat)">
          <div class="stat-value" :class="stat.color">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title flex-between">
          <span>快捷操作</span>
        </div>
        <div class="quick-actions">
          <div
            v-for="action in quickActions"
            :key="action.label"
            class="action-item"
            @click="handleAction(action)"
          >
            <div class="action-icon" :style="{ backgroundColor: action.bgColor }">
              <van-icon :name="action.icon" size="24" color="#fff" />
            </div>
            <span class="action-label">{{ action.label }}</span>
          </div>
        </div>
      </div>

      <div v-if="recentVisits.length > 0" class="card">
        <div class="card-title flex-between">
          <span>最近走访</span>
          <van-button type="primary" size="small" plain @click="goVisitRecords">
            查看更多
          </van-button>
        </div>
        <div v-for="visit in recentVisits" :key="visit.id" class="visit-item">
          <div class="visit-info">
            <div class="visit-name">{{ visit.correction_object_name }}</div>
            <div class="visit-meta">
              <span>{{ visit.visit_way_display }}</span>
              <span class="divider">|</span>
              <span>{{ formatDate(visit.visit_date) }}</span>
            </div>
          </div>
          <span :class="['risk-tag', `risk-${getRiskLevel(visit)}`]">
            {{ getRiskText(visit) }}
          </span>
        </div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getStatistics } from '@/api/system'
import { getVisitRecords } from '@/api/visitRecord'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()
const active = ref('/home')

const statistics = ref({})
const recentVisits = ref([])

const roleText = computed(() => {
  const roleMap = {
    judicial: '司法所',
    social_worker: '社工',
    family: '家属'
  }
  return roleMap[userStore.userRole] || ''
})

const avatarUrl = computed(() => {
  return userStore.user?.avatar || ''
})

const stats = computed(() => {
  const role = userStore.userRole
  if (role === 'judicial') {
    return [
      { label: '在矫对象', value: statistics.value.total_objects || 0, color: 'text-primary', key: 'objects' },
      { label: '高风险', value: statistics.value.high_risk || 0, color: 'text-danger', key: 'high_risk' },
      { label: '今日计划', value: statistics.value.today_plans || 0, color: 'text-warning', key: 'today_plans' },
      { label: '本月走访', value: statistics.value.monthly_visits || 0, color: 'text-success', key: 'monthly_visits' }
    ]
  } else if (role === 'social_worker') {
    return [
      { label: '负责对象', value: statistics.value.total_objects || 0, color: 'text-primary', key: 'objects' },
      { label: '高风险', value: statistics.value.high_risk || 0, color: 'text-danger', key: 'high_risk' },
      { label: '今日计划', value: statistics.value.today_plans || 0, color: 'text-warning', key: 'today_plans' },
      { label: '本月走访', value: statistics.value.monthly_visits || 0, color: 'text-success', key: 'monthly_visits' }
    ]
  } else {
    return [
      { label: '关联对象', value: statistics.value.related_objects || 0, color: 'text-primary', key: 'objects' },
      { label: '本月走访', value: statistics.value.monthly_visits || 0, color: 'text-success', key: 'monthly_visits' },
      { label: '我的反馈', value: statistics.value.my_feedbacks || 0, color: 'text-warning', key: 'feedbacks' },
      { label: '未读消息', value: statistics.value.unread_notifications || 0, color: 'text-danger', key: 'notifications' }
    ]
  }
})

const quickActions = computed(() => {
  const role = userStore.userRole
  if (role === 'judicial') {
    return [
      { label: '新建对象', icon: 'add-o', bgColor: '#1989fa', action: 'createObject' },
      { label: '走访计划', icon: 'calendar-o', bgColor: '#07c160', action: 'visitPlans' },
      { label: '风险等级', icon: 'warning-o', bgColor: '#ff976a', action: 'riskLevel' },
      { label: '通知中心', icon: 'bell-o', bgColor: '#ee0a24', action: 'notifications' }
    ]
  } else if (role === 'social_worker') {
    return [
      { label: '走访登记', icon: 'edit', bgColor: '#1989fa', action: 'createVisit' },
      { label: '我的计划', icon: 'calendar-o', bgColor: '#07c160', action: 'visitPlans' },
      { label: '对象列表', icon: 'friends-o', bgColor: '#ff976a', action: 'objects' },
      { label: '定位记录', icon: 'location-o', bgColor: '#7232dd', action: 'location' }
    ]
  } else {
    return [
      { label: '提交反馈', icon: 'edit', bgColor: '#1989fa', action: 'createFeedback' },
      { label: '我的反馈', icon: 'comment-o', bgColor: '#07c160', action: 'feedbacks' },
      { label: '对象信息', icon: 'friends-o', bgColor: '#ff976a', action: 'objects' },
      { label: '走访记录', icon: 'calendar-o', bgColor: '#7232dd', action: 'visitRecords' }
    ]
  }
})

const fetchStatistics = async () => {
  try {
    const res = await getStatistics()
    statistics.value = res
  } catch (error) {
    console.error('Get statistics error:', error)
  }
}

const fetchRecentVisits = async () => {
  try {
    const res = await getVisitRecords({ page_size: 3 })
    recentVisits.value = res.results || res || []
  } catch (error) {
    console.error('Get recent visits error:', error)
  }
}

const getRiskLevel = (visit) => {
  return visit.risk_change || 'medium'
}

const getRiskText = (visit) => {
  const map = { low: '低风险', medium: '中风险', high: '高风险' }
  return map[visit.risk_change] || '中风险'
}

const formatDate = (date) => {
  return dayjs(date).format('MM-DD HH:mm')
}

const handleStatClick = (stat) => {
  const keyMap = {
    objects: '/objects',
    today_plans: '/visit-plans',
    monthly_visits: '/visit-records',
    high_risk: '/objects?risk_level=high',
    feedbacks: '/feedbacks',
    notifications: '/notifications'
  }
  if (keyMap[stat.key]) {
    router.push(keyMap[stat.key])
  }
}

const handleAction = (action) => {
  const actionMap = {
    createObject: '/objects/create',
    visitPlans: '/visit-plans',
    riskLevel: '/objects',
    notifications: '/notifications',
    createVisit: '/visit-create',
    objects: '/objects',
    location: '/location-records',
    createFeedback: '/feedbacks/create',
    feedbacks: '/feedbacks',
    visitRecords: '/visit-records'
  }
  if (actionMap[action.action]) {
    router.push(actionMap[action.action])
  }
}

const goNotifications = () => {
  router.push('/notifications')
}

const goVisitRecords = () => {
  router.push('/visit-records')
}

onMounted(() => {
  fetchStatistics()
  if (userStore.userRole !== 'family') {
    fetchRecentVisits()
  }
})
</script>

<style scoped>
.home-page {
  background-color: #f5f5f5;
}

.welcome-card {
  background: linear-gradient(135deg, #1989fa 0%, #00b4ff 100%);
  color: #fff;
}

.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info h3 {
  color: #fff;
  font-size: 20px;
  margin-bottom: 4px;
}

.user-role {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.stat-item {
  text-align: center;
  padding: 20px 12px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px 8px;
}

.action-item {
  text-align: center;
  cursor: pointer;
}

.action-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 8px;
}

.action-label {
  font-size: 12px;
  color: #333;
}

.visit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.visit-item:last-child {
  border-bottom: none;
}

.visit-name {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 4px;
}

.visit-meta {
  font-size: 12px;
  color: #999;
}

.divider {
  margin: 0 6px;
  color: #ddd;
}
</style>
