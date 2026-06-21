<template>
  <div class="feedback-create-page">
    <van-nav-bar title="提交帮教反馈" left-arrow @click-left="goBack" fixed placeholder />

    <van-form @submit="handleSubmit">
      <van-cell-group inset title="选择对象">
        <van-field
          v-model="selectedObjectName"
          is-link
          readonly
          label="矫正对象"
          placeholder="请选择矫正对象"
          @click="showObjectPicker = true"
          :rules="[{ required: true, message: '请选择矫正对象' }]"
        />
      </van-cell-group>

      <van-cell-group inset title="反馈日期">
        <van-field
          v-model="form.feedback_date"
          readonly
          label="反馈日期"
          placeholder="请选择反馈日期"
          @click="showDatePicker = true"
          :rules="[{ required: true, message: '请选择反馈日期' }]"
        />
      </van-cell-group>

      <van-cell-group inset title="帮教情况">
        <van-field
          v-model="form.behavior_situation"
          type="textarea"
          label=""
          placeholder="请详细描述近期帮教情况"
          rows="4"
          autosize
          :rules="[{ required: true, message: '请填写帮教情况' }]"
        />
      </van-cell-group>

      <van-cell-group inset title="思想动态">
        <van-field
          v-model="form.mental_state"
          type="textarea"
          label=""
          placeholder="请描述近期思想动态（选填）"
          rows="3"
          autosize
        />
      </van-cell-group>

      <van-cell-group inset title="生活状况">
        <van-field
          v-model="form.life_condition"
          type="textarea"
          label=""
          placeholder="请描述近期生活状况（选填）"
          rows="3"
          autosize
        />
      </van-cell-group>

      <van-cell-group inset title="工作学习情况">
        <van-field
          v-model="form.work_study"
          type="textarea"
          label=""
          placeholder="请描述工作或学习情况（选填）"
          rows="3"
          autosize
        />
      </van-cell-group>

      <van-cell-group inset title="存在问题">
        <van-field
          v-model="form.problems"
          type="textarea"
          label=""
          placeholder="请描述存在的问题（选填）"
          rows="3"
          autosize
        />
      </van-cell-group>

      <van-cell-group inset title="意见建议">
        <van-field
          v-model="form.suggestions"
          type="textarea"
          label=""
          placeholder="请输入您的意见或建议（选填）"
          rows="3"
          autosize
        />
      </van-cell-group>

      <div style="margin: 16px; padding-bottom: 20px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          提交反馈
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showObjectPicker" position="bottom" round>
      <div class="picker-header">
        <h3>选择矫正对象</h3>
        <van-icon name="cross" size="20" @click="showObjectPicker = false" />
      </div>
      <div class="object-list">
        <div
          v-for="obj in relatedObjects"
          :key="obj.id"
          class="object-option"
          @click="selectObject(obj)"
        >
          <div class="option-name">{{ obj.name }}</div>
          <span :class="['risk-tag', `risk-${obj.risk_level}`]">
            {{ obj.risk_level_display }}
          </span>
        </div>
      </div>
    </van-popup>

    <van-calendar
      v-model:show="showDatePicker"
      @confirm="onDateConfirm"
      color="#1989fa"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { createFamilyFeedback } from '@/api/familyFeedback'
import { getCorrectionObjects } from '@/api/correctionObject'
import { showToast } from 'vant'
import dayjs from 'dayjs'

const router = useRouter()
const userStore = useUserStore()

const form = reactive({
  correction_object: '',
  feedback_date: dayjs().format('YYYY-MM-DD'),
  behavior_situation: '',
  mental_state: '',
  life_condition: '',
  work_study: '',
  problems: '',
  suggestions: ''
})

const loading = ref(false)
const showObjectPicker = ref(false)
const showDatePicker = ref(false)
const selectedObjectName = ref('')
const relatedObjects = ref([])

const fetchRelatedObjects = async () => {
  try {
    const res = await getCorrectionObjects({ page_size: 100 })
    relatedObjects.value = res.results || res || []
  } catch (error) {
    console.error('Get related objects error:', error)
  }
}

const selectObject = (obj) => {
  form.correction_object = obj.id
  selectedObjectName.value = obj.name
  showObjectPicker.value = false
}

const onDateConfirm = (value) => {
  form.feedback_date = dayjs(value).format('YYYY-MM-DD')
  showDatePicker.value = false
}

const goBack = () => {
  router.back()
}

const handleSubmit = async () => {
  if (!form.correction_object) {
    showToast('请选择矫正对象')
    return
  }

  loading.value = true
  try {
    await createFamilyFeedback(form)
    showToast('反馈提交成功')
    router.replace('/feedbacks')
  } catch (error) {
    console.error('Submit error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchRelatedObjects()
})
</script>

<style scoped>
.feedback-create-page {
  background-color: #f5f5f5;
  min-height: 100vh;
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.picker-header h3 {
  margin: 0;
  font-size: 16px;
}

.object-list {
  max-height: 400px;
  overflow-y: auto;
}

.object-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
}

.option-name {
  font-size: 15px;
}
</style>
