<template>
  <n-modal
    v-model:show="show"
    preset="card"
    style="width: min(760px, 96vw); max-height: min(92vh, 860px)"
    :mask-closable="false"
    :segmented="{ content: true, footer: 'soft' }"
    title="📐 宏观结构规划"
  >
    <template #header-extra>
      <n-text depth="3" style="font-size: 12px">AI 生成部-卷-幕框架，确认后写入结构树</n-text>
    </template>

    <!-- Step 1：配置 -->
    <n-scrollbar style="max-height: min(76vh, 720px)">
      <n-space vertical :size="20">
        <n-space v-if="!generated" vertical :size="16">
          <n-alert type="info" :show-icon="true">
            根据当前 Bible（世界观 + 写作公约）和目标篇幅，AI 生成完整的部-卷-幕叙事骨架，供你编辑后确认写入结构树。
          </n-alert>

          <n-card title="规划参数" size="small" :bordered="false">
            <n-space vertical :size="14">
              <n-form-item label="目标章节数" label-placement="left" label-width="100" :show-feedback="false">
                <n-input-number
                  v-model:value="form.target_chapters"
                  :min="10"
                  :max="1000"
                  :step="10"
                  style="width: 140px"
                />
                <n-text depth="3" style="margin-left:8px;font-size:12px">章（10-1000）</n-text>
              </n-form-item>

              <n-form-item label="结构分布" label-placement="left" label-width="100" :show-feedback="false">
                <n-space :size="12" align="center" wrap>
                  <n-space align="center" :size="4">
                    <n-text style="font-size:13px">部</n-text>
                    <n-input-number v-model:value="form.structure.parts" :min="1" :max="10" style="width:72px" size="small" />
                  </n-space>
                  <n-text depth="3">×</n-text>
                  <n-space align="center" :size="4">
                    <n-text style="font-size:13px">卷/部</n-text>
                    <n-input-number v-model:value="form.structure.volumes_per_part" :min="1" :max="10" style="width:72px" size="small" />
                  </n-space>
                  <n-text depth="3">×</n-text>
                  <n-space align="center" :size="4">
                    <n-text style="font-size:13px">幕/卷</n-text>
                    <n-input-number v-model:value="form.structure.acts_per_volume" :min="1" :max="10" style="width:72px" size="small" />
                  </n-space>
                  <n-tag type="info" size="small" round>
                    共 {{ form.structure.parts * form.structure.volumes_per_part * form.structure.acts_per_volume }} 幕
                  </n-tag>
                </n-space>
              </n-form-item>
            </n-space>
          </n-card>
        </n-space>

        <!-- Step 2：预览 + 编辑 -->
        <template v-if="generated">
          <n-alert type="success" :show-icon="true">
            已生成 {{ structurePreview.length }} 个顶层节点的叙事骨架，可直接编辑标题和描述后确认写入。
          </n-alert>

          <n-scrollbar style="max-height:52vh">
            <n-space vertical :size="6" style="padding-right:8px">
              <n-card
                v-for="(node, idx) in structurePreview"
                :key="idx"
                size="small"
                :bordered="true"
                style="background: var(--n-color)"
              >
                <template #header>
                  <n-space align="center" :size="8">
                    <n-tag :type="node.type === 'part' ? 'error' : node.type === 'volume' ? 'warning' : 'info'" size="small" round>
                      {{ nodeTypeLabel(node.type) }}
                    </n-tag>
                    <n-input
                      v-model:value="node.title"
                      size="small"
                      placeholder="标题"
                      style="flex:1"
                    />
                  </n-space>
                </template>
                <n-input
                  v-if="node.description !== undefined"
                  v-model:value="node.description"
                  type="textarea"
                  size="small"
                  placeholder="叙事目标（可选）"
                  :autosize="{ minRows: 1, maxRows: 3 }"
                />
              </n-card>
            </n-space>
          </n-scrollbar>
        </template>
      </n-space>
    </n-scrollbar>

    <template #footer>
      <n-space justify="space-between">
        <n-button @click="handleClose" :disabled="loading || confirming">取消</n-button>
        <n-space :size="8">
          <n-button v-if="generated" secondary @click="reset">重新生成</n-button>
          <n-button
            v-if="!generated"
            type="primary"
            :loading="loading"
            @click="doGenerate"
          >
            AI 生成框架
          </n-button>
          <n-button
            v-else
            type="primary"
            :loading="confirming"
            @click="doConfirm"
          >
            确认写入结构树
          </n-button>
        </n-space>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { planningApi } from '../../api/planning'

const props = defineProps<{ show: boolean; novelId: string }>()
const emit = defineEmits<{
  'update:show': [v: boolean]
  confirmed: []
}>()

const show = computed({
  get: () => props.show,
  set: (v) => emit('update:show', v),
})

const message = useMessage()

const form = ref({
  target_chapters: 100,
  structure: { parts: 3, volumes_per_part: 3, acts_per_volume: 3 },
})

const loading = ref(false)
const confirming = ref(false)
const generated = ref(false)
const rawResult = ref<Record<string, unknown> | null>(null)
const structurePreview = ref<{ type: string; title: string; description?: string }[]>([])

const nodeTypeLabel = (type: string) => {
  const map: Record<string, string> = { part: '部', volume: '卷', act: '幕', chapter: '章' }
  return map[type] || type
}

const flattenStructure = (nodes: unknown[]): { type: string; title: string; description?: string }[] => {
  const result: { type: string; title: string; description?: string }[] = []
  const walk = (items: unknown[]) => {
    for (const item of items) {
      const n = item as Record<string, unknown>
      result.push({ type: String(n.type || ''), title: String(n.title || ''), description: n.description as string | undefined })
      if (Array.isArray(n.children)) walk(n.children)
    }
  }
  walk(nodes)
  return result
}

const doGenerate = async () => {
  loading.value = true
  try {
    const res = await planningApi.generateMacro(props.novelId, form.value) as unknown as Record<string, unknown>
    rawResult.value = res
    // 尝试提取 structure 或 nodes 字段
    const nodes = (res.structure as unknown[]) || (res.nodes as unknown[]) || (res.data as unknown[]) || [res]
    structurePreview.value = flattenStructure(Array.isArray(nodes) ? nodes : [nodes])
    if (structurePreview.value.length === 0) {
      structurePreview.value = [{ type: 'part', title: '（AI 返回格式未识别，请查看控制台）' }]
    }
    generated.value = true
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    message.error(err?.response?.data?.detail || '生成失败，请确认 AI 密钥已配置')
  } finally {
    loading.value = false
  }
}

const doConfirm = async () => {
  confirming.value = true
  try {
    await planningApi.confirmMacro(props.novelId, { structure: structurePreview.value as Record<string, unknown>[] })
    message.success('结构框架已写入结构树')
    emit('confirmed')
    handleClose()
  } catch (e: unknown) {
    const err = e as { response?: { data?: { detail?: string } } }
    message.error(err?.response?.data?.detail || '写入失败')
  } finally {
    confirming.value = false
  }
}

const reset = () => {
  generated.value = false
  rawResult.value = null
  structurePreview.value = []
}

const handleClose = () => {
  if (loading.value || confirming.value) return
  reset()
  show.value = false
}
</script>
