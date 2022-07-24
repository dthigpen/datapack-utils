import json
from pathlib import Path
from typing import List
from typing import Tuple

VERSION = '1.18'
DATA_PATH = Path(__file__).parent / '..' / '..' / 'minecraft-data' / 'data' / 'pc' / VERSION
ITEMS_PATH = DATA_PATH / 'items.json'
BLOCKS_PATH =  DATA_PATH / 'blocks.json'
RECIPES_PATH =  DATA_PATH / 'recipes.json'
FOODS_PATH =  DATA_PATH / 'foods.json'
ITEM_TAGS_PATH =   Path(__file__).parent / '..' / 'minecraft_jar' / 'data' / 'minecraft' / 'tags' / 'items'
BLOCK_TAGS_PATH =   Path(__file__).parent / '..' / 'minecraft_jar' / 'data' / 'minecraft' / 'tags' / 'blocks'

if not DATA_PATH.exists():
    raise ValueError(f'Minecraft data folder does not exist at {DATA_PATH}. Run unpack_jar.sh first')
else:
    if not RECIPES_PATH.exists():
        raise ValueError(f'Minecraft recipes resources do not exist at {RECIPES_PATH}.')
    if not ITEM_TAGS_PATH.exists():
        raise ValueError(f'Minecraft item tags resources do not exist at {ITEM_TAGS_PATH}.')
    if not BLOCK_TAGS_PATH.exists():
        raise ValueError(f'Minecraft item tags resources do not exist at {BLOCK_TAGS_PATH}.')
    if not ITEMS_PATH.exists():
        raise ValueError(f'Minecraft item list does not exist at {ITEMS_PATH}.')

def __read_json_file(json_path: Path):
    with open(json_path, 'r') as json_file:
        return json.load(json_file)
    return None

def __get_json_array_items(json_path: Path):
    for value in __read_json_file(json_path):
        yield value

def get_items():
    return __get_json_array_items(ITEMS_PATH)

# TODO refactor to be get_items_dict_by_id
def get_items_dict():
    return { item['id']: item for item in get_items() }

def get_items_dict_by_name():
    return { item['name']: item for item in get_items() }

def get_blocks():
    return __get_json_array_items(BLOCKS_PATH)

def get_recipes():
    for result,recipe in __read_json_file(RECIPES_PATH).items():
        yield (result,recipe)

# TODO refactor to be get_items_recipes_by_id
def get_recipes_dict():
    return __read_json_file(RECIPES_PATH)

def get_foods():
    return __get_json_array_items(FOODS_PATH)

def get_items_with_chars():
    num = 1
    leftmost_num = 'E'
    for item in get_items():
        item['char'] = f'\\u{leftmost_num}{str(num).zfill(3)}'
        yield item
        num += 1
        if num == 1000:
            leftmost_num = chr(ord(leftmost_num) + 1)
        num = num % 1000

def __get_values_for_tag(all_tags: list[dict], tag: dict):
    id_values = [value for value in tag["values"] if not value.startswith('#')]
    tag_values = [value for value in tag["values"] if value.startswith('#')]

    for value in tag_values:
        tag_name = value[len('#minecraft:'):]
        # print(f'tag_name: {tag_name}')
        tag = [t for t in all_tags if t['name'] == tag_name][0]
        id_values.extend(__get_values_for_tag(all_tags, tag))

    tag['values'] = id_values
    return id_values

def __get_tag_values_from_name(path: Path) -> set[str]:
    values = set()
    # print(f'reading: {path.stem}')

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

def get_tags_dict():
    return {tag['name']: tag['values'] for tag in get_tags()}
    
if __name__ == "__main__":
    providers = []
    for item in get_items_with_chars():
        
        providers.append({
            "type": "bitmap",
            "file": f"minecraft:items/{item['name']}.png",
            "ascent": 8,
            "height": 10,
            "chars": [item['char']]
        })
        # providers[-1]['chars'][0] = "\\" + providers[-1]['chars'][0]

    with open('items.json','w') as f:
        json.dump({"providers":providers}, f, indent=4)
        