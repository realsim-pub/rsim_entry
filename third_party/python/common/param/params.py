import json
import os

from enum import Enum, IntEnum
from typing import List, Optional
from dataclasses import dataclass, field
from venv import logger

from third_party.python.common.string2object import deep_convert_dict

class RunType(Enum):
    PDC = "thousands_pdc"
    FULL = "thousands_full"
    HIL = "rsim_hil"
    CUSTOM_RUNNER = "custom_runner"
    UNDEDINED = "undefined"

class TimeParam(object):
    def __init__(self, time_param: object) -> None:
        self.sim_time_: Optional[int] = (
            int(time_param.simTimeStamp)
            if hasattr(time_param, "simTimeStamp")
            else None
        )
        self.start_time_: Optional[int] = (
            int(time_param.startTimestamp)
            if hasattr(time_param, "startTimestamp")
            else None
        )
        self.event_time_: Optional[int] = (
            int(time_param.eventTimeStamp)
            if hasattr(time_param, "eventTimeStamp")
            else None
        )
        self.end_time_: Optional[int] = (
            int(time_param.endTimestamp)
            if hasattr(time_param, "endTimestamp")
            else None
        )

    @property
    def sim_time(self) -> int:
        return self.sim_time_

    @property
    def start_time(self) -> int:
        return self.start_time_

    @property
    def event_time(self) -> int:
        return self.event_time_

    @property
    def end_time(self) -> int:
        return self.end_time_

class CaseInfoParam(object):
    def __init__(self, case_info: object) -> None:
        self.case_type_: str = (
            case_info.caseType if hasattr(case_info, "caseType") else ""
        )
        self.case_name_: str = (
            case_info.caseName if hasattr(case_info, "caseName") else ""
        )
        self.case_id_: int = case_info.caseId if hasattr(case_info, "caseId") else None
        self.usr_defined_label_: str = (
            case_info.userDefinedLabel if hasattr(case_info, "userDefinedLabel") else ""
        )
        self.scenario_url_: str = (
            case_info.scenarioUrl if hasattr(case_info, "scenarioUrl") else ""
        )

        self.scenario_md5_: str = (
            case_info.scenarioMd5 if hasattr(case_info, "scenarioMd5") else ""
        )

    @property
    def case_type(self) -> str:
        return self.case_type_

    @property
    def case_name(self) -> str:
        return self.case_name_

    @property
    def case_id(self) -> int:
        return self.case_id_

    @property
    def usr_defined_label(self) -> str:
        return self.usr_defined_label_

    @property
    def scenario_url(self) -> str:
        return self.scenario_url_
    
    @property
    def scenario_md5(self) -> str:
        return self.scenario_md5_

class MapParam(object):
    def __init__(self, map_param: object) -> None:
        self.map_id_: int = map_param.mapId if hasattr(map_param, "mapId") else None
        self.map_md5_: int = map_param.mapMd5 if hasattr(map_param, "mapMd5") else None
        self.map_scene_: str = (
            map_param.mapScene if hasattr(map_param, "mapScene") else ""
        )
        self.map_url_: str = map_param.mapUrl if hasattr(map_param, "mapUrl") else ""
        self.map_version_: str = (
            map_param.mapVersion if hasattr(map_param, "mapVersion") else ""
        )
        self.offset_z_: float = (
            map_param.offsetZ if hasattr(map_param, "offsetZ") else None
        )
        self.world_name_: str = map_param.worldName if hasattr(map_param, "worldName") else self.map_scene_
        
    @property
    def map_id(self) -> int:
        return self.map_id_

    @property
    def map_md5(self) -> int:
        return self.map_md5_

    @property
    def name(self) -> str:
        return self.map_scene_
    
    @property
    def world_name(self) -> str:
        return self.world_name_

    @property
    def map_url(self) -> str:
        return self.map_url_

    @property
    def map_version(self) -> str:
        return self.map_version_

    @property
    def offset_z(self) -> float:
        return self.offset_z_

