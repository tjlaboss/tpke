"""
Arguments

Deal with argument parsing
"""
import argparse
from tpke.yamlin import SCHEMA


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
