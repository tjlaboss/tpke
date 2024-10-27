"""
Arguments

Deal with argument parsing
"""
import argparse
from tpke.yamlin import SCHEMA


LOGO = r"""
 ___________              ________
      |     | /         / ...... / \
      | |\  |/   __    | ...... | O |
      | |/  |\  |_      \ ...... \ /
      | |   | \ |__      | ....v  |
     [NPRE 560 CP-1]     Wwv..^
"""


class SchemaDumpAction(argparse.Action):
	"""
	Argparse action to dump the Yamale schema to a YAML file.

	Action objects are used by an ArgumentParser to represent the information
	needed to parse a single argument from one or more strings from the
	command line. The keyword arguments to the Action constructor are also
	all attributes of Action instances.
	"""
	
	def __call__(self, parser, namespace, values, option_string=None):
		fname = values
		if not fname.lower().endswith('.yml'):
			fname += '.yml'
		with open(fname, 'w') as fs:
			fs.write(SCHEMA)
		print("YAML schema dumped to:", fname)
		exit(0)


def get_arguments(args=None) -> argparse.Namespace:
	"""
	Get and parse the command line arguments

	Parameters
	----------
	args: Iterable; optional
		List of arguments to override the actual command line arguments
		[Default: None]

	Returns
	-------
	arparse.Namespace
		Parsed arguments
	"""
	ap = argparse.ArgumentParser(description=LOGO,
	                             formatter_class=argparse.RawDescriptionHelpFormatter)
	
	ap.add_argument('-o', '--output-dir', type=str, default='.',
	                help="Results output directory (default: same as input file).")
	ap.add_argument('-y', '--yaml-validate', action="store_true", default=False,
	                help="Validate the YAML input file and exit.")
	ap.add_argument('-s', '--dump-schema', action=SchemaDumpAction,
	                help="Dump the YAML schema to a file and exit.")
	ap.add_argument("input_file", type=str,
	                help="Path to the input YAML file.")
	
	return ap.parse_args(args)