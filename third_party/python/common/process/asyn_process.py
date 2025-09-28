from multiprocessing import Process, Queue
from queue import Empty
from third_party.python.common.profile import profile
from typing import Callable, Any
import threading

class AsyncProcess(object):
    def __init__(self, target, *args):
        self.target_ = target
        self.args_ = args
        
        def _func(*args):
            queue = args[0]
            target_args = args[1:]
            try:
              result = target(*target_args)
            except:
              result = None
            finally:
                queue.put(result)
        
        self.queue_ = Queue()
        pass_args = (self.queue_, *args)
        self.process_ = Process(target=_func, args=pass_args)
    
    def start(self):
        self.process_.start()
    
    def get_wait(self):
        result = self.queue_.get()
        self.process_.join()
        
        return result
        
    def get_nowait(self):
        try:
            result = self.queue_.get(block=False, timeout=0.001)
            if result is not None:
                self.process_.join()
                return result
        except Empty as err:
            #print(err)
            result = None
        except Exception as e:
            self.process_.join()
            result = None
        
        return result
    
    
class AsynThreadTask(object):
    def __init__(self, task:Callable, thread:threading.Thread):
        self.method_ = task
        self.lock_ = threading.Lock()
        self.thread_ = thread if thread else threading.Thread(self._run)
    
        self.result_:Any = None
        self.args_:Any = None
        self.kwargs_:Any = None
    
    def _run(self):
        pass
    
if __name__ == '__main__':
    import time
    
    def foo(a,b):
        time.sleep(10)
        return a + b
    
    async_procss = AsyncProcess(foo, 1,2)
    async_procss.start()
    
    while 1:
        result = async_procss.get_nowait()
        if result is not None:
            print(result)
            break
        pass
    