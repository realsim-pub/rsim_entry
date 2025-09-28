#!/usr/bin/env python
import sys
import time
import traceback
from typing import Any,List,Dict,Callable
from queue import PriorityQueue as ThreadPriorityQueue
import threading
from concurrent.futures import ThreadPoolExecutor, Future, CancelledError, TimeoutError

from common.logger.logger import Logger
logger = Logger.get_logger(__name__)

class TaskQueue:
    def __init__(self, executor:Callable[[Any], bool], max_concurrency:int):
        self.queue_ = ThreadPriorityQueue()
        self.pool_:List[str] = []
        self.executor_ = executor
        self.max_concurrency_ = max_concurrency
        threading.Thread(target=self._loop,  daemon=True).start()
        self.thread_pool_ = ThreadPoolExecutor(max_workers=max_concurrency)
        self.futures_ = []
        self.doing_ = []
        self.timeouter_ = None
    
    def set_timeout_processor(self, timeouter):
        self.timeouter_ = timeouter
    
    def add(self, key:str, obj:Any, priority:int=0, timeout_at:float=None) -> bool:
        if key in self.pool_:
            return False
        self.pool_.append(key)
        add_time = time.time()
        self.queue_.put((-priority, add_time, (key, obj)), block=True)
        logger.debug(f'taskQueue add task priority={priority}, add_time={add_time}, data={(key, obj)}')
        return True

    def _loop(self):
        while True:
            time.sleep(0.1)
            
            if self.queue_.empty() or len(self.doing_) >= self.max_concurrency_:
                continue
 
            priority, add_time, data = self.queue_.get()
            logger.info(f'taskQueue get task priority={priority}, add_time={add_time}, data={data}')
            future = self.thread_pool_.submit(self._do_task, data[0], data[1])
            threading.Thread(target=self._monitor_timeout, daemon=True, args=(data[0], future)).start()
            self.futures_.append(future)
            self.doing_.append(data[0])

    def _do_task(self, key:str, obj:Any) -> None:
        try:
            if not self.executor_:
                return
            ret = self.executor_(key, obj)
            if not ret:
                self.pool_.remove(key)
        except Exception as e:
            logger.info(f'do_task thread execute fail, exception={traceback.format_exc()}')
        finally:
            self.doing_.remove(key)
            
    def _monitor_timeout(self, key:str, future:Future):
        timeout_times = 0
        first_running = False
        while not future.done():
            time.sleep(0.01)
            now = time.time()
            if not first_running and future.running():
                logger.info(f'thread for {key} first checked running at {now}')
                first_running = True
            if not first_running:
                continue
            timeout_at = self.timeouter_.get_task_timeout_at(key)
            if timeout_at and timeout_at <= now:
                logger.info(f'thread for {key} timeout_at={timeout_at} < now={now}, set task timeout')
                timeout_times += 1
            elif timeout_at and timeout_at > now:
                try:
                    timeout_times = 0
                    future.result(timeout=timeout_at - now)
                except CancelledError:
                    logger.info(f'thread for {key} canceled')
                    break
                except TimeoutError:
                    timeout_times += 1
                    logger.info(f'thread for {key} timeout at {timeout_at}')
                except Exception as e:
                    logger.info(f'thread for {key} result occurs exception: {e}')
            if timeout_times > 1:
                break
        if timeout_times > 1:
            self.timeouter_.timeout_task(key)
            bret = future.cancel()
            logger.info(f'thread for {key} timeout, cancel it ret={bret}')
        else:
            logger.info(f'thread for {key} finished normally.')
