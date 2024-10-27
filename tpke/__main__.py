"""
Travis's Point Kinetics Equations
"""
import typing
import tpke
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import warnings

np.set_printoptions(legacy='1.25', linewidth=np.inf)


def solution(input_dict: typing.Mapping, output_dir: tpke.tping.PathType):
	plots = input_dict.get('plots', {})
	method = tpke.matrices.METHODS[input_dict['method']]
	total = input_dict['time']['total']
	dt = input_dict['time']['dt']
	num_steps = 1 + int(np.floor(total / dt))  # Will raise total if not divisible
	rxdict = dict(input_dict['reactivity'])
	rxtype = rxdict.pop("type")
	reactivity_vals = tpke.reactivity.get_reactivity_vector(
		r_type=rxtype,
		n=num_steps,
		dt=dt,
		**rxdict
	)
	np.savetxt(os.path.join(output_dir, "reactivities.txt"), reactivity_vals)
	print("Reactivity:", reactivity_vals)  # tmp
	matA, matB = method(
		n=num_steps,
		dt=dt,
		betas=input_dict['data']['delay_fractions'],
		lams=input_dict['data']['decay_constants'],
		L=input_dict['data']['Lambda'],
		rho_vec=reactivity_vals.copy()
	)
	to_show = plots.get('show', 0)
	if plots.get('spy'):
		tpke.plotter.plot_matrices(matA)
		plt.savefig(os.path.join(output_dir, "spy.pdf"))
		if to_show > 1:
			plt.show()
	power_vals, concentration_vals = tpke.solver.linalg(matA, matB, num_steps)
	np.savetxt(os.path.join(output_dir, "powers.txt"), power_vals)
	np.savetxt(os.path.join(output_dir, "concentrations.txt"), concentration_vals)
	# print(np.vstack((power_vals, concentration_vals)))
	print("Power", power_vals) # tmp
	prplot = plots.get('power_reactivity')
	times = np.linspace(0, num_steps*dt, num_steps)
	if prplot == 1:
		tpke.plotter.plot_reactivity_and_power(times, reactivity_vals, power_vals)
		plt.savefig(os.path.join(output_dir, "power_reactivity.pdf"))
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
	shutil.copy(input_file, os.path.join(args.output_dir, "config.yml"))
	solution(input_dict, args.output_dir)


if __name__ == "__main__":
	exit(main())
