import json
from pathlib import Path
import minecraft_data
MCD = minecraft_data('1.19')
from importlib import resources as impresources
from .data import mcmeta
from .data import minecraft_assets

DATA_PATH = impresources.files(mcmeta) / 'data'
RECIPES_PATH =  DATA_PATH / 'minecraft' / 'recipes'
ITEM_TAGS_PATH =  DATA_PATH / 'minecraft' / 'tags' / 'items'
BLOCK_TAGS_PATH =  DATA_PATH / 'minecraft' / 'tags' / 'blocks'

# From the minecraft-assets submodule
# TODO look into why not all models do not exist in submodule
ASSETS_PATH =  Path(__file__).parent / '..' / 'minecraft-assets' / 'assets'
MODELS_PATH = ASSETS_PATH / 'minecraft' / 'models'
MODELS_ITEMS_PATH = MODELS_PATH / 'item'
MODELS_BLOCKS_PATH = MODELS_PATH / 'block'

def path_exists(path: Path):
    if not path.exists():
        ValueError(f'{path} does not exist. Please ensure all submodules are cloned and on the correct tag/branch')



def __get_tag_values_from_name(path: Path) -> set[str]:
    values = set()
    with path.open('r') as json_file:
        json_dict = json.load(json_file)
        for value in json_dict['values']:
            if value.startswith('#'):
                file_name = value[len('#minecraft:'):] + '.json'
                if (item_tag := ITEM_TAGS_PATH / file_name).is_file():
                    value = values.union(__get_tag_values_from_name(item_tag))
                if (block_tag := BLOCK_TAGS_PATH / file_name).is_file():
                    values = values.union(__get_tag_values_from_name(block_tag))
            else:
                values.add(value)
    
    return values

def get_tags(strip_namespace=False):
    tags = []
    paths = [p for p in ITEM_TAGS_PATH.iterdir() if p.is_file()]
    paths.extend([p for p in BLOCK_TAGS_PATH.iterdir() if p.is_file()])
    for path in paths:
        values = __get_tag_values_from_name(path)
        tag = {"name":path.stem, "values": [value[len('minecraft:'):] if strip_namespace else value for value in values]}
        tag['values'].sort()
        tags.append(tag)

    return tags

def get_items():
    return [MCD.find_item_or_block(i) for i in MCD.items]

# TODO refactor to be get_items_dict_by_id
def get_items_dict() -> dict:
    return { item['id']: item for item in get_items() }

def get_items_dict_by_name() -> dict:
    return { item['name']: item for item in get_items() }

# TODO refactor to be get_items_recipes_by_id
def get_recipes_dict() -> dict:
    return MCD.recipes

def get_tags_dict() -> dict:
    return {tag['name']: tag['values'] for tag in get_tags()}