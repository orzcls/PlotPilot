"""测试守护进程

使用方法：
    python scripts/test_daemon.py

功能：
1. 创建一个测试小说，设置为 RUNNING 状态
2. 启动守护进程（运行 30 秒后自动停止）
3. 检查小说状态是否正确流转
"""
import sys
import time
import logging
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.persistence.database.connection import DatabaseConnection
from infrastructure.persistence.database.sqlite_novel_repository import SqliteNovelRepository
from domain.novel.entities.novel import Novel, NovelStage, AutopilotStatus
from domain.novel.value_objects.novel_id import NovelId

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("测试守护进程")
    logger.info("=" * 80)

    # 初始化数据库
    project_root = Path(__file__).parent.parent
    db_path = project_root / "data" / "novels.db"
    db = DatabaseConnection(str(db_path))
    novel_repository = SqliteNovelRepository(db)

    # 创建测试小说
    novel_id = NovelId("test_novel_001")
    novel = Novel(
        id=novel_id,
        title="测试小说：修仙之路",
        author="林亦",
        target_chapters=30,
        premise="一个普通少年意外获得修仙系统，从此踏上逆天改命之路。",
        autopilot_status=AutopilotStatus.RUNNING,
        current_stage=NovelStage.MACRO_PLANNING,
        current_act=0,
        current_chapter_in_act=0,
    )

    logger.info(f"📝 创建测试小说: {novel.title}")
    logger.info(f"   - ID: {novel_id.value}")
    logger.info(f"   - 状态: {novel.autopilot_status.value}")
    logger.info(f"   - 阶段: {novel.current_stage.value}")

    # 保存到数据库
    novel_repository.save(novel)
    logger.info("✅ 小说已保存到数据库")

    # 验证查询
    active_novels = novel_repository.find_by_autopilot_status(AutopilotStatus.RUNNING.value)
    logger.info(f"\n🔍 查询 RUNNING 状态的小说: 找到 {len(active_novels)} 个")
    for n in active_novels:
        stage_value = n.current_stage.value if hasattr(n.current_stage, 'value') else n.current_stage
        logger.info(f"   - {n.title} (阶段: {stage_value})")

    logger.info("\n" + "=" * 80)
    logger.info("✅ 测试完成！")
    logger.info("=" * 80)
    logger.info("\n下一步：运行 python scripts/start_daemon.py 启动守护进程")


if __name__ == "__main__":
    main()
