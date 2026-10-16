"""Refresh portfolio figures, measured results and source download after a run."""
import hashlib
import json
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'code/custom_lpv_mpc'
RESULTS = SOURCE/'results'
report = json.loads((RESULTS/'metrics.json').read_text())
for name, digest in report['source_sha256'].items():
    if hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() != digest:
        raise SystemExit(f'{name} changed since the simulation. Run run.py again first.')
for name in ['custom-lpv-paths', 'custom-lpv-errors', 'custom-lpv-constraints']:
    shutil.copy2(RESULTS/f'{name}.webp', ROOT/'assets/images'/f'{name}.webp')
shutil.copy2(RESULTS/'metrics.json', ROOT/'assets/downloads/custom-lpv-metrics.json')
with ZipFile(ROOT/'assets/downloads/Custom_LPV_MPC.zip', 'w', ZIP_DEFLATED) as archive:
    for path in sorted(SOURCE.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
            archive.write(path, Path('custom_lpv_mpc')/path.relative_to(SOURCE))
with ZipFile(ROOT/'assets/downloads/Custom_LPV_MPC.zip') as archive:
    if archive.testzip() is not None:
        raise SystemExit('Source archive verification failed.')
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
print('Published custom plots, verified source bundle and measured result table.')
