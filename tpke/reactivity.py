"""
Reactivity

Generate reactivity functions.
All units are arbitrary.
"""
import typing
import numpy as np
import tpke.keys as K
from tpke.tping import T_arr

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


FUNCTIONS = {
	K.STEP: step,
	K.RAMP: ramp,
	K.SINE: sine
}


def get_reactivity_vector(
		r_type: str,
		n: int,
		dt: float,
		**kwargs: typing.Mapping
) -> T_arr:
	"""Get a 1D array of the reactivity over time.
	
	Parameters:
	-----------
	r_type: str
		'step', 'ramp', or 'sign'
	
	n: int
		Number of steps to generate (not counting 0).
	
	dt: float
		Amount of time between each step.
	
	kwargs: dict
		Keyword arguments for the reactivity function generator.
	
	Returns:
	--------
	rho_vector: np.ndarray
	"""
	times = np.linspace(0, n*dt, n)  # n+1?
	r_type = r_type.lower()
	if r_type not in FUNCTIONS:
		raise KeyError(f"Unknown function type: {r_type}. "
		               f"Expected one of: {list(FUNCTIONS.keys())}")
	f = np.vectorize(FUNCTIONS[r_type](**kwargs))
	return f(times)
