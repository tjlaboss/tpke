"""
Travis's Point Kinetics Equations
"""
import tpke
import tpke.keys as K
import os
import shutil
import numpy as np

np.set_printoptions(legacy='1.25', linewidth=np.inf)


def main():
	args = tpke.arguments.get_arguments()
	input_file = os.path.abspath(args.input_file)
	if not os.path.isfile(input_file):
		raise FileNotFoundError(input_file)
	input_dict = tpke.yamlin.load_input_file(input_file)
	if args.yaml_validate:
		# If not, we would have errored out above.
		print("Input file is valid:", input_file)
		exit(0)
	if args.no_plot:
		# Delete input file plotting options.
		input_dict[K.PLOT] = {}
	os.makedirs(args.output_dir, exist_ok=True)
	shutil.copy(input_file, os.path.join(args.output_dir, K.FNAME_CFG))
	tpke.modes.solution(input_dict, args.output_dir)


if __name__ == "__main__":
	exit(main())
