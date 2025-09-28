import dill
import multiprocessing

from dataclasses import dataclass
from typing import List, TypeVar, Generic, Type, NewType
from multiprocessing import  Queue as MultiprocessingQueue
from queue import Queue as ThreadQueue
from abc import ABC, abstractmethod
from third_party.python.common.logger.logger import Logger
logger = Logger.get_logger(__name__)

# @dataclass
# class Message:
#     topic:str
#     timestamp:float
#     message:object

class Message(object):
    __slots__ = ['topic', 'timestamp', 'message', 'alias']
    
    def __init__(self, topic, timestamp, message, alias):
        self.topic =  topic
        self.timestamp = timestamp
        self.message = message
        self.alias = alias
    
    
@dataclass
class Item:
    closed:bool
    data:object
    

T = TypeVar('T')  # Key type.

class _Queue(Generic[T], ABC):
    def __init__(self, queue=None) -> None:
        super().__init__()
        
        if queue:
            self.queue_ = queue
        else:
            self.queue_ = self.contruct_queue()
        self.closed_ = False

    def queue(self):
        return self.queue_
        
    @abstractmethod
    def contruct_queue(self):
        pass
    
    def qsize(self):
        return self.queue_.qsize()
    
    def is_empty(self):
        return self.queue_.empty()
    
    def get_with_count(self, mesasge_count=100) -> List[T]:
        q_size = self.qsize()
        q_list:List[T] = []
        get_count = 0
        
        while(get_count < min(mesasge_count, q_size)):
            item = self.get() 
            if not item:
                break
            q_list.append(item)
            get_count = get_count + 1
        
        return q_list
    
    def get(self)->T:
        if self.closed_ and self.is_empty():
            return None
        
        item = None
        
        try:
            item:Item = self.queue_.get()
            if item.closed == True:
                self.closed_ = True
        except:
            self.closed_ = True
            return None
        else:
            return item.data
        
    def put(self, v:T):
        if self.closed_:
            return
        
        try:
            item = Item(closed=False, data=v)
            self.queue_.put(item)
        except Exception as e:
            logger.error(f"put queue with error:{str(e)}")
    
    def clear(self):
        if self.queue_:
            self.queue_ = None
        
    def close(self):
        if self.closed_:
            return
        
        if self.queue_:
            item = Item(closed=True, data=None)
            self.queue_.put(item)
            self.closed_ = True
        
    def is_close(self):
        return self.closed_ and self.is_empty()
    
    def dumps(self)->str:
        authkey = bytes(multiprocessing.current_process().authkey)
        authkey_dumped = dill.dumps(authkey).hex()
        queue_dumped = dill.dumps(self.queue_).hex()
        
        return authkey_dumped + "," + queue_dumped
    
    @staticmethod
    def loads_queue(dumped_str):
        args = dumped_str.split(",")
        authkey_dumped = bytes.fromhex(args[0])
        queue_dumped = bytes.fromhex(args[1])
        
        authkey = dill.loads(authkey_dumped)
        multiprocessing.current_process().authkey = authkey
    
        queue = dill.loads(queue_dumped)
        return queue

class ProcessQueue(Generic[T], _Queue[T]):
    def contruct_queue(self):
        return multiprocessing.Manager().Queue()
    
    @staticmethod
    def loads(dumped_str):
        queue = _Queue.loads_queue(dumped_str)
        return ProcessQueue(queue)

class Queue(Generic[T], _Queue[T]):
    def contruct_queue(self):
        return ThreadQueue()

    @staticmethod
    def loads(dumped_str):
        queue = _Queue.loads_queue(dumped_str)
        return Queue(queue)

if __name__ == '__main__':
    queue:ProcessQueue[int] = ProcessQueue()
    
    queue.put(1)
    queue.put(2)
    queue.put(3)
    queue.close()
    
    while True:
        a = queue.get()
        if not a:
            break
        print(a)
        print(queue.queue().empty())
        
    a = queue.get()
    print(queue.queue().empty())
    print(a)
    
    