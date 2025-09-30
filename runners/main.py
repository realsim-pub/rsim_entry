import rsim
import argparse

from runners.runner.runner import Runner
from runners.custom_runner import CustomRunner
from runners.pnc_runner import PNCRunner
from third_party.python.common.param.task_param import TaskParams
from third_party.python.common.param.params import RunType
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)


class RunnerFactory(object):

    @staticmethod
    def create(task_params: TaskParams, server: rsim.PythonServerBase) -> Runner:
        if task_params.run_time.run_type == RunType.CUSTOM_RUNNER:
            return CustomRunner(task_params=task_params,
                                server=server)
        else:
            return PNCRunner(task_params=task_params,
                             server=server)

class RunnerServer(object):
    def __init__(self, task_param_b64: bytes):
        self._task_params = TaskParams(task_param_b64=task_param_b64)
        self._server: rsim.PythonServerBase = rsim.PythonServerBase("adapter", "127.0.0.1", 7007, 7008)
        self._runner: Runner = RunnerFactory.create(task_params=self._task_params, server=self._server)
        self._init()
        
    def _init(self):
        logger.info(f"task param b64:{self._task_params.task_param_b64}, object:{self._task_params.task_param_json}")
        self._server.bind_async_action("init", self._runner.init)
        self._server.bind_async_action("start", self._runner.start)
        self._server.bind_async_action("stop", self._runner.stop)
        self._server.update_state(rsim.ModuleState.INIT)
    
    def loop(self):
        while True:
         self._server.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--task_param_b64", help="task parameter")
    args, _ = parser.parse_known_args()
    
    task_param_b64 = args.task_param_b64
    runner_server: RunnerServer = RunnerServer(task_param_b64=task_param_b64)
    runner_server.loop() 