from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import json
from pathlib import Path
import sys
import os
import re

try:
    import cog
except:
    # print('Failed to import cog')
    pass

from . import minecraft_data
from . import recipes


def dump_json(json_dict, path):
    # cog.msg(f'Path: {get_parent_dir() / Path(path)}')
    json.dump(json_dict, open(get_parent_dir() / Path(path),'w'), indent = 4)

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





def divide_into_lists_of_size(l, n):
    for i in range(0, len(l), n):
        yield l[i: i+n]

def divide_into_n_lists(l, n):
    size = len(l) // n
    # print(len(l), n, size)
    for i in range(0, len(l) -1, size):
        if i + size >= len(l) -1:
            yield l[i:]
        else:
            yield l[i:i+size]

def path_to_datapack_path(path: Path) -> str:
    relevant_parts = list(path.parts[path.parts.index('data') + 1:])
    namespace = relevant_parts.pop(0)
    relevant_parts.pop(0) # functions
    relevant_parts.pop() # last
    relevant_parts.append(path.stem)
    return f'{namespace}:{"/".join(relevant_parts)}'


def write_file_max_lines(path: Path, lines: list[str], max_lines: int, return_top_level=True, suffix='_gen'):
    cog.msg('writing at ' + str(path))
    if not return_top_level:
        f = open(path, 'w')
        f.write('# GENERATED FILE\n')

    if len(lines) <= max_lines:
        for line in lines:
            out_line = line
            if return_top_level:
                yield out_line
            else:
                f.write(out_line + '\n')
    else:

        sublists = divide_into_n_lists(lines, max_lines)
        for sublist in sublists:
            lower_bound = re.match(r'(execute .*? matches )(\d+) run',sublist[0]).group(2)
            upper_bound = re.match(r'(execute .*? matches )(\d+) run',sublist[-1]).group(2)
            generated_dir = path.parent / (path.stem + suffix)
            if not generated_dir.exists():
                os.makedirs(generated_dir)
            sublist_path = generated_dir / (path.stem + f'_{lower_bound}_{upper_bound}.mcfunction')
            # break
            cog.msg('going to write: ' + str(sublist_path))

            [i for i in write_file_max_lines(sublist_path, sublist, max_lines, return_top_level=False)]
            out_line = f'execute if score $id dt.tmp matches {lower_bound}..{upper_bound} run function {path_to_datapack_path(sublist_path)}'
            if return_top_level:
                yield out_line
            else:
                f.write(out_line + '\n')
                
            

    if not return_top_level:
        f.close()

def consecutive_pattern_file_writer(lines: list[str]):
    return write_file_max_lines(Path(cog.inFile), lines, 4, return_top_level=True)
    
def post_process(lines):
    processor = ConsecutivePattern('(execute .*? matches )\d+ run',minimum=2,match_group=1, run_tranform=consecutive_pattern_file_writer)
        # ConsecutivePattern('execute .*?run',minimum=4,match_group=0, run_tranform=dummy_new_funct),
    for line in processor.run(lines):
        yield line

    

def cog_write(lines: list[str], do_post_process=True):
    out_lines = post_process(lines) if do_post_process else lines
    for line in out_lines:
        cog.outl(line)


def get_parent_dir(override_dir=None):
    if 'cog' in sys.modules:
        return Path(cog.inFile).parent
    elif override_dir:
        return Path(override_dir)
    else:
        return Path(os.getcwd())

def pop_n(numbers, n):
    popped = []
    while numbers and n > 0:
        popped.append(numbers.pop(0))
        n -= 1
    return popped

def create_parent(nodes):
    return {'min': nodes[0]['min'], 'max': nodes[-1]['max'], 'children':nodes}

def create_parents(nodes, max_siblings):
    sibling_sets = divide_into_lists_of_size(nodes, max_siblings)
    return [create_parent(siblings) for siblings in sibling_sets]
    
def numbers_to_forest(numbers, max_siblings):
    nodes = [{'min': i, 'max': i, 'children':[]} for i in sorted(numbers)]
    while len(nodes) > max_siblings:
        nodes = create_parents(nodes, max_siblings)
    return nodes

def write_number_forest(path, forest: list, file_name_lambda, parent_lambda, leaf_lambda, file_prefix=None, file_suffix=None, level = 0) -> list[dict]:
    lines = []
    # for each tree in the forest
    # write its applicable leaf or parent statement
    for number_tree_node in forest:
        new_file = {'type':'file','name': file_name_lambda(number_tree_node['min'],number_tree_node['max'], level)+'.mcfunction', 'contents':[]}
        children = number_tree_node['children']
        contents = new_file['contents']

        for child in children:
            contents.extend(write_number_forest(path, [child], file_name_lambda, parent_lambda, leaf_lambda,level=level + 1, file_prefix=file_prefix, file_suffix=None))

        if contents:
            write_file_dict(path, new_file)
            parent_lambda_lines = parent_lambda(number_tree_node['min'],number_tree_node['max'], level)
            lines.extend(parent_lambda_lines)
        else:
            leaf_lines = leaf_lambda(number_tree_node['min'], level)
            lines.extend(leaf_lines)
    if file_prefix:
        lines = file_prefix() + lines
    if file_suffix:
        lines = lines + file_suffix()

    return lines
    # if has_leaf:
    #     contents.insert(0,leaf_file_prefix_lambda() + '\n')
    
    # return file_name_lambda(number_tree,level)

