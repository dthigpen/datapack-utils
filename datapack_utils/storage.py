import json
from pathlib import Path
from string import Template
from typing import List
from typing import Tuple

STORAGE_MODIFY_TEMPLATE = Template('data modify storage $namespace $key $action value $value')

def __format_value(value) -> str:
    return json.dumps(value).replace('[[[', '[ [ [').replace(']]]','] ] ]')

def set_array(namespace: str, key: str, values):
    yield STORAGE_MODIFY_TEMPLATE.substitute({'namespace': namespace, 'action': 'set', 'key':key, 'value':'[]'})
    for value in values:
        formatted_value = __format_value(value)
        yield STORAGE_MODIFY_TEMPLATE.substitute({'namespace': namespace, 'action': 'append', 'key':key, 'value':formatted_value})

def set_value(namespace: str, key: str, value):
    return STORAGE_MODIFY_TEMPLATE.substitute({'namespace': namespace, 'action': 'set', 'key':key, 'value':__format_value(value)})