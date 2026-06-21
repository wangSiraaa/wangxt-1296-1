<template>
  <div class="visit-create-page">
    <van-nav-bar title="走访登记" left-arrow @click-left="goBack" fixed placeholder />

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

      <van-cell-group inset title="走访信息">
        <van-field
          v-model="form.visit_way"
          is-link
          readonly
          name="visit_way"
          label="走访方式"
          placeholder="请选择走访方式"
          @click="showWayPicker = true"
          :rules="[{ required: true, message: '请选择走访方式' }]"
        />
        <van-field
          v-model="form.visit_date"
          name="visit_date"
          label="走访时间"
          placeholder="请选择走访时间"
          readonly
          @click="showDateTime = true"
          :rules="[{ required: true, message: '请选择走访时间' }]"
        />
      </van-cell-group>

      <van-cell-group inset title="定位信息">
        <div class="location-section">
          <div class="location-btn" @click="getLocation">
            <van-icon name="location-o" size="20" color="#1989fa" />
            <span>{{ locationText }}</span>
          </div>
          <div v-if="locationValid !== null" class="location-result" :class="{ valid: locationValid, invalid: !locationValid }">
            <van-icon :name="locationValid ? 'checked' : 'close'" size="16" />
            <span>{{ locationResultText }}</span>
          </div>
          <div v-if="locationInfo" class="location-detail">
            <p>经度：{{ locationInfo.longitude }}</p>
            <p>纬度：{{ locationInfo.latitude }}</p>
            <p v-if="deviation !== null">偏离距离：{{ deviation.toFixed(1) }} 米</p>
          </div>
        </div>
      </van-cell-group>

      <van-cell-group inset title="谈话摘要">
        <van-field
          v-model="form.talk_summary"
          type="textarea"
          name="talk_summary"
          label=""
          placeholder="请输入谈话内容摘要"
          rows="6"
          autosize
          :rules="[{ required: true, message: '请填写谈话摘要' }]"
        />
      </van-cell-group>

      <van-cell-group inset title="风险评估">
        <van-field
          v-model="form.risk_change"
          is-link
          readonly
          name="risk_change"
          label="风险变化"
          placeholder="选择风险等级（不变可不选）"
          @click="showRiskPicker = true"
        />
      </van-cell-group>

      <van-cell-group inset title="走访照片">
        <van-uploader
          v-model="fileList"
          multiple
          max-count="9"
          :after-read="afterRead"
        />
      </van-cell-group>

      <van-cell-group inset title="备注">
        <van-field
          v-model="form.remark"
          type="textarea"
          rows="2"
          placeholder="请输入备注信息"
        />
      </van-cell-group>

      <div style="margin: 16px; padding-bottom: 20px;">
        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="loading"
          :disabled="!canSubmit"
        >
          提交走访记录
        </van-button>
        <p v-if="!canSubmit && locationValid === false" class="submit-tip">
          定位偏离允许范围，无法提交走访记录
        </p>
      </div>
    </van-form>

    <van-popup v-model:show="showObjectPicker" position="bottom" round>
      <div class="picker-header">
        <h3>选择矫正对象</h3>
        <van-icon name="cross" size="20" @click="showObjectPicker = false" />
      </div>
      <van-search v-model="objectSearch" placeholder="搜索对象" shape="round" />
      <div class="object-list">
        <div
          v-for="obj in filteredObjects"
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

    <van-popup v-model:show="showWayPicker" position="bottom">
      <van-picker
        :columns="wayColumns"
        @confirm="onWayConfirm"
        @cancel="showWayPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showRiskPicker" position="bottom">
      <van-picker
        :columns="riskColumns"
        @confirm="onRiskConfirm"
        @cancel="showRiskPicker = false"
      />
    </van-popup>

    <van-calendar
      v-model:show="showDateTime"
      type="datetime"
      @confirm="onDateTimeConfirm"
      color="#1989fa"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast } from 'vant'
import { createVisitRecord } from '@/api/visitRecord'
import { getCorrectionObjects } from '@/api/correctionObject'
import { getVisitPlan } from '@/api/visitPlan'
import { validateLocation } from '@/api/locationRecord'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()

const form = reactive({
  correction_object: '',
  visit_way: '',
  visit_date: '',
  talk_summary: '',
  risk_change: '',
  remark: ''
})

const loading = ref(false)
const showObjectPicker = ref(false)
const showWayPicker = ref(false)
const showRiskPicker = ref(false)
const showDateTime = ref(false)

const selectedObjectName = ref('')
const objectList = ref([])
const objectSearch = ref('')

const locationText = ref('点击获取定位')
const locationValid = ref(null)
const locationInfo = ref(null)
const deviation = ref(null)
const fileList = ref([])
const planId = ref(null)

const canSubmit = computed(() => {
  return locationValid.value !== false
})

const locationResultText = computed(() => {
  if (locationValid.value === null) return ''
  return locationValid.value ? '定位有效' : '定位偏离'
})

