"""
Solver

Solve the system of equations

Right now, we only use scipy.linalg.solve().
It'd probably be more efficient to use scipy's sparse matrix methods
or to write my own Gauss-Seidel iterator, but that's not a priority.
"""

import scipy.linalg as la
from tpke.tping import T_arr


def __split_results(vecX: T_arr, n: int):
	"""Split power and precusor concentration results
	
	Parameters:
	----------
	vecX: np.ndarray
		1D array of the solution results
	
	n: int
		Number of timesteps
	"""
	ndg = len(vecX)//n - 1
	P = vecX[:n]
	C = vecX[n:].reshape((ndg, n))
	return P, C


def linalg(matA: T_arr, vecB: T_arr, n: int):
	"""Solve using scipy
	
	Let M be the size of the matrix,
	    n be the number of timesteps, and
	    ndg be the number of delayed groups
	
	Paramters:
	----------
	matA: np.ndarray
		[M x M] square array of RHS
		
	vecB: np.ndarray
		[1 x M] vector of LHS
	
	n: int
		Number of timesteps
	
	Returns:
	--------
	P: np.ndarray
		[1 x ndg] vector of powers
	
	C: np.ndarray
		[ndg x n] array of precursor group concentrations
	"""
	vecX = la.solve(matA, vecB)
	return __split_results(vecX, n)


def inversion(matA, matB, n):
	"""Solve by matrix inversion.
	
	Let M be the size of the matrix,
	    n be the number of timesteps, and
	    ndg be the number of delayed groups
	
	Paramters:
	----------
	matA: np.ndarray
		[M x M] square array of RHS
		
	vecB: np.ndarray
		[1 x M] vector of LHS
	
	n: int
		Number of timesteps
	
	Returns:
	--------
	P: np.ndarray
		[1 x ndg] vector of powers
	
	C: np.ndarray
		[ndg x n] array of precursor group concentrations
	"""
	invA = la.inv(matA, overwrite_a=False)
	vecX = invA.dot(matB)
	return __split_results(vecX, n)
