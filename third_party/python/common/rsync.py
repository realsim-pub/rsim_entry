
from typing import Tuple
from third_party.python.common.shell_run import ShellRun

class Rsync(object):
    
    @staticmethod
    def diff(base_dir: str, 
             input_dir: str, 
             patch_file: str,
             timeout: float=180) -> Tuple[bool, str]:
        
        diff_cmd = f"rsync -rl --delete --timeout={timeout} --only-write-batch={patch_file} {input_dir} {base_dir} >> /dev/null"
        code, msg, _ = ShellRun.async_run(diff_cmd)
        return code==0, msg
    
    @staticmethod
    def patch(base_dir: str, 
              patch_file: str,
              timeout: float=180) -> Tuple[bool, str]:
        
        patch_cmd = f"rsync -rl --delete  --timeout={timeout} --read-batch={patch_file} {base_dir} >> /dev/null"
        code, msg, _= ShellRun.sync_run(patch_cmd)
        
        return code==0, msg