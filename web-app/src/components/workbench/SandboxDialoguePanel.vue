<template>
  <div class="sandbox-panel">
    <n-space vertical :size="12">
      <!-- 筛选区 -->
      <n-card title="对话白名单筛选" size="small" :bordered="false">
        <n-space vertical :size="8">
          <n-space :size="8" wrap>
            <n-form-item label="章节号" label-placement="left" label-width="54" :show-feedback="false">
              <n-input-number
                v-model:value="filterChapter"
                :min="1"
                clearable
                placeholder="全部"
                style="width: 90px"
                size="small"
              />
            </n-form-item>
            <n-form-item label="说话人" label-placement="left" label-width="54" :show-feedback="false">
              <n-input
                v-model:value="filterSpeaker"
                placeholder="全部"
                clearable
                size="small"
                style="width: 120px"
              />
            </n-form-item>
          </n-space>
          <n-button type="primary" size="small" :loading="loading" @click="loadWhitelist">查询</n-button>
        </n-space>
      </n-card>

      <!-- 结果 -->
      <div v-if="result !== null">
        <n-space align="center" justify="space-between" style="margin-bottom: 6px">
          <n-text strong>共 {{ result.total_count }} 条对话</n-text>
          <n-input
            v-model:value="searchText"
            size="tiny"
            placeholder="关键词搜索…"
            clearable
            style="width: 140px"
          />
        </n-space>

        <n-spin :show="loading">
          <n-scrollbar style="max-height: 420px">
            <n-space vertical :size="6" style="padding-right: 4px">
              <n-card
                v-for="d in filteredDialogues"
                :key="d.dialogue_id"
                size="small"
                :bordered="true"
                style="background: var(--n-color)"
              >
                <template #header>
                  <n-space align="center" :size="6">
                    <n-tag type="info" size="tiny" round>第{{ d.chapter }}章</n-tag>
                    <n-tag type="error" size="tiny" round>{{ d.speaker }}</n-tag>
                    <n-space :size="4">
                      <n-tag
                        v-for="tag in d.tags"
                        :key="tag"
                        size="tiny"
                        round
                      >{{ tag }}</n-tag>
                    </n-space>
                  </n-space>
                </template>
                <n-space vertical :size="4">
                  <n-blockquote style="margin: 0; font-size: 13px; line-height: 1.6">{{ d.content }}</n-blockquote>
                  <n-text depth="3" style="font-size: 11px">{{ d.context }}</n-text>
                </n-space>
              </n-card>
              <n-empty v-if="filteredDialogues.length === 0" description="无匹配对话" />
            </n-space>
          </n-scrollbar>
        </n-spin>
      </div>

      <n-empty v-else-if="!loading" description="点击「查询」载入对话白名单" />
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { sandboxApi } from '../../api/sandbox'
import type { DialogueWhitelistResponse, DialogueEntry } from '../../api/sandbox'

const props = defineProps<{ slug: string }>()
const message = useMessage()

const loading = ref(false)
const result = ref<DialogueWhitelistResponse | null>(null)
const filterChapter = ref<number | null>(null)
const filterSpeaker = ref('')
const searchText = ref('')

const filteredDialogues = computed<DialogueEntry[]>(() => {
  if (!result.value) return []
  const kw = searchText.value.trim().toLowerCase()
  if (!kw) return result.value.dialogues
  return result.value.dialogues.filter(d =>
    d.content.toLowerCase().includes(kw) ||
    d.speaker.toLowerCase().includes(kw) ||
    d.context.toLowerCase().includes(kw)
  )
})

const loadWhitelist = async () => {
  loading.value = true
  try {
    result.value = await sandboxApi.getDialogueWhitelist(
      props.slug,
      filterChapter.value ?? undefined,
      filterSpeaker.value.trim() || undefined
    )
  } catch {
    message.error('查询失败，请确认后端服务已启动')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.sandbox-panel {
  padding: 10px 12px;
  height: 100%;
  overflow-y: auto;
}
</style>
