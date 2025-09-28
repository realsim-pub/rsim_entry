import json
import threading

from typing import List, Optional, Dict
from collections import OrderedDict
from third_party.python.common.process.thread_util import (
    thread_get_specific_recursively,
    thread_set_specific,
    thread_get_specific,
)
from third_party.python.common.string2object import (
    base64_json_to_object,
    json_string_to_object,
    base64_to_json,
)

from third_party.python.common.param.params import (
    TimeParam,
    VehicleParam,
    CaseInfoParam,
    RunTimeParam,
    MapParam,
    MetricsParam,
    ResourceParam,
    WorldParam,
    ExtendParam
)
from third_party.python.common.logger.logger import Logger

logger = Logger.get_logger(__name__)


def get_task_id_from_b64(task_param_b64):
    task_param = base64_json_to_object(task_param_b64)
    return int(task_param.taskId) if hasattr(task_param, "taskId") else -1


_task_params_key = "task_ids"


def push_task_param_context(task_id: int):
    assert task_id is not None and task_id > 0
    task_ids = thread_get_specific(_task_params_key)
    if task_ids is None:
        task_ids = []
        ids_from_upper = thread_get_specific_recursively(_task_params_key)
        if ids_from_upper:
            task_ids.extend(ids_from_upper)
        thread_set_specific(_task_params_key, task_ids)
    if task_ids and task_ids[-1] == task_id:
        pass
    else:
        task_ids.append(task_id)
        logger.debug(
            f"push context, thread={threading.currentThread().getName()} push task_id={task_id}, context={task_ids}"
        )


def pop_task_param_context():
    lst = thread_get_specific(_task_params_key)
    assert lst is not None and len(lst) > 0
    logger.debug(
        f"pop context, thread={threading.currentThread().getName()} context={lst}, pop last={lst[-1]}"
    )
    lst.pop()


class TaskParams(object):
    params_map_: Dict[int, "TaskParams"] = OrderedDict()

    def __new__(cls, *args, **kwargs):
        # get taskid
        taskid: int = None
        if "task_param_b64" in kwargs:
            task_id = get_task_id_from_b64(kwargs["task_param_b64"])
            assert task_id is not None and task_id > 0
        else:
            task_ids = thread_get_specific_recursively(_task_params_key)
            # fixme not support none context later
            # assert(task_ids is not None and len(task_ids) > 0)
            if not task_ids:
                assert len(cls.params_map_) > 0
                task_id = list(cls.params_map_.keys())[-1]
                # logger.warning(f"plz set TaskParams taskid context, none context is dangerous")
            else:
                task_id = task_ids[-1]
            assert task_id in cls.params_map_

        # instance
        if task_id not in cls.params_map_:
            cls.params_map_[task_id] = super(TaskParams, cls).__new__(cls)

        # context set
        if "task_param_b64" in kwargs:
            push_task_param_context(task_id)

        return cls.params_map_[task_id]

    def __init__(self, task_param_b64: Optional[bytes] = None):
        if not task_param_b64:
            return
        if hasattr(self, "task_param_b64_") and self.task_param_b64_:
            return

        self.task_param_b64_: Optional[bytes] = task_param_b64
        self.task_param_json_: str = ""
        self._parse_param()

    def _parse_param(self):
        try:
            self.task_param_json_ = json.dumps(
                json.loads(base64_to_json(self.task_param_b64_).decode("utf-8"))
            )
            self.param_object_ = base64_json_to_object(self.task_param_b64_)

            self.map_param_: MapParam = (
                MapParam(self.param_object_.map)
                if hasattr(self.param_object_, "map")
                else None
            )
            self.runtime_param_: RunTimeParam = RunTimeParam(self.param_object_)
            self.case_info_param_: CaseInfoParam = (
                CaseInfoParam(self.param_object_.caseInfo)
                if hasattr(self.param_object_, "caseInfo")
                else None
            )
            self.vehicle_param_: VehicleParam = (
                VehicleParam(self.param_object_.vehicle)
                if hasattr(self.param_object_, "vehicle")
                else None
            )
            self.time_param_: TimeParam = (
                TimeParam(self.param_object_.caseInfo)
                if hasattr(self.param_object_, "caseInfo")
                else None
            )
            self.metric_params_: MetricsParam = (
                MetricsParam(self.param_object_.metric)
                if hasattr(self.param_object_, "metric")
                else None
            )
            self.resource_param_: ResourceParam = (
                ResourceParam(self.param_object_.resource)
                if hasattr(self.param_object_, "resource")
                else None
            )
            
            self.world_param_: WorldParam = WorldParam(self.param_object_)
            self.extend_param_: ExtendParam = ExtendParam(self.param_object_)
        except Exception as e:
            logger.info(f"parse param with error:{str(e)}")
            raise Exception("task param参数解析失败!")

    def __enter__(self):
        push_task_param_context(self.run_param.task_id)
        return self

    def __exit__(self, exc_type, exc_value, trace):
        if trace:
            raise Exception("task param load 失败!")
        pop_task_param_context()
        return self

    @property
    def map(self) -> MapParam:
        return self.map_param_

    @property
    def run_time(self) -> RunTimeParam:
        return self.runtime_param_

    @property
    def extend(self) -> ExtendParam:
        return self.extend_param_

    @property
    def case_info(self) -> CaseInfoParam:
        return self.case_info_param_

    @property
    def vehicle(self) -> VehicleParam:
        return self.vehicle_param_

    @property
    def time_info(self) -> TimeParam:
        return self.time_param_

    @property
    def metrics(self) -> MetricsParam:
        return self.metric_params_

    @property
    def resource(self) -> ResourceParam:
        return self.resource_param_
    
    @property
    def world_param(self) -> WorldParam:
        return self.world_param_
    
    @property
    def task_param_b64(self) -> bytes:
        return self.task_param_b64_
    
    @property
    def task_param_json(self) -> Dict:
        return self.task_param_json_
    
