/**
 * 统一的规划 API
 */

import { apiClient } from './config'

// ==================== 类型定义 ====================

export interface StructurePreference {
  parts: number
  volumes_per_part: number
  acts_per_volume: number
}

export interface MacroPlanRequest {
  target_chapters: number
  structure: StructurePreference
}

export interface ActChaptersRequest {
  chapter_count?: number
}

export interface ContinuePlanningRequest {
  current_chapter: number
}

export interface ContinuePlanResult {
  /** 当前幕是否写完 */
  is_act_complete: boolean
  /** 是否需要创建下一幕 */
  needs_next_act: boolean
  /** 当前幕 story_node id（用于 createNextAct） */
  current_act_id: string | null
  /** 当前幕标题 */
  current_act_title?: string
  /** 当前章号在幕内的进度说明 */
  progress_message?: string
  /** 幕内已写章节数 */
  completed_chapters?: number
  /** 幕内总规划章节数 */
  total_chapters?: number
  /** 后端原始消息（兜底） */
  message?: string
  [key: string]: unknown
}

/** story_node 结构节点（树形） */
export interface StoryNode {
  id: string
  type: 'part' | 'volume' | 'act' | 'chapter'
  title: string
  number?: number
  description?: string
  children?: StoryNode[]
  [key: string]: unknown
}

// ==================== API ====================

export const planningApi = {
  // ==================== 宏观规划 ====================

  generateMacro: (novelId: string, data: MacroPlanRequest) =>
    apiClient.post(`/planning/novels/${novelId}/macro/generate`, data),

  confirmMacro: (novelId: string, data: { structure: Record<string, unknown>[] }) =>
    apiClient.post(`/planning/novels/${novelId}/macro/confirm`, data),

  // ==================== 幕级规划 ====================

  generateActChapters: (actId: string, data: ActChaptersRequest) =>
    apiClient.post(`/planning/acts/${actId}/chapters/generate`, data),

  confirmActChapters: (actId: string, data: { chapters: Record<string, unknown>[] }) =>
    apiClient.post(`/planning/acts/${actId}/chapters/confirm`, data),

  // ==================== AI 续规划 ====================

  continuePlanning: (novelId: string, data: ContinuePlanningRequest) =>
    apiClient.post<ContinuePlanResult>(`/planning/novels/${novelId}/continue`, data) as unknown as Promise<ContinuePlanResult>,

  createNextAct: (actId: string) =>
    apiClient.post<Record<string, unknown>>(`/planning/acts/${actId}/create-next`) as unknown as Promise<Record<string, unknown>>,

  // ==================== 查询 ====================

  getStructure: (novelId: string) =>
    apiClient.get<{ success: boolean; data: StoryNode }>(`/planning/novels/${novelId}/structure`) as unknown as Promise<{ success: boolean; data: StoryNode }>,

  getActDetail: (actId: string) =>
    apiClient.get<{ success: boolean; data: StoryNode }>(`/planning/acts/${actId}`) as unknown as Promise<{ success: boolean; data: StoryNode }>,

  getChapterDetail: (chapterId: string) =>
    apiClient.get<{ success: boolean; data: { chapter: StoryNode; elements: unknown[] } }>(`/planning/chapters/${chapterId}`) as unknown as Promise<{ success: boolean; data: { chapter: StoryNode; elements: unknown[] } }>,
}