class VehicleParam(object):
    def __init__(self, vehicle_param: object) -> None:
        self.vehicle_type_: str = (
            vehicle_param.vehicleType if hasattr(vehicle_param, "vehicleType") else ""
        )
        self.vehicle_model_: str = (
            vehicle_param.vehicleModel if hasattr(vehicle_param, "vehicleModel") else ""
        )
        self.dynamic_file_url_: str = (
            vehicle_param.dynamicFileUrl if hasattr(vehicle_param, "dynamicFileUrl") else ""
        )
        self.dynamic_file_md5_: str = (
            vehicle_param.dynamicFileMd5 if hasattr(vehicle_param, "dynamicFileMd5") else ""
        )
        self.blueprint_: str = (
            vehicle_param.blueprint if hasattr(vehicle_param, "blueprint") else ""
        )
        self.config_ = deep_convert_dict(vehicle_param.config) if hasattr(vehicle_param, "config") else None
        self.width_: Optional[int] = None
        self.length_: Optional[int] = None
        self.height_: Optional[int] = None
        
        self._parse_vehicle_param()
    
    def _parse_vehicle_param(self):
        if not self.config_:
            return

        self.width_ = self.config_.width if hasattr(self.config_, "width") else ""
        self.length_ = self.config_.length if hasattr(self.config_, "length") else ""
        self.height_ = self.config_.height if hasattr(self.config_, "height") else ""

    @property
    def vehicle_type(self) -> str:
        return self.vehicle_type_

    @property
    def vehicle_model(self) -> str:
        return self.vehicle_model_
    
    @property
    def dynamic_file_url(self) -> str:
        return self.dynamic_file_url_
    
    @property
    def dynamic_file_md5(self) -> str:
        return self.dynamic_file_md5_

    @property
    def blueprint(self) -> str:
        return self.blueprint_
    
    @property
    def config(self) -> dict:
        return self.config_
    
    @property
    def width(self) -> float:
        return self.width_
    
    @property
    def height(self) -> float:
        return self.height_
    
    @property
    def length(self) -> float:
        return self.length_

    # @config.setter
    # def config(self, value: dict) -> None:
    #     self.config_ = value

class MultiEgoInfo(object):
     def __init__(self, ego_name: str, ego_image_tag: str):
         self._ego_name:str = ego_name
         self._ego_image_tag: str = ego_image_tag
    
     @property
     def ego_name(self) -> str:
        return self._ego_name
     
     @property
     def ego_image_tag(self) -> str:
         return self._ego_image_tag

class SensorDeployment(object):
    def __init__(self, 
                 sensor_id: str, 
                 render_ip: str, 
                 render_host_name: str, 
                 device_address: str,
                 render_gpu_card_num: int, 
                 render_group_id: int):
        self._sensor_id: str = sensor_id
        self._render_ip: str = render_ip
        self._render_host_name: str = render_host_name
        self._device_address: str = device_address
        self._render_gpu_card_num: int = render_gpu_card_num
        self._render_group_id: int = render_group_id
    
    @property
    def sensor_id(self) -> str:
        return self._sensor_id
    
    @property
    def render_ip(self) -> str:
        return self._render_ip
    
    @property
    def render_host_name(self) -> str:
        return self._render_host_name
    
    @property
    def device_address(self) -> str:
        return self._device_address

    @property
    def render_gpu_card_num(self) -> int:
        return self._render_gpu_card_num

    @property
    def render_group_id(self) -> int:
        return self._render_group_id 

