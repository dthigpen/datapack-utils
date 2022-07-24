import argparse
import glob
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Doc():
    path: str
    description: str
    params_block: str
    output_block: str

    def __str__(self):
        # output =  f'> {self.path}\n'
        output = ''
        output += f'{self.description}\n'
        if self.params_block:
            output += '@params\n'
            output += f'{self.params_block}\n'
        if self.output_block:
            output += '@output\n'   
            output += f'{self.output_block}\n'
        
        output = '\n'.join('# ' + line for line in output.splitlines())
        output = f'#> {self.path}\n' + output
        return output

    def create_markdown_str(self):
        nl = '\n'
        markdown = ''
        markdown += f'`function {self.path}`' + nl
        markdown = f'''#### `function {self.path}`
{self.description}
```
@params
{self.params_block}
@output
{self.output_block}
```
'''
        return markdown

    
def existing_dir(potential_dir: str) -> Path:
    path = Path(potential_dir)
    if not path.is_dir():
        raise argparse.ArgumentTypeError('Path does not exist or is not a directory')
    return path
def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('datapack', type=existing_dir, help='Path to datapack directory containing a pack.mcmeta file')
    return parser.parse_args()

def pop(things, strip=False):
    try:
        thing = things.pop(0)
        return thing.strip() if thing and strip else thing
    except: 
        return None
    

def doc_str_to_doc(doc_str: str) -> Doc:
    lines = doc_str.splitlines()
    path = pop(lines, strip=True)[2:]
    line = pop(lines,strip=True)
    
    description = ''
    while line is not None and (not line.strip().startswith('@params') and not line.strip().startswith('@output')):
        if description:
            description += '\n'
        description += line
        line = pop(lines,strip=True)
        
    if description:
        description = description[0].upper() + description[1:]
    
    params = ''
    if line is not None and line.strip().startswith('@params'):
        line = pop(lines)
        while line is not None and not line.strip().startswith('@output'):
            if params:
                params += '\n'
            params += line
            line = pop(lines)
    
    output = ''
    if line is not None and line.strip().startswith('@output'):
        output = '\n'.join(lines)
    
    return Doc(path, description, params, output)

def generate_api_docs(datapack_path: Path, pretty_name=None):
    print(f'dp path {datapack_path}')
    if not pretty_name:
        pretty_name = datapack_path.name.replace('-',' ').replace('_',' ').title()
    nl = '\n'
    
    with open(datapack_path / 'documentation.md','w') as doc_file:
        doc_file.write(f'# {pretty_name} Documentation')
        doc_file.write(nl * 2)
        mcfunction_paths = datapack_path.glob('**/functions/api/**/*.mcfunction')
        table_of_contents = '### Functions\n\n'
        doc_content = ''
        
        for mcf_path in mcfunction_paths:
            print(mcf_path)
            doc_str = ''
            with open(mcf_path, 'r') as mcf_file:
                for line in mcf_file:
                    line = line.strip()
                    if line.startswith('#'):
                        doc_str += line[1:] + '\n'
                    else:
                        break
            doc = doc_str_to_doc(doc_str)
            table_of_contents += f'- [{doc.path}](#function{doc.path})\n'
            doc_content += doc.create_markdown_str()
        doc_file.write(table_of_contents)
        doc_file.write(doc_content)
if __name__ == "__main__":
    args = get_args()
    generate_api_docs(args.datapack)