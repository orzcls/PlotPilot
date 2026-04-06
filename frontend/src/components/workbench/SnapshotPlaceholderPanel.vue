<template>
  <div class="snapshot-placeholder">
    <n-alert type="info" :show-icon="true" title="版本快照（语义快照）" style="margin-bottom: 14px">
      用于保存章节指针、伏笔与图谱状态并<strong>回滚</strong>，与左侧「剧情时间轴」中的<strong>叙事事件</strong>不是同一概念。
    </n-alert>
    <n-text v-if="slug" depth="3" style="font-size: 11px; display: block; margin-bottom: 8px">
      书目：{{ slug }}
    </n-text>
    <n-empty description="后端快照 API 接入后，将在此列出快照与分支">
      <template #icon>
        <span style="font-size: 42px">📸</span>
      </template>
      <template #extra>
        <n-text depth="3" style="font-size: 12px; max-width: 280px; text-align: center">
          规划接口：novel_snapshots 列表 / 创建 / rollback（与 application/snapshot 对齐）。
        </n-text>
      </template>
    </n-empty>
  </div>
</template>

<script setup lang="ts">
defineProps<{ slug: string }>()
</script>

<style scoped>
.snapshot-placeholder {
  height: 100%;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 16px 20px;
}
</style>
