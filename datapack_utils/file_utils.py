import argparse
import json
from pathlib import Path
import sys
import os

try:
    import cog
except:
    pass

def dump_json(json_dict, path):
    json.dump(json_dict, open(get_current_dir() / Path(path),'w'), indent = 4)


def path_to_function_call(path: Path) -> str:
    relevant_parts = list(path.parts[path.parts.index('data') + 1:])
    namespace = relevant_parts.pop(0)
    relevant_parts.pop(0) # functions
    relevant_parts.pop() # last
    relevant_parts.append(path.stem)
    return f'{namespace}:{"/".join(relevant_parts)}'


def get_current_dir(override_dir=None):
    if 'cog' in sys.modules:
        return Path(cog.inFile).parent
    elif override_dir:
        return Path(override_dir)
    else:
        # raise Exception('Must provide an override dir if not in cog context')
        return Path(os.getcwd())

def write_file_dict(path: Path, json_dict: dict):
    if json_dict['name'].endswith('.mcfunction'):
        new_path = path / json_dict['name'].replace('-','n')
    else:
        new_path = path / json_dict['name']
    # print(f'writing {new_path}')
    if json_dict['type'] == 'directory':
        os.makedirs(new_path)
        for item in json_dict['contents']:
            write_file_dict(new_path, item)
    elif json_dict['type'] == 'file':
        if new_path.exists():
            print(f'warning: {new_path} already exists')
            # raise ValueError(f'{new_path} already exists')
        with open(new_path, 'w') as f:
            # cog.msg(f'Writing to {new_path}')
            f.writelines((l + '\n' for l in json_dict.get('contents', [])))
