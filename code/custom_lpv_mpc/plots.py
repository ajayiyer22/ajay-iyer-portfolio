"""Standard Matplotlib figures generated from the closed-loop simulation data."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from model import SCENARIOS


def save(fig, output, name):
    """Save scientific figures and a matching web-sized format."""
    fig.savefig(output/f'{name}.png', dpi=200, bbox_inches='tight')
    fig.savefig(output/f'{name}.svg', bbox_inches='tight')
    with Image.open(output/f'{name}.png') as im:
        im.save(output/f'{name}.webp', quality=95)
    plt.close(fig)


def format_axis(ax, xlabel, ylabel):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle=':', linewidth=0.7, alpha=0.65)
    ax.set_axisbelow(True)
    ax.tick_params(direction='in', top=True, right=True)


def render(results, cfg, output):
    # Explicitly use Matplotlib's standard scientific appearance, not site branding.
    with plt.style.context('default'), plt.rc_context({
        'font.size': 10, 'axes.titlesize': 11, 'axes.labelsize': 10,
        'legend.fontsize': 8, 'figure.facecolor': 'white',
        'axes.facecolor': 'white', 'savefig.facecolor': 'white',
        'svg.fonttype': 'none',
    }):
        fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.8), layout='constrained')
        fig.suptitle('LPV-MPC trajectory tracking', fontsize=13)
        for ax, (name, r) in zip(axes, results.items()):
            ref, state = r['reference'], r['state']
            ax.plot(ref[:, 0], ref[:, 1], '--', color='tab:orange', lw=2,
                    label='Reference trajectory')
            ax.plot(state[:, 0], state[:, 1], color='tab:blue', lw=1.2,
                    label='Vehicle trajectory')
            ax.plot(*state[0, :2], 'o', color='tab:green', ms=4, label='Initial position')
            title = SCENARIOS[name][1]
            ax.set_title(f"{title}\nPosition RMSE = {r['metrics']['position_rmse_m']:.3f} m")
            format_axis(ax, 'x [m]', 'y [m]')
            if name == 'lane_change':
                ax.axvspan(120, 130, color='gray', alpha=0.15,
                           label='Reference region: 24–26 s')
                ax.set_ylim(-3, 11)
                ax.text(0.98, 0.03, 'Unequal x/y scales', transform=ax.transAxes,
                        ha='right', fontsize=8)
            else:
                ax.set_aspect('equal', adjustable='datalim')
                ax.margins(0.15)
            ax.legend(loc='upper right')
        save(fig, output, 'custom-lpv-paths')

        fig, axes = plt.subplots(2, 3, figsize=(13.5, 6.8), sharex='col',
                                 sharey='row', layout='constrained')
        fig.suptitle('LPV-MPC tracking errors', fontsize=13)
        for col, (name, r) in enumerate(results.items()):
            for row, (idx, label) in enumerate([(1, 'Cross-track error [m]'),
                                                (3, 'Speed error [m/s]')]):
                ax = axes[row, col]
                ax.axhline(0, color='black', lw=0.7)
                ax.plot(r['time'], r['error'][:, idx], color='tab:blue', lw=1.4,
                        label='Tracking error')
                format_axis(ax, 'Time [s]', label)
                if row == 0:
                    ax.set_title(SCENARIOS[name][1])
                if name == 'lane_change':
                    ax.axvspan(24, 26, color='gray', alpha=0.2, label='Disturbance: 24–26 s')
                ax.legend(loc='upper right')
        save(fig, output, 'custom-lpv-errors')

        r = results['figure_eight']
        fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True, layout='constrained')
        fig.suptitle('Figure-eight: control inputs and input rates', fontsize=13)
        t, u = r['time'][:-1], r['control']
        rates = np.diff(np.vstack((np.zeros(2), u)), axis=0)/cfg.dt
        series = [
            (np.rad2deg(u[:, 0]), 'Steering angle', r'$\delta$ [deg]',
             -np.rad2deg(cfg.steering_limit), np.rad2deg(cfg.steering_limit)),
            (u[:, 1], 'Acceleration command', r'$a$ [m/s$^2$]',
             cfg.acceleration_min, cfg.acceleration_max),
            (np.rad2deg(rates[:, 0]), 'Steering rate', r'$\Delta\delta/\Delta t$ [deg/s]',
             -np.rad2deg(cfg.steering_rate), np.rad2deg(cfg.steering_rate)),
            (rates[:, 1], 'Commanded jerk', r'$\Delta a/\Delta t$ [m/s$^3$]',
             -cfg.jerk_limit, cfg.jerk_limit),
        ]
        for ax, (values, title, ylabel, lo, hi) in zip(axes.flat, series):
            ax.step(t, values, where='post', color='tab:blue', lw=1.2, label='Applied input / rate')
            ax.axhline(lo, color='tab:red', linestyle='--', lw=1, label='Constraint bounds')
            ax.axhline(hi, color='tab:red', linestyle='--', lw=1)
            ax.set_title(title)
            format_axis(ax, 'Time [s]', ylabel)
            ax.set_ylim(lo-0.22*(hi-lo), hi+0.22*(hi-lo))
            ax.legend(loc='upper right')
        save(fig, output, 'custom-lpv-constraints')
