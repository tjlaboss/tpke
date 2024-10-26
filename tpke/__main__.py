"""
Travis's Point Kinetics Equations
"""
import tpke
import numpy as np
import os


def solution(input_dict):
	method = tpke.matrices.METHODS[input_dict['method']]
	total = input_dict['time']['total']
	dt = input_dict['time']['dt']
	num_steps = int(np.ceil(total / dt)),  # Will raise total if not divisible
	matA, matB = method(
		n=num_steps,
		dt=dt,
		betas=input_dict['data']['delay_fractions'],
		lams=input_dict['data']['decay_constants'],
		L=input_dict['data']['Lambda'],
		rho_vec=[0]*num_steps #rhos
	)
	


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


if __name__ == "__main__":
	exit(main())
