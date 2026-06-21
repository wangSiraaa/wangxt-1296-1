<template>
  <div class="visit-plan-page page-container">
    <van-nav-bar title="走访计划" fixed placeholder>
      <template #right>
        <van-icon v-if="userStore.userRole === 'judicial'" name="plus" size="20" @click="goCreate" />
      </template>
    </van-nav-bar>

    <van-tabs v-model:active="activeTab" @change="onTabChange">
      <van-tab title="全部" name="all" />
      <van-tab title="待执行" name="pending" />
      <van-tab title="进行中" name="in_progress" />
      <van-tab title="已完成" name="completed" />
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
            class="plan-item card"
            @click="goDetail(item.id)"
          >
            <div class="plan-header">
              <span class="plan-date">{{ item.plan_date }}</span>
              <span :class="['status-tag', `status-${item.status}`]">
                {{ item.status_display }}
              </span>
            </div>
            <h4 class="plan-name">{{ item.correction_object_name }}</h4>
            <div class="plan-meta">
              <span class="meta-item">
                <van-icon name="todo-list-o" size="12" />
                {{ item.plan_type }}
              </span>
              <span class="meta-item">
                <van-icon name="user-o" size="12" />
                {{ item.assigned_worker_name || '未分配' }}
              </span>
            </div>
            <div v-if="item.remark" class="plan-remark">
              {{ item.remark }}
            </div>
          </div>
        </van-list>
      </van-pull-refresh>

      <div v-if="!loading && list.length === 0" class="empty-state">
        <van-empty description="暂无走访计划" />
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

    <van-action-sheet v-model:show="showCreateMenu" title="创建走访计划">
      <van-cell-group inset>
        <van-cell title="单个创建" is-link @click="goSingleCreate" />
        <van-cell title="批量生成月度计划" is-link @click="showBatchGenerate" />
      </van-cell-group>
    </van-action-sheet>

    <van-dialog v-model:show="showBatchDialog" title="批量生成月度计划" show-cancel-button @confirm="handleBatchGenerate">
      <div style="padding: 16px;">
        <van-field
          v-model="batchRiskLevel"
          is-link
          readonly
          label="风险等级"
          placeholder="选择风险等级（不选则全部）"
          @click="showRiskPicker = true"
        />
      </div>
    </van-dialog>

    <van-popup v-model:show="showRiskPicker" position="bottom">
      <van-picker
        :columns="riskColumns"
        @confirm="onRiskConfirm"
        @cancel="showRiskPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getVisitPlans, batchGeneratePlans } from '@/api/visitPlan'
import { showToast } from 'vant'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const active = ref('/visit-plans')

const list = ref([])
const loading = ref(false)
const refreshing = ref(false)
const finished = ref(false)
const page = ref(1)
const pageSize = 20
const activeTab = ref('all')

const showCreateMenu = ref(false)
const showBatchDialog = ref(false)
const showRiskPicker = ref(false)
const batchRiskLevel = ref('')
const batchRiskLevelText = ref('')

const riskColumns = [
  { text: '全部对象', value: '' },
  { text: '低风险', value: 'low' },
  { text: '中风险', value: 'medium' },
  { text: '高风险', value: 'high' }
]

const fetchList = async () => {
  try {
    const params = {
      page: page.value,
      page_size: pageSize
    }

    if (activeTab.value !== 'all') {
      params.status = activeTab.value
    }

    if (route.query.correction_object_id) {
      params.correction_object_id = route.query.correction_object_id
    }

    const res = await getVisitPlans(params)
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
    console.error('Get visit plans error:', error)
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
  router.push(`/visit-plans/${id}`)
}

const goCreate = () => {
  if (userStore.userRole === 'judicial') {
    showCreateMenu.value = true
  }
}

const goSingleCreate = () => {
  showCreateMenu.value = false
  router.push('/visit-plans/create')
}

const showBatchGenerate = () => {
  showCreateMenu.value = false
  showBatchDialog.value = true
}

const onRiskConfirm = ({ selectedOptions }) => {
  batchRiskLevel.value = selectedOptions[0].value
  batchRiskLevelText.value = selectedOptions[0].text
  showRiskPicker.value = false
}

const handleBatchGenerate = async () => {
  try {
    const res = await batchGeneratePlans({ risk_level: batchRiskLevel.value || undefined })
    showToast(`成功生成${res.plan_count}条计划`)
    showBatchDialog.value = false
    onRefresh()
  } catch (error) {
    console.error('Batch generate error:', error)
  }
}

onMounted(() => {
  loading.value = true
  fetchList()
})
</script>

<style scoped>
.visit-plan-page {
  background-color: #f5f5f5;
}

.plan-item {
  cursor: pointer;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.plan-date {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-pending {
  background-color: #fff7e8;
  color: #ff976a;
}

.status-in_progress {
  background-color: #e8f3ff;
  color: #1989fa;
}

.status-completed {
  background-color: #e8f7ee;
  color: #07c160;
}

.status-cancelled {
  background-color: #f0f0f0;
  color: #969799;
}

.plan-name {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 8px 0;
}

.plan-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #666;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.plan-remark {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: #999;
}
</style>
