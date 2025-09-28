#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import json
import random
from typing import Dict, Tuple
from singleton_decorator import singleton
import urllib.request
import urllib.parse

from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)

@singleton
class HttpReqestUtil:
    def request_post(self, http_url: str, params: Dict, headers: Dict = {}, timeout_sec: int=60) -> Tuple[bool, str]:
        logger.info(f"request post url={http_url}, header={headers}, params={params}, timeout={timeout_sec}")
        req = urllib.request.Request(http_url, json.dumps(params).encode())
        req.add_header("Content-Type", "application/x-www-form-urlencoded;charset=utf-8;")
        self.__add_headers(req, headers)
        return self.__do_request_with_retry(req, timeout_sec)

    def request_get(self, http_url: str, params: Dict={}, headers: Dict={}, timeout_sec: int=60) -> Tuple[bool, str]:
        all_url = http_url
        if params:
            url_param = urllib.parse.urlencode(params)
            all_url = http_url + "?" + url_param
        logger.info(f"request get url={all_url}, header={headers}, timeout={timeout_sec}")
        req = urllib.request.Request(all_url)
        self.__add_headers(req, headers)
        return self.__do_request_with_retry(req, timeout_sec)
        
    def request_put(self, http_url: str, params: Dict, headers: Dict = {}, timeout_sec: int=60) -> Tuple[bool, str]:
        logger.info(f"request put url={http_url}, header={headers}, params={params}, timeout={timeout_sec}")
        req = urllib.request.Request(http_url, json.dumps(params).encode(), method='PUT')
        req.add_header('Content-Type', 'application/json')
        self.__add_headers(req, headers)
        return self.__do_request_with_retry(req, timeout_sec)
    
    def __add_headers(self, req_body: urllib.request.Request, headers: Dict={}) -> None:
        if not headers:
            return
        for key in headers.keys():
            req_body.add_header(key, headers[key])
    
    def __do_request_with_retry(self, req_body: urllib.request.Request, timeout_sec: int, retry_cnt=5) -> Tuple[bool, str]:
        idx = 0
        ret, data = None, None
        while idx <= retry_cnt:
            ret, data = self.__do_request(req_body, timeout_sec)
            if ret:
                break
            time.sleep(random.randint(1,3))
            idx += 1
        return ret, data
    
    def __do_request(self, req_body: urllib.request.Request, timeout_sec: int) -> Tuple[bool, str]:
        try:
            result = urllib.request.urlopen(req_body, timeout=timeout_sec)
            res = result.read().decode()
            return True, res
        except Exception as e:
            return False, str(e)
