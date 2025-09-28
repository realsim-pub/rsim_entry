import rsim

from pathlib import Path

from runners.runner.runner import Runner, try_except
from runners.runner.perception_openloop import PerceptionOpenLoop
from third_party.python.common.param.task_param import TaskParams
from third_party.python.common.reflection import Reflection
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)

class CustomRunner(Runner):
    def __init__(self, task_params: TaskParams, server: rsim.PythonServerBase):
        super(CustomRunner, self).__init__()
        self._task_params: TaskParams = task_params
        self._server: rsim.PythonServerBase = server
        self._runner: Runner = self.create_runner()

    def create_runner(self) -> Runner:
        #fix helloliu by load 
        return PerceptionOpenLoop(log_dir=self._task_params.run_time.log_dir, 
                                    record_dir=self._task_params.run_time.view_dir,
                                    percep_data_file=str(Path(self._task_params.resource.scenario_file).expanduser()))
    
    @try_except
    def init(self):
        logger.info("on init...")
        self._runner.init()
        self._server.update_state(rsim.ModuleState.READY)
    
    @try_except
    def start(self):
        logger.info("on start...")
        self._server.update_state(rsim.ModuleState.RUNNING)
        self._runner.start()
        self._server.update_state(rsim.ModuleState.FINISHED)
    
    @try_except
    def stop(self):
        logger.info("on stop...")
        self._runner.stop()
        self._server.update_state(rsim.ModuleState.FINISHED)
    
