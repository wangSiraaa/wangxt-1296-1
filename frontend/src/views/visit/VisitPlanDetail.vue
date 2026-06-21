<template>
  <div class="visit-plan-detail-page">
    <van-nav-bar title="走访计划详情" left-arrow @click-left="goBack" fixed placeholder />

    <div class="page-content">
      <div v-if="loading" style="text-align: center; padding: 40px 0;">
        <van-loading type="spinner">加载中...</van-loading>
      </div>

      <template v-else-if="planInfo">
        <div class="card">
          <div class="plan-header">
            <div class="plan-date">{{ planInfo.plan_date }}</div>
            <span :class="['status-tag', `status-${planInfo.status}`]">
              {{ planInfo.status_display }}
            </span>
          </div>
          <h3 class="plan-name">{{ planInfo.correction_object_name }}</h3>
          <div class="plan-type">{{ planInfo.plan_type }}</div>
        </div>

        <van-cell-group inset title="基本信息">
          <van-cell title="负责社工" :value="planInfo.assigned_worker_name || '未分配'" />
          <van-cell title="创建人" :value="planInfo.created_by_name || '-'" />
          <van-cell title="创建时间" :value="formatTime(planInfo.created_at)" />
          <van-cell title="是否自动生成" :value="planInfo.is_auto_generated ? '是' : '否'" />
        </van-cell-group>

        <div v-if="planInfo.remark" class="card">
          <div class="card-title">备注</div>
          <p class="remark-text">{{ planInfo.remark }}</p>
        </div>

        <div v-if="userStore.userRole === 'social_worker' && planInfo.status === 'pending'" class="action-bar">
          <van-button type="primary" block @click="goVisit">开始走访</van-button>
        </div>

        <div v-if="userStore.userRole === 'judicial' && planInfo.status === 'pending'" class="action-bar">
          <van-button type="danger" block @click="handleCancel">取消计划</van-button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getVisitPlan, cancelVisitPlan } from '@/api/visitPlan'
import { showConfirmDialog, showToast } from 'vant'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const planInfo = ref(null)
const loading = ref(false)

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await getVisitPlan(route.params.id)
    planInfo.value = res
  } catch (error) {
    console.error('Get plan detail error:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const goVisit = () => {
  router.push(`/visit-create/${route.params.id}`)
}

const handleCancel = async () => {
  try {
    await showConfirmDialog({
      title: '提示',
      message: '确定要取消该走访计划吗？'
    })
    await cancelVisitPlan(route.params.id)
    showToast('已取消')
    router.back()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Cancel plan error:', error)
    }
  }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.visit-plan-detail-page {
  background-color: #f5f5f5;
  min-height: 100vh;
  padding-bottom: 80px;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.plan-date {
  font-size: 18px;
  font-weight: 600;
}

.plan-name {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.plan-type {
  font-size: 14px;
  color: #666;
}

.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
}

.status-pending {
  background-color: #fff7e8;
  color: #ff976a;
}

.status-completed {
  background-color: #e8f7ee;
  color: #07c160;
}

.status-cancelled {
  background-color: #f0f0f0;
  color: #969799;
}

.remark-text {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 16px;
  background-color: #fff;
  box-shadow: 0 -1px 4px rgba(0, 0, 0, 0.1);
  z-index: 100;
}
</style>
