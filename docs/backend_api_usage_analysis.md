# Backend API 实现状态分析

本文档分析后端 API 端点的实现状态及前端使用情况。

## 📊 总览

| 模块 | 已实现 | 前端使用 | 未使用 |
|------|--------|----------|--------|
| Generation API | 13 | 8 | 5 |
| Bible API | 4 | 4 | 0 |
| Knowledge API | 3 | 3 | 0 |
| Story Structure API | 2 | 2 | 0 |
| Storylines API | 2 | 2 | 0 |
| Plot Arc API | 2 | 2 | 0 |
| Chapter API | 6 | 6 | 0 |
| Novel API | 3 | 3 | 0 |
| **总计** | **35** | **30** | **5** |

## ✅ 已实现并使用的核心 API (30个)

### 1. 章节生成 (Generation API)

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|--------------|
| `/novels/{id}/generate-chapter` | POST | 同步生成章节 | `workflow.ts` |
| `/novels/{id}/generate-chapter-stream` | POST | 流式生成章节 (SSE) | `workflow.ts` → `consumeGenerateChapterStream` |
| `/novels/{id}/hosted-write-stream` | POST | 托管多章连写 (SSE) | `workflow.ts` → `consumeHostedWriteStream` |
| `/novels/{id}/plan` | POST | 生成小说规划 | `workflow.ts` |
| `/novels/{id}/chapters/{n}/review` | POST | AI 审阅章节 | `workflow.ts`, `chapter.ts` |
| `/novels/{id}/outline/extend` | POST | 扩展大纲 | `ChapterList.vue` |
| `/novels/{id}/bible/generate` | POST | AI 生成世界观 | `BiblePanel.vue` |
| `/novels/{id}/knowledge/generate` | POST | AI 生成知识库 | `KnowledgePanel.vue` |

### 2. 世界观与知识库

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|--------------|
| `/novels/{id}/bible` | GET | 获取世界观设定 | `bible.ts` |
| `/novels/{id}/bible` | PUT | 更新世界观设定 | `bible.ts` |
| `/novels/{id}/bible/status` | GET | 检查 Bible 生成状态 | `bible.ts`, `NovelSetupGuide.vue` |
| `/novels/{id}/bible/generate` | POST | 手动触发 Bible 生成 | `bible.ts`, `NovelSetupGuide.vue` |
| `/novels/{id}/knowledge` | GET | 获取知识库 | `knowledge.ts` |
| `/novels/{id}/knowledge` | PUT | 更新知识库 | `knowledge.ts` |

### 3. 叙事结构

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|--------------|
| `/novels/{id}/structure` | GET | 获取结构树 | 前端多处使用 |
| `/novels/{id}/structure/initialize` | POST | 手动触发结构规划 | `ChapterList.vue` |

### 4. 故事线管理

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|--------------|
| `/novels/{id}/storylines` | GET | 获取所有故事线 | `StorylinePanel.vue` |
| `/novels/{id}/storylines` | POST | 创建新故事线 | `StorylinePanel.vue` |

### 5. 情节弧线管理

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|--------------|
| `/novels/{id}/plot-arc` | GET | 获取情节弧线 | `PlotArcPanel.vue` |
| `/novels/{id}/plot-arc` | POST | 创建/更新情节弧线 | `PlotArcPanel.vue` |

### 6. 章节管理

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|--------------|
| `/novels/{id}/chapters` | GET | 列出所有章节 | 前端多处使用 |
| `/novels/{id}/chapters/{n}` | GET | 获取指定章节 | 前端多处使用 |
| `/novels/{id}/chapters/{n}` | PUT | 更新章节内容 | 前端多处使用 |
| `/novels/{id}/chapters/{n}/review` | GET | 获取章节审阅 | `chapter.ts` |
| `/novels/{id}/chapters/{n}/review` | PUT | 更新审阅状态 | `chapter.ts` |
| `/novels/{id}/chapters/{n}/review-ai` | POST | AI 审阅章节 | `chapter.ts` |

### 7. 小说管理

