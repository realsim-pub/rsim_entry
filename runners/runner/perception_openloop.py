from runners.runner.runner import Runner
from third_party.python.common.shell_run import ShellRun
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)

class PerceptionOpenLoop(Runner):
    def __init__(self, log_dir: str, record_dir: str, percep_data_file: str):
        self._log_dir: str = log_dir
        self._record_dir: str = record_dir
        self._percep_data_file: str = percep_data_file
        
    def init(self):
        start_perception_cmd = f"cd /workspace/workspace/hv_percep_x86_20250915_service/install; bash run_exec.sh > {self._log_dir}/perception.log 2>&1"
        ShellRun.async_run(start_perception_cmd)
        return True

    def start_record(self):
        record_cmd = (
            f"ros2 bag record -o {self._record_dir}/realview.mcap "
            f"--max-bag-size 5368709120 "
            f"--max-bag-duration 600  --all "
            f" > {self._log_dir}/record_mcap.log 2>&1"
        )
        ShellRun.async_run(record_cmd)
        logger.info(f"record mcap cmd:{record_cmd}")
    
    def start_replay(self):
        play_cmd = f"ros2 bag play --storage sqlite3 {self._percep_data_file} > {self._log_dir}/play_mcap.log 2>&1"
        code, msg, _ = ShellRun.sync_run(play_cmd)
        logger.error(f"play bag cmd: {play_cmd} failed:{msg}")
        return code <=0

    def start(self):
        self.start_record()
        self.start_replay()
        
    def stop(self):
        play_cmd = f"pkill -f realview.mcap"
        ShellRun.sync_run(play_cmd)
        return True

        