import os
import json
import yaml
import shutil
import time
import pandas as pd

from typing import List, Dict, Optional

from third_party.python.common.logger.logger import Logger
from third_party.python.common.shell_run import ShellRun

logger = Logger.get_logger(__name__)

class FileUtil:
    @staticmethod
    def remove_dir(input_dir):
        try:
            if not os.path.exists(input_dir):
                return True
            shutil.rmtree(input_dir)
        except Exception as e:
            logger.error(f"check dir exists with error:{str(e)}")
            return False
        return True
    
    @staticmethod
    def csv_reader(csv_file:str) -> pd.DataFrame :
        df = pd.read_csv(csv_file)
        return pd.DataFrame(df)
    
    @staticmethod
    def load_yaml(yaml_path) -> dict:
        yaml_config = dict()
        try:
            with open(yaml_path) as f:
                yaml_config = yaml.safe_load(f.read())
        except Exception as e:
            logger.error(f"load yaml:{yaml_path} with error:{str(e)}")
        return yaml_config

    @staticmethod
    def load_json(json_path: str) -> dict:
        data = dict()
        try:
            with open(json_path, 'r') as file:
                data = json.load(file)
        except Exception as e:
            logger.error(f"load json:{json_path} with error:{str(e)}")
        return data
    
    @staticmethod
    def load_binary_file(file_path: str) -> Optional[str]:
        content = None
        try:
            with open(file_path, 'rb') as file:
                content = file.read()
        except Exception as e:
            logger.error(f"load_binary_file:{file_path} with error:{str(e)}")
        return content

    @staticmethod
    def make_dir(input_dir, root_user=False):
        try:
            if os.path.exists(input_dir):
                return True
            if not root_user:
                os.makedirs(input_dir)
            else:
                ShellRun.sync_run(f"sudo mkdir -m 777 -p '{input_dir}'")
        except Exception as e:
            return False    
        return True
    
    @staticmethod
    def copy(src_dir: str, dest_dir: str):
        code, msg, _ = ShellRun.sync_run(f'mkdir -p "{dest_dir}"; cp -rf "{src_dir}" "{dest_dir}"')
        if code > 0:
            logger.error(f"copy file with error:{msg}")
            return False
        else:
            return True  

    @staticmethod
    def wait_ready(input_dir, time_out=2):
        start_time = time.time()
        while time.time() - start_time < time_out:
            if os.path.exists(input_dir):
                return True
            time.sleep(0.1)
        return False
    
    @staticmethod
    def dump_file(file_content:str, file_name:str, decode=True):
        try:
            with open(file_name, "+w") as f:
                if decode:
                    f.write(file_content.decode("utf-8"))
                else:
                  f.write(file_content)
        except Exception as e:
            logger.error(f"dump file with error:{str(e)}")

    @staticmethod
    def dump_yaml(file_content:Dict, file_name:str):
        try:
            with open(file_name, "w") as f:
                yaml.dump(file_content, f)
        except Exception as e:
            logger.error(f"dump file with error:{str(e)}")

    @staticmethod
    def dump_json(file_content:Dict, file_name:str):
        try:
            with open(file_name, 'w') as file:
                json.dump(file_content, file, indent=4) 
        except Exception as e:
            logger.error(f"dump file with error:{str(e)}")

    @staticmethod
    def make_dir(input_dir, root_user=False):
        try:
            if os.path.exists(input_dir):
                return True
            
            if not root_user:
                os.makedirs(input_dir)
            else:
                ShellRun.sync_run(f"sudo mkdir -m 777 -p '{input_dir}'")
        except Exception as e:
            return False
            
        return True

    @staticmethod
    def remove_dir(input_dir):
        try:
            if not os.path.exists(input_dir):
                return True
            shutil.rmtree(input_dir)
        except Exception as e:
            logger.error(f"check dir exists with error:{str(e)}")
            return False
            
        return True

    @staticmethod
    def remove_file(input_dir):
        try:
            if not os.path.exists(input_dir):
                return True
            os.remove(input_dir)
        except Exception as e:
            logger.error(f"remove file with error:{str(e)}")
            return False
            
        return True

    @staticmethod
    def remove_files(input_files: List[str]):
        for input_file in input_files:
            try:
                if not os.path.exists(input_file):
                    continue
                os.remove(input_file)
            except Exception as e:
                logger.error(f"remove file with error:{str(e)}")
        return True