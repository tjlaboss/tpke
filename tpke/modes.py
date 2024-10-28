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
	dts = sorted(dts)
	errors = []
	ref = np.nan
	for i, dt in enumerate(dts):
		cfg = dict(input_dict)
		cfg[K.TIME][K.TIME_DELTA] = dt
		out_fpath = os.path.join(output_dir, str(i))
		os.makedirs(out_fpath, exist_ok=True)
		with open(os.path.join(out_fpath, K.FNAME_DT), 'w') as f:
			f.write(str(dt))
		solution(cfg, out_fpath)
		power = _load_solution(out_fpath)
		report = f"\tP(dt={dt:.2e} s): {power:.4f}"
		# Calculate the relative error vs. the reference solution.
		if i == 0:
			ref = power
			error = 0
		else:
			error = (power - ref)/ref
			report += f" | Error: {error:+8.4%}"
		print(report)
		errors.append(error)
	with open(os.path.join(output_dir, K.FNAME_REPORT), 'w') as f:
		f.write(report)
	plot_dts = np.array(dts)[1:]
	plot_err = np.array(errors)[1:]*100
	tpke.plotter.plot_convergence(plot_dts, plot_err, in_percent=True)
	fpath_plot = os.path.join(output_dir, K.FNAME_CONVERGE)
	plt.savefig(fpath_plot)
	print("Results plotted to:", fpath_plot)
	plt.show()


def _load_solution(study_dir: tpke.tping.PathType) -> float:
	"""Load the last power from a transient."""
	fpath = os.path.join(study_dir, K.FNAME_P)
	try:
		powers = np.loadtxt(fpath)
		endpow = powers.flatten()[-1]
		return float(endpow)
	except Exception as e:
		warnings.warn(f"Failed to load {fpath}: {e}", Warning)
	return np.nan
