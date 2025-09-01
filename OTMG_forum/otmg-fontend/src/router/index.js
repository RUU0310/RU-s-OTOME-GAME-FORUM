import { createRouter, createWebHistory } from 'vue-router'
import BackstageLayout from '../layouts/BackstageLayout.vue'
import Games from '../views/Backstage/Games/games.vue'
import Users from '../views/Backstage/users.vue'
import Login from '../views/Login.vue'
import AdminPage from '../views/Backstage/adminPage.vue'
import MainLayout from '../layouts/MainLayout.vue'
import GameOverViews from '../views/Main/Games/GameOverViews.vue'
import GameDetail from '../views/Main/Games/GameDetail.vue'
import UserPage from '../views/Main/Personal/UserPage.vue'
import axios from 'axios'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/backstage',
    component: BackstageLayout,
    children: [
      {
        path: 'games',
        name: 'Games',
        component: Games
      },
      {
        path: 'game-audit',
        name: 'GameAudit',
        component: () => import('../views/Backstage/gameAudit.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: Users
      },
      {
        path: 'adminPage',
        name: 'AdminPage',
        component: AdminPage
      },
      {
        path: 'characters',
        name: 'Characters',
        component: () => import('../views/Backstage/Games/characters.vue')
      },
      {
        path: 'groups',
        name: 'Groups',
        component: () => import('../views/Backstage/GroupPost/groups.vue')
      },
      {
        path: 'tags',
        name: 'Tags',
        component: () => import('../views/Backstage/FantasyTime/tags.vue')
      },
      {
        path: 'character-tags',
        name: 'CharacterTags',
        component: () => import('../views/Backstage/FantasyTime/character_tags.vue')
      },
      {
        path: 'group-buys',
        name: 'GroupBuys',
        component: () => import('../views/Backstage/GroupBuy/group_buys.vue')
      },
      {
        path: 'posts',
        name: 'Posts',
        component: () => import('../views/Backstage/GroupPost/posts.vue')
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/games-overview',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'GamesOverview',
        component: GameOverViews
      },
      {
        path: '/games/:id',
        name: 'GameDetail',
        component: GameDetail
      },
      {
        path: '/user',
        name: 'UserPage',
        component: UserPage
      },
      {
        path: '/group-overview',
        name: 'GroupOverViews',
        component: () => import('../views/Main/GroupPost/GroupOverViews.vue')
      },
      {
        path: '/group/:id',
        name: 'GroupDetail',
        component: () => import('../views/Main/GroupPost/GroupDetail.vue')
      },
      {
        path: '/group/:id/post/create',
        name: 'PostCreate',
        component: () => import('../views/Main/GroupPost/PostCreate.vue')
      },
      {
        path: '/post/:id',
        name: 'PostDetail',
        component: () => import('../views/Main/GroupPost/PostDetail.vue')
      },
      {
        path: '/post/:id/edit',
        name: 'PostEdit',
        component: () => import('../views/Main/GroupPost/PostEdit.vue')
      },
      {
        path: '/group-buy-overview',
        name: 'GroupBuyOverViews',
        component: () => import('../views/Main/GroupBuy/GroupBuyOverViews.vue')
      },
      {
        path: '/group-buy/:id',
        name: 'GroupBuyDetail',
        component: () => import('../views/Main/GroupBuy/GroupBuyDetail.vue')
      },
      {
        path: '/messages',
        name: 'MessageCenter',
        component: () => import('../views/Main/Personal/MessageCenter.vue')
      },
      {
        path: '/fantasy-rating',
        name: 'FantasyRating',
        component: () => import('../views/Main/FantasyTime/FantasyRating.vue')
      },
      {
        path: '/preference-report',
        name: 'PreferenceReport',
        component: () => import('../views/Main/FantasyTime/PreferenceReport.vue')
      },
      {
        path: '/fantasy-time',
        name: 'FantasyTime',
        component: () => import('../views/Main/FantasyTime/FantasyTime.vue')
      }
    ]
  },
  
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  if (to.path.startsWith('/backstage')) {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (!user) {
      next('/login')
      return
    }
    if (from.path === '/login') {
      try {
        const res = await axios.get('http://localhost:5000/users')
        if (Array.isArray(res.data)) {
          const hasPending = res.data.some(u => u.upgrade_status === 'pending')
          window.dispatchEvent(new CustomEvent('set-user-upgrade-pending', { detail: hasPending }))
        }
        
        // 检查待审核游戏
        const auditRes = await axios.get('http://localhost:5000/games/audit?status=pending')
        if (auditRes.data.status === 'success') {
          const hasPendingAudit = auditRes.data.results.length > 0
          window.dispatchEvent(new CustomEvent('set-pending-audit', { detail: hasPendingAudit }))
        }
      } catch {}
    }
  }
  if (to.matched.some(r => r.components && r.components.default === MainLayout)) {
    const user = JSON.parse(localStorage.getItem('user') || 'null')
    if (user) {
      try {
        const reqRes = await axios.get(`http://localhost:5000/api/group-buy/group-buys/requests?leader_id=${user.user_id}`)
        const hasPendingRequest = reqRes.data && reqRes.data.success && reqRes.data.data && reqRes.data.data.some(r => r.status === 'pending')
        const msgRes = await axios.get(`http://localhost:5000/api/messages/?user_id=${user.user_id}`)
        const hasUnreadMsg = msgRes.data && msgRes.data.success && msgRes.data.data && msgRes.data.data.some(m => !m.is_read)
        window.dispatchEvent(new CustomEvent('set-header-notification-dot', { detail: hasPendingRequest || hasUnreadMsg }))
      } catch {}
    }
  }
  next()
})

export default router
