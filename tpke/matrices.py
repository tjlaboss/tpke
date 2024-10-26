"""
Matrices

Matrix builders for Point Kinetics Equations
"""

import numpy as np
import numpy.typing as npt
import typing

_T_arr = npt.NDArray[np.floating]



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
        rho_vec: _T_arr,
        dt: float,
        betas: _T_arr,
        lams: _T_arr,
        L: float,
        P0: float=1,
) -> typing.Tuple[_T_arr, _T_arr]:
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
        Array of reactivities at each timestep.
    
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
    size = (1 + ndg)*n
    A = np.zeros((size, size))
    B = np.zeros(size)
    C0s = (P0*betas)/(lams*L)  # Initial precursor concentrations
    for ip in range(n-1):
        rho1 = rho_vec[ip+1]
        dtrbl = dt*(rho1 - beff)/L
        dtl = dt*beff/L
        # P, normal nodes
        A[ip, ip] = -1            # P_n
        A[ip, ip+1] =  1 - dtrbl  # P_{n+1}
        for k in range(ndg):
            ic = ip + n*(k+1)
            A[ip, ic+1] = -dt*lams[k]       # C_{k,n+1}
            # C, normal nodes
            A[ic, ip+1] = -dtl              # P_{n+1}
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

