"""
Travis's Point Kinetics Equations
"""
import typing
import tpke
import os
import numpy as np

np.set_printoptions(legacy='1.25', linewidth=np.inf)


def solution(input_dict: typing.Mapping):
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
	print(reactivity_vals)  # tmp
	matA, matB = method(
		n=num_steps,
		dt=dt,
		betas=input_dict['data']['delay_fractions'],
		lams=input_dict['data']['decay_constants'],
		L=input_dict['data']['Lambda'],
		rho_vec=reactivity_vals
	)
	power_vals, concentration_vals = tpke.solver.linalg(matA, matB, num_steps)
	# print(np.vstack((power_vals, concentration_vals)))
	print(power_vals)


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
	# Todo: implement the other stuff.
	print(input_dict)
	solution(input_dict)


if __name__ == "__main__":
	exit(main())