def create_ingredient_search_tree(working_dir, ing_tree, max_siblings, ing_number=0, prefix=''):
    mml=lambda min,max,l: f'l{l}_min_{min}_max_{max}'
    file_name_lambda = lambda min, max, l: f'{prefix}{mml(min,max,l)}'
    file_suffix = lambda: ['scoreboard players reset $id dt.tmp']
    mc_function_call_prefix = path_to_datapack_path(get_parent_dir())
    def call_next_ingredient_tree(id, level) -> list[str]:
        next_lines = []
        if id in ing_tree:
            next_lines.extend(create_ingredient_search_tree(working_dir, ing_tree[id], max_siblings, ing_number= ing_number + 1, prefix=f'{prefix}{id}_'))
        next_lines = [f'execute if score $id dt.tmp matches {id} run function {mc_function_call_prefix}/search_tree/{line.replace("_-2","_n2")}' for line in next_lines]
        # if 'recipes' in ing_tree:
        #     next_lines.append('# TODO add recipes')
        return next_lines
    
    # get all the ingredient ids at this level
    lines = []
    id_keys = [k for k in ing_tree.keys() if k != 'recipes']
    if id_keys:
        parent_lambda = lambda min,max, l: [f'execute if score $id dt.tmp matches {min}..{max} run function {mc_function_call_prefix}/search_tree/{file_name_lambda(min,max,l).replace("-","n")}']
        # leaf_lambda = lambda value, l: [f'execute if score $id dt.tmp matches {value} run say you have value {value}!']
        leaf_lambda = call_next_ingredient_tree

        numbers = [int(k) for k in id_keys]
        # create a tree for finding the specific id
        # at the end of the tree start looking for tree
        sibling_nodes = numbers_to_forest(numbers, max_siblings)
        # print(f'ing{ing_number} nums: {sorted(numbers)}, num-sibs: {len(sibling_nodes)}')
        lines = write_number_forest(working_dir, sibling_nodes, file_name_lambda, parent_lambda, leaf_lambda, file_suffix=file_suffix)
    if 'recipes' in ing_tree:
        for r in ing_tree['recipes']:
            lines.insert(0,f'execute if score $id dt.tmp matches -999999 run data modify storage call_stack: global.dt.recipes append value {r["result"]}')

    lines.insert(0, 'data remove storage call_stack: global.dt.item_ids[0]')
    lines.insert(1, 'scoreboard players set $id dt.tmp -999999')
    lines.insert(2, 'execute if data storage call_stack: global.dt.item_ids[0] store result score $id dt.tmp run data get storage call_stack: global.dt.item_ids[0]\n')
    # lines.insert(1, 'tellraw @p ["DEBUG global.dt.item_ids: ",{"nbt":"global.dt.item_ids","storage":"call_stack:"}]')
    file_name = f'{prefix}ing{ing_number}_start'.replace('-2','n2')
    lines.insert(0,f'say Running {file_name}')
    lines = lines + file_suffix()

    new_file = {'type':'file','name': file_name + '.mcfunction', 'contents':lines}
    write_file_dict(working_dir, new_file)

    return [file_name]

def write_recipe_search_tree(dest_dir: Path, json_resource_name='non_existent_resource') -> str:
    recipes_by_ingredient = Path(__file__).parent / 'resources' / json_resource_name
    recipes_by_ing = json.load(open(recipes_by_ingredient,'r'))
    def to_int_keys(d: dict):
        d = {int(k) if k != 'recipes' else k :v for k,v in d.items()}
        d = {k:to_int_keys(v) if isinstance(v, dict) else v for k,v in d.items()}
        
        return d
    recipes_by_ing = to_int_keys(recipes_by_ing)
    # cog.msg(str(dest_dir))
    return create_ingredient_search_tree(dest_dir, recipes_by_ing, 12)
    


def write_id_search_tree(dest_dir: Path, function_prefix) -> None:
    os.makedirs(dest_dir, exist_ok=True)
    items_dict = minecraft_data.get_items_dict()
    mml=lambda min,max,l: f'l{l}_min_{min}_max_{max}'
    file_name_lambda = lambda min, max, l: f'{mml(min,max,l)}'
    parent_lambda = lambda min,max, l: [f'execute if score $id dt.tmp matches {min}..{max} run function {function_prefix}{file_name_lambda(min,max,l)}']
    leaf_lambda = lambda value, l: [f'execute if score $id dt.tmp matches {value} run data modify storage call_stack: global.dt.name set value "minecraft:{items_dict[value]["name"]}"']
    
    # cog.msg(str([r['result'][0] for r in recipes.get_recipes()][0]))
    forest = numbers_to_forest((r['id'] for r in minecraft_data.get_items()),8)
    with open(dest_dir / 'start.mcfunction','w') as f:
        lines = write_number_forest(dest_dir, forest, file_name_lambda, parent_lambda, leaf_lambda, file_suffix=lambda: ['scoreboard players reset $id dt.tmp'])
        f.write('\n'.join(lines))