<template>
  <div class="preference-report">
    <div style="display: flex; gap: 16px; margin-bottom: 32px;">
      <el-button type="primary" class="pink-girly-btn" @click="generateReport">刷新报告</el-button>
      <el-button type="success" class="fantasy-btn" @click="enterFantasyTime">进入幻想时间</el-button>
    </div>
    <div v-if="loading" style="text-align:center;padding:40px;">加载中...</div>
    <div v-else>
      <div class="user-block" style="font-size:20px;font-weight:bold;margin-bottom:8px;">
        {{ user?.nickname || '未登录用户' }}：
      </div>
      <div class="summary-block">
        <p class="summary-line" v-if="summary.hair || summary.eye || summary.glass || summary.aura || summary.age">
          外貌：你最喜欢
          <span v-if="summary.hair" class="tag-pink">{{ summary.hair }}</span>发色，
          <span v-if="summary.eye" class="tag-pink">{{ summary.eye }}</span>瞳色，
          <span v-if="summary.glass" class="tag-pink">{{ summary.glass }}</span>，
          形象<span v-if="summary.aura" class="tag-pink">{{ summary.aura }}</span>，
          的<span v-if="summary.age" class="tag-pink">{{ summary.age }}</span>角色。
        </p>
        <p class="summary-line" v-if="summary.baseChar || summary.tone || summary.world">
          性格：你喜欢性格
          <span v-if="summary.baseChar" class="tag-pink">{{ summary.baseChar }}</span>
          的角色，用
          <span v-if="summary.tone" class="tag-pink">{{ summary.tone }}</span>的语气，
          <span v-if="summary.world" class="tag-pink">{{ summary.world }}</span>的方式，
          和你聊天。
        </p>
      </div>
      <div v-for="(option, tag) in chartOptions" :key="tag" class="chart-section">
        <h3 style="text-align:left;">{{ tag }} 偏好分布</h3>
        <v-chart :option="option" style="height:320px;width:100%;max-width:700px;margin:0 auto;" autoresize />
      </div>
      <div v-html="reportHtml" style="margin-top:32px;"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent } from 'echarts/components'
import { useRouter } from 'vue-router'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, LegendComponent, TitleComponent])

const router = useRouter()
const loading = ref(false)
const reportHtml = ref('')
const chartOptions = ref({})
const user = JSON.parse(localStorage.getItem('user') || 'null')
const summary = ref({
  hair: '',
  eye: '',
  glass: '',
  aura: '',
  age: '',
  baseChar: '',
  tone: '',
  world: ''
})

