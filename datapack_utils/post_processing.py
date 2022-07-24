from abc import ABC, abstractmethod
import argparse
import re
from pathlib import Path, PurePosixPath

try:
    import cog
except:
    # print('Failed to import cog')
    pass

def dummy_new_funct(lines: list[str]) -> list[str]:
    transformed = ['new_funct:']
    transformed.extend(['  ' + l for l in lines])
    return transformed

class LinePostProcessor(ABC):
    @abstractmethod
    def run(self, lines: list[str]) -> list[str]:
        pass

class ConsecutivePattern(LinePostProcessor):
    
    def __init__(self, pattern,minimum=2, match_group=0,run_tranform=lambda lines: lines):
        self.pattern = pattern
        self.minimum = minimum
        self.match_group = match_group
        self.run_tranform = run_tranform
    
    def __transform_lines(self, consecutive_lines, minimum = 2):
        if len(consecutive_lines) < max(1, minimum):
            return consecutive_lines
        else:
            return self.run_tranform(consecutive_lines)

    def run(self, lines):
        consecutive_lines = []
        for line in lines:
            match = re.match(self.pattern, line)
            last_match = re.match(self.pattern, consecutive_lines[-1]) if consecutive_lines else None
            # if the line matches the regex, accumulate it and output nothing
            if match:
                if last_match is None or last_match.group(self.match_group) == match.group(self.match_group):
                    consecutive_lines.append(line)
                else:
                    for output_line in self.__transform_lines(consecutive_lines, self.minimum):
                        yield output_line
                    consecutive_lines = [line]
            # if the line doesn't match, dump accumulated lines through transform and output
            else:
                # print(f'nomatch {line}')
                for output_line in self.__transform_lines(consecutive_lines, self.minimum):
                    yield output_line
                yield line
                consecutive_lines = []
        for output_line in self.__transform_lines(consecutive_lines, self.minimum):
            yield output_line

class MultilineExecute(LinePostProcessor):
    
    def run(self, lines):
        new_lines = []
        lines_iter = iter(lines)
        execute_statement = None
        execute_indent = None
        has_run_statement = False
        while (line := next(lines_iter, None)) is not None:
            line_length = len(line)
            stripped_line = line.lstrip()
            indent = line[:line_length - len(stripped_line)]
            if stripped_line.startswith('#'):
                new_lines.append(line)
                continue
            # stripped_line = stripped_line.rstrip()
            if execute_statement:
                if len(indent) > len(execute_indent):
                    new_lines.append(execute_statement + ' ' + stripped_line)
                    has_run_statement = True
                    continue
                else:
                    execute_statement = None
                    execute_indent = None
                    has_run_statement = False

            if stripped_line.startswith('execute ') and (' run' not in stripped_line or stripped_line.endswith(' run')):
                    
                execute_statement = indent + stripped_line
                execute_indent = indent
                if not stripped_line.endswith(' run'):
                    execute_statement += ' run'
            else:
                new_lines.append(line)

        if execute_statement and not has_run_statement:
            new_lines.append(execute_statement)
        return new_lines



def run_all(text: str):
    fix_execs = MultilineExecute()
    cog.out('\n'.join(fix_execs.run(text.splitlines())))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir',type=Path)
    return parser.parse_args()

if __name__ == '__main__':
    post_processors = [MultilineExecute()]

    args = get_args()
    for path in args.dir.rglob('*.mcfunction'):
        if 'rx.playerdb' in str(path):
            continue
        original_lines = []
        new_lines = []
        with open(path, 'r') as f:
            original_lines = f.read().splitlines()
            new_lines = original_lines.copy()
            for pp in post_processors:
                new_lines = pp.run(new_lines)
        # print(new_lines)
        # break
        def Diff(li1, li2):
            return list(set(li1) - set(li2)) + list(set(li2) - set(li1))
        if original_lines != new_lines:
            print(f'Post processing {path}')
            # print(f'Diff {Diff(original_lines, new_lines)}')
            path2 = path.parent / (path.stem + '_new' + path.suffix)
            print(f'new path: {path2}')
            with open(path2, 'w') as f:
                f.write('\n'.join(new_lines))

