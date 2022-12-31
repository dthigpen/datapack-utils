import sys
try:
    import cog
except ImportError as e:
    sys.stderr.write('Cog import error\n')

def msg(line: str, end: str = '\n'):
    if 'cog' in sys.modules:
        cog.msg(line + end)
    else:
        print(f'cog.msg: {line}', end=end)

def _out(line: str, end):
    if 'cog' in sys.modules:
        cog.out(line + end)
    else:
        print(f'cog.out: {line}', end=end)


def out(line_or_lines: str | list[str], end='\n'):
        if isinstance(line_or_lines, str):
            _out(line_or_lines, end)
        else:
            for line in line_or_lines:
                _out(line, end)

