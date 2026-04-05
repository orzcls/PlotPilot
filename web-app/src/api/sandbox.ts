/**
 * 对话沙盒 API
 * 获取对话白名单，用于沙盒场景规划
 */

import { apiClient } from './config'

export interface DialogueEntry {
  dialogue_id: string
  chapter: number
  speaker: string
  content: string
  context: string
  tags: string[]
}

export interface DialogueWhitelistResponse {
  dialogues: DialogueEntry[]
  total_count: number
}

export const sandboxApi = {
  /** GET /api/v1/novels/{novel_id}/sandbox/dialogue-whitelist */
  getDialogueWhitelist(
    novelId: string,
    chapterNumber?: number,
    speaker?: string
  ): Promise<DialogueWhitelistResponse> {
    return apiClient.get(
      `/novels/${novelId}/sandbox/dialogue-whitelist`,
      { params: { ...(chapterNumber ? { chapter_number: chapterNumber } : {}), ...(speaker ? { speaker } : {}) } }
    ) as unknown as Promise<DialogueWhitelistResponse>
  },
}
