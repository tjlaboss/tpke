"""
Travis's Point Kinetics Equations
"""
import typing
import tpke
import tpke.keys as K
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import warnings

np.set_printoptions(legacy='1.25', linewidth=np.inf)


def solution(input_dict: typing.Mapping, output_dir: tpke.tping.PathType):
	"""
	
	This function should be replaced with a "solve" step and a "plot" step.
	
	In the "solve" step, the user will provide the input file and ouput directory,
		and then TPKE will find the solution.
	In the "plot" step, the user will provide the output directory,
		and then TPKE will read it and plot the results.
	 
	"""
	plots = input_dict.get(K.PLOT, {})
	method = tpke.matrices.METHODS[input_dict[K.METH]]
	total = input_dict[K.TIME][K.TIME_TOTAL]
	dt = input_dict[K.TIME][K.TIME_DELTA]
	num_steps = 1 + int(np.floor(total / dt))  # Will raise total if not divisible
	times = np.linspace(0, num_steps*dt, num_steps)
	np.savetxt(os.path.join(output_dir, K.FNAME_TIME), times)
	rxdict = dict(input_dict[K.REAC])
	rxtype = rxdict.pop(K.REAC_TYPE)
	reactivity_vals = tpke.reactivity.get_reactivity_vector(
		r_type=rxtype,
		n=num_steps,
		dt=dt,
		**rxdict
	)
	np.savetxt(os.path.join(output_dir, K.FNAME_RHO), reactivity_vals)
	print("Reactivity:", reactivity_vals)  # tmp
	matA, matB = method(
		n=num_steps,
		dt=dt,
		betas=input_dict[K.DATA][K.DATA_B],
		lams=input_dict[K.DATA][K.DATA_L],
		L=input_dict[K.DATA][K.DATA_BIG_L],
		rho_vec=reactivity_vals.copy()
	)
	np.savetxt(os.path.join(output_dir, K.FNAME_MATRIX_A), matA)
	np.savetxt(os.path.join(output_dir, K.FNAME_MATRIX_B), matB)
	to_show = plots.get(K.PLOT_SHOW, 0)
	if plots.get(K.PLOT_SPY):
		tpke.plotter.plot_matrix(matA)
		plt.savefig(os.path.join(output_dir, K.FNAME_SPY))
		if to_show > 1:
			plt.show()
	power_vals, concentration_vals = tpke.solver.linalg(matA, matB, num_steps)
	np.savetxt(os.path.join(output_dir, K.FNAME_P), power_vals)
	np.savetxt(os.path.join(output_dir, K.FNAME_C), concentration_vals)
	# print(np.vstack((power_vals, concentration_vals)))
	print("Power", power_vals) # tmp
	prplot = plots.get(K.PLOT_PR)
	if prplot == 1:
		tpke.plotter.plot_reactivity_and_power(times, reactivity_vals, power_vals)
		plt.savefig(os.path.join(output_dir, K.FNAME_PR))
	elif prplot == 2:
		# Plot them separately
		warnings.warn("Not implemented yet: separate power and reactivity plots", FutureWarning)
	if to_show > 1:
		plt.show()
	
	# keep at end
	if to_show:
		plt.show()


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
	os.makedirs(args.output_dir, exist_ok=True)
	shutil.copy(input_file, os.path.join(args.output_dir, K.FNAME_CFG))
	solution(input_dict, args.output_dir)


if __name__ == "__main__":
	exit(main())
