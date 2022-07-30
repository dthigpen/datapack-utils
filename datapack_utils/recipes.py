import json
from collections import Counter
from collections import defaultdict
from pathlib import Path
from string import Template
from typing import List
from typing import Tuple
import copy
import itertools

from . import resources


def __create_storage_tree(data_list: list, operations: list) -> dict:
    current_tree = defaultdict(lambda: [])
    if not operations:
        return data_list
    
    operation = operations[0]
    for data in data_list:
        key = operation(data)
        current_tree[key].append(data)

    for key in current_tree:
        current_tree[key] = __create_storage_tree(current_tree[key], operations[1:])
            
    return dict(current_tree)

# def __get_unique_ingredient_count(recipe_json: dict) -> int:
#     return len(recipe_json['ingredients'])

def get_recipes():
    recipes = []
    items_dict = resources.get_items_dict()
    for _,recipe_variants in resources.get_recipes_dict().items():
        # if recipe_variants[0]['result']['id'] != 1079:
        #     continue
        # print(f"Creating {recipe_variants[0]['result']['id']}")
        merged_shaped_recipe = {"items":[],"slots":[],"result":[],"shapeless": 0}
        merged_shapeless_recipe = {"items":[[]],"slots":[],"result":[],"shapeless": 1}
        for variant in recipe_variants:
            # print(variant)
            name = items_dict[variant['result']['id']]['name']
            # print(variant)
            row_index = 0
            temp_slots = []

            if 'inShape' in variant:
                merged_shaped_recipe['shapeless'] = 0
                merged_shaped_recipe['name'] = name
                if not merged_shaped_recipe['result']:
                    merged_shaped_recipe['result'] = [variant['result']['id'],variant['result']['count']]
                merged_rows = merged_shaped_recipe['items']

                for row in variant['inShape']:
                    
                    if row_index == len(merged_shaped_recipe['slots']):
                        row_slots = [1 if i is not None else 0 for i in row]
                        merged_shaped_recipe['slots'].append(row_slots)

                    if row_index == len(merged_rows):
                        merged_rows.append([])
                    col_index = 0
                    merged_cols = merged_rows[row_index]
                    for item_id_in in row:
                        if col_index == len(merged_cols):
                            merged_cols.append([])
                        merged_col_ids = merged_cols[col_index]
                        if item_id_in is None:
                            item_id_in = 0
                        if item_id_in not in merged_col_ids:
                            merged_col_ids.append(item_id_in)
                        col_index += 1
                    row_index += 1
            elif 'ingredients' in variant:
                merged_shapeless_recipe['shapeless'] = 1
                merged_shapeless_recipe['name'] = name

                if not merged_shapeless_recipe['result']:
                    merged_shapeless_recipe['result'] = [variant['result']['id'],variant['result']['count']]
                merged_rows = merged_shapeless_recipe['items'][0]
                
                index = 0
                for item_id_in in variant['ingredients']:
                    if index == len(merged_rows):
                        merged_rows.append([])
                    
                    row_ids = merged_rows[index]
                    if item_id_in is None:
                        item_id_in = 0
                    if item_id_in not in row_ids:
                        row_ids.append(item_id_in)
                    index += 1
        if merged_shaped_recipe['result']:
            recipes.append(merged_shaped_recipe)
        if merged_shapeless_recipe['result']:
            recipes.append(merged_shapeless_recipe)
    return recipes

def get_recipes_dict_by_count():
    counts = {}
    for r in get_recipes():
        count = __get_total_ingredient_count(r)
        if count not in counts:
            counts[count] = []
        counts[count].append(r)
    return counts

def __get_total_ingredient_count(recipe):
    count = 0
    for row in recipe['items']:
        for col in row:
            if col != [0]:
                count += 1
    return count


def __remove_zeros(id_sets: list) -> list:
    new_id_sets = []
    for ids in id_sets:
        new_ids = [item_id for item_id in ids if item_id != 0]
        if new_ids:
            new_id_sets.append(new_ids)
    # if len(id_sets) != len(new_id_sets):
    #     print(f'Old: {id_sets}')
    #     print(f'New: {new_id_sets}')
    return new_id_sets

def get_recipe_items(recipe: dict, mirror_horizontal=False, include_row_ends=True) -> list:
    items = []
    placeholder = [-2]
    for row in recipe['items']:
        if mirror_horizontal:
            row = reversed(row)
        if recipe['shapeless'] == 1:
            items.append(row)
        else:
            for id_set in row:
                items.append(id_set)
            if include_row_ends:
                items.append(placeholder)
        
    if include_row_ends and items[-1] == placeholder:
        items.pop()
    # return __remove_zeros(items)
    return items

def get_recipe_item_pairs():
    pairs = []
    for recipe in get_recipes():
        t = (recipe, get_recipe_items(recipe))
        pairs.append(t)
    return pairs


def items_start_with_sequence(ingredients, sequence) -> bool:
    index = 0
    seq2 = sequence.copy()
    for ingredient_options in ingredients:
        if not sequence:
            break
        else:
            # print(f'{sequence[0]} not in {ingredient_options}')
            if sequence.pop(0) not in ingredient_options:
                return -1
        index += 1
    if not sequence:
        return index
    else:
        return -1


def __equal_dicts(dict1: dict, dict2: dict) -> bool:
    return json.dumps(dict1, sort_keys=True, indent=2) == json.dumps(dict2, sort_keys=True, indent=2)


def __add_to_tree(tree: dict, keys: list, value: dict):
    key_set = keys[0]
    for key in key_set:
        key = int(key)
        if key not in tree:
            tree[key] = dict()
        if len(keys) == 1:
            if "recipes" not in tree[key]:
                tree[key]["recipes"] = []
            value_copy = copy.deepcopy(value)
            value_copy.pop('items')
            if not any(d for d in tree[key]["recipes"] if __equal_dicts(value_copy, d)):
                tree[key]["recipes"].append(value_copy)
        else:
            __add_to_tree(tree[key], keys[1:], value)
        


def build_recipe_tree(include_shapeless=True, include_shaped=True):
    tree = {}
    recipe_item_pairs = [(r,i) for r,i in get_recipe_item_pairs() if len(i) >= 8 and r['result'][0] != 245]
    count = 1
    total_count = len(recipe_item_pairs)
    for recipe,items in recipe_item_pairs:
        print(f'{count}: processing recipe {recipe["result"][0]}/{total_count}')
        
        # shapeless order permutations
        if include_shapeless and recipe['shapeless'] == 1:
            print('processing shapeless')
            for item_permutation in itertools.permutations(items):
                __add_to_tree(tree, list(item_permutation), recipe)
            count += 1
            # break
        if include_shaped:
            __add_to_tree(tree, items, recipe)
            __add_to_tree(tree, get_recipe_items(recipe, mirror_horizontal=True), recipe)
            count += 1
        
        # if count == 500:
        #     break

    return tree

def __print_tree_size(tree, indent=0):
    space = ' '*indent
    print(f'{space}{len(tree)} keys')
    for key in tree:
        if isinstance(key, int):
            __print_tree_size(tree[key], indent+1)
        else:
            print(f'{space}recipes: {len(tree[key])}')