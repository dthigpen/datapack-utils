import json
from pathlib import Path
from typing import List
from typing import Tuple
import os
import sys
from . import minecraft_data

DATA_PATH = Path(__file__).parent / '..' / 'minecraft_jar' / 'data'
RECIPES_PATH =  DATA_PATH / 'minecraft' / 'recipes'
ITEM_TAGS_PATH =  DATA_PATH / 'minecraft' / 'tags' / 'items'
ITEMS_PATH = DATA_PATH / 'items.txt'
ASSETS_PATH =  Path(__file__).parent / '..' / 'minecraft_jar' / 'assets'
MODELS_PATH = ASSETS_PATH / 'minecraft' / 'models'
MODELS_ITEMS_PATH = MODELS_PATH / 'item'
MODELS_BLOCKS_PATH = MODELS_PATH / 'block'

if not DATA_PATH.exists():
    raise ValueError(f'Minecraft data folder does not exist at {DATA_PATH}. Run unpack_jar.sh first')
else:
    if not RECIPES_PATH.exists():
        raise ValueError(f'Minecraft recipes resources do not exist at {RECIPES_PATH}.')
    if not ITEM_TAGS_PATH.exists():
        raise ValueError(f'Minecraft item tags resources do not exist at {ITEMS_PATH}.')
    if not ITEMS_PATH.exists():
        with open(ITEMS_PATH,'w') as f:
            for i in minecraft_data.get_items():
                f.write(f'mineraft:{i["name"]}\n')
        if not ITEMS_PATH.exists():
            raise ValueError(f'Minecraft item list does not exist at {ITEMS_PATH}.')
    

def get_item_dict_by_file_name(file_name: str) -> dict:
    with open(ITEM_TAGS_PATH / (f'{file_name}.json'), 'r') as json_file:
        return json.load(json_file)
    return None

def get_path_to_json_dicts(path: Path) -> Tuple[str,dict]:
    for file_path in path.glob('*.json'):
        with open(file_path, 'r') as json_file:
            yield (file_path, json.load(json_file))

def get_item_tags() -> Tuple[str,dict]:
    return get_path_to_json_dicts(ITEM_TAGS_PATH)

def get_all_recipes() -> Tuple[str,dict]:
    for recipe_path in RECIPES_PATH.glob('*.json'):
        with open(recipe_path, 'r') as tag_file:
            yield ( recipe_path, json.loads(tag_file.read()))

def get_unique_result_recipes():
    all_items = set()
    count = 0
    for _, recipe_dict in get_all_recipes():
        if 'result' in recipe_dict:
            result = recipe_dict["result"] if isinstance(
            recipe_dict["result"], str) else recipe_dict["result"]["item"]
            if not result in all_items:
                count+=1
                all_items.add(result)
                yield result

def get_unique_result_recipes_new():
    all_items = set()
    count = 0
    for _, recipe_dict in get_all_recipes():
        if 'result' in recipe_dict:
            result = recipe_dict["result"] if isinstance(
            recipe_dict["result"], str) else recipe_dict["result"]["item"]
            if not result in all_items:
                count+=1
                all_items.add(result)
                yield result
    
def get_items(strip_prefix=False) -> List[str]:
    all_items = []
    with open(ITEMS_PATH, 'r') as items_file:
        for item in items_file.readlines():
            all_items.append(item.strip()[len('minecraft:'):] if strip_prefix else item.strip())
    return all_items

def path_exists(path: Path):
    if not path.exists():
        raise ValueError(f'Minecraft data resources do not exist at {path}')


def get_script_path():
    return Path(os.path.realpath(__file__)).parent

def generate_recipe_tree_resources():
    from . import recipes
    json.dump(recipes.build_recipe_tree(include_shapeless=False),open(get_script_path() / 'resources/shaped_recipes_by_ingredient.json','w'), indent=2, sort_keys=False)
    json.dump(recipes.build_recipe_tree(include_shaped=False),open(get_script_path() / 'resources/shapeless_recipes_by_ingredient.json','w'), indent=2, sort_keys=False)

