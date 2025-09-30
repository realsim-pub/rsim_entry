import rsim

from runners.runner.runner import Runner, try_except
from third_party.python.common.param.task_param import TaskParams
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)


class PNCRunner(Runner):
    def __init__(self, task_params: TaskParams, server: rsim.PythonServerBase):
        super(PNCRunner, self).__init__()
        self._task_params: TaskParams = task_params
        self._server: rsim.PythonServerBase = server

    @try_except
    def init(self):
        logger.info("on init...")
        self._server.update_state(rsim.ModuleState.READY)

    
    @try_except
    def start(self):
        logger.info("on start...")
        self._server.update_state(rsim.ModuleState.RUNNING)
    
    @try_except
    def stop(self):
        logger.info("on stop...")
        self._server.update_state(rsim.ModuleState.FINISHED)
    
    def on_error(self, msg):
        self._server.update_state(rsim.ModuleState.RUNNING_ERROR)
    
