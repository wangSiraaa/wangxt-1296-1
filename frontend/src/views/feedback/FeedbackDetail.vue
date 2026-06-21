<template>
  <div class="feedback-detail-page">
    <van-nav-bar title="反馈详情" left-arrow @click-left="goBack" fixed placeholder />

    <div class="page-content">
      <div v-if="loading" style="text-align: center; padding: 40px 0;">
        <van-loading type="spinner">加载中...</van-loading>
      </div>

      <template v-else-if="feedbackInfo">
        <div class="card">
          <div class="feedback-header">
            <h3 class="feedback-object">{{ feedbackInfo.correction_object_name }}</h3>
            <span :class="['status-tag', `status-${feedbackInfo.status}`]">
              {{ feedbackInfo.status_display }}
            </span>
          </div>
          <div class="feedback-meta">
            <span>
              <van-icon name="calendar-o" size="14" />
              {{ feedbackInfo.feedback_date }}
            </span>
            <span>
              <van-icon name="user-o" size="14" />
              {{ feedbackInfo.family_user_name }}
            </span>
          </div>
        </div>

        <div class="card">
          <div class="card-title">帮教情况</div>
          <p class="content-text">{{ feedbackInfo.behavior_situation }}</p>
        </div>

        <div v-if="feedbackInfo.mental_state" class="card">
          <div class="card-title">思想动态</div>
          <p class="content-text">{{ feedbackInfo.mental_state }}</p>
        </div>

        <div v-if="feedbackInfo.life_condition" class="card">
          <div class="card-title">生活状况</div>
          <p class="content-text">{{ feedbackInfo.life_condition }}</p>
        </div>

        <div v-if="feedbackInfo.work_study" class="card">
          <div class="card-title">工作学习情况</div>
          <p class="content-text">{{ feedbackInfo.work_study }}</p>
        </div>

        <div v-if="feedbackInfo.problems" class="card">
          <div class="card-title">存在问题</div>
          <p class="content-text">{{ feedbackInfo.problems }}</p>
        </div>

        <div v-if="feedbackInfo.suggestions" class="card">
          <div class="card-title">意见建议</div>
          <p class="content-text">{{ feedbackInfo.suggestions }}</p>
        </div>

        <div v-if="feedbackInfo.status === 'reviewed'" class="card">
          <div class="card-title">审核意见</div>
          <p class="content-text">{{ feedbackInfo.review_remark || '无' }}</p>
          <p class="review-info">
            审核人：{{ feedbackInfo.reviewed_by_name || '-' }}
            <br />
            审核时间：{{ feedbackInfo.reviewed_at || '-' }}
          </p>
        </div>

        <div v-if="userStore.userRole === 'judicial' && feedbackInfo.status === 'submitted'" class="action-bar">
          <van-button type="primary" block @click="showReviewDialog = true">
            审核反馈
          </van-button>
        </div>
      </template>
    </div>

    <van-dialog v-model:show="showReviewDialog" title="审核反馈" show-cancel-button @confirm="handleReview">
      <div style="padding: 16px;">
        <van-field
          v-model="reviewRemark"
          type="textarea"
          label="审核意见"
          placeholder="请输入审核意见"
          rows="3"
        />
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getFamilyFeedback, reviewFamilyFeedback } from '@/api/familyFeedback'
import { showToast } from 'vant'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const feedbackInfo = ref(null)
const loading = ref(false)
const showReviewDialog = ref(false)
const reviewRemark = ref('')

const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await getFamilyFeedback(route.params.id)
    feedbackInfo.value = res
  } catch (error) {
    console.error('Get feedback detail error:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const handleReview = async () => {
  try {
    await reviewFamilyFeedback(route.params.id, {
      review_remark: reviewRemark.value
    })
    showToast('审核成功')
    showReviewDialog.value = false
    fetchDetail()
  } catch (error) {
    console.error('Review error:', error)
  }
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.feedback-detail-page {
  background-color: #f5f5f5;
  min-height: 100vh;
  padding-bottom: 80px;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.feedback-object {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.feedback-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #666;
}

.feedback-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
}

.status-submitted {
  background-color: #fff7e8;
  color: #ff976a;
}

.status-reviewed {
  background-color: #e8f7ee;
  color: #07c160;
}

.content-text {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  margin: 0;
}

.review-info {
  font-size: 12px;
  color: #999;
  margin-top: 12px;
  line-height: 1.8;
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
