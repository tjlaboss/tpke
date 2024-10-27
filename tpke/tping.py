"""
tping

custom typing
"""

import os as _os
import pathlib as _pl
import numpy as _np
import numpy.typing as _npt

T_arr = _npt.NDArray[_np.floating]

PathType = (str, _os.PathLike, _pl.Path)
