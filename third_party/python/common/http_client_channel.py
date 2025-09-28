#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
import time
import urllib.parse
import urllib.request

from enum import IntEnum
from collections import deque
from threading import Thread
from dataclasses import dataclass
from singleton_decorator import singleton

from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)


class ERROR_CODE(IntEnum):
    OK = 0,
    FAIL = 1,
    EXCEPTION = 2,
    TIMEOUT = 3,
    RESOURCE_LIMIT = 4,
    PARAM_ILLEGAL = 5,
    URL_NOT_FOUND = 6,
    RESOURCE_NOT_FOUND = 7

@dataclass
class Status:
    code:int
    message:str
    
    def __repr__(self):
        return f"code:{self.code}, message:{self.message}"

@dataclass
class RequestItem:
    url: str
    body: str
    method: str
    headers: str
    
    @staticmethod
    def create(url: str, body: str, method: str, headers:str):
        return RequestItem(url, body, method, headers)

    def __repr__(self):
        return f"code:{self.url}, message:{self.body}"

@singleton
class HttpClientChannel:
    
    def __init__(self) -> None:
        self.message_queue_ = deque()
        self.message_consume_thread_ = Thread(target=self._message_consume_loop)
        self.message_consume_thread_.setDaemon(True)
        self.message_consume_thread_.start()
    
    def request(self, url, params, method=None, headers=None, timeout=10, latch=False, retry_times=1) -> Status:
        logger.info(f"resquest:{url}, params:{params}, method:{method}")
        if not latch:
             return self._do_retry(url, params, method, headers, timeout, retry_times=retry_times)
        else:
            request_status = Status(code=ERROR_CODE.OK, message="")
            
            try:
                self.message_queue_.append(RequestItem.create(url, params, method, json.dumps(headers) if headers else None))
            except Exception as e:
                request_status.code = ERROR_CODE.FAIL
                request_status.message = f"请求发送失败:{str(e)}"
                logger.error(request_status)
            
            return request_status
    
    def _do_retry(self, url, params, method, headers, timeout=10, latch=False, retry_times=1):
        try_count = 0
        request_status = Status(code=ERROR_CODE.OK, message="")
        
        while try_count < retry_times:
            request_status = self._do_request(url, params, method, headers, timeout)
            if request_status.code == ERROR_CODE.OK:
                return request_status
            try_count += 1
            time.sleep(1)
        
        return request_status
    
    def _do_request(self, url, params, method, headers, timeout=10) -> Status:
        request_status = Status(code=ERROR_CODE.OK, message="")
        req = urllib.request.Request(url, params.encode("utf-8"), method=method)
        if headers:
            for k,v in headers.items():
                req.add_header(k, v)
        else:
            req.add_header("Content-Type", "application/json;charset=utf-8;")
        
        try:
            result = urllib.request.urlopen(req, timeout=timeout)
            res = result.read()
            request_status.message = res.decode()
        except Exception as e:
            logger.error(f"HTTP, exception is {str(e)}")
            request_status.message = str(e)
            request_status.code = ERROR_CODE.FAIL
        
        return request_status
    
    def _message_consume_loop(self):
        while True:
            
            if not self.message_queue_:
                time.sleep(0.1)
                continue
            
            request_item = self.message_queue_.popleft()
            request_status = self._do_request(request_item.url, request_item.body, request_item.method, json.loads(request_item.headers) if request_item.headers else None)
            
            if request_status.code == ERROR_CODE.FAIL:
                self.message_queue_.appendleft(request_item)
     
            time.sleep(0.1)
            

