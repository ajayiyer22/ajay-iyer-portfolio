"""Vehicle equations and analytic reference paths, written for this project.

SI units throughout. The vehicle state is [x, y, heading, speed]; commands
are [front-wheel steering angle, longitudinal acceleration].
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Settings:
    dt: float = 0.1
    horizon: int = 20
    wheelbase: float = 2.7
    steering_limit: float = np.deg2rad(25.0)
    steering_rate: float = np.deg2rad(35.0)
    acceleration_min: float = -2.5
    acceleration_max: float = 2.0
    jerk_limit: float = 3.0
    speed_min: float = 1.0
    speed_max: float = 10.0


SCENARIOS = {
    "oval": (52.0, "Variable-speed oval"),
    "figure_eight": (64.0, "Figure-eight tracking"),
    "lane_change": (36.0, "Lane change + disturbance"),
}


def wrap(angle):
    return np.arctan2(np.sin(angle), np.cos(angle))


def reference(name, time, settings):
    """Analytic position and derivatives, including beyond the simulation end.

    No repeated final waypoint: the controller receives a continuous preview.
    Returns columns x, y, heading, speed, curvature, acceleration, steering.
    """
    t = np.atleast_1d(time).astype(float)
    if name in ("oval", "figure_eight"):
        omega = 2 * np.pi / SCENARIOS[name][0]
        phase = omega * t
        if name == "oval":
            x, y = 42 * np.cos(phase), 25 * np.sin(phase)
            dx, dy = -42 * omega * np.sin(phase), 25 * omega * np.cos(phase)
            ddx, ddy = -42 * omega**2 * np.cos(phase), -25 * omega**2 * np.sin(phase)
        else:
            x, y = 45 * np.sin(phase), 16 * np.sin(2 * phase)
            dx, dy = 45 * omega * np.cos(phase), 32 * omega * np.cos(2 * phase)
            ddx, ddy = -45 * omega**2 * np.sin(phase), -64 * omega**2 * np.sin(2 * phase)
    elif name == "lane_change":
        a, b = np.tanh((t - 9) / 2), np.tanh((t - 19) / 2)
        x, y = 5 * t, 3 * (a - b)
        dx, dy = np.full_like(t, 5), 1.5 * (b*b - a*a)
        ddx, ddy = np.zeros_like(t), 1.5 * (b * (1-b*b) - a * (1-a*a))
    else:
        raise ValueError(f"Unknown scenario: {name}")
    speed = np.hypot(dx, dy)
    curvature = (dx * ddy - dy * ddx) / speed**3
    acceleration = (dx * ddx + dy * ddy) / speed
    return np.column_stack((x, y, np.arctan2(dy, dx), speed, curvature,
                            acceleration, np.arctan(settings.wheelbase * curvature)))


def tracking_error(state, ref):
    """Signed along/cross-track errors in the time-indexed reference frame."""
    c, s = np.cos(ref[2]), np.sin(ref[2])
    dx, dy = state[:2] - ref[:2]
    return np.array([c*dx+s*dy, -s*dx+c*dy, wrap(state[2]-ref[2]), state[3]-ref[3]])


def error_dynamics(error, command, ref, settings):
    """Exact continuous tracking-error dynamics for the kinematic plant."""
    along, cross, heading, dv = error
    speed, curvature = ref[3:5]
    yaw_rate = speed * curvature
    return np.array([
        (speed+dv)*np.cos(heading)-speed+yaw_rate*cross,
        (speed+dv)*np.sin(heading)-yaw_rate*along,
        (speed+dv)*np.tan(command[0])/settings.wheelbase-yaw_rate,
        command[1]-ref[5],
    ])


def scheduled_model(ref, settings):
    """First-order LPV error approximation, scheduled by speed and curvature.

    e_dot = A(rho)e + B(rho)(u-u_ref), rho=[v_ref, curvature_ref].
    Forward-Euler prediction at 100 ms; the plant uses separate RK4 integration.
    """
    speed, curvature, _, steering = ref[3:7]
    yaw_rate = speed * curvature
    a = np.array([[0, yaw_rate, 0, 1], [-yaw_rate, 0, speed, 0],
                  [0, 0, 0, curvature], [0, 0, 0, 0]], dtype=float)
    b = np.zeros((4, 2))
    b[2, 0] = speed / (settings.wheelbase * np.cos(steering)**2)
    b[3, 1] = 1
    return np.eye(4) + settings.dt*a, settings.dt*b


def disturbance(name, time):
    """Unmodeled lateral drift and longitudinal load, active on [24, 26) s."""
    if name == "lane_change" and 24 <= time < 26:
        return np.array([0.35, -0.6])
    return np.zeros(2)


def advance(state, command, time, name, settings):
    """Integrate the nonlinear bicycle with five RK4 substeps; no clipping."""
    def derivative(z, t):
        drift, load = disturbance(name, t)
        x, y, yaw, speed = z
        return np.array([speed*np.cos(yaw), speed*np.sin(yaw)+drift,
                         speed*np.tan(command[0])/settings.wheelbase, command[1]+load])
    z = state.copy()
    h = settings.dt / 5
    for j in range(5):
        t = time + j*h
        k1 = derivative(z, t)
        k2 = derivative(z+h*k1/2, t+h/2)
        k3 = derivative(z+h*k2/2, t+h/2)
        # Left limit at a scheduled disturbance boundary avoids sampling the next interval.
        k4 = derivative(z+h*k3, np.nextafter(t+h, t))
        z += h*(k1+2*k2+2*k3+k4)/6
    z[2] = wrap(z[2])
    return z
