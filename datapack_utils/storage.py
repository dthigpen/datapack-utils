import json
from pathlib import Path
from string import Template
from typing import List
from typing import Tuple

STORAGE_MODIFY_TEMPLATE = Template('data modify storage $namespace $key $action value $value')

def write_object(key, json_dict, namespace):
    return write_key_value(key, json.dumps(json_dict), namespace, 'set')

def write_array(key, value, namespace):
    write_key_value(key, '[]', namespace, 'set')
    # for val in value:
    #     # print(type(val))
    #     yield write_key_value(key, val, namespace, 'append')
    return '\n'.join([write_key_value(key, val, namespace, 'append') for val in value])

def write_key_value(key, value, namespace, action):
    formatted_value = value
    if isinstance(value, dict):
        formatted_value = json.dumps(value)
    return STORAGE_MODIFY_TEMPLATE.substitute({'namespace': namespace, 'action': action, 'key':key, 'value':formatted_value})
    
def write(key, value, namespace):
    if isinstance(value, dict):
        return write_object(key, value, namespace)
    elif isinstance(value, list):
        return write_array(key, value, namespace)
    else:
        return write_key_value(key, value, namespace, 'set')

def from_dict(json_dict: dict, namespace: str):
    for key in json_dict:
        yield write(key, json_dict[key], namespace)