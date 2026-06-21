<template>
  <div class="register-container">
    <van-nav-bar title="用户注册" left-arrow @click-left="goBack" />

    <van-form @submit="handleRegister">
      <van-cell-group inset>
        <van-field
          v-model="form.username"
          name="username"
          label="用户名"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请填写用户名' }]"
        />
        <van-field
          v-model="form.real_name"
          name="real_name"
          label="真实姓名"
          placeholder="请输入真实姓名"
          :rules="[{ required: true, message: '请填写真实姓名' }]"
        />
        <van-field
          v-model="form.password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请填写密码' }]"
        />
        <van-field
          v-model="form.confirm_password"
          type="password"
          name="confirm_password"
          label="确认密码"
          placeholder="请再次输入密码"
          :rules="[{ required: true, message: '请确认密码' }]"
        />
        <van-field
          v-model="form.phone"
          name="phone"
          label="手机号"
          placeholder="请输入手机号"
        />
        <van-field
          v-model="form.email"
          name="email"
          label="邮箱"
          placeholder="请输入邮箱"
        />
        <van-field
          v-model="form.department"
          name="department"
          label="所属部门"
          placeholder="请输入所属部门"
        />
        <van-field
          v-model="form.role"
          is-link
          readonly
          name="role"
          label="角色"
          placeholder="请选择角色"
          @click="showRolePicker = true"
        />
      </van-cell-group>

      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          注册
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showRolePicker" position="bottom">
      <van-picker
        :columns="roleColumns"
        @confirm="onRoleConfirm"
        @cancel="showRolePicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { register } from '@/api/auth'

const router = useRouter()

const form = ref({
  username: '',
  real_name: '',
  password: '',
  confirm_password: '',
  phone: '',
  email: '',
  department: '',
  role: ''
})
const loading = ref(false)
const showRolePicker = ref(false)

const roleColumns = [
  { text: '司法所', value: 'judicial' },
  { text: '社工', value: 'social_worker' },
  { text: '家属', value: 'family' }
]

const goBack = () => {
  router.back()
}

const onRoleConfirm = ({ selectedOptions }) => {
  form.value.role = selectedOptions[0].value
  showRolePicker.value = false
}

const handleRegister = async () => {
  if (form.value.password !== form.value.confirm_password) {
    showToast('两次密码不一致')
    return
  }
  if (!form.value.role) {
    showToast('请选择角色')
    return
  }

  loading.value = true
  try {
    await register(form.value)
    showToast('注册成功，请登录')
    router.replace('/login')
  } catch (error) {
    console.error('Register error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}
</style>
