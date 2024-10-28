"""
Modes

Run modes for TPKE
"""
import os
import sys
import typing
import warnings
import numpy as np
import matplotlib.pyplot as plt
import tpke
import tpke.keys as K


def plot_only(output_dir: tpke.tping.PathType):
	"""Only plot the existing results
	
	Parameters:
	-----------
	output_dir: str or PathLike
		Output folder to read existing results from.
	
	Returns:
	--------
	le: int
		Error status.
		le == 0 is OK, le != 0 indicates errors.
	"""
	errs = []
	# Spy plot of Matrix A
	afpath = os.path.join(output_dir, K.FNAME_MATRIX_A)
	if not os.path.exists(afpath):
		errs.append(f"Matrix A could not be found at: {afpath}")
	else:
		try:
			matA = np.loadtxt(afpath)
			tpke.plotter.plot_matrix(matA)
		except Exception as e:
			errs.append(f"Failed to plot Matrix A: {type(e)}: {e}")
		else:
			plt.savefig(K.FNAME_SPY)
			print("Matrix A spy plot saved to:", K.FNAME_SPY)
	# Power-Reactivity plot
	tfpath = os.path.join(output_dir, K.FNAME_TIME)
	rfpath = os.path.join(output_dir, K.FNAME_RHO)
	pfpath = os.path.join(output_dir, K.FNAME_P)
	if not os.path.exists(tfpath):
		errs.append(f"Times could not be found at: {tfpath}")
	elif not os.path.exists(rfpath):
		errs.append(f"Reactivities could not be found at: {rfpath}")
	elif not os.path.exists(pfpath):
		errs.append(f"Reactor powers could not be found at: {pfpath}")
	else:
		try:
			times = np.loadtxt(tfpath)
			reactivities = np.loadtxt(rfpath)
			powers = np.loadtxt(pfpath)
			# if len(times) != len(reactivities) != len(powers)  -> handled in plotting
			tpke.plotter.plot_reactivity_and_power(times, reactivities, powers)
		except Exception as e:
			errs.append(f"Failed to plot power and reactivity: {type(e)}: {e}")
		else:
			plt.savefig(K.FNAME_PR)
			print("Power and reactivity plot saved to:", K.FNAME_PR)
	le = len(errs)
	if le:
		errstr = f"There were {le} errors:\n\t"
		errstr += "\n\t".join(errs)
		print(errs, sys.stderr)
	plt.show()
	return le


def solution(input_dict: typing.Mapping, output_dir: tpke.tping.PathType):
	"""Solve the Point Kinetics Reactor Equations
	
	Numerically solve the PKRE, write the data to the output directory,
	make the indicated plots, and save plots to the output directory.
	
	Parameters:
	-----------
	input_dict: dict
		Dictionary of the the parsed input file.
	
	output_dir: str or PathLike
		Output folder to write results to.
		If it does not exist, it will be created.
	
	"""
	plots = input_dict.get(K.PLOT, {})
	method = tpke.matrices.METHODS[input_dict[K.METH]]
	total = input_dict[K.TIME][K.TIME_TOTAL]
	dt = input_dict[K.TIME][K.TIME_DELTA]
	num_steps = int(np.ceil(total/dt))  # Will raise total if not divisible
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
	prplot = plots.get(K.PLOT_PR)
	if prplot == 1:
		tpke.plotter.plot_reactivity_and_power(
			times=times,
			reacts=reactivity_vals,
			powers=power_vals,
			plot_type=plots.get(K.PLOT_LOG)
		)
		plt.savefig(os.path.join(output_dir, K.FNAME_PR))
	elif prplot == 2:
		# Plot them separately
		warnings.warn("Not implemented yet: separate power and reactivity plots", FutureWarning)
	if to_show > 1:
		plt.show()
	
	# keep at end
	if to_show:
		plt.show()


def study_timesteps(
		input_dict: typing.Mapping,
		output_dir: tpke.tping.PathType,
		dts: typing.Iterable[float]
):
	"""Study the effect of timestep size upon final power.
	
	Parameters:
	-----------
	input_dict: dict
		Dictionary of the the parsed input file.
	
	output_dir: str or PathLike
		Output folder to write results to.
		If it does not exist, it will be created.
		Each result will create a subfolder in 'output_dir'.
	
	dts: iterable of float
		List of timestep sizes (s).
	"""
	pass

