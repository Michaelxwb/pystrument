"""
数据发送器模块
"""
import json
import time
import queue
import threading
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
import requests
import logging

logger = logging.getLogger(__name__)


class DataSender:
    """性能数据发送器"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "X-Project-Key": config.project_key,
            "User-Agent": f"performance-monitor-sdk/{config.sdk_version}"
        })
        
        # 批量发送相关
        self._batch_queue: queue.Queue = queue.Queue()
        self._batch_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # 线程池
        self._executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="perf-sender")
        
        if config.async_send:
            self._start_batch_processor()
    
    def send_sync(self, performance_data: Dict[str, Any]) -> bool:
        """同步发送性能数据"""
        try:
            endpoint = f"{self.config.api_endpoint}/v1/performance/collect"
            
            response = self.session.post(
                endpoint,
                json=performance_data,
                timeout=self.config.request_timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.debug(f"性能数据发送成功: {performance_data.get('trace_id')}")
                    return True
                else:
                    logger.error(f"性能数据发送失败: {result.get('msg')}")
                    return False
            else:
                logger.error(f"性能数据发送失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"发送性能数据异常: {str(e)}")
            return False
    
    def send_async(self, performance_data: Dict[str, Any]):
        """异步发送性能数据"""
        try:
            # 添加到批量队列
            if self.config.batch_size > 1:
                self._batch_queue.put(performance_data)
            else:
                # 直接异步发送
                self._executor.submit(self.send_sync, performance_data)
                
        except Exception as e:
            logger.error(f"异步发送失败: {str(e)}")
    
    def send_batch(self, batch_data: List[Dict[str, Any]]) -> bool:
        """批量发送性能数据"""
        try:
            if not batch_data:
                return True
            
            endpoint = f"{self.config.api_endpoint}/v1/performance/batch"
            
            payload = {
                "records": batch_data,
                "batch_size": len(batch_data)
            }
            
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.config.request_timeout * 2  # 批量请求延长超时时间
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    logger.debug(f"批量发送成功: {len(batch_data)} 条记录")
                    return True
                else:
                    logger.error(f"批量发送失败: {result.get('msg')}")
                    return False
            else:
                logger.error(f"批量发送失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"批量发送异常: {str(e)}")
            return False
    
    def _start_batch_processor(self):
        """启动批量处理线程"""
        if self._batch_thread and self._batch_thread.is_alive():
            return
        
        self._batch_thread = threading.Thread(
            target=self._batch_processor,
            daemon=True,
            name="performance-batch-processor"
        )
        self._batch_thread.start()
        logger.debug("批量处理线程已启动")
    
    def _batch_processor(self):
        """批量处理器"""
        batch_data = []
        last_send_time = time.time()
        
        while not self._stop_event.is_set():
            try:
                # 尝试获取数据（带超时）
                try:
                    data = self._batch_queue.get(timeout=1.0)
                    batch_data.append(data)
                except queue.Empty:
                    data = None
                
                current_time = time.time()
                should_send = False
                
                # 检查发送条件
                if len(batch_data) >= self.config.batch_size:
                    should_send = True
                elif batch_data and (current_time - last_send_time) >= self.config.batch_timeout:
                    should_send = True
                
                if should_send and batch_data:
                    # 发送批量数据
                    self._executor.submit(self._send_batch_with_retry, batch_data.copy())
                    batch_data.clear()
                    last_send_time = current_time
                    
            except Exception as e:
                logger.error(f"批量处理器异常: {str(e)}")
                time.sleep(1)
        
        # 发送剩余数据
        if batch_data:
            self._send_batch_with_retry(batch_data)
    
    def _send_batch_with_retry(self, batch_data: List[Dict[str, Any]]):
        """带重试的批量发送"""
        max_retries = self.config.retry_times
        retry_delay = self.config.retry_delay
        
        for attempt in range(max_retries + 1):
            try:
                if self.send_batch(batch_data):
                    return
                
                if attempt < max_retries:
                    time.sleep(retry_delay * (2 ** attempt))  # 指数退避
                    
            except Exception as e:
                logger.error(f"批量发送重试 {attempt + 1} 失败: {str(e)}")
                if attempt < max_retries:
                    time.sleep(retry_delay * (2 ** attempt))
        
        logger.error(f"批量发送最终失败，丢弃 {len(batch_data)} 条记录")
    
    def flush(self, timeout: int = 30):
        """刷新所有待发送的数据"""
        try:
            # 等待队列清空
            start_time = time.time()
            while not self._batch_queue.empty() and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            # 等待线程池任务完成
            self._executor.shutdown(wait=True, timeout=timeout)
            
        except Exception as e:
            logger.error(f"刷新数据失败: {str(e)}")
    
    def close(self):
        """关闭发送器"""
        try:
            # 停止批量处理器
            self._stop_event.set()
            
            # 刷新数据
            self.flush()
            
            # 关闭session
            self.session.close()
            
            logger.debug("数据发送器已关闭")
            
        except Exception as e:
            logger.error(f"关闭发送器失败: {str(e)}")
    
    def __del__(self):
        """析构函数"""
        try:
            self.close()
        except:
            pass