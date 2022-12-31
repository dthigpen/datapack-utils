import json
from pathlib import Path
import minecraft_data
MCD = minecraft_data('1.19')

# From the mcmeta submodule
DATA_PATH = Path(__file__).parent / '..' / 'mcmeta' / 'data'
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

# data check
path_exists(DATA_PATH)
path_exists(RECIPES_PATH)
path_exists(ITEM_TAGS_PATH)
path_exists(BLOCK_TAGS_PATH)
# assets check
# path_exists(ASSETS_PATH)
# path_exists(MODELS_ITEMS_PATH)
# path_exists(MODELS_BLOCKS_PATH)



def __get_tag_values_from_name(path: Path) -> set[str]:
    values = set()
    if path.exists():
        with open(path,'r') as json_file:
            json_dict = json.load(json_file)
            for value in json_dict['values']:
                if value.startswith('#'):
                    file_name = value[len('#minecraft:'):] + '.json'
                    values = values.union(__get_tag_values_from_name(ITEM_TAGS_PATH / file_name))
                    values.union(__get_tag_values_from_name(BLOCK_TAGS_PATH / file_name))
                else:
                    values.add(value)
    else:
        # print(f'Nothing found matching {path}')
        pass
    # print(f'read: {path.stem}')
    # print(values)
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