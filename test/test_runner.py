import os
import json
import base64

from runners.main import RunnerServer

test_param_json = {
    "runtime":
    {
        "runType": "custom_runner",
        "runEnv": "online",
    },
    "taskId": 1234,
    "resource":{
        "scenario_file": f"{os.path.dirname(os.path.abspath(__file__))}",
    }
}

def test_runners():
    test_param_b64 = base64.b64encode(json.dumps(test_param_json).encode("utf-8"))
    runner_server = RunnerServer(task_param_b64=test_param_b64)
    runner_server.loop()


if __name__ == "__main__":
    test_runners()