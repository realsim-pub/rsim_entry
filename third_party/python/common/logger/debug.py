import time
from typing import Optional
from third_party.python.common.logger.logger import Logger
logger = Logger.get_logger(__name__)

_logged = set()
_disabled = False
_periodic_log = False
_last_logged = 0.0


def log_once(key, periodic=False, print_key=False):
    """Returns True if this is the "first" call for a given key.

    Various logging settings can adjust the definition of "first".

    Example:
        >>> if log_once("some_key"):
        ...     logger.info("Some verbose logging statement")
    """

    global _last_logged

    if _disabled:
        return False
    elif key not in _logged:
        _logged.add(key)
        _last_logged = time.time()
        
        if print_key:
            logger.info(key)
        return True
    elif (_periodic_log or periodic) and time.time() - _last_logged > 60.0:
        _logged.clear()
        _last_logged = time.time()
        return False
    else:
        return False


def disable_log_once_globally():
    """Make log_once() return False in this process."""

    global _disabled
    _disabled = True


def enable_periodic_logging():
    """Make log_once() periodically return True in this process."""

    global _periodic_log
    _periodic_log = True




import cProfile, pstats, io
from pstats import SortKey
class ContextProfile:
    def __init__(self, sortby=SortKey.TIME):
        self.pr_ = cProfile.Profile()
        self.states_ = None
        self.sortby_ = sortby
        
    def __enter__(self):
        self.pr_.enable()
        return self
    
    def __exit__(self, type, value, traceback):
        self.pr_.disable()
        s = io.StringIO()
        ps = pstats.Stats(self.pr_, stream=s).sort_stats(self.sortby_)
        ps.print_stats()
        self.states_ = s.getvalue()
        
    @property
    def states(self):
        return self.states_
    
    @states.setter
    def states(self, states):
        self.states_ = states
        

global_disable = False
class warn_if_slow:
    """Prints a warning if a given operation is slower than 100ms.

    Example:
        >>> with warn_if_slow("some_operation", 0.1):
        ...    do_something(something)
    """

    DEFAULT_MESSAGE = "The `{name}` operation took {duration:.3f} s, " \
                      "which may be a performance bottleneck."

    def __init__(self,
                 name: str,
                 threshold: Optional[float] = 0.09,
                 message: Optional[str] = None,
                 profile: Optional[bool] = False,
                 profile_sortby=SortKey.TIME,
                 disable: bool = False):
        if global_disable:
            return
        
        self.disable = disable
        if disable:
            return
        
        self.profile_ = profile
        if profile:
            self.cp_ = ContextProfile(sortby=profile_sortby)
        
        self.name = name
        self.threshold = threshold
        self.message = message or self.DEFAULT_MESSAGE
        self.too_slow = False
        

    def __enter__(self):
        if global_disable or self.disable:
            return self
        
        self.start = time.time()
        
        if self.profile_:
            self.cp_.__enter__()
            
        return self

    def __exit__(self, type, value, traceback):
        if global_disable or self.disable:
            return
        
        if self.profile_:
            self.cp_.__exit__(type, value, traceback)
            
        now = time.time()
        if now - self.start > self.threshold:
            self.too_slow = True
            duration = now - self.start
            logger.warning(
                self.message.format(name=self.name, duration=duration))
            
            if self.profile_:
                logger.warning(f"profile:\n{self.cp_.states}")
        
