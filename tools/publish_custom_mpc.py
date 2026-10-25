"""Refresh portfolio figures and measured results from local experiment files."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent/'portfolio_project_sources/custom_lpv_mpc'
RESULTS = SOURCE/'results'
report = json.loads((RESULTS/'metrics.json').read_text())
for name, digest in report['source_sha256'].items():
    if hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() != digest:
        raise SystemExit(f'{name} changed since the simulation. Run run.py again first.')
for name in ['paths', 'errors', 'constraints']:
    shutil.copy2(RESULTS/f'custom-lpv-{name}.webp', ROOT/'assets/images'/f'vehicle-tracking-{name}.webp')
report['implementation'] = 'Precision Vehicle Tracking and Disturbance Recovery: reference-scheduled LPV-MPC with nonlinear kinematic bicycle plant'
(ROOT/'assets/downloads/vehicle-tracking-metrics.json').write_text(json.dumps(report, indent=2)+'\n')
data = json.loads((ROOT/'data/projects.json').read_text())
project = next(p for p in data if p['slug'] == 'vehicle-mpc')
labels = {'oval': 'Variable-speed oval', 'figure_eight': 'Figure-eight', 'lane_change': 'Disturbed lane change'}
project['resultsTable'] = {
    'caption': 'Full-run errors, including startup and the lane-change disturbance.',
    'headers': ['Scenario', 'Position RMSE (m)', 'Cross-track RMSE (m)'],
    'rows': [[labels[name], f"{m['position_rmse_m']:.3f}", f"{m['cross_track_rmse_m']:.3f}"]
             for name, m in report['scenarios'].items()]
}
(ROOT/'data/projects.json').write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')
print('Published vehicle tracking plots and measured result table.')
