from pathlib import Path
import os
import re

from . import resources
from . import writer
from .file_utils import path_to_function_call, write_file_dict

def _divide_into_lists_of_size(l, n):
    for i in range(0, len(l), n):
        yield l[i: i+n]

def _divide_into_n_lists(l, n):
    size = len(l) // n
    # print(len(l), n, size)
    for i in range(0, len(l) -1, size):
        if i + size >= len(l) -1:
            yield l[i:]
        else:
            yield l[i:i+size]

def _pop_n(numbers, n):
    popped = []
    while numbers and n > 0:
        popped.append(numbers.pop(0))
        n -= 1
    return popped


def write_file_max_lines(path: Path, lines: list[str], max_lines: int, return_top_level=True, suffix='_gen'):
    writer.msg('writing at ' + str(path))
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

        sublists = _divide_into_n_lists(lines, max_lines)
        for sublist in sublists:
            lower_bound = re.match(r'(execute .*? matches )(\d+) run',sublist[0]).group(2)
            upper_bound = re.match(r'(execute .*? matches )(\d+) run',sublist[-1]).group(2)
            generated_dir = path.parent / (path.stem + suffix)
            if not generated_dir.exists():
                os.makedirs(generated_dir)
            sublist_path = generated_dir / (path.stem + f'_{lower_bound}_{upper_bound}.mcfunction')
            # break
            writer.msg('going to write: ' + str(sublist_path))

            [i for i in write_file_max_lines(sublist_path, sublist, max_lines, return_top_level=False)]
            out_line = f'execute if score $id dt.tmp matches {lower_bound}..{upper_bound} run function {path_to_function_call(sublist_path)}'
            if return_top_level:
                yield out_line
            else:
                f.write(out_line + '\n')
    if not return_top_level:
        f.close()

def _create_parent(nodes):
    return {'min': nodes[0]['min'], 'max': nodes[-1]['max'], 'children':nodes}

def _create_parents(nodes, max_siblings):
    sibling_sets = _divide_into_lists_of_size(nodes, max_siblings)
    return [_create_parent(siblings) for siblings in sibling_sets]
    
def _numbers_to_forest(numbers, max_siblings):
    nodes = [{'min': i, 'max': i, 'children':[]} for i in sorted(numbers)]
    while len(nodes) > max_siblings:
        nodes = _create_parents(nodes, max_siblings)
    return nodes

def __write_number_forest(path, forest: list, file_name_lambda, parent_lambda, leaf_lambda, file_prefix=None, file_suffix=None, level = 0) -> list[dict]:
    lines = []
    # for each tree in the forest
    # write its applicable leaf or parent statement
    for number_tree_node in forest:
        new_file = {'type':'file','name': file_name_lambda(number_tree_node['min'],number_tree_node['max'], level)+'.mcfunction', 'contents':[]}
        children = number_tree_node['children']
        contents = new_file['contents']

        for child in children:
            contents.extend(__write_number_forest(path, [child], file_name_lambda, parent_lambda, leaf_lambda,level=level + 1, file_prefix=file_prefix, file_suffix=None))

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

def write_id_search_tree(dest_dir: Path, function_prefix) -> None:
    os.makedirs(dest_dir, exist_ok=True)
    items_dict = resources.get_items_dict()
    mml=lambda min,max,l: f'l{l}_min_{min}_max_{max}'
    file_name_lambda = lambda min, max, l: f'{mml(min,max,l)}'
    parent_lambda = lambda min,max, l: [f'execute if score $id dt.tmp matches {min}..{max} run function {function_prefix}{file_name_lambda(min,max,l)}']
    leaf_lambda = lambda value, l: [f'execute if score $id dt.tmp matches {value} run data modify storage call_stack: global.dt.name set value "minecraft:{items_dict[value]["name"]}"']
    
    # writer.msg(str([r['result'][0] for r in recipes.get_recipes()][0]))
    forest = _numbers_to_forest((r['id'] for r in resources.get_items()),8)
    with open(dest_dir / 'start.mcfunction','w') as f:
        lines = __write_number_forest(dest_dir, forest, file_name_lambda, parent_lambda, leaf_lambda, file_suffix=lambda: ['scoreboard players reset $id dt.tmp'])
        f.write('\n'.join(lines))
