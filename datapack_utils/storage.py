import json
from string import Template

STORAGE_MODIFY_TEMPLATE = Template('data modify storage $namespace $key $action value $value')

def _format_value(value) -> str:
    return json.dumps(value).replace('[[[', '[ [ [').replace(']]]','] ] ]')

def modify_storage(namespace: str, key: str, action, value):
    return STORAGE_MODIFY_TEMPLATE.substitute({'namespace': namespace, 'action': action, 'key':key, 'value':value})

def set_string_value(namespace: str, key: str, str_value):
    return modify_storage(namespace, key, 'set', str_value)

def append_string_value(namespace: str, key: str, str_value):
    return modify_storage(namespace, key, 'append', str_value)

def append_value(namespace: str, key: str, value):
    return append_string_value(namespace, key, _format_value(value))
    
def set_value(namespace: str, key: str, value, split=False):
    if split:
        if isinstance(value, dict):
            return set_dict(namespace, key, value)
        elif isinstance(value, list):
            return set_array(namespace, key, value)
    return set_string_value(namespace, key, _format_value(value))

def set_dict(namespace: str, key: str, values):
    yield set_value(namespace, key, {})
    for subkey,value in values.items():
        yield set_value(namespace, f'{key}.{subkey}', value)

def set_array(namespace: str, key: str, values):
    yield set_value(namespace, key, [])
    for value in values:
        yield append_value(namespace, key, value)