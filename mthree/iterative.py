# This code is part of Mthree.
#
# (C) Copyright IBM 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
# pylint: disable=no-name-in-module, invalid-name
"""Iterative solver routines"""
import logging
import time
import numpy as np
import scipy.sparse.linalg as spla

from mthree.norms import ainv_onenorm_est_iter
from mthree.matvec import M3MatVec
from mthree.utils import counts_to_vector, vector_to_quasiprobs
from mthree.exceptions import M3Error

logger = logging.getLogger(__name__)


def iterative_solver(
    mitigator,
    counts,
    qubits,
    distance,
    tol=1e-5,
    max_iter=25,
    details=0,
    callback=None,
    return_mitigation_overhead=False,
):
    """Compute solution using GMRES and Jacobi preconditioning.

    Parameters:
        counts (dict): Input counts dict.
        qubits (int): Qubits over which to calibrate.
        tol (float): Tolerance to use.
        max_iter (int): Maximum number of iterations to perform.
        distance (int): Distance to correct for. Default=num_bits
        details (bool): Return col norms.
        callback (callable): Callback function to record iteration count.
        return_mitigation_overhead (bool): Returns the mitigation overhead, default=False.

    Returns:
        QuasiDistribution: dict of Quasiprobabilites

    Raises:
        M3Error: Solver did not converge.
    """
    cals = mitigator._form_cals(qubits)
    st = time.perf_counter()
    M = M3MatVec(dict(counts), cals, distance)
    fin = time.perf_counter()
    logger.info(f"MatVec build time is {fin-st}")
    L = spla.LinearOperator(
        (M.num_elems, M.num_elems),
        matvec=M.matvec,
        rmatvec=M.rmatvec,
        dtype=np.float32,
    )
    st = time.perf_counter()
    diags = M.get_diagonal()
    fin = time.perf_counter()
    logger.info(f"Diagonal build time: {fin-st}")

    def precond_matvec(x):
        out = x / diags
        return out

    P = spla.LinearOperator(
        (M.num_elems, M.num_elems), precond_matvec, dtype=np.float32
    )
    st = time.perf_counter()
    vec = np.asarray(M.probs, np.float32)
    fin = time.perf_counter()
    logger.info(f"Counts to vector time: {fin-st}")

    st = time.perf_counter()
    out, error = spla.gmres(
        L,
        vec,
        rtol=tol,
        atol=tol,
        maxiter=max_iter,
        M=P,
        callback=callback,
        callback_type="legacy",
    )
    fin = time.perf_counter()
    logger.info(f"Iterative solver time: {fin-st}")
    if error:
        raise M3Error("GMRES did not converge: {}".format(error))

    gamma = None
    if return_mitigation_overhead:
        gamma = ainv_onenorm_est_iter(M, tol=tol, max_iter=max_iter)

    st = time.perf_counter()
    quasi = vector_to_quasiprobs(out, M.sorted_counts)
    fin = time.perf_counter()
    logger.info(f"Vector to quasi time: {fin-st}")
    if details:
        return quasi, M.get_col_norms(), gamma
    return quasi, gamma
