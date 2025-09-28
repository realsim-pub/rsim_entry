#!/usr/bin python
# -*- coding: UTF-8 -*-


import json
import base64

from dataclasses import fields
from collections import namedtuple, OrderedDict

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())

def b64_to_dict(b64_str): return json.loads(base64_to_json(b64_str))
def base64_to_json(b64_str): return base64.b64decode(b64_str)
def base64_json_to_object(str): return json_string_to_object(base64.b64decode(str))
def json_str_to_dict(json_str): return json.loads(json_str)
def json_string_to_object(json_str): return json.loads(json_str, object_hook=_json_object_hook) if json_str else None
def dict_to_object(input_dict): return json.loads(json.dumps(input_dict), object_hook=_json_object_hook) if input_dict else None

def deep_convert_dict(layer):
    to_ret = layer
    if isinstance(layer, OrderedDict):
        to_ret = dict(layer)
    elif hasattr(layer, "__dict__"):
        to_ret = dict(layer.__dict__)
    try:
        for key, value in to_ret.items():
            if isinstance(value, tuple):
                try:
                    to_ret[key] = deep_convert_dict(value._asdict())
                except:
                    pass
            elif isinstance(value, list):
                to_ret[key] = []
                for v in value:
                    try:
                        to_ret[key].append(deep_convert_dict(v._asdict()))
                    except:
                        to_ret[key].append(deep_convert_dict(v))
            else:
                to_ret[key] = deep_convert_dict(value)
    except AttributeError:
        pass
    if isinstance(layer, list):
        to_ret = []
        for v in layer:
            try:
                to_ret.append(deep_convert_dict(v._asdict()))
            except:
                to_ret.append(deep_convert_dict(v))
    return to_ret

def dict_to_dataclass(dataclass_type, dict_obj):
    field_names = {f.name for f in fields(dataclass_type)}
    filtered_dict = {key: value for key, value in dict_obj.items() if key in field_names}
    return dataclass_type(**filtered_dict)