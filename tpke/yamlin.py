"""
YAML in

YAML reading
"""

import typing

try:
    from ruamel import yaml
    RUAMEL = True
except ModuleNotFoundError:
    import yaml
    RUAMEL = False


def load_input_file(fpath: str) -> typing.Mapping:
    """Load and check a YAML input file using the best available data."""
    with open(fpath, 'r') as fy:
        if RUAMEL:
            ydict = _ruamel_load_input_file(fy)
    # TODO: Check
    return ydict
        

def _ruamel_load_input_file(stream: typing.TextIO) -> typing.Mapping:
    y = yaml.YAML(typ="safe")
    return y.load(stream)


def _pyyaml_load_input_file(stream: typing.TextIO) -> typing.Mapping:
    return yaml.safe_load(stream)

