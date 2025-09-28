from threading import Timer,Thread,Event,Condition
import time
import random
class Interval:
   def __init__(self, t, hFunction, *args, **kwargs):
      def fun_():
         return hFunction(*args, **kwargs)

      self.t_ = t
      self.hFunction_ = fun_
      self.cv_ = Condition()
      self.thread_ = Thread(target=self._run, daemon=True)
      self.canceled_:bool = False
      self.random_:bool = False

   def handle_function(self):
      self.timer_ = Timer(self.t_ ,self.handle_function)

      self.hFunction_()

      self.start()

   def _run(self):
      start_time = time.time()
      end_time = time.time()

      while not self.canceled_:
         t = random.randint(1, self.t_) if self.random_ else self.t_
         dt = t - (end_time - start_time)
         dt = max(0, dt)
         time.sleep(dt)
         start_time = time.time()
         if not self.canceled_: # in case we still have to execute hFunction 1 time if cancel is called when this thread is sleeping
            self.hFunction_()

         end_time = time.time()

   def start(self, with_random:bool=False):
      self.random_ = with_random
      self.thread_.start()

   def cancel(self):
      self.canceled_ = True

class Count(Interval):
   def __init__(self, t, hFunction, count:int, *args, **kwargs):
      times = 0
      def count_func(*args, **kwargs):
         nonlocal times
         times += 1
         if times >= count:
            self.cancel()

         return hFunction(*args, **kwargs)

      super().__init__(t, count_func, *args, **kwargs)

if __name__ == '__main__':
   def c():
      print(f"{time.time()}")
      time.sleep(2)
   # count = Count(1, c, 3)
   # count.start()
   heartbeat_interval = Interval(10, c)
   heartbeat_interval.start()

   while True:
      time.sleep(1)