import os
import time
import uuid
import socket
import telnetlib

from typing import Iterable, List
from contextlib import contextmanager
from singleton_decorator import singleton

from third_party.python.common.file_util import FileUtil
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)


def retry(num: int, wait_time: float):
    """
    重试某个方法, 方法必须返回true方可中止重试
    :param num: 重试次数
    :param wait_time: 重试等待间隔时间，若不指定有默认值
    """
    def wrapper(func):
        def wrap(*args, **kwargs):
            ret = None
            try_time_count = 0
        
            while try_time_count < num:   
                try:         
                    ret = func(*args, **kwargs)
                except Exception as e:
                    pass
                
                if ret:
                    break
                try_time_count = try_time_count + 1
                time.sleep(wait_time)
            logger.info(f'try {try_time_count} times with status:{try_time_count < num}...')
            return ret   
        return wrap
    return wrapper

@contextmanager
def get_free_loopback_tcp_port() -> Iterable[str]:
    if socket.has_ipv6:
        tcp_socket = socket.socket(socket.AF_INET6)
    else:
        tcp_socket = socket.socket(socket.AF_INET)
    tcp_socket.bind(('', 0))
    address_tuple = tcp_socket.getsockname()
    yield f"{address_tuple[1]}"
    tcp_socket.close()
    
@singleton
class PortSelect:
    def __init__(self):
        self.count_ = 0
    
    def select_port(self, port_list: List[int]=[]):
        self.count_ += 1

        if port_list:
            return port_list[self.count_%len(port_list)]
        
        try:
            with get_free_loopback_tcp_port() as tcp_port:
                select_port = tcp_port
        except Exception as e:
            logger.error(f"auto select port with error:{str(e)}")
        return select_port


def generate_uds_fd():
    uds_fd_dir = "/tmp/rpc"
    FileUtil.make_dir(uds_fd_dir)
    return f"{uds_fd_dir}/{str(uuid.uuid4())}.sock"

@retry(num=200, wait_time=0.1)
def check_uds_exist(uds_fd, try_times=100):
    return os.path.exists(uds_fd)
  
class NetworkUtil(object):
    # 检查端口连通性
    @staticmethod
    def check_telnet(ip, port, retry_cnt=1):
        cnt = 0
        while cnt < retry_cnt:
            cnt += 1
            if cnt > 1:
                time.sleep(0.1)
            try:
                telnetlib.Telnet(ip, int(port), timeout=1)
                return True
            except Exception as e:
                continue
        return False
    
    @staticmethod
    def get_host_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 这里连接到任意一个外部地址，只是为了获取IP
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]
        except socket.error:
            ip_address = 'Unable to get IP address'
        finally:
            s.close()
        return ip_address