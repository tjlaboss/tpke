"""
Matrices

Matrix builders for Point Kinetics Equations
"""

import numpy as np
import typing
from tpke import keys
from tpke.tping import T_arr


def __check_inputs(n, rho_vec, betas, lams):
    """Check the lenghts of inputs for matrix builders."""
    len_rho = len(rho_vec)
    assert len_rho == n, f"Expected {n} reactivities; got {len_rho}."
    len_beta = len(betas)
    len_lams = len(lams)
    assert len_beta == len_lams, \
        (f"Number of delayed neutron fractions ({len_beta}) does not match"
         f"number of delayed neutron decay constants ({len_lams}).")


def implicit_euler(
        n: int,
        rho_vec: T_arr,
        dt: float,
        betas: T_arr,
        lams: T_arr,
        L: float,
        P0: float=1,
) -> typing.Tuple[T_arr, T_arr]:
    """Build A and B matrices using Implicit Euler.
    
    Example for 1 delayed group:
    
        [-1] P_n  +  [1 - dt*(rho - beta)/L] P_{n+1}  +                    [-dt*lambda_k] C_{k,n+1} = 0
        [+1] P_0                                                                                    = P0
                     [-dt*beta_k/Lambda]     P_{n+1}  +  [-1] C_{k,n} + [1 + dt*lambda_k] C_{k,n+1} = 0
                                                         [+1] C_{k,n}                               = C0_k
    
    
    Parameters:
    -----------
    n: int
        Number of timesteps
    
    rho_vec: np.ndarray(float)
        Array of reactivities at each timestep ($).
    
    dt: float
        Timestep size (s).
    
    betas: np.ndarray(float)
        Array of delayed neutron precursor fission yields.
    
    lams: np.ndarray(float)
        Array of delayed neutron precursor decay constants (s^-1).
    
    L: float
        Prompt neutron lifetime (s).
        
    P0: float, optional.
        Starting power.
        [Default: 1]
    
    Returns:
    --------
    A: np.ndarray
        Square [NxN] array, for LHS of matrix solution.
    
    B: np.ndarray
        Vector [Nx1] array, for RHS of matrix solution.
    """
    __check_inputs(n, rho_vec, betas, lams)
    ndg = len(betas)    # number of delayed groups
    beff = sum(betas)   # beta effective
    rho_vec *= beff     # convert from $
    size = (1 + ndg)*n
    A = np.zeros((size, size))
    B = np.zeros(size)
    C0s = (P0*betas)/(lams*L)  # Initial precursor concentrations
    for ip in range(n-1):
        rho1 = rho_vec[ip+1]
        dtrbl = dt*(rho1 - beff)/L
        # P, normal nodes
        A[ip, ip] = -1            # P_n
        A[ip, ip+1] =  1 - dtrbl  # P_{n+1}
        for k in range(ndg):
            ic = ip + n*(k+1)
            A[ip, ic+1] = -dt*lams[k]       # C_{k,n+1}
            # C, normal nodes
            A[ic, ip+1] = -dt*betas[k]/L    # P_{n+1}
            A[ic, ic] = -1                  # C_{n,k}
            A[ic, ic+1] = 1 + dt*lams[k]    # C_{n,k+1}
    # Boundary Conditions
    # Initial Condition: P
    A[n-1, 0] = 1
    B[n-1] = P0
    # Initial Condition: C
    for k in range(ndg):
        A[n*(k+2)-1, n*(k+1)] = 1
        B[n*(k+2)-1] = C0s[k]
    return A, B


def explicit_euler(
        n: int,
        rho_vec: T_arr,
        dt: float,
        betas: T_arr,
        lams: T_arr,
        L: float,
        P0: float = 1,
) -> typing.Tuple[T_arr, T_arr]:
    """Build A and B matrices using Explicit Euler.

    Example for 1 delayed group:

        [-1 - dt*(rho - beta)/L] P_n  +  [+1] P_{n+1}  + [-dt*lambda_k] C_{k,n}                    = 0
        [+1]                     P_0                                                               = P0
        [-dt*beta_k/Lambda]      P_n  +              [-1 + dt*lambda_k] C_{k,n}  +  [+1] C_{k,n+1} = 0
                                                                   [+1] C_{k,n}                    = C0_k


    Parameters:
    -----------
    n: int
        Number of timesteps

    rho_vec: np.ndarray(float)
        Array of reactivities at each timestep ($).

    dt: float
        Timestep size (s).

    betas: np.ndarray(float)
        Array of delayed neutron precursor fission yields.

    lams: np.ndarray(float)
        Array of delayed neutron precursor decay constants (s^-1).

    L: float
        Prompt neutron lifetime (s).

    P0: float, optional.
        Starting power.
        [Default: 1]

    Returns:
    --------
    A: np.ndarray
        Square [NxN] array, for LHS of matrix solution.

    B: np.ndarray
        Vector [Nx1] array, for RHS of matrix solution.
    """
    __check_inputs(n, rho_vec, betas, lams)
    ndg = len(betas)    # number of delayed groups
    beff = sum(betas)   # beta effective
    rho_vec *= beff     # convert from $
    size = (1 + ndg)*n
    A = np.zeros((size, size))
    B = np.zeros(size)
    C0s = (P0*betas)/(lams*L)  # Initial precursor concentrations
    for ip in range(n - 1):
        rho0 = rho_vec[ip]
        dtrbl = dt*(rho0 - beff)/L
        # P, normal nodes
        A[ip, ip] = -1 - dtrbl  # P_n
        A[ip, ip+1] = 1         # P_{n+1}
        for k in range(ndg):
            ic = ip + n*(k + 1)
            A[ip, ic] = -dt*lams[k]     # C_{k,n}
            # C, normal nodes
            A[ic, ip] = -dt*betas[k]/L  # P_{n}
            A[ic, ic] = -1 + dt*lams[k] # C_{k,n}
            A[ic, ic+1] = 1             # next C
    # Boundary Conditions
    # Initial Condition: P
    A[n-1, 0] = 1
    B[n-1] = P0
    # Initial Condition: C
    for k in range(ndg):
        A[n*(k+2)-1, n*(k+1)] = 1
        B[n*(k+2)-1] = C0s[k]
    return A, B


METHODS = {
	key: implicit_euler for key in keys.IMPLICIT_NAMES
} | {
	key: explicit_euler for key in keys.EXPLICIT_NAMES
}

