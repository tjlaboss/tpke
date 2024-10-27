"""
YAML in

YAML reading and validation.
"""

import typing
import yamale
import numpy as np
from tpke.matrices import METHODS

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
	return  string


SCHEMA = f"""\
time: include('time_type')
data: include('data_type')
plots: include('plot_type', required=False)
reactivity: any(include('step_type'), include('ramp_type'), include('sine_type'))
method: {_enum(METHODS.keys(), ignore_case=True)}
---
time_type:
  total: num(min=0)
  dt: num(min=0)
---
data_type:
  delay_fractions: list(num(min=0))
  decay_constants: list(num(min=0))
  Lambda: num(min=0)
---
plot_type:
  show: int(min=0, max=2, required=False)
  spy: int(min=0, max=1, required=False)
  power_reactivity: int(min=0, max=2, required=False)
---
step_type:
  type: str(equals="step", ignore_case=True)
  rho: num()
---
ramp_type:
  type: str(equals="ramp", ignore_case=True)
  rho: num()
  slope: num()
---
sine_type:
  type: str(equals="sine", ignore_case=True)
  rho: num()
  frequency: num(min=0)
"""

yamale_schema = yamale.make_schema(content=SCHEMA, parser=PARSER)


def load_input_file(fpath: str) -> typing.Mapping:
	"""Load and check a YAML input file using the best available data."""
	with open(fpath, 'r') as fy:
		data = yamale.make_data(fpath, parser=PARSER)
		yamale.validate(yamale_schema, data)
		ydict = data[0][0]
	check_input(ydict)
	# Let's make these arrays for later.
	ydict['data']['delay_fractions'] = np.array(ydict['data']['delay_fractions'])
	ydict['data']['decay_constants'] = np.array(ydict['data']['decay_constants'])
	ydict['reactivity']['rho'] = float(ydict['reactivity']['rho'])
	return ydict


def check_input(config: typing.Mapping):
	errs = []
	if len(config['data']['delay_fractions']) != len(config['data']['decay_constants']):
		errs.append("Number of delay fractions does not match number of decay constants.")
	if config['time']['total'] < config['time']['dt']:
		errs.append("Total time is less than timestep size.")
	rx = config['reactivity']
	if rx['type'] == "ramp" and np.sign(rx['rho'] != np.sign(rx['slope'])):
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

