import argparse
import json
from pathlib import Path
from string import Template

STORAGE_MODIFY_TEMPLATE = Template('data modify storage $namespace $key $action value $value')

def write_object(mc_file, key, json_dict, namespace):
    write_key_value(mc_file, key, json.dumps(json_dict), namespace, 'set')

def write_array(mc_file, key, value, namespace):
    write_key_value(mc_file, key, '[]', namespace, 'set')
    for val in value:
        # print(type(val))
        write_key_value(mc_file, key, val, namespace, 'append')


def write_key_value(mc_file, key, value, namespace, action):
    formatted_value = value
    if isinstance(value, dict):
        formatted_value = json.dumps(value)
    mc_file.write(STORAGE_MODIFY_TEMPLATE.substitute({'namespace': namespace, 'action': action, 'key':key, 'value':formatted_value}) + '\n')
    
def write(mc_file, key, value, namespace):
    if isinstance(value, dict):
        write_object(mc_file, key, value, namespace)
    elif isinstance(value, list):
        write_array(mc_file, key, value, namespace)
    else:
        write_key_value(mc_file, key, value, namespace, 'set')


def extant_file(potential_path: str):
    path = Path(potential_path)
    if path.exists and path.is_file:
        return path
    raise ValueError(potential_path + " does not exist")

def some_file(potential_path: str):
    return Path(potential_path)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('json_path', type=extant_file, help="Path to the JSON file to be translated into mcfunction files")
    parser.add_argument('mcfunction_path', type=some_file, help="Path to the .mcfunction file the json contents will be written to")
    parser.add_argument('--namespace', help='Minecraft storage namespace')
    return parser.parse_args()


def from_dict(json_dict: dict, mcfunction_path: Path, namespace: str):
    mcfunction_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mcfunction_path, 'w') as mc_file:
        print(f'Writing {mcfunction_path}')
        for key in json_dict:
            write(mc_file, key, json_dict[key], namespace)

def convert_files(json_path: Path, mcfunction_path: Path, namespace: str):
    with open(json_path, 'r') as json_file:
        json_dict = json.load(json_file)
        from_dict(json_dict, mcfunction_path, namespace)

if __name__ == "__main__":
    args = get_args()
    convert_files(args.json_path, args.mcfunction_path, args.namespace)