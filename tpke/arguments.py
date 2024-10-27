"""
Arguments

Deal with argument parsing
"""
import argparse
from tpke.actions import SchemaDumpAction


LOGO = r"""
 ___________              ________
      |     | /         / ...... / \
      | |\  |/   __    | ...... | O |
      | |/  |\  |_      \ ...... \ /
      | |   | \ |__      | ....v  |
     [NPRE 560 CP-1]     Wwv..^
"""


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
	                help="Results output directory (default: active directory).")
	ap.add_argument('-y', '--yaml-validate', action="store_true", default=False,
	                help="Validate the YAML input file and exit.")
	ap.add_argument('-s', '--dump-schema', action=SchemaDumpAction,
	                help="Dump the YAML schema to a file and exit.")
	ap.add_argument("input_file", type=str,
	                help="Path to the input YAML file.")
	
	return ap.parse_args(args)