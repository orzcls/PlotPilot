"""流式消息总线 - 用于自动驾驶守护进程与 SSE 接口之间的实时通信

守护进程在独立进程中运行，SSE 接口在主进程中运行。
使用 multiprocessing.Queue 实现跨进程通信。

注意：每个小说有独立的队列，避免消息混乱。

重要：Manager 必须在主进程中初始化，因为守护进程（daemon=True）不允许创建子进程。
"""
import asyncio
import json
import multiprocessing as mp
import threading
import time
import logging
from collections import defaultdict
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# 全局队列管理器（单例）
# 使用 Manager 创建跨进程共享的字典
# 重要：必须在主进程中调用 init_streaming_bus() 初始化，不能懒加载
# 因为守护进程（daemon=True）不允许创建子进程，而 Manager 需要启动管理进程
_manager: Optional[mp.Manager] = None
_stream_queues: Optional[Dict] = None  # novel_id -> Queue
_lock = threading.Lock()
_initialized = False


def init_streaming_bus():
    """在主进程中初始化 StreamingBus 的 Manager。
    
    必须在启动守护进程前调用，因为守护进程（daemon=True）不允许创建子进程。
    Manager() 会启动一个管理进程，所以必须在主进程中创建。
    
    Example:
        # 在 main.py 中，启动守护进程之前调用
        from application.engine.services.streaming_bus import init_streaming_bus
        init_streaming_bus()
        start_autopilot_daemon_thread()
    """
    global _manager, _stream_queues, _initialized
    
    if _initialized:
        logger.debug("[StreamingBus] 已初始化，跳过")
        return
    
    with _lock:
        if _initialized:
            return
        
        logger.info("[StreamingBus] 在主进程中初始化 Manager...")
        _manager = mp.Manager()
        _stream_queues = _manager.dict()
        _initialized = True
        logger.info("[StreamingBus] Manager 初始化完成")


def _get_manager():
    """获取全局 Manager（必须在主进程中预先初始化）"""
    global _manager, _stream_queues, _initialized
    
    if not _initialized or _manager is None:
        # 如果未初始化，尝试在非守护进程中初始化
        # 如果当前是守护进程，会抛出 "daemonic processes are not allowed to have children"
        import multiprocessing as mp_check
        current_process = mp_check.current_process()
        if current_process.daemon:
            logger.error(
                "[StreamingBus] 错误：在守护进程中调用但 Manager 未初始化！"
                "请在主进程中调用 init_streaming_bus() 启动守护进程前。"
            )
            raise RuntimeError(
                "StreamingBus Manager 未初始化。"
                "必须在主进程启动守护进程前调用 init_streaming_bus()。"
            )
        
        # 非守护进程：可以尝试初始化
        init_streaming_bus()
    
    return _manager, _stream_queues


def _get_or_create_queue(novel_id: str) -> mp.Queue:
    """获取或创建指定小说的队列"""
    _, queues = _get_manager()
    if novel_id not in queues:
        with _lock:
            if novel_id not in queues:
                queues[novel_id] = _manager.Queue(maxsize=2000)
                logger.debug(f"[StreamingBus] 创建队列: {novel_id}")
    return queues[novel_id]


class StreamingBus:
    """流式消息总线 - 发布/订阅模式（基于 multiprocessing.Queue）"""
    
    def __init__(self):
        # 本地订阅者（SSE 接口使用）
        self._subscribers: Dict[str, asyncio.Queue] = defaultdict(list)
        # 本地读取位置追踪（用于从 mp.Queue 读取时去重）
        self._local_positions: Dict[str, int] = defaultdict(int)
    
    def publish(self, novel_id: str, chunk: str):
        """发布增量文字（守护进程调用）"""
        if not chunk:
            return
        
        try:
            queue = _get_or_create_queue(novel_id)
            # 非阻塞写入，队列满时丢弃最旧的
            try:
                queue.put_nowait(chunk)
            except:
                # 队列满，清空一部分后重试
                try:
                    for _ in range(100):
                        queue.get_nowait()
                except:
                    pass
                try:
                    queue.put_nowait(chunk)
                except:
                    pass
            
            logger.debug(f"[StreamingBus] publish: {novel_id}, {len(chunk)} chars")
        except Exception as e:
            logger.error(f"[StreamingBus] publish 失败: {e}")
    
    def subscribe(self, novel_id: str) -> asyncio.Queue:
        """订阅增量文字（SSE 接口调用）"""
        queue = asyncio.Queue(maxsize=1000)
        self._subscribers[novel_id].append(queue)
        return queue
    
    def unsubscribe(self, novel_id: str, queue: asyncio.Queue):
        """取消订阅"""
        if novel_id in self._subscribers:
            try:
                self._subscribers[novel_id].remove(queue)
            except ValueError:
                pass
    
    def get_chunk(self, novel_id: str, timeout: float = 0.1) -> Optional[str]:
        """从跨进程队列获取增量文字（非阻塞，带超时）"""
        try:
            _, queues = _get_manager()
            if novel_id not in queues:
                return None
            
            mp_queue = queues[novel_id]
            try:
                # 使用短超时避免阻塞
                chunk = mp_queue.get(timeout=timeout)
                return chunk
            except:
                return None
        except Exception as e:
            logger.debug(f"[StreamingBus] get_chunk 异常: {e}")
            return None
    
    def clear(self, novel_id: str):
        """清空指定小说的队列"""
        try:
            _, queues = _get_manager()
            if novel_id in queues:
                mp_queue = queues[novel_id]
                # 清空队列
                while True:
                    try:
                        mp_queue.get_nowait()
                    except:
                        break
                logger.debug(f"[StreamingBus] 清空队列: {novel_id}")
        except Exception as e:
            logger.debug(f"[StreamingBus] clear 异常: {e}")


# 全局单例
streaming_bus = StreamingBus()
