import traceback

from abc import ABC, abstractmethod
from functools import wraps
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)

def try_except(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger.error(
                f"call func with error:{func}, {str(e)}, traceback:{traceback.print_exc()}"
            )
            self.on_error(f"adapter has error.")
    return wrapper

class Runner(ABC):
    
    @abstractmethod
    def init(self) -> bool:
        return True
    
    @abstractmethod
    def start(self) -> bool:
        return True
    
    @abstractmethod
    def stop(self) -> bool:
        return True
    
    def on_error(self, msg: str) -> bool:
        return True