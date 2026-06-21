import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/home',
    meta: { requiresAuth: true }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/objects',
    name: 'Objects',
    component: () => import('@/views/objects/ObjectList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/objects/:id',
    name: 'ObjectDetail',
    component: () => import('@/views/objects/ObjectDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/objects/create',
    name: 'ObjectCreate',
    component: () => import('@/views/objects/ObjectCreate.vue'),
    meta: { requiresAuth: true, roles: ['judicial'] }
  },
  {
    path: '/objects/edit/:id',
    name: 'ObjectEdit',
    component: () => import('@/views/objects/ObjectCreate.vue'),
    meta: { requiresAuth: true, roles: ['judicial'] }
  },
  {
    path: '/visit-plans',
    name: 'VisitPlans',
    component: () => import('@/views/visit/VisitPlanList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/visit-plans/:id',
    name: 'VisitPlanDetail',
    component: () => import('@/views/visit/VisitPlanDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/visit-records',
    name: 'VisitRecords',
    component: () => import('@/views/visit/VisitRecordList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/visit-records/:id',
    name: 'VisitRecordDetail',
    component: () => import('@/views/visit/VisitRecordDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/visit-create/:planId?',
    name: 'VisitCreate',
    component: () => import('@/views/visit/VisitCreate.vue'),
    meta: { requiresAuth: true, roles: ['social_worker'] }
  },
  {
    path: '/feedbacks',
    name: 'Feedbacks',
    component: () => import('@/views/feedback/FeedbackList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/feedbacks/create',
    name: 'FeedbackCreate',
    component: () => import('@/views/feedback/FeedbackCreate.vue'),
    meta: { requiresAuth: true, roles: ['family'] }
  },
  {
    path: '/feedbacks/:id',
    name: 'FeedbackDetail',
    component: () => import('@/views/feedback/FeedbackDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/NotificationList.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.roles && !to.meta.roles.includes(userStore.userRole)) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
