import os
from pathlib import Path
import json
from .. import resources
from .. import resources

BLOCK_DIR = resources.MODELS_BLOCKS_PATH
ITEM_DIR = resources.MODELS_ITEMS_PATH
OUTPUT_DIR = Path('output')
OUTPUT_BLOCK_DIR =  OUTPUT_DIR / 'minecraft/assets/minecraft/models' / 'block'
OUTPUT_ITEM_DIR = OUTPUT_DIR / 'minecraft/assets/minecraft/models' / 'item'
ITEM_IDS = set(resources.get_items_dict_by_name().keys())
def ref_to_path(ref: str) -> Path:
    ref = ref.replace('minecraft:','')
    ref = ref + '.json'
    if ref.startswith('block/'):
        return BLOCK_DIR / ref[len('block/'):]
    if ref.startswith('item/'):
        return ITEM_DIR / ref[len('item/'):]
    raise ValueError(f'Unknown parent reference: {ref}')

def get_json(model_path: Path, recurse = True, replacements: dict = None):
        
    child_model = {}
    parent_model = {}

    if replacements is None:
        replacements = []
    
    with open(model_path, 'r') as f:
        content = f.read()
        # for find,replace in replacements:
        #     content = content.replace(find, replace)
        
        child_model = json.loads(content)

    if 'textures' in child_model:
        for texture_name, texture_value in child_model['textures'].items():
            replacements.append(('#' + texture_name, texture_value))
    
    if not recurse:
        return child_model

    if 'parent' in child_model and 'builtin' not in child_model['parent']:
        parent_model = get_json(ref_to_path(child_model['parent']), recurse=recurse, replacements=replacements)
        child_model.pop('parent')
        # parent_model.pop('textures', None)

        # if 'textures' in parent_model:
        #     parent_textures = parent_model['textures']
        #     new_textures = parent_textures.copy()
        #     if 'textures' in child_model:
        #         child_textures = child_model['textures']
        #         for parent_texture_name,parent_texture_value in parent_textures.items():
        #             if parent_texture_value[0] == '#':
        #                 if parent_texture_value[1:] in child_textures:
        #                     new_textures[parent_texture_name] = child_textures[parent_texture_value[1:]]
                            # if 'elements' in parent_model:
                                # for element in parent_model['elements']:
                                #     for face_name, face_value in element['faces'].items():
        #                                 if face_value['texture'] == parent_texture_value:
        #                                     face_value['texture'] = child_textures[parent_texture_value[1:]]

            # parent_model['textures'] = new_textures    

        # textures = model_dict['textures']
    updated_child_model = parent_model | child_model
    content = json.dumps(updated_child_model)
    # print(replacements)
    for find,replace in replacements:
            content = content.replace(find, replace)
    
    updated_child_model = json.loads(content)

    if 'elements' in updated_child_model:
        for element in updated_child_model['elements']:
            for face_name, face_value in element['faces'].items():
                if 'textures' not in updated_child_model:
                    updated_child_model['textures'] = {}
                updated_child_model['textures'][face_name] = face_value['texture']
    
    return updated_child_model

        

def write_json(json_dict: dict, path: Path):
    with open(path, 'w') as f:
        json.dump(json_dict, f, indent=4)

def is_leaf_model(model: dict) -> bool:
    if 'textures' in model:
        for _,value in model['textures'].items():
            if value[0] == '#':
                return False
    return True

def is_valid_model(model_path: Path):
    if model_path.stem in ITEM_IDS:
        json_dict = get_json(model_path, recurse=False)
        if is_leaf_model(json_dict):
            return True
    return False

def run():
    print('Generating')
    os.makedirs(OUTPUT_BLOCK_DIR, exist_ok=True)
    os.makedirs(OUTPUT_ITEM_DIR, exist_ok=True)
    
    # print(item_ids[0])
    for model_path in BLOCK_DIR.iterdir():
        
        if is_valid_model(model_path):
            json_dict = get_json(model_path, recurse=False)
            # print(f'Handling {model_path}')
            json_dict = get_json(model_path)
            
            output_dir = OUTPUT_BLOCK_DIR if 'models/block' in str(model_path) else OUTPUT_ITEM_DIR
            full_output_path = output_dir / model_path.name
            write_json(json_dict, full_output_path)

    for model_path in ITEM_DIR.iterdir():
        
        if is_valid_model(model_path):
            json_dict = get_json(model_path, recurse=False)
            # print(f'Handling {model_path}')
            json_dict = get_json(model_path)
            
            output_dir = OUTPUT_BLOCK_DIR if 'models/block' in str(model_path) else OUTPUT_ITEM_DIR
            full_output_path = output_dir / model_path.name
            write_json(json_dict, full_output_path)

# def _get_item_dict_by_file_name(file_name: str) -> dict:
#     with open(ITEM_TAGS_PATH / (f'{file_name}.json'), 'r') as json_file:
#         return json.load(json_file)
#     return None

# def _get_path_to_json_dicts(path: Path) -> Tuple[str,dict]:
#     for file_path in path.glob('*.json'):
#         with open(file_path, 'r') as json_file:
#             yield (file_path, json.load(json_file))

# def _get_item_tags() -> Tuple[str,dict]:
#     return _get_path_to_json_dicts(ITEM_TAGS_PATH)

# def _get_all_recipes() -> Tuple[str,dict]:
#     for recipe_path in RECIPES_PATH.glob('*.json'):
#         with open(recipe_path, 'r') as tag_file:
#             yield ( recipe_path, json.loads(tag_file.read()))

# def _get_unique_result_recipes():
#     all_items = set()
#     count = 0
#     for _, recipe_dict in _get_all_recipes():
#         if 'result' in recipe_dict:
#             result = recipe_dict["result"] if isinstance(
#             recipe_dict["result"], str) else recipe_dict["result"]["item"]
#             if not result in all_items:
#                 count+=1
#                 all_items.add(result)
#                 yield result

# def _get_unique_result_recipes_new():
#     all_items = set()
#     count = 0
#     for _, recipe_dict in _get_all_recipes():
#         if 'result' in recipe_dict:
#             result = recipe_dict["result"] if isinstance(
#             recipe_dict["result"], str) else recipe_dict["result"]["item"]
#             if not result in all_items:
#                 count+=1
#                 all_items.add(result)
#                 yield result
    
