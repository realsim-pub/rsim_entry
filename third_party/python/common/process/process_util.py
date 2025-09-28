import psutil

class ProcessUtil(object):
    
    @staticmethod
    def is_process_running(process_name: str) -> bool:
        """
        Check if there is any running process with the given name.

        :param process_name: Name of the process to check
        :return: True if the process is running, False otherwise
        """
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == process_name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process has been terminated or no permission to access
                continue
        return False