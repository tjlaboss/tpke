"""
YAML in

YAML reading and validation.
"""

import typing
import yamale
import numpy as np
from tpke.matrices import METHODS
from tpke.tping import PathType
from tpke.keys import *

try:
	from ruamel import yaml
	PARSER = "ruamel"
except ModuleNotFoundError:
	import yaml
	PARSER = "PyYaml"


def _enum(iterable: typing.Iterable, **kwargs) -> str:
	"""Turn an interable into a yamale-compatible enum string"""
	string = 'enum(' + ','.join([repr(s) for s in iterable])
	for k, v in kwargs.items():
		string += f', {k}={v}'
	string += ')'
	return string


SCHEMA = f"""\
{TIME}: include('time_type')
{DATA}: include('data_type')
{PLOT}: include('plot_type', required=False)
{REAC}: any(include('step_type'), include('ramp_type'), include('sine_type'))
{METH}: {_enum(METHODS.keys(), ignore_case=True)}
---
time_type:
  {TIME_TOTAL}: num(min=0)
  {TIME_DELTA}: num(min=0)
---
data_type:
  {DATA_B}: list(num(min=0))
  {DATA_L}: list(num(min=0))
  {DATA_BIG_L}: num(min=0)
---
plot_type:
  {PLOT_SHOW}: int(min=0, max=2, required=False)
  {PLOT_SPY}: int(min=0, max=1, required=False)
  {PLOT_PR}: int(min=0, max=2, required=False)
  {PLOT_LOG}: {_enum(PLOT_TYPES, ignore_case=True, required=False)}
---
step_type:
  {REAC_TYPE}: str(equals="{STEP}", ignore_case=True)
  {RHO}: num()
---
ramp_type:
  {REAC_TYPE}: str(equals="{RAMP}", ignore_case=True)
  {RHO}: num()
  {RAMP_SLOPE}: num()
---
sine_type:
  {REAC_TYPE}: str(equals="{SINE}", ignore_case=True)
  {RHO}: num()
  {SINE_OMEGA}: num(min=0)
"""

yamale_schema = yamale.make_schema(content=SCHEMA, parser=PARSER)


def load_input_file(fpath: PathType) -> typing.MutableMapping:
	"""Load and check a YAML input file using the best available data.
	
	This function also does some type enforcement.
	This isn't where I want to do that. Move eventually...
	
	Parameters:
	-----------
	fpath: str or PathLike
		Path to the input YAML file to read
	
	Returns:
	--------
	ydict: dict
		Dictionary of the input parameters.
	"""
	data = yamale.make_data(fpath, parser=PARSER)
	yamale.validate(yamale_schema, data)
	ydict = data[0][0]
	check_input(ydict)
	# Let's make these arrays for later.
	ydict[DATA][DATA_B] = np.array(ydict[DATA][DATA_B])*1e-5
	ydict[DATA][DATA_L] = np.array(ydict[DATA][DATA_L])
	ydict[REAC][RHO] = float(ydict[REAC][RHO])
	return ydict


def check_input(config: typing.Mapping):
	"""Check the input dictionary and raise an error if appropriate"""
	errs = []
	if len(config[DATA][DATA_B]) != len(config[DATA][DATA_L]):
		errs.append("Number of delayed fractions does not match number of decay constants.")
	if config[TIME][TIME_TOTAL] < config[TIME][TIME_DELTA]:
		errs.append("Total time is less than timestep size.")
	rx = config[REAC]
	if rx[REAC_TYPE] == RAMP and np.sign(rx[RHO]) != np.sign(rx[RAMP_SLOPE]):
		errs.append("Reactivity inserted and insertion ramp slope have different signs.")
	# Might add some more checks later.
	if errs:
		errstr = f"There were {len(errs)} errors:\n\t"
		errstr += "\n\t".join(errs)
		raise ValueError(errstr)
		

def _ruamel_load_input_file(stream: typing.TextIO) -> typing.Mapping:
	y = yaml.YAML(typ="safe")
	return y.load(stream)


def _pyyaml_load_input_file(stream: typing.TextIO) -> typing.Mapping:
	return yaml.safe_load(stream)


def _ruamel_dump_input_file(data: typing.Mapping, stream: typing.TextIO):
	y = yaml.YAML(typ="safe")
	return y.dump(data, stream)


def _pyyaml_dump_input_file(data: typing.Mapping, stream: typing.TextIO):
	return yaml.safe_dump(data, stream)


def dump(fpath: PathType, data: typing.Mapping):
	"""Dump a dictionary to a file.
	
	Parameters:
	-----------
	fpath: str or PathLike
		File to dump the YAML to.
	
	data: dict
		Dictionary of data to dump.
	"""
	with open(fpath, 'w') as fy:
		if PARSER == "ruamel":
			return _ruamel_dump_input_file(data, fy)
		else:
			return _pyyaml_dump_input_file(data, fy)

