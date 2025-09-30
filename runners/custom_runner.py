import rsim

from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from runners.runner.runner import Runner, try_except
from third_party.python.common.param.task_param import TaskParams
from third_party.python.common.file_util import FileUtil
from third_party.python.common.reflection import Reflection
from third_party.python.common.string2object import dict_to_dataclass, deep_convert_dict
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)

@dataclass
class RunnerConf:
    exec: str = ""
    def to_dict(self):
        return deep_convert_dict(self)


class CustomRunner(Runner):
    def __init__(self, task_params: TaskParams, server: rsim.PythonServerBase):
        super(CustomRunner, self).__init__()
        self._task_params: TaskParams = task_params
        self._server: rsim.PythonServerBase = server
        self._runner: Optional[Runner] = self.create_runner()

    def create_runner(self) -> Optional[Runner]:
        conf_file: str = str(Path(self._task_params.resource.runner_dir).joinpath("config.json"))
        runner_conf: RunnerConf = dict_to_dataclass(RunnerConf, FileUtil.load_json(conf_file))
        if not runner_conf or not runner_conf.exec:
             self.on_error("do not find runner config or exec is empty in config.json.")
             return None
        
        runner_file: str = str(Path(self._task_params.resource.runner_dir).joinpath(runner_conf.exec))
        runner_cls: Optional[Runner] = Reflection.load_subclasses_from_file(runner_file, Runner)
        if not runner_cls:
            self.on_error("create runner class failed.")
            return None

        return runner_cls[0](log_dir=self._task_params.run_time.log_dir, 
                             record_dir=self._task_params.run_time.view_dir,
                             percep_data_file=str(Path(self._task_params.resource.scenario_file).expanduser()))
    
    @try_except
    def init(self):
        logger.info("on init...")
        self._runner: Optional[Runner] = self.create_runner()
        if not self._runner:
            return

        if self._runner.init():
            self._server.update_state(rsim.ModuleState.READY)
        else:
            self.on_error(f"init {self._runner.runner_name} failed.")
    
    @try_except
    def start(self):
        logger.info("on start...")
        if not self._runner:
            return

        self._server.update_state(rsim.ModuleState.RUNNING)
        if self._runner.start():
            self._server.update_state(rsim.ModuleState.FINISHED)
        else:
            self.on_error(f"start {self._runner.runner_name} failed.")
    
    @try_except
    def stop(self):
        logger.info("on stop...")
        if not self._runner:
            return
        
        if self._runner.stop():
            self._server.update_state(rsim.ModuleState.FINISHED)
        else:
            self.on_error(f"stop {self._runner.runner_name} failed.")
    
    def on_error(self, msg):
        self._server.update_state(rsim.ModuleState.RUNNING_ERROR)
    
