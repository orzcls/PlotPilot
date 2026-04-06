<template>
  <div class="timeline-panel">
    <header class="panel-header">
      <div class="header-main">
        <div class="title-row">
          <h3 class="panel-title">剧情时间轴</h3>
          <n-tag size="small" round :bordered="false">叙事事件</n-tag>
        </div>
        <p class="panel-lead">
          管理故事<strong>世界内</strong>的时间流逝与事件顺序（叙事用）。<strong>不是</strong>「版本快照 / 回滚」——后者见叙事脉络中的<strong>版本快照</strong>。
        </p>
      </div>
      <n-space class="header-actions" :size="8" align="center">
        <n-button size="small" secondary @click="showAddModal = true">
          + 添加事件
        </n-button>
        <n-button size="small" type="primary" :loading="loading" @click="loadTimeline">
          刷新
        </n-button>
      </n-space>
    </header>

    <div class="panel-content">
      <n-spin :show="loading">
        <n-empty v-if="timelineEvents.length === 0" description="暂无时间线事件，点击「添加事件」开始规划">
          <template #icon>
            <span style="font-size: 48px">⏱️</span>
          </template>
        </n-empty>

        <n-space v-else vertical :size="12">
          <n-card
            v-for="(event, index) in sortedEvents"
            :key="index"
            size="small"
            :bordered="true"
            hoverable
          >
            <template #header>
              <div class="event-header">
                <n-tag type="info" size="small" round>
                  {{ event.time_point || '未指定时间' }}
                </n-tag>
                <n-text strong>{{ event.event }}</n-text>
              </div>
            </template>

            <n-space vertical :size="8">
              <div v-if="event.description" class="info-row">
                <n-text depth="3">描述:</n-text>
                <n-text>{{ event.description }}</n-text>
              </div>
            </n-space>

            <template #action>
              <n-space :size="8">
                <n-button size="tiny" secondary @click="editEvent(index)">编辑</n-button>
                <n-button size="tiny" type="error" secondary @click="deleteEvent(index)">删除</n-button>
              </n-space>
            </template>
          </n-card>
        </n-space>
      </n-spin>
    </div>

    <!-- 添加/编辑事件模态框 -->
    <n-modal v-model:show="showAddModal" preset="card" :title="editingIndex >= 0 ? '编辑事件' : '添加事件'" style="width: 600px">
      <n-form ref="formRef" :model="formData" :rules="formRules" label-placement="left" label-width="100">
        <n-form-item label="时间点" path="time_point">
          <n-input
            v-model:value="formData.time_point"
            placeholder="例：第三年冬、2024-01-01、三天后"
          />
        </n-form-item>

        <n-form-item label="事件" path="event">
          <n-input
            v-model:value="formData.event"
            placeholder="事件名称或简述"
          />
        </n-form-item>

        <n-form-item label="详细描述" path="description">
          <n-input
            v-model:value="formData.description"
            type="textarea"
            placeholder="事件的详细描述（可选）"
            :rows="4"
          />
        </n-form-item>
      </n-form>

      <template #action>
        <n-space justify="end">
          <n-button @click="showAddModal = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { bibleApi } from '../../api/bible'
import type { TimelineNoteDTO } from '../../api/bible'

interface Props {
  slug: string
}

const props = defineProps<Props>()
const message = useMessage()

const loading = ref(false)
const timelineEvents = ref<TimelineNoteDTO[]>([])
const showAddModal = ref(false)
const editingIndex = ref(-1)

const formData = ref({
  time_point: '',
  event: '',
  description: ''
})

const formRules = {
  event: { required: true, message: '请输入事件名称', trigger: 'blur' }
}

const sortedEvents = computed(() => {
  return [...timelineEvents.value]
})

const loadTimeline = async () => {
  loading.value = true
  try {
    const bible = await bibleApi.getBible(props.slug)
    timelineEvents.value = bible.timeline_notes || []
  } catch (error: any) {
    if (error?.response?.status !== 404) {
      message.error(error.response?.data?.detail || '加载时间线失败')
    }
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formData.value.event.trim()) {
    message.error('请输入事件名称')
    return
  }

  const newEvent: TimelineNoteDTO = {
    id: editingIndex.value >= 0 ? timelineEvents.value[editingIndex.value].id : `timeline-${Date.now()}`,
    time_point: formData.value.time_point,
    event: formData.value.event,
    description: formData.value.description
  }

  if (editingIndex.value >= 0) {
    timelineEvents.value[editingIndex.value] = newEvent
  } else {
    timelineEvents.value.push(newEvent)
  }

  await saveTimeline()

  showAddModal.value = false
  editingIndex.value = -1
  formData.value = { time_point: '', event: '', description: '' }
}

const editEvent = (index: number) => {
  editingIndex.value = index
  const event = timelineEvents.value[index]
  formData.value = {
    time_point: event.time_point || '',
    event: event.event,
    description: event.description || ''
  }
  showAddModal.value = true
}

const deleteEvent = async (index: number) => {
  timelineEvents.value.splice(index, 1)
  await saveTimeline()
}

const saveTimeline = async () => {
  try {
    const bible = await bibleApi.getBible(props.slug)
    await bibleApi.updateBible(props.slug, {
      ...bible,
      timeline_notes: timelineEvents.value
    })
    message.success('时间线已保存')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存时间线失败')
  }
}

watch(() => props.slug, (slug) => {
  if (slug) loadTimeline()
})

onMounted(() => {
  loadTimeline()
})
</script>

<style scoped>
.timeline-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--aitext-panel-muted);
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid var(--aitext-split-border);
  background: var(--app-surface);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.header-main {
  flex: 1;
  min-width: 0;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.panel-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color-1);
}

.panel-lead {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-color-3);
}

.header-actions {
  flex-shrink: 0;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.event-header {
  display: flex;
  gap: 8px;
  align-items: center;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
</style>
