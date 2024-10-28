"""
Travis's Point Kinetics Equations
"""
import tpke
import tpke.keys as K
import os
import shutil
import numpy as np
import time

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
		return 0
	print(tpke.arguments.LOGO)
	if args.no_plot or args.study_timesteps:
		# Delete input file plotting options.
		input_dict[K.PLOT] = {}
	os.makedirs(args.output_dir, exist_ok=True)
	shutil.copy(input_file, os.path.join(args.output_dir, K.FNAME_CFG))
	if args.study_timesteps:
		dts = args.study_timesteps
		if len(dts) < 2:
			raise ValueError("Timestep study requires at least 2 values.")
		if min(dts) <= 0:
			raise ValueError("Timestep sizes must be >0.")
		print("Starting timestep study.")
		return tpke.modes.study_timesteps(input_dict, args.output_dir, dts)
	# Otherwise, run normally.
	tick = time.time()
	print("Solving...")
	tpke.modes.solution(input_dict, args.output_dir)
	tock = time.time()
	print(f"...Completed in {tock - tick:.2f} seconds. Outputs saved to: {args.output_dir}.")
	return 0


if __name__ == "__main__":
	exit(main())
