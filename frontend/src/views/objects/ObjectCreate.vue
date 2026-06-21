<template>
  <div class="object-create-page">
    <van-nav-bar :title="isEdit ? '编辑对象' : '新增对象'" left-arrow @click-left="goBack" fixed placeholder />

    <van-form @submit="handleSubmit">
      <van-cell-group inset title="基本信息">
        <van-field
          v-model="form.name"
          name="name"
          label="姓名"
          placeholder="请输入姓名"
          :rules="[{ required: true, message: '请填写姓名' }]"
        />
        <van-field
          v-model="form.id_card"
          name="id_card"
          label="身份证号"
          placeholder="请输入身份证号"
          :rules="[{ required: true, message: '请填写身份证号' }]"
        />
        <van-field
          v-model="form.gender"
          is-link
          readonly
          name="gender"
          label="性别"
          placeholder="请选择性别"
          @click="showGenderPicker = true"
        />
        <van-field
          v-model="form.age"
          name="age"
          type="number"
          label="年龄"
          placeholder="请输入年龄"
          :rules="[{ required: true, message: '请填写年龄' }]"
        />
        <van-field
          v-model="form.phone"
          name="phone"
          label="联系电话"
          placeholder="请输入联系电话"
        />
        <van-field
          v-model="form.address"
          name="address"
          label="居住地址"
          placeholder="请输入居住地址"
          type="textarea"
          rows="2"
        />
      </van-cell-group>

      <van-cell-group inset title="矫正信息">
        <van-field
          v-model="form.correction_type"
          name="correction_type"
          label="矫正类型"
          placeholder="请输入矫正类型"
          :rules="[{ required: true, message: '请填写矫正类型' }]"
        />
        <van-field
          v-model="form.correction_start"
          name="correction_start"
          label="矫正开始日期"
          placeholder="请选择开始日期"
          readonly
          @click="showStartDate = true"
          :rules="[{ required: true, message: '请选择开始日期' }]"
        />
        <van-field
          v-model="form.correction_end"
          name="correction_end"
          label="矫正结束日期"
          placeholder="请选择结束日期"
          readonly
          @click="showEndDate = true"
          :rules="[{ required: true, message: '请选择结束日期' }]"
        />
        <van-field
          v-model="form.risk_level"
          is-link
          readonly
          name="risk_level"
          label="风险等级"
          placeholder="请选择风险等级"
          @click="showRiskPicker = true"
          :rules="[{ required: true, message: '请选择风险等级' }]"
        />
        <van-field
          v-model="form.status"
          is-link
          readonly
          name="status"
          label="状态"
          placeholder="请选择状态"
          @click="showStatusPicker = true"
        />
      </van-cell-group>

      <van-cell-group inset title="定位信息">
        <van-field
          v-model="form.home_longitude"
          name="home_longitude"
          type="number"
          label="家庭经度"
          placeholder="请输入家庭住址经度"
        />
        <van-field
          v-model="form.home_latitude"
          name="home_latitude"
          type="number"
          label="家庭纬度"
          placeholder="请输入家庭住址纬度"
        />
        <van-field
          v-model="form.allowed_deviation"
          name="allowed_deviation"
          type="number"
          label="允许偏离距离"
          placeholder="请输入允许偏离距离(米)"
        />
      </van-cell-group>

      <van-cell-group inset title="备注">
        <van-field
          v-model="form.remark"
          name="remark"
          type="textarea"
          rows="3"
          placeholder="请输入备注信息"
        />
      </van-cell-group>

      <div style="margin: 16px; padding-bottom: 20px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          {{ isEdit ? '保存修改' : '提交' }}
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showGenderPicker" position="bottom">
      <van-picker
        :columns="genderColumns"
        @confirm="onGenderConfirm"
        @cancel="showGenderPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showRiskPicker" position="bottom">
      <van-picker
        :columns="riskColumns"
        @confirm="onRiskConfirm"
        @cancel="showRiskPicker = false"
      />
    </van-popup>

    <van-popup v-model:show="showStatusPicker" position="bottom">
      <van-picker
        :columns="statusColumns"
        @confirm="onStatusConfirm"
        @cancel="showStatusPicker = false"
      />
    </van-popup>

    <van-calendar v-model:show="showStartDate" @confirm="onStartDateConfirm" color="#1989fa" />
    <van-calendar v-model:show="showEndDate" @confirm="onEndDateConfirm" color="#1989fa" />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { showToast } from 'vant'
import { createCorrectionObject, updateCorrectionObject, getCorrectionObject } from '@/api/correctionObject'
import dayjs from 'dayjs'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const loading = ref(false)

const form = reactive({
  name: '',
  id_card: '',
  gender: '',
  age: null,
  phone: '',
  address: '',
  correction_type: '',
  correction_start: '',
  correction_end: '',
  risk_level: 'medium',
  status: 'active',
  home_longitude: null,
  home_latitude: null,
  allowed_deviation: 500,
  remark: ''
})

const showGenderPicker = ref(false)
const showRiskPicker = ref(false)
const showStatusPicker = ref(false)
const showStartDate = ref(false)
const showEndDate = ref(false)

const genderColumns = [
  { text: '男', value: 'male' },
  { text: '女', value: 'female' }
]

const riskColumns = [
  { text: '低风险', value: 'low' },
  { text: '中风险', value: 'medium' },
  { text: '高风险', value: 'high' }
]

const statusColumns = [
  { text: '在矫中', value: 'active' },
  { text: '已解矫', value: 'completed' },
  { text: '暂停', value: 'suspended' }
]

const goBack = () => {
  router.back()
}

const onGenderConfirm = ({ selectedOptions }) => {
  form.gender = selectedOptions[0].value
  showGenderPicker.value = false
}

const onRiskConfirm = ({ selectedOptions }) => {
  form.risk_level = selectedOptions[0].value
  showRiskPicker.value = false
}

const onStatusConfirm = ({ selectedOptions }) => {
  form.status = selectedOptions[0].value
  showStatusPicker.value = false
}

const onStartDateConfirm = (value) => {
  form.correction_start = dayjs(value).format('YYYY-MM-DD')
  showStartDate.value = false
}

const onEndDateConfirm = (value) => {
  form.correction_end = dayjs(value).format('YYYY-MM-DD')
  showEndDate.value = false
}

const fetchDetail = async () => {
  try {
    const res = await getCorrectionObject(route.params.id)
    Object.assign(form, res)
  } catch (error) {
    console.error('Get object detail error:', error)
  }
}

const handleSubmit = async () => {
  loading.value = true
  try {
    if (isEdit.value) {
      await updateCorrectionObject(route.params.id, form)
      showToast('修改成功')
    } else {
      await createCorrectionObject(form)
      showToast('创建成功')
    }
    router.back()
  } catch (error) {
    console.error('Submit error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (isEdit.value) {
    fetchDetail()
  }
})
</script>

<style scoped>
.object-create-page {
  background-color: #f5f5f5;
  min-height: 100vh;
}
</style>
