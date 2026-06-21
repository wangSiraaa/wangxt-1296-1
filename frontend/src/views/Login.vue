<template>
  <div class="login-container">
    <div class="login-header">
      <h2>社区矫正走访系统</h2>
      <p class="subtitle">Community Correction Visit System</p>
    </div>

    <van-form @submit="handleLogin">
      <van-cell-group inset>
        <van-field
          v-model="form.username"
          name="username"
          label="用户名"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请填写用户名' }]"
        />
        <van-field
          v-model="form.password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请填写密码' }]"
        />
      </van-cell-group>

      <div style="margin: 16px;">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          登录
        </van-button>
      </div>
    </van-form>

    <div class="login-footer">
      <span>还没有账号？</span>
      <router-link to="/register" class="register-link">立即注册</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { showToast } from 'vant'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  try {
    await userStore.login(form.value)
    showToast('登录成功')
    const redirect = route.query.redirect || '/home'
    router.replace(redirect)
  } catch (error) {
    console.error('Login error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  padding: 40px 20px;
  background: linear-gradient(135deg, #1989fa 0%, #00b4ff 100%);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  padding-top: 40px;
}

.login-header h2 {
  color: #fff;
  font-size: 28px;
  margin-bottom: 8px;
}

.subtitle {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  color: #666;
  font-size: 14px;
}

.register-link {
  color: #1989fa;
  text-decoration: none;
  margin-left: 4px;
}
</style>
