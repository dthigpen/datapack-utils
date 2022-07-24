import argparse
from pathlib import Path
from . import file_utils

def run(datapack_path: Path):
    called_functions = set()
    all_functions = set()
    for p in datapack_path.glob('**/*.mcfunction'):
        if 'test' in p.parts:
            continue
        all_functions.add(file_utils.path_to_datapack_path(p))
        with open(p, 'r') as f:
            for line in f:
                line = line.strip()
                index = line.find('function ') 
                if line and line[0] != '#' and index > -1:
                    function_call = line[index + 9:]
                    # print(f'call: {line}')
                    if file_utils.path_to_datapack_path(p) != function_call:
                        called_functions.add(function_call)
    uncalled_functions = all_functions.difference(called_functions)
    filtered = sorted([f for f in uncalled_functions if ':test' not in f and ':tick' not in f and ':load' not in f])
    print('Uncalled functions:')
    for f in filtered:
        print(f)
    
    nonexistent_functions = called_functions.difference(all_functions)
    filtered = sorted([f for f in nonexistent_functions if ':test' not in f and ':tick' not in f and ':load' not in f])
    
    print('  ')
    print('Non-existent functions:')
    for f in filtered:
        print(f)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('Analyze datapacks for unused functions')
    parser.add_argument('datapack_path',type=Path, help='The main datapack to be analyzed. Dependency datapacks are assumed to be bundled or in the same directory.')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    run(args.datapack_path)
    
