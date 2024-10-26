"""
Reactivity

Generate reactivity functions.
All units are arbitrary.
"""
import typing
import numpy as np

def step(rho: float, start=0, stop=np.inf) -> typing.Callable:
	"""Generate a step function
	
	Parameters:
	-----------
	rho: float
		Height of the step
	
	start: float, optional
		Start of the step.
		[Default: 0]
	
	stop: float, optional
		End of the step.
		[Default: 0]
	
	Returns:
	--------
	step_function(t)
	"""
	def step_function(t):
		if start <= t <= stop:
			return rho
		else:
			return 0
	return step_function


def ramp(rho: float, slope: float, start=0) -> typing.Callable:
	"""Generate a ramp reactivity insertion from 0 to rho.
	
	The ramp stops when 'rho' is reached.
	
	Paramters:
	----------
	rho: float
		 Maximum reactivity insertion (or withdrawal).
	
	slope: float
		Slope of the power ramp.
	
	start: float, optional
		Start of the ramp.
		[Default: 0]
	
	Returns:
	--------
	ramp_function(t)
	"""
	def ramp_function(t):
		if t < start:
			return 0
		r = slope*t
		if r < rho:
			return r
		return rho
	return ramp_function


def sine(rho: float, frequency: float) -> typing.Callable:
	"""Generate sinusoidal reactivity insertion from [+rho , -rho]

	Paramters:
	----------
	rho: float
		Amplitude of oscillation.

	frequency: float
		Frequency of the oscillation in rad/time.
	
	Returns:
	--------
	sine_function(t)
	"""
	def sine_function(t):
		return rho*np.sin(frequency*t)
	return sine_function
