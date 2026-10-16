# Custom LPV-MPC vehicle-tracking study

A fresh implementation for Ajay Iyer's portfolio. The model, analytic trajectories,
QP construction, simulator, metrics, tests and figures were written for this study
with AI coding assistance. No source from the earlier Mark Misin reference project
is copied or imported. The earlier project supplied the conceptual starting point:
use a varying linear prediction model, solve a constrained horizon problem, apply
the first command, and repeat. This is a new experiment, not a reproduction of
the earlier six-state dynamic model or its reported results.

NumPy, SciPy, OSQP, Matplotlib and Pillow remain third-party dependencies with
their own licenses. In particular, OSQP supplies the numerical QP solver; it is
not claimed as a custom optimization algorithm.

## Run

Tested with Python 3.10. On Linux, place the virtual environment on a filesystem
that supports symbolic links (the home directory is suitable):

```sh
python3 -m venv "$HOME/.venvs/custom-lpv-mpc"
source "$HOME/.venvs/custom-lpv-mpc/bin/activate"
python -m pip install -r requirements.txt
python -m unittest discover -s . -v
python run.py
```

From the website root, the equivalent final two commands are
`python -m unittest discover -s code/custom_lpv_mpc -v` and
`python code/custom_lpv_mpc/run.py`. Run in an environment without unrelated
ROS/Python path overrides. No ROS nodes, robot hardware, or external simulator
are needed. Optional: `python run.py --output /path/to/results`.

The run regenerates all data and plots. `results/*.csv` is readable without
Python; the final row has blank-equivalent NaN command fields because no command
is applied after the last recorded state. NPZ files contain the same arrays
plus controller timings. PNG, SVG and WebP versions of each figure are provided.
`metrics.json` records configuration, package versions and SHA-256 source hashes.
Wall-clock timings vary by machine; trajectory data is deterministic to solver
tolerance on the same numerical environment.

## Model and derivation

Plant state `z = [x, y, psi, v]`; control `u = [delta, a]`. All angles are radians
inside the code. Wheelbase `L = 2.7 m`:

```text
x_dot   = v cos(psi)
y_dot   = v sin(psi) + lateral_drift
psi_dot = (v/L) tan(delta)
v_dot   = a + longitudinal_load
```

The plant is integrated by RK4 with five substeps per 0.1 s control interval.
It receives the first QP command without clipping. The controller has full-state
feedback and a known, analytic reference trajectory. It is not an estimator.

Define `e = [e_s, e_y, e_psi, e_v]`, where the first two errors are the actual
minus reference position rotated into the reference heading frame. This is
time-indexed trajectory tracking, not nearest-point geometric path following.
For reference speed `v_r`, curvature `kappa_r`, yaw rate `w_r = v_r*kappa_r`,
feedforward steering `delta_r = atan(L*kappa_r)` and reference acceleration `a_r`:

```text
e_s_dot   = (v_r+e_v) cos(e_psi) - v_r + w_r e_y
e_y_dot   = (v_r+e_v) sin(e_psi) - w_r e_s
e_psi_dot = ((v_r+e_v)/L) tan(delta) - w_r
e_v_dot   = a - a_r
```

The local first-order approximation about zero error and the feedforward input is:

```text
A_c = [[0,     w_r,  0,    1      ],
       [-w_r,  0,    v_r,  0      ],
       [0,     0,    0,    kappa_r],
       [0,     0,    0,    0      ]]

B_c = [[0,                         0],
       [0,                         0],
       [v_r/(L*cos(delta_r)^2),     0],
       [0,                         1]]

A_d = I + dt*A_c; B_d = dt*B_c
e[k+1] = A_d[k] e[k] + B_d[k] (u[k] - u_ref[k])
```

These matrices vary with reference speed and curvature across the 20-step horizon.
This is a reference-scheduled LPV approximation of the nonlinear tracking-error
system, equivalently a known linear time-varying prediction sequence. It is a
local approximation, not an exact global LPV embedding of the nonlinear plant.
Prediction uses forward Euler; plant propagation deliberately uses separate RK4.

## Quadratic program

Decision vector: all 21 predicted error states, then 20 steering/acceleration
pairs. There are 124 scalar decision variables. Dynamics and the measured initial
error are equality constraints. The objective is:

```text
sum(k=0..N-1) e[k]'Q e[k]
  + e[N]'(3Q)e[N]
  + sum(k=0..N-1) (u[k]-u_ref[k])'R(u[k]-u_ref[k])
  + sum(k=0..N-1) (u[k]-u[k-1])'S(u[k]-u[k-1])

Q = diag(4, 22, 12, 4)
R = diag(3, 0.25)
S = diag(12, 0.8)
```

The first input difference is measured from the actual previous command, initially
zero. Sparse matrices are assembled explicitly; no MPC framework is used. OSQP
is initialized for each horizon with the previous primal solution as a numerical
warm start. There is no claim of persistent factorization reuse or shifted warm
starts. Only the `solved` status is accepted. Feasibility is checked independently
against the assembled constraints; failures stop the run rather than fabricate a
fallback command. Solver tolerances are 1e-6; the independent constraint residual
threshold is 2e-5 in each row's native units.

| Quantity | Constraint |
|---|---|
| Steering | ±25 degrees |
| Steering rate | ±35 degrees/s |
| Acceleration command | -2.5 to +2.0 m/s² |
| Commanded jerk | ±3.0 m/s³ |
| Predicted vehicle speed | 1 to 10 m/s |

The speed constraint is on predicted states. The run separately checks the actual
nonlinear plant's sampled speed. This is validation of these runs, not a guarantee
for arbitrary disturbances. Commanded jerk does not include the sudden external
load applied to the disturbed plant.

## Experiments and metrics

- Variable-speed oval: 42 m and 25 m semiaxes, 52 s duration.
- Figure-eight: x = 45 sin(theta), y = 16 sin(2 theta), 64 s duration.
- Lane change: x = 5t, y = 3[tanh((t-9)/2)-tanh((t-19)/2)], 36 s duration.
  A global-y drift of +0.35 m/s and a longitudinal load of -0.6 m/s² act during
  [24, 26) seconds. They are not passed to the controller. The shaded x-region
  in the trajectory plot corresponds to the reference at that time interval.

Every scenario starts at -1 m along-track, +1.4 m cross-track, +8 degrees heading
error, and -0.7 m/s speed error. No startup or disturbance samples are removed
from the main metrics. Position RMSE is `sqrt(mean(dx² + dy²))`, computed against
the time-matched reference. Signed cross-track error uses the moving reference
frame; it is not Euclidean distance to the closest path point. The separately
named `cross_track_rmse_after_5s_m` metric excludes only the first five seconds.

The three full runs contain 1,520 QP solves and 1,523 state samples. Main measured
results are in `results/metrics.json`; the website reports rounded values from
that file. Local timing covers QP assembly, solver setup and solve. It excludes
plant integration and is not a real-time performance guarantee.

## Validation and scope

Five tests check reference derivatives, LPV Jacobians against finite differences,
RK4 constant-turn motion against an analytic circle, frame/sign/angle conventions,
and both the straight-line QP equilibrium and rejection of an infeasible problem.
All simulation runs also check finite states, optimizer success, input limits,
input-rate limits and sampled plant speeds.

This is a deterministic kinematic simulation. It does not model tire slip, actuator
lag, measurement noise, localization uncertainty, obstacles or collision avoidance.
It contains no hardware validation, robust-MPC proof, recursive feasibility proof,
or formal terminal invariant set. The small steady tracking errors rely on perfect
state information and an accurately known reference. Results must not be compared
directly with the earlier six-state/reference-code simulation as a benchmark gain.

## Concept and library references

- Earlier learning context: Mark Misin's LPV-MPC teaching project supplied by Ajay;
  its source remains in the separate legacy portfolio bundle, with its notices.
- [Adaptive path-following MPC overview](https://www.mathworks.com/help/mpc/ref/pathfollowingcontrolsystem.html)
  describes updating a vehicle prediction model as operating conditions change.
- [OSQP Python API](https://osqp.org/docs/interfaces/python.html) documents the
  numerical solver interface used here.
- [OSQP status codes](https://osqp.org/docs/interfaces/status_values.html) documents
  the status check. No example implementation from these references is copied.
