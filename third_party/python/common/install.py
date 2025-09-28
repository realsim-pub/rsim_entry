import subprocess
 
def check_command_exists(command):
    try:
        subprocess.check_output(['which', command])
        return True
    except subprocess.CalledProcessError:
        return False