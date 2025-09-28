import time
import logging
from functools import wraps
from typing import Dict, List

from dataclasses import dataclass

from third_party.python.common.string2object import deep_convert_dict
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)

@dataclass
class ProfileDaTa:
    name: str=""
    start_time: float=0
    end_time: float=0
    duration: float=0

@dataclass
class PerfItem:
    step: str
    sub_step: str
    duration: float
    start_time: int 
    end_time: int 
    extension: str=""

@dataclass
class PerfDataParam:
    task_id: int
    step_v_o_list: List[PerfItem]
    
    def to_dict(self):
        return deep_convert_dict(self) 

def profile(func):
    def wrap(*args, **kwargs):
        started_at = time.time()
        result = func(*args, **kwargs)
        logger.info(f"profile-{func}-{time.time() - started_at}")
        return result

    return wrap

def profile(profile_data: ProfileDaTa, name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            ret = func(*args, **kwargs)
            end_time = time.time()
            
            profile_data.name = name
            profile_data.start_time = start_time
            profile_data.end_time = end_time
            profile_data.duration = end_time - start_time
               
            return ret
        return wrapper
    return decorator 

def report_perf(step: str, sub_step: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            ret = func(*args, **kwargs)
            end_time = time.time()
            report_perf_data(step, sub_step,
                            (end_time - start_time),
                            start_time,
                            end_time)
            return ret
        return wrapper
    return decorator 

def report_perf_data(step: str, 
                     sub_step: str, 
                     duration: float,
                     start_time:float, 
                     end_time: float):
    
    perf_item  = PerfItem(step=step,
                          sub_step=sub_step, 
                          duration=int(max((duration)*1e3, 0)),
                          start_time=int(start_time*1e3),
                          end_time=int(end_time*1e3))
            

def profile_add(profile_dict: Dict, name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            begin_time = time.time()
            ret = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - begin_time
            
            if name not in profile_dict.keys():
                profile_dict[name] = duration
            else:
               profile_dict[name] = profile_dict[name] + duration
               
            return ret
        return wrapper
    return decorator

def coast_time(func):
    def fun(*args, **kwargs):
        t = time.perf_counter()
        result = func(*args, **kwargs)
        if time.perf_counter() - t > 0.1:
            logger.info(f'func {func.__name__} coast time:{time.perf_counter() - t:.8f} s')
        return result

    return fun