const filteredObjects = computed(() => {
  if (!objectSearch.value) return objectList.value
  const keyword = objectSearch.value.toLowerCase()
  return objectList.value.filter(obj =>
    obj.name.toLowerCase().includes(keyword) ||
    obj.id_card.includes(keyword)
  )
})

const wayColumns = [
  { text: '入户走访', value: 'home' },
  { text: '电话走访', value: 'telephone' },
  { text: '视频走访', value: 'video' },
  { text: '司法所报到', value: 'office' },
  { text: '其他', value: 'other' }
]

const riskColumns = [
  { text: '不变', value: '' },
  { text: '低风险', value: 'low' },
  { text: '中风险', value: 'medium' },
  { text: '高风险', value: 'high' }
]

const goBack = () => {
  router.back()
}

const fetchObjects = async () => {
  try {
    const res = await getCorrectionObjects({ page_size: 100 })
    objectList.value = res.results || res || []
  } catch (error) {
    console.error('Get objects error:', error)
  }
}

const fetchPlanInfo = async (planId) => {
  try {
    const plan = await getVisitPlan(planId)
    form.correction_object = plan.correction_object
    selectedObjectName.value = plan.correction_object_name
    form.visit_date = dayjs().format('YYYY-MM-DD HH:mm:ss')
    form.visit_way = 'home'
  } catch (error) {
    console.error('Get plan error:', error)
  }
}

const selectObject = (obj) => {
  form.correction_object = obj.id
  selectedObjectName.value = obj.name
  showObjectPicker.value = false
  locationValid.value = null
  locationInfo.value = null
  locationText.value = '点击获取定位'
}

const onWayConfirm = ({ selectedOptions }) => {
  form.visit_way = selectedOptions[0].value
  showWayPicker.value = false
}

const onRiskConfirm = ({ selectedOptions }) => {
  form.risk_change = selectedOptions[0].value
  showRiskPicker.value = false
}

const onDateTimeConfirm = (value) => {
  form.visit_date = dayjs(value).format('YYYY-MM-DD HH:mm:ss')
  showDateTime.value = false
}

const getLocation = () => {
  locationText.value = '定位中...'

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords
        locationInfo.value = { latitude, longitude }
        locationText.value = '已获取定位'

        if (form.correction_object) {
          try {
            const res = await validateLocation({
              correction_object_id: form.correction_object,
              longitude: longitude,
              latitude: latitude
            })
            locationValid.value = res.valid
            deviation.value = res.deviation
          } catch (error) {
            console.error('Validate location error:', error)
            locationValid.value = true
          }
        } else {
          showToast('请先选择矫正对象')
          locationValid.value = null
        }
      },
      (error) => {
        console.error('Geolocation error:', error)
        locationText.value = '定位失败，请检查定位权限'
        showToast('定位失败，请检查定位权限')

        if (form.correction_object) {
          locationValid.value = true
          locationInfo.value = { latitude: 0, longitude: 0 }
        }
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    )
  } else {
    locationText.value = '浏览器不支持定位'
    showToast('浏览器不支持定位功能')

    if (form.correction_object) {
      locationValid.value = true
      locationInfo.value = { latitude: 0, longitude: 0 }
    }
  }
}

const afterRead = (file) => {
  console.log('File uploaded:', file)
}

const handleSubmit = async () => {
  if (!form.correction_object) {
    showToast('请选择矫正对象')
    return
  }

  if (locationValid.value === false) {
    showToast('定位偏离允许范围，无法提交')
    return
  }

  loading.value = true
  try {
    const submitData = {
      ...form,
      visit_plan: planId.value || undefined,
      longitude: locationInfo.value?.longitude,
      latitude: locationInfo.value?.latitude,
      location_valid: locationValid.value,
      location_deviation: deviation.value,
      photos: fileList.value.map(f => f.url || f.content)
    }

    await createVisitRecord(submitData)
    showToast('走访记录提交成功')
    router.replace('/visit-records')
  } catch (error) {
    console.error('Submit error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchObjects()

  if (route.params.planId) {
    planId.value = route.params.planId
    fetchPlanInfo(route.params.planId)
  } else {
    form.visit_date = dayjs().format('YYYY-MM-DD HH:mm:ss')
  }
})
</script>

<style scoped>
.visit-create-page {
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

.location-section {
  padding: 16px;
}

.location-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background-color: #f5f9ff;
  border-radius: 8px;
  color: #1989fa;
  cursor: pointer;
  font-size: 14px;
}

.location-result {
  text-align: center;
  margin-top: 12px;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.location-result.valid {
  color: #07c160;
}

.location-result.invalid {
  color: #ee0a24;
}

.location-detail {
  margin-top: 12px;
  padding: 12px;
  background-color: #f9f9f9;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
}

.location-detail p {
  margin: 4px 0;
}

.submit-tip {
  text-align: center;
  color: #ee0a24;
  font-size: 13px;
  margin-top: 8px;
}
</style>
