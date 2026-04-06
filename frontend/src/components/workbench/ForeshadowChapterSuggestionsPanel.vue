<template>
  <div class="fs-suggestions">
    <n-alert type="default" :show-icon="true" style="margin-bottom: 12px; font-size: 12px">
      根据本章大纲匹配待回收伏笔，与<strong>伏笔账本</strong>共用同一数据源；勾选联动核销可在后端「建议回收」接口就绪后启用。
    </n-alert>

    <n-empty v-if="!currentChapterNumber" description="请先在左侧选择章节，再查看本章建议回收项">
      <template #icon>
        <span style="font-size: 40px">📌</span>
      </template>
    </n-empty>

    <n-empty v-else description="建议回收 API 未接入（如 GET …/foreshadowing/suggested?chapter=）">
      <template #icon>
        <span style="font-size: 40px">🔮</span>
      </template>
      <template #extra>
        <n-text depth="3" style="font-size: 12px">
          当前可在「伏笔账本」中手动维护待兑现项；上下文生成仍会使用 pending 伏笔。
        </n-text>
      </template>
    </n-empty>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  slug: string
  currentChapterNumber?: number | null
}>()
</script>

<style scoped>
.fs-suggestions {
  height: 100%;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 16px 20px;
}
</style>