class RunTimeParam(object):
    def __init__(self, param_object: object) -> None:
        run_time = param_object.runtime if hasattr(param_object, "runtime") else None
        self._run_env: str = run_time.runEnv if run_time else ""
        self._run_type: RunType = self._convert_runtype(run_time.runType) if run_time else ""
        self._task_id: Optional[int] = param_object.taskId if hasattr(param_object, "taskId") else None
        self._run_identity: Optional[int] = param_object.runIdentity if hasattr(param_object, "runIdentity") else None
        self._server_port: Optional[int] = param_object.serverPort if hasattr(param_object, "serverPort") else None
        self._server_ip: Optional[str] = param_object.serverIp if hasattr(param_object, "serverIp") else None
        self._sim_image: str = run_time.simImage if run_time and hasattr(run_time, "simImage") else ""
        self._testobject_image: str = run_time.testobjectImage if run_time and hasattr(run_time, "testobjectImage") else ""
        self._is_multi_ego: bool = run_time.isMultiEgos if run_time and hasattr(run_time, "isMultiEgos") else ""
        self._multi_ego_infos: List = self._init_multi_egos(run_time.multiEgoInfos if run_time and hasattr(run_time, "multiEgoInfos") else [])
        self._sensor_deployments: List[SensorDeployment] = self._init_sensor_deployments(run_time.sensorDeployments if run_time and hasattr(run_time, "sensorDeployments") else "")
        self._output_dir: str = (
            param_object.containerOutputPath if hasattr(param_object, "containerOutputPath") else "/tmp"
        )
    
    def _init_multi_egos(self, multi_ego_infos: List) -> List[MultiEgoInfo]:
        ego_infos: List[MultiEgoInfo] = []
        for ego_info in multi_ego_infos:
            new_ego_info = MultiEgoInfo(ego_name=ego_info.name if hasattr(ego_info, "name") else "",
                                        ego_image_tag=ego_info.tag if hasattr(ego_info, "tag") else "")
            ego_infos.append(new_ego_info)
        return ego_infos 
    
    def _init_sensor_deployments(self, sensor_deployments_str: str) -> List[SensorDeployment]:
        if sensor_deployments_str == "":
            return []
        
        sensor_deployments: List = []
        try:
            sensor_deployments = json.loads(sensor_deployments_str)
        except Exception as e:
            logger.error(f"load sensor deployments with error:{str(e)}")

        deployments: List[SensorDeployment] = []
        for deployment in sensor_deployments:
            new_deploy = SensorDeployment(sensor_id=deployment.get("sensor_id", ""),
                                          render_ip=deployment.get("render_ip", ""),
                                          render_host_name=deployment.get("render_host_name", ""),
                                          device_address=deployment.get("device_address", ""),
                                          render_gpu_card_num=deployment.get("render_gpu_card_num", 0),
                                          render_group_id=deployment.get("render_group_id", 0))
            deployments.append(new_deploy)
        return deployments
    
    @property
    def is_multi_ego(self) -> bool:
        return self._is_multi_ego
    
    @property
    def multi_ego_infos(self) -> List[MultiEgoInfo]:
        return self._multi_ego_infos
    
    @property
    def sensor_deployments(self) -> List[SensorDeployment]:
        return self._sensor_deployments
        
    @property
    def task_id(self) -> int:
        return self._task_id
    
    @property
    def run_identity(self) -> int:
        return self._run_identity

    @property
    def run_env(self) -> str:
        return self._run_env

    @property
    def run_type(self) -> RunType:
        return self._run_type
    
    @property
    def server_port(self) -> int:
        return self._server_port

    @property
    def server_ip(self) -> str:
        return self._server_ip
    
    @property
    def sim_image(self) -> str:
        return self._sim_image
    
    @property
    def testobject_image(self) -> str:
        return self._testobject_image

    @property
    def output_dir(self) -> str:
        return self._output_dir

    @property
    def log_dir(self) -> str:
        return os.path.join(self._output_dir, "logs")
    
    @property
    def view_dir(self) -> str:
        return os.path.join(self._output_dir, "realview")
    
    def _convert_runtype(self, runtype: str):
        try:
            return RunType(runtype)
        except Exception:
            return RunType.UNDEDINED

class MetricType(IntEnum):
    OFFICIAL = 0
    CUSTOM = 1
    NONE = 3

class ExtendParam(object):
    def __init__(self, param_object: object):
        extend = param_object.extend if hasattr(param_object, "extend") else None
        self._run_step: float = extend.runStep if extend and hasattr(extend, "runStep") else 0.01
        self._run_frame_count: float = extend.runFrameCount if extend and hasattr(extend, "runFrameCount") else 100

    @property
    def run_step(self) -> float:
        return self._run_step
    
    @property
    def run_frame_count(self) -> float:
        return self._run_frame_count