| 端点 | 方法 | 功能 | 前端调用位置 |
|------|------|------|--------------|
| `/novels` | GET | 列出所有小说 | 前端多处使用 |
| `/novels` | POST | 创建新小说 | 前端多处使用 |
| `/novels/{id}` | GET | 获取小说详情 | 前端多处使用 |

## ⚠️ 已实现但未使用的 API (5个)

这些 API 已在后端实现，但前端尚未集成或仅定义了接口未实际调用：

| 端点 | 方法 | 功能 | 状态 |
|------|------|------|------|
| `/novels/{id}/consistency-report` | GET | 获取一致性分析报告 | 前端已定义接口但未调用 |
| `/novels/{id}/generate-outline` | POST | 生成章节大纲 | 后端已实现但前端未使用 |
| `/novels/{id}/continue-chapter` | POST | 续写章节 | 后端已实现但前端未使用 |
| `/novels/{id}/rewrite-chapter` | POST | 重写章节 | 后端已实现但前端未使用 |
| `/novels/{id}/polish-chapter` | POST | 润色章节 | 后端已实现但前端未使用 |

## 🔄 最近的重要变更

### 新书创建流程优化 (2026-04-03)

**变更前：**
```
创建小说 → 自动生成 Bible → 自动生成幕结构
```

**变更后：**
```
创建小说 → 手动触发 Bible 生成 → 轮询状态 → 引导设置故事线和情节弧 → 进入工作台
```

**相关 API 变更：**
- `POST /novels` - 移除自动生成 Bible 的逻辑
- `POST /novels/{id}/bible/generate` - 新增手动触发接口
- `GET /novels/{id}/bible/status` - 新增状态检查接口
- `POST /novels/{id}/structure/initialize` - 重命名并明确为手动触发

**新增功能：**
- `NovelSetupGuide.vue` - 4步向导引导用户完成新书设置
- `StorylinePanel.vue` - 故事线管理面板（主线、支线、暗线）
- `PlotArcPanel.vue` - 情节弧线管理面板（可视化剧情点）

**提交记录：**
- `e6ad109` - 移除自动生成逻辑
- `aa3c4ad` - 添加手动生成接口
- `10a1bca` - 添加 NovelSetupGuide 向导
- `54ffd6b` - 移除重复的设置按钮

### 故事线和情节弧线功能集成 (2026-04-03)

**新增组件：**
- `StorylinePanel.vue` - 支持创建、查看、管理故事线
- `PlotArcPanel.vue` - 支持创建、可视化情节点

**集成位置：**
- 在 `SettingsPanel.vue` 中添加了两个新标签页
- 用户可以在工作台右侧面板访问这些功能

**API 集成：**
- `GET /novels/{id}/storylines` - 获取故事线列表
- `POST /novels/{id}/storylines` - 创建新故事线
- `GET /novels/{id}/plot-arc` - 获取情节弧线
- `POST /novels/{id}/plot-arc` - 创建/更新情节弧线

## 📋 建议

### 高优先级
1. **集成一致性报告功能** - 后端已实现，前端接口已定义，只需添加 UI 调用
2. **章节编辑增强功能** - 集成续写、重写、润色等章节编辑辅助功能

### 中优先级
3. **大纲生成功能** - 为章节添加独立的大纲生成功能

### 低优先级
4. **评估未使用 API** - 如果不计划使用，考虑标记为废弃或移除

## 📈 API 使用率

- **整体使用率**: 85.7% (30/35)
- **核心功能覆盖**: 100% (所有核心写作流程已实现并使用)
- **高级功能覆盖**: 50% (故事线、情节弧线已集成；一致性报告、章节编辑辅助功能未使用)

## 🎯 结论

后端 API 实现完善，核心写作流程的所有功能都已实现并在前端正常使用。最近新增的故事线和情节弧线管理功能已成功集成到前端，用户可以在工作台右侧面板中使用。未使用的 5 个 API 主要是章节编辑辅助功能和一致性分析，属于增强特性，不影响基本使用。
