"""Custom sparse multiple-shooting QP assembly for scheduled linear MPC.

The optimization algorithm itself is supplied by the standard OSQP library.
No previous project's controller, trajectory code, or plotting code is used.
"""
import numpy as np
from scipy import sparse
import osqp
from model import scheduled_model


class Controller:
    def __init__(self, settings):
        self.cfg = settings
        n = settings.horizon
        self.nx = 4 * (n+1)
        self.nz = self.nx + 2*n
        q = np.diag([4.0, 22.0, 12.0, 4.0])
        self.r = sparse.kron(sparse.eye(n), np.diag([3.0, 0.25]), format="csc")
        self.s = sparse.kron(sparse.eye(n), np.diag([12.0, 0.8]), format="csc")
        # D U = [u0, u1-u0, ...]; subtract the previously applied u for row zero.
        self.d = sparse.kron(sparse.eye(n)-sparse.diags(np.ones(n-1), -1),
                             sparse.eye(2), format="csc")
        qx = sparse.block_diag([q]*n + [3*q], format="csc")
        self.p = sparse.triu(2*sparse.block_diag(
            [qx, self.r + self.d.T @ self.s @ self.d], format="csc"), format="csc")
        self.selector = sparse.hstack([sparse.csc_matrix((2*n, self.nx)),
                                       sparse.eye(2*n)], format="csc")
        self.rate_selector = sparse.hstack([sparse.csc_matrix((2*n, self.nx)),
                                            self.d], format="csc")
        self.speed_selector = sparse.csc_matrix(
            (np.ones(n), (np.arange(n), 4*np.arange(1, n+1)+3)), shape=(n, self.nz))
        self.previous_solution = None

    def assemble(self, error, preview, previous_command):
        c, n = self.cfg, self.cfg.horizon
        rows, cols, values = [], [], []
        def add(row, col, block):
            rr, cc = np.nonzero(block)
            rows.extend((row+rr).tolist())
            cols.extend((col+cc).tolist())
            values.extend(block[rr, cc].tolist())
        add(0, 0, np.eye(4))
        rhs = np.zeros(self.nx)
        rhs[:4] = error
        feedforward = preview[:n, [6, 5]].reshape(-1)
        for k in range(n):
            a, b = scheduled_model(preview[k], c)
            row = 4*(k+1)
            add(row, 4*k, -a)
            add(row, row, np.eye(4))
            add(row, self.nx+2*k, -b)
            rhs[row:row+4] = -b @ feedforward[2*k:2*k+2]
        dynamics = sparse.csc_matrix((values, (rows, cols)), shape=(self.nx, self.nz))
        prior = np.zeros(2*n)
        prior[:2] = previous_command
        linear = np.zeros(self.nz)
        linear[self.nx:] = -2*(self.r @ feedforward + self.d.T @ self.s @ prior)
        limit = np.tile([c.steering_rate*c.dt, c.jerk_limit*c.dt], n)
        lower = np.concatenate((rhs,
            np.tile([-c.steering_limit, c.acceleration_min], n),
            prior-limit, c.speed_min-preview[1:n+1, 3]))
        upper = np.concatenate((rhs,
            np.tile([c.steering_limit, c.acceleration_max], n),
            prior+limit, c.speed_max-preview[1:n+1, 3]))
        constraint = sparse.vstack((dynamics, self.selector, self.rate_selector,
                                    self.speed_selector), format="csc")
        return linear, constraint, lower, upper

    def command(self, error, preview, previous_command):
        q, a, lower, upper = self.assemble(error, preview, previous_command)
        solver = osqp.OSQP()
        solver.setup(P=self.p, q=q, A=a, l=lower, u=upper, verbose=False,
                     eps_abs=1e-6, eps_rel=1e-6, max_iter=12000,
                     polishing=True, warm_starting=True)
        if self.previous_solution is not None:
            solver.warm_start(x=self.previous_solution)
        result = solver.solve(raise_error=False)
        if result.info.status_val != 1 or result.x is None:
            raise RuntimeError(f"QP failed: {result.info.status}")
        z = result.x
        violation = max(0.0, float(np.max(lower-a@z)), float(np.max(a@z-upper)))
        if not np.isfinite(z).all() or violation > 2e-5:
            raise RuntimeError(f"QP feasibility residual: {violation}")
        self.previous_solution = z
        return z[self.nx:self.nx+2].copy(), violation, result.info.iter
