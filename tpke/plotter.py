"""
Plotter

Plotting thingies
"""
import numpy as np
import matplotlib.pyplot as plt
import typing

V_float = typing.Collection[float]


def show():
	return plt.show()


def plot_power_and_reactivity(
		times: V_float,
		reacts: V_float,
		powers: V_float,
		power_units=None
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
	
	power_units: str
		Units to show for the y-axis for power.
		[Default: None --> relative power]
	"""
	n = len(times)
	len_p = len(powers)
	len_r = len(reacts)
	assert len_p == len_r == n, \
		f"The number of times ({n}), powers ({len_p}), and reactivities ({len_r}) must be equal."
	if power_units is None:
		power_units = "Relative"
	# continue...


def plot_matrices(matA):
	"""Spy plots of the generated matrix"""
	axA = plt.figure().add_subplot()
	axA.spy(matA)
	axA.set_title(r"$\overline{\overline{A}}$")
	return axA
