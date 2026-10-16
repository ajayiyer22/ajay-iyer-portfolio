"""Reproduce every scenario, raw sample, metric and portfolio figure."""
import argparse
from dataclasses import asdict
import hashlib
import importlib.metadata
import json
from pathlib import Path
import time
import numpy as np
from model import Settings, SCENARIOS, reference, tracking_error, advance
from controller import Controller


def simulate(name, cfg):
    duration = SCENARIOS[name][0]
    steps = round(duration/cfg.dt)
    times = np.arange(steps+1)*cfg.dt
    refs = reference(name, np.arange(steps+cfg.horizon+1)*cfg.dt, cfg)
    states = np.zeros((steps+1, 4))
    states[0] = refs[0, :4]
    # Same initial errors in every experiment, expressed in its own reference frame.
    yaw = refs[0, 2]
    states[0, :2] += [-1*np.cos(yaw)-1.4*np.sin(yaw), -1*np.sin(yaw)+1.4*np.cos(yaw)]
    states[0, 2] += np.deg2rad(8)
    states[0, 3] -= 0.7
    controls = np.zeros((steps, 2))
    errors = np.zeros((steps+1, 4))
    elapsed, violations, iterations = [], [], []
    controller = Controller(cfg)
    previous = np.zeros(2)
    for k in range(steps):
        errors[k] = tracking_error(states[k], refs[k])
        start = time.perf_counter()
        controls[k], violation, iteration = controller.command(
            errors[k], refs[k:k+cfg.horizon+1], previous)
        elapsed.append(1000*(time.perf_counter()-start))
        violations.append(violation)
        iterations.append(iteration)
        states[k+1] = advance(states[k], controls[k], times[k], name, cfg)
        previous = controls[k]
    errors[-1] = tracking_error(states[-1], refs[steps])
    rates = np.diff(np.vstack((np.zeros(2), controls)), axis=0)/cfg.dt
    position_error = np.linalg.norm(states[:, :2]-refs[:steps+1, :2], axis=1)
    metrics = {
        "duration_s": duration, "samples": steps+1, "qp_solves": steps,
        "position_rmse_m": float(np.sqrt(np.mean(position_error**2))),
        "cross_track_rmse_m": float(np.sqrt(np.mean(errors[:, 1]**2))),
        "max_position_error_m": float(np.max(position_error)),
        "cross_track_rmse_after_5s_m": float(np.sqrt(np.mean(errors[times>=5, 1]**2))),
        "speed_rmse_mps": float(np.sqrt(np.mean(errors[:, 3]**2))),
        "max_abs_steering_deg": float(np.rad2deg(np.max(np.abs(controls[:, 0])))),
        "max_abs_steering_rate_deg_s": float(np.rad2deg(np.max(np.abs(rates[:, 0])))),
        "acceleration_min_mps2": float(controls[:, 1].min()),
        "acceleration_max_mps2": float(controls[:, 1].max()),
        "max_abs_jerk_mps3": float(np.max(np.abs(rates[:, 1]))),
        "speed_min_mps": float(states[:, 3].min()), "speed_max_mps": float(states[:, 3].max()),
        "max_qp_constraint_violation": float(max(violations)),
        "controller_wall_time_median_ms": float(np.median(elapsed)),
        "controller_wall_time_p95_ms": float(np.percentile(elapsed, 95)),
        "max_qp_iterations": int(max(iterations)), "all_qps_solved": True,
    }
    if not np.isfinite(states).all():
        raise RuntimeError("Non-finite plant state")
    if (np.max(np.abs(controls[:, 0])) > cfg.steering_limit+2e-5
        or controls[:, 1].min() < cfg.acceleration_min-2e-5
        or controls[:, 1].max() > cfg.acceleration_max+2e-5
        or np.max(np.abs(rates[:, 0])) > cfg.steering_rate+2e-4
        or np.max(np.abs(rates[:, 1])) > cfg.jerk_limit+2e-4
        or states[:, 3].min() < cfg.speed_min-2e-4
        or states[:, 3].max() > cfg.speed_max+2e-4):
        raise RuntimeError("Applied control or simulated speed violated a configured limit")
    return dict(time=times, state=states, reference=refs[:steps+1], control=controls,
                error=errors, controller_ms=np.array(elapsed), metrics=metrics)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).parent/'results')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    cfg = Settings()
    results = {}
    for name in SCENARIOS:
        result = simulate(name, cfg)
        results[name] = result
        np.savez_compressed(args.output/f'{name}.npz', **{k:v for k,v in result.items() if k!='metrics'})
        count = len(result['time'])
        command = np.vstack((result['control'], np.full((1, 2), np.nan)))
        np.savetxt(args.output/f'{name}.csv', np.column_stack((result['time'], result['state'],
            result['reference'][:, :4], result['error'], command)), delimiter=',', comments='',
            header='time_s,x_m,y_m,yaw_rad,speed_mps,ref_x_m,ref_y_m,ref_yaw_rad,ref_speed_mps,along_error_m,cross_error_m,heading_error_rad,speed_error_mps,steering_rad,acceleration_mps2')
        print(f"{name}: {count} samples, position RMSE {result['metrics']['position_rmse_m']:.4f} m", flush=True)
    sources = sorted(Path(__file__).parent.glob('*.py'))
    report = {
        'implementation': 'Custom reference-scheduled LPV-MPC with nonlinear kinematic bicycle plant',
        'settings': asdict(cfg),
        'metric_scope': 'All samples including initial offset and disturbances; after_5s metric excludes only t < 5 s.',
        'timing_scope': 'Measured local wall time for QP construction, setup and solve; not a real-time guarantee.',
        'disturbance': 'Lane-change case only: global-y drift +0.35 m/s and longitudinal acceleration load -0.6 m/s^2 during [24,26) seconds; not provided to the controller.',
        'initial_error': {'along_m': -1, 'cross_m': 1.4, 'heading_deg': 8, 'speed_mps': -0.7, 'previous_input': [0, 0]},
        'packages': {p:importlib.metadata.version(p) for p in ['numpy','scipy','osqp','matplotlib','pillow']},
        'source_sha256': {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'scenarios': {name:r['metrics'] for name,r in results.items()},
    }
    (args.output/'metrics.json').write_text(json.dumps(report, indent=2)+'\n')
    from plots import render
    render(results, cfg, args.output)


if __name__ == '__main__':
    main()
