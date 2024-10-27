"""
Actions

Action objects are used by an ArgumentParser to represent the information
needed to parse a single argument from one or more strings from the
command line. The keyword arguments to the Action constructor are also
all attributes of Action instances.
"""
import argparse
import os.path
from tpke.modes import plot_only
from tpke.yamlin import SCHEMA

class SchemaDumpAction(argparse.Action):
	"""Argparse action to dump the Yamale schema to a YAML file."""
	def __call__(self, parser, namespace, values, option_string=None):
		fname = values
		if not fname.lower().endswith('.yml'):
			fname += '.yml'
		with open(fname, 'w') as fs:
			fs.write(SCHEMA)
		print("YAML schema dumped to:", fname)
		exit(0)


class PlotOnlyAction(argparse.Action):
	"""Argparse action to make plots intead of reading."""
	def __call__(self, parser, namespace, values, option_string=None):
		fpath = values
		if not os.path.isdir(fpath):
			raise NotADirectoryError(fpath)
		exit(plot_only(fpath))