class WorldParam(object):
    def __init__(self, param_object: object):
        run_time = param_object.runtime if hasattr(param_object, "runtime") else None
        multi_egos = run_time.multiEgos if run_time and hasattr(run_time, "multiEgos") else None
        
        self._world_ip: Optional[str] = multi_egos.worldIp if multi_egos and hasattr(multi_egos, "worldIp") else ""
        self._world_port: Optional[int] = multi_egos.worlpPort if multi_egos and hasattr(multi_egos, "worlpPort") else 0
        self._world_ego_id: Optional[str] = multi_egos.worldEgoId if multi_egos and hasattr(multi_egos, "worldEgoId") else ""
        self._ego_id: Optional[str] = multi_egos.egoId if multi_egos and hasattr(multi_egos, "egoId") else ""
    
    @property
    def world_ip(self) -> Optional[str]:
        return self._world_ip
    
    @property
    def world_port(self) -> Optional[int]:
        return self._world_port
    
    @property
    def world_ego_id(self) -> Optional[str]:
        return self._world_ego_id
    
    @property
    def ego_id(self) -> Optional[str]:
        return self._ego_id 
    
class MetricParam(object):
    def __init__(self, metric_param: object) -> None:
        self.md5_: int = metric_param.md5 if hasattr(metric_param, "md5") else None
        self.name_: str = metric_param.name if hasattr(metric_param, "name") else ""
        self.uuid_: int = metric_param.uuid if hasattr(metric_param, "uuid") else None
        self.url_: str = metric_param.url if hasattr(metric_param, "url") else ""
        self.type_: MetricType = self._type_map(
            metric_param.type if hasattr(metric_param, "type") else ""
        )
        self.metrics_: List[str] = (
            metric_param.metrics if hasattr(metric_param, "metrics") else []
        )

    def _type_map(self, type: str) -> MetricType:
        if type == "official":
            return MetricType.OFFICIAL
        elif type == "custom":
            return MetricType.CUSTOM
        else:
            return MetricType.NONE

    @property
    def md5(self) -> int:
        return self.md5_

    @property
    def name(self) -> str:
        return self.name_

    @property
    def uuid(self) -> int:
        return self.uuid_

    @property
    def url(self) -> str:
        return self.url_

    @property
    def type(self) -> MetricType:
        return self.type_

    @property
    def metrics(self) -> List[str]:
        return self.metrics_
class MetricsParam(object):
    def __init__(self, metrics_param: object) -> None:
        self.metrics_: List[MetricParam] = [
            MetricParam(item) for item in metrics_param.metrics
        ]
    
    @property
    def metrics(self) -> List[MetricParam]:
        return self.metrics_
class ResourceParam(object):
    def __init__(self, resource_param: object) -> None:
        self._map_dir: str = (
            resource_param.map_dir if hasattr(resource_param, "map_dir") else ""
        )
        self._map_name: str = (
            resource_param.map_name if hasattr(resource_param, "map_name") else ""
        )
        self._scenario_file: str = (
            resource_param.scenario_file
            if hasattr(resource_param, "scenario_file")
            else ""
        )
        self._vehicle_conf_dir: str = (
            resource_param.vehicle_conf_dir
            if hasattr(resource_param, "vehicle_conf_dir")
            else ""
        )
        self._sensor_conf: str = (
            resource_param.sensor_conf if hasattr(resource_param, "sensor_conf") else ""
        )

    @property
    def map_dir(self) -> str:
        return self._map_dir
    
    @map_dir.setter
    def map_dir(self, value) -> None:
        self._map_dir = value
    
    @property
    def map_name(self) -> str:
        return self._map_name
    
    @property
    def map_file(self) -> str:
        return self.map_dir

    @property
    def scenario_file(self) -> str:
        return self._scenario_file
    
    @scenario_file.setter
    def scenario_file(self, value: str) -> None:
        self._scenario_file = value

    @property
    def vehicle_conf_dir(self) -> str:
        return self._vehicle_conf_dir

    @vehicle_conf_dir.setter
    def vehicle_conf_dir(self, value) -> None:
        self._vehicle_conf_dir = value

    @property
    def sensor_conf(self) -> str:
        return self._sensor_conf
    
    def __dict__(self):
        return {
            "map_dir": self._map_dir,
            "scenario_file": self._scenario_file,
            "vehicle_conf_dir": self._vehicle_conf_dir,
            "sensor_conf": self._sensor_conf,
        }
