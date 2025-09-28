from runners.runner.runner import Runner
from third_party.python.common.shell_run import ShellRun
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)

class PerceptionOpenLoop(Runner):
    def __init__(self, log_dir: str, record_dir: str, percep_data_file: str):
        self._log_dir: str = log_dir
        self._record_dir: str = record_dir
        self._percep_data_file: str = percep_data_file
        
    def init(self) -> bool:
        start_perception_cmd = ""
        ShellRun.async_run(start_perception_cmd)
        return True

    def start_record(self):
        record_cmd = (
            f"ros2 bag record -o {self._record_dir}/realview.mcap "
            f"--max-bag-size 5368709120 "
            f"--max-bag-duration 600 "
            f" > {self._log_dir}/record_mcap.log 2>&1"
        )
        ShellRun.async_run(record_cmd)
    
    def start_replay(self):
        play_cmd = f"ros2 bag play {self._percep_data_file}"
        status, msg, _ = ShellRun.sync_run(play_cmd)
        if status > 0:
            logger.error(f"replay bag {self._percep_data_file} with error:{msg}.")
        return status <= 0

    def start(self) -> bool:
        self.start_record()
        self.start_replay()
        
    def stop(self):
        play_cmd = f"pkill -f realview.mcap"
        ShellRun.sync_run(play_cmd)
        return True

        