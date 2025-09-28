import os
import subprocess

from pathlib import Path

class Util:
    
    @staticmethod
    def get_sys_version() -> str:
        shell_file = Path(__file__).parent / "sys_version.sh"
        sys_version = subprocess.run(["bash", str(shell_file)], capture_output=True, text=True).stdout.strip()
        return sys_version
    
    @staticmethod
    def get_pid(self) -> int:
        return os.getpid()