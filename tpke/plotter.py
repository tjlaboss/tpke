"""
Plotter

Plotting thingies
"""
import numpy as np
import matplotlib.pyplot as plt
import typing

V_float = typing.Collection[float]

COLOR_P = "forestgreen"
COLOR_R = "firebrick"


def show():
	return plt.show()


def plot_reactivity_and_power(
		times: V_float,
		reacts: V_float,
		powers: V_float,
		power_units=None,
		title_text=""
):
	"""Plot the reactor power and reactivity vs. time
	
	Parameters:
	-----------
	times: collection of float
		List of times (s)
		
	reacts: collection of float
		List of reactivities ($)
	
	powers: collection of float
		List of powers (power_units).
	
	power_units: str, optional
		Units to show for the y-axis for power.
		[Default: None --> relative power]
	
	title_text: str, optional
		Title for the plot.
		[Default: None]
	"""
	n = len(times)
	len_p = len(powers)
	len_r = len(reacts)
	assert len_p == len_r == n, \
		f"The number of times ({n}), powers ({len_p}), and reactivities ({len_r}) must be equal."
	if power_units is None:
		power_units = "Relative"
	
	# Plot power
	fig, pax = plt.subplots()
	plines = pax.plot(times, powers, "-", color=COLOR_P, label=r"$P(t)$")
	pax.tick_params(axis="y", labelcolor=COLOR_P)
	pax.set_ylabel(f"Power ({power_units})", color=COLOR_P)
	
	# Plot reactivity
	rax = pax.twinx()
	rlines = rax.plot(times, reacts, "--", color=COLOR_R, label=r"$\rho(t)$")
	rax.tick_params(axis="y", labelcolor=COLOR_R)
	rax.set_ylabel("Reactivity (\$)", color=COLOR_R)
	
	lines = plines + rlines
	pax.legend(lines, [l.get_label() for l in lines], loc=0)
	pax.set_xlim([0, max(times)])
	pax.set_xlabel("Time (s)")
	
	# continue...
	if title_text:
		plt.suptitle(title_text)
	plt.tight_layout()


def plot_matrices(matA):
	"""Spy plots of the generated matrix"""
	axA = plt.figure().add_subplot()
	axA.spy(matA)
	axA.set_title(r"$\overline{\overline{A}}$")
	return axA
