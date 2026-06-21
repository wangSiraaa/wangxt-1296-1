<template>
  <div class="object-detail-page">
    <van-nav-bar title="对象详情" left-arrow @click-left="goBack" fixed placeholder />

    <div class="page-content">
      <div v-if="loading" style="text-align: center; padding: 40px 0;">
        <van-loading type="spinner">加载中...</van-loading>
      </div>

      <template v-else-if="objectInfo">
        <div class="base-info card">
          <div class="info-header">
            <div class="info-main">
              <h3 class="object-name">{{ objectInfo.name }}</h3>
              <div class="tags">
                <span :class="['risk-tag', `risk-${objectInfo.risk_level}`]">
                  {{ objectInfo.risk_level_display }}
                </span>
                <span :class="['status-tag', `status-${objectInfo.status}`]">
                  {{ objectInfo.status_display }}
                </span>
              </div>
            </div>
          </div>

          <van-cell-group inset style="margin-top: 12px;">
            <van-cell title="身份证号" :value="maskIdCard(objectInfo.id_card)" />
            <van-cell title="性别" :value="objectInfo.gender === 'male' ? '男' : '女'" />
            <van-cell title="年龄" :value="objectInfo.age + '岁'" />
            <van-cell title="联系电话" :value="objectInfo.phone || '-'" />
            <van-cell title="居住地址" :value="objectInfo.address" />
          </van-cell-group>
        </div>

        <div class="card">
          <div class="card-title">矫正信息</div>
          <van-cell-group inset>
            <van-cell title="矫正类型" :value="objectInfo.correction_type" />
            <van-cell title="矫正开始日期" :value="objectInfo.correction_start" />
            <van-cell title="矫正结束日期" :value="objectInfo.correction_end" />
            <van-cell title="负责社工" :value="objectInfo.assigned_worker_name || '-'" />
            <van-cell title="负责司法所" :value="objectInfo.assigned_judicial_name || '-'" />
          </van-cell-group>
        </div>

        <div v-if="objectInfo.home_longitude" class="card">
          <div class="card-title">定位信息</div>
          <van-cell-group inset>
            <van-cell title="家庭住址经度" :value="objectInfo.home_longitude" />
            <van-cell title="家庭住址纬度" :value="objectInfo.home_latitude" />
            <van-cell title="允许偏离距离" :value="objectInfo.allowed_deviation + '米'" />
          </van-cell-group>
        </div>

        <div v-if="objectInfo.remark" class="card">
          <div class="card-title">备注</div>
          <p class="remark-text">{{ objectInfo.remark }}</p>
        </div>

        <div class="card">
          <div class="card-title">快捷操作</div>
          <div class="action-grid">
            <div class="action-item" @click="goVisitPlans">
            <van-icon name="calendar-o" size="22" color="#1989fa" />
            <span>走访计划</span>
          </div>
            <div class="action-item" @click="goVisitRecords">
            <van-icon name="todo-list-o" size="22" color="#07c160" />
            <span>走访记录</span>
          </div>
            <div class="action-item" @click="goFeedbacks">
            <van-icon name="comment-o" size="22" color="#ff976a" />
            <span>帮教反馈</span>
          </div>
          <div v-if="userStore.userRole === 'judicial'" class="action-item" @click="showRiskChange">
            <van-icon name="warning-o" size="22" color="#ee0a24" />
            <span>调整风险</span>
          </div>
        </div>
      </div>

      <div v-if="userStore.userRole === 'judicial'" class="action-bar">
        <van-button type="primary" block @click="goEdit">编辑</van-button>
      </div>
    </template>
    </div>

    <van-action-sheet v-model:show="showRiskSheet" title="调整风险等级" cancel-text="取消">
      <div style="padding: 16px;">
        <h4 style="margin-bottom: 16px;">当前风险等级：{{ objectInfo?.risk_level_display }}</h4>
        <van-radio-group v-model="newRiskLevel">
          <van-cell-group inset>
            <van-cell title="低风险" clickable @click="newRiskLevel = 'low'">
              <template #right-icon>
                <van-radio name="low" />
              </template>
            </van-cell>
            <van-cell title="中风险" clickable @click="newRiskLevel = 'medium'">
              <template #right-icon>
                <van-radio name="medium" />
              </template>
            </van-cell>
            <van-cell title="高风险" clickable @click="newRiskLevel = 'high'">
              <template #right-icon>
                <van-radio name="high" />
              </template>
            </van-cell>
          </van-cell-group>
        </van-radio-group>
        <van-field
          v-model="riskReason"
          type="textarea"
          label="调整原因"
          placeholder="请输入调整原因"
          rows="3"
          style="margin-top: 16px;"
        />
        <van-button
          type="primary"
          block
          style="margin-top: 16px;"
          @click="confirmRiskChange"
          :loading="riskLoading"
        >
          确认调整
        </van-button>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getCorrectionObject, changeRiskLevel } from '@/api/correctionObject'
import { showToast } from 'vant'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const objectInfo = ref(null)
const loading = ref(false)
const showRiskSheet = ref(false)
const newRiskLevel = ref('')
const riskReason = ref('')
const riskLoading = ref(false)

const maskIdCard = (idCard) => {
  if (!idCard) return '-'
  if (idCard.length < 8) return idCard
  return idCard.slice(0, 6) + '********' + idCard.slice(-4)
}

const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await getCorrectionObject(route.params.id)
    objectInfo.value = res
    newRiskLevel.value = res.risk_level
  } catch (error) {
    console.error('Get object detail error:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const goEdit = () => {
  router.push(`/objects/edit/${route.params.id}`)
}

const goVisitPlans = () => {
  router.push(`/visit-plans?correction_object_id=${route.params.id}`)
}

const goVisitRecords = () => {
  router.push(`/visit-records?correction_object_id=${route.params.id}`)
}

const goFeedbacks = () => {
  router.push(`/feedbacks?correction_object_id=${route.params.id}`)
}

const showRiskChange = () => {
  newRiskLevel.value = objectInfo.value.risk_level
  riskReason.value = ''
  showRiskSheet.value = true
}

const confirmRiskChange = async () => {
  if (!riskReason.value) {
    showToast('请输入调整原因')
    return
  }
  riskLoading.value = true
  try {
    await changeRiskLevel(route.params.id, {
      to_level: newRiskLevel.value,
      reason: riskReason.value
    })
    showToast('风险等级调整成功')
    showRiskSheet.value = false
    fetchDetail()
  } catch (error) {
    console.error('Change risk level error:', error)
  } finally {
    riskLoading.value = false
  }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.object-detail-page {
  background-color: #f5f5f5;
  min-height: 100vh;
  padding-bottom: 80px;
}

.info-header {
  margin-bottom: 12px;
}

.object-name {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 8px;
}

.tags {
  display: flex;
  gap: 8px;
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

.remark-text {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px 8px;
}

.action-item {
  text-align: center;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #333;
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