async function generateReport() {
  loading.value = true
  try {
    // 获取所有角色
    const charRes = await axios.get('http://localhost:5000/api/game-character/list')
    if (!charRes.data.success) throw new Error('角色获取失败')
    let all = charRes.data.data.filter(c => c.role_type === '可攻略')
    // 获取评分
    let rated = []
    if (user) {
      const ratingRes = await axios.get(`http://localhost:5000/api/game-character/ratings/user?user_id=${user.user_id}`)
      if (ratingRes.data.success) {
        const ratingMap = {}
        ratingRes.data.data.forEach(r => {
          ratingMap[r.character_id] = r
        })
        all.forEach(c => {
          if (ratingMap[c.id]) {
            c.appearance_star = ratingMap[c.id].appearance_score ? ratingMap[c.id].appearance_score / 2 : 0
            c.personality_star = ratingMap[c.id].personality_score ? ratingMap[c.id].personality_score / 2 : 0
          } else {
            c.appearance_star = 0
            c.personality_star = 0
          }
        })
      } else {
        all.forEach(c => {
          c.appearance_star = 0
          c.personality_star = 0
        })
      }
    } else {
      all.forEach(c => {
        c.appearance_star = 0
        c.personality_star = 0
      })
    }
    rated = all.filter(c => c.appearance_star > 0 || c.personality_star > 0)
    if (!rated.length) {
      reportHtml.value = '<p style="text-align:center;color:#aaa;">暂无评分数据</p>'
      chartOptions.value = {}
      loading.value = false
      return
    }
    // 统计基础
    const weight = [0, 1, 2, 3, 4, 5]
    let appearanceSum = 0, personalitySum = 0
    let appearanceCount = 0, personalityCount = 0
    let favChar = null, favScore = -1
    let gameCount = {}
    rated.forEach(c => {
      if (c.appearance_star > 0) {
        appearanceSum += c.appearance_star * weight[c.appearance_star]
        appearanceCount += weight[c.appearance_star]
      }
      if (c.personality_star > 0) {
        personalitySum += c.personality_star * weight[c.personality_star]
        personalityCount += weight[c.personality_star]
      }
      // 统计最喜欢的角色（外貌+性格分最高）
      const totalScore = (c.appearance_star || 0) + (c.personality_star || 0)
      if (totalScore > favScore) {
        favScore = totalScore
        favChar = c
      }
      if (c.game_name) {
        gameCount[c.game_name] = (gameCount[c.game_name] || 0) + 1
      }
    })
    let favGame = Object.entries(gameCount).sort((a, b) => b[1] - a[1])[0]?.[0] || ''
    // 统计标签维度（累计分数法，外貌分）
    const ratedIds = rated.map(c => c.id)
    const tagScoreMap = {}
    const characterTagsMap = {}
    const tagReqs = ratedIds.map(id =>
      axios.get(`http://localhost:5000/api/character-tags?character_id=${id}`)
    )
    const resArr = await Promise.all(tagReqs)
    resArr.forEach((res, idx) => {
      if (res.data.status === 'success') {
        characterTagsMap[ratedIds[idx]] = res.data.results
      }
    })
    rated.forEach(c => {
      // 外貌标签分数
      if (c.appearance_star > 0) {
        (characterTagsMap[c.id] || []).forEach(ct => {
          const tag = ct.tag
          if (!tag) return
          const values = (ct.value || '').split(',')
          values.forEach(val => {
            if (!val) return
            if (!tagScoreMap[tag.name]) tagScoreMap[tag.name] = {}
            if (!tagScoreMap[tag.name][val]) tagScoreMap[tag.name][val] = 0
            // 外貌相关标签
            if (["发色", "瞳色", "眼镜配饰", "整体气质", "年龄特征"].includes(tag.name)) {
              tagScoreMap[tag.name][val] += c.appearance_star
            }
          })
        })
      }
      // 性格标签分数
      if (c.personality_star > 0) {
        (characterTagsMap[c.id] || []).forEach(ct => {
          const tag = ct.tag
          if (!tag) return
          const values = (ct.value || '').split(',')
          values.forEach(val => {
            if (!val) return
            if (!tagScoreMap[tag.name]) tagScoreMap[tag.name] = {}
            if (!tagScoreMap[tag.name][val]) tagScoreMap[tag.name][val] = 0
            // 性格相关标签
            if (["基础性格", "语气", "世界观倾向"].includes(tag.name)) {
              tagScoreMap[tag.name][val] += c.personality_star
            }
          })
        })
      }
    })
    // 生成图表 option
    const options = {}
    for (const tagName in tagScoreMap) {
      const valueMap = tagScoreMap[tagName]
      const labels = Object.keys(valueMap)
      const data = labels.map(l => valueMap[l])
      options[tagName] = {
        title: { text: `${tagName} 偏好分布`, left: 'center', top: 10, textStyle: { fontSize: 18 } },
        tooltip: { trigger: 'axis' },
        grid: { left: 40, right: 20, bottom: 40, top: 50 },
        xAxis: { type: 'category', data: labels, axisLabel: { fontSize: 14 } },
        yAxis: { type: 'value', minInterval: 1 },
        series: [
          {
            type: 'bar',
            data,
            itemStyle: {
              color: '#d63384',
              borderRadius: [8, 8, 0, 0]
            },
            barWidth: 32
          }
        ]
      }
    }
    chartOptions.value = options
    // 文字报告
    const tagFavs = []
    const tagFavMap = {} // {tagName: {value, score}}
    for (const tagName in tagScoreMap) {
      const valueMap = tagScoreMap[tagName]
      let best = null, bestScore = -1
      for (const val in valueMap) {
        if (valueMap[val] > bestScore) {
          bestScore = valueMap[val]
          best = val
        }
      }
      if (best) {
        tagFavs.push({ tag: tagName, value: best, score: bestScore })
        tagFavMap[tagName] = { value: best, score: bestScore }
      }
    }
    // 结构化赋值 summary
    summary.value = {
      hair: tagFavMap['发色']?.value || '',
      eye: tagFavMap['瞳色']?.value || '',
      glass: tagFavMap['眼镜配饰']?.value || '',
      aura: tagFavMap['整体气质']?.value || '',
      age: tagFavMap['年龄特征']?.value || '',
      baseChar: tagFavMap['基础性格']?.value || '',
      tone: tagFavMap['语气']?.value || '',
      world: tagFavMap['世界观倾向']?.value || ''
    }
    let tagHtml = tagFavs.map(t => `<p>你在【<span style='color:#d63384;font-weight:bold;'>${t.tag}</span>】最喜欢：<b style='color:#d63384;'>${t.value}</b>（累计分 ${t.score}）</p>`).join('')
    reportHtml.value = `
      <p>你共为 <b>${rated.length}</b> 位角色打过分。</p>
      <p>你最喜欢的角色：<b>${favChar ? favChar.name : '暂无'}</b></p>
      <p>你最常评分的游戏：<b>${favGame || '暂无'}</b></p>
      <hr/>
      <b>你的标签维度偏好：</b>
      ${tagHtml}
    `
  } catch (e) {
    reportHtml.value = '<p style="color:red;">报告生成失败</p>'
    chartOptions.value = {}
  } finally {
    loading.value = false
  }
}

function enterFantasyTime() {
  router.push('/fantasy-time')
}

onMounted(() => {
  generateReport()
})
</script>

<style scoped>
.preference-report {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 0;
  min-height: 100vh;
}
.pink-girly-btn, .fantasy-btn{
  background: linear-gradient(90deg, #ffb6d5 0%, #ffd6ec 100%);
  color: #d63384;
  border: none;
  border-radius: 16px;
  font-size: 13px;
  font-family: 'Smiley Sans', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-weight: 500;
  padding: 4px 16px;
  margin-left: 8px;
  box-shadow: none;
  transition: none;
}
.pink-girly-btn:hover, .fantasy-btn:hover {
  background: linear-gradient(90deg, #ffb6d5 0%, #ffd6ec 100%);
  color: #d63384;
  box-shadow: none;
  transform: none;
}

.chart-section {
  margin-bottom: 40px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 16px #f8bbd0;
  padding: 24px 16px 8px 16px;
}
.summary-block {
  margin-bottom: 24px;
}
.summary-line {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}
.tag-pink {
  color: #d63384;
  font-weight: bold;
  margin-right: 2px;
}
</style> 