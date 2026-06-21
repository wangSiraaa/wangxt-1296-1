<template>
  <div class="visit-record-detail-page">
    <van-nav-bar title="走访记录详情" left-arrow @click-left="goBack" fixed placeholder />

    <div class="page-content">
      <div v-if="loading" style="text-align: center; padding: 40px 0;">
        <van-loading type="spinner">加载中...</van-loading>
      </div>

      <template v-else-if="recordInfo">
        <div class="card">
          <div class="record-header">
            <h3 class="record-name">{{ recordInfo.correction_object_name }}</h3>
            <span :class="['way-tag', `way-${recordInfo.visit_way}`]">
              {{ recordInfo.visit_way_display }}
            </span>
          </div>
          <div class="record-time">
            <van-icon name="clock-o" size="14" />
            <span>{{ formatDateTime(recordInfo.visit_date) }}</span>
          </div>
          <div class="record-visitor">
            <van-icon name="user-o" size="14" />
            <span>走访人：{{ recordInfo.visitor_name || '-' }}</span>
          </div>
        </div>

        <div class="card">
          <div class="card-title">谈话摘要</div>
          <p class="talk-summary">{{ recordInfo.talk_summary }}</p>
        </div>

        <div class="card">
          <div class="card-title">定位信息</div>
          <van-cell-group inset>
            <van-cell
              title="定位状态"
              :value="recordInfo.location_valid ? '有效' : '偏离'"
              :value-class="recordInfo.location_valid ? 'text-success' : 'text-danger'"
            />
            <van-cell
              v-if="recordInfo.location_deviation !== null"
              title="偏离距离"
              :value="recordInfo.location_deviation + ' 米'"
            />
          </van-cell-group>
        </div>

        <div v-if="recordInfo.risk_change" class="card">
          <div class="card-title">风险变化</div>
          <div class="risk-change">
            <span :class="['risk-tag', `risk-${recordInfo.risk_change}`]">
              {{ recordInfo.risk_change_display }}
            </span>
          </div>
        </div>

        <div v-if="recordInfo.photos && recordInfo.photos.length > 0" class="card">
          <div class="card-title">走访照片</div>
          <van-image-preview
            v-model:show="showPreview"
            :images="recordInfo.photos"
            :start-position="previewStart"
          />
          <div class="photo-grid">
            <img
              v-for="(photo, index) in recordInfo.photos"
              :key="index"
              :src="photo"
              class="photo-item"
              @click="onPreview(index)"
            />
          </div>
        </div>

        <div v-if="recordInfo.remark" class="card">
          <div class="card-title">备注</div>
          <p class="remark-text">{{ recordInfo.remark }}</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getVisitRecord } from '@/api/visitRecord'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()

const recordInfo = ref(null)
const loading = ref(false)
const showPreview = ref(false)
const previewStart = ref(0)

const formatDateTime = (datetime) => {
  return dayjs(datetime).format('YYYY-MM-DD HH:mm')
}

const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await getVisitRecord(route.params.id)
    recordInfo.value = res
  } catch (error) {
    console.error('Get record detail error:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const onPreview = (index) => {
  previewStart.value = index
  showPreview.value = true
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.visit-record-detail-page {
  background-color: #f5f5f5;
  min-height: 100vh;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.record-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.way-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
  background-color: #e8f3ff;
  color: #1989fa;
}

.record-time,
.record-visitor {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
  margin-bottom: 6px;
}

.talk-summary {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  margin: 0;
}

.risk-change {
  text-align: center;
  padding: 12px 0;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.photo-item {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
}

.remark-text {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}
</style>
