# Ajay Iyer — Robotics, Automation & Controls

A static portfolio website with a homepage and nine project case studies. It works with GitHub Pages and requires no server-side software or Node build step.

## Preview locally

From this folder:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765. Stop the preview with Ctrl+C in its terminal.

## Publish with GitHub Pages

This folder is a standalone Git repository with `index.html` at the root. Connect it to the intended GitHub repository and push `main`. To publish, configure GitHub Pages to serve the root of that branch. The website has not yet been published.

The updated ZIP contains the active website files, editing tools, license credit, and current résumé compatibility links. The original downloaded website ZIP remains unchanged outside this folder.

## Edit the content

- `data/projects.json`: titles, descriptions, contributions, results, images, links, and project metadata.
- `tools/build_site.py`: shared page layout and homepage biography, experience, education, and publications.
- `assets/site.css`: responsive styling.
- `assets/site.js`: mobile navigation and project filters.
- `assets/images/`: project photographs, report figures, and simulation plots.
- `assets/documents/`: résumé and project reports.
- `assets/downloads/`: custom LPV-MPC source/data bundle and measurements; the older attributed reference bundle is retained for compatibility.
- `code/custom_lpv_mpc/`: new controller, simulator, scenarios, tests, reproducible plots, and model derivation.

After editing content, regenerate the HTML and check links:

```sh
python3 tools/build_site.py
python3 tools/check_site.py
```

Both commands use the Python standard library. GitHub Pages serves the generated HTML directly; Python is only an optional editing tool.

## Content and attribution

The portfolio uses the supplied résumé, original website demonstrations, welding report and implementation, AVA technical overview, master's thesis, bachelor's thesis, and IIT Bombay internship report. Source notes appear with each project.

- Welding photographs and GUI images are extracted from the supplied project report. The closed-loop description reflects Ajay's confirmation that this work was completed; the older report predates that completion. Literature links are evaluation references, not claims of measured benchmark scores. The proprietary welding source is not included.
- AVA lane and segmentation figures are labeled as the team's initial LaneATT/PSPNet baselines. They are not attributed to Ajay's later CLRerNet/SAM results.
- The primary MPC page now presents a fresh four-state kinematic LPV-MPC implementation, three custom scenarios, and new plots. The application code was developed with AI coding assistance and uses standard scientific libraries plus OSQP. The earlier Mark Misin-based learning project remains the conceptual context; its unmodified source archive and notices remain in the legacy download. No reference code is included in the new custom source bundle. The reference author's UAV thesis is not distributed.
- Ongoing semantic exploration work is labeled as research in progress.
- EKF-SLAM simulation and embedded SPARK-V navigation are described separately.
- The local drone video and existing Google Drive links are retained from the original website. Drive videos open directly in a new tab to avoid blank embedded players; access depends on their external sharing settings.
- Original template credit and license files are retained.

## Verification

The generated site was checked for local link and anchor integrity, image descriptions, served assets, project filters, mobile navigation, and desktop/mobile layout. All ten pages and local file targets passed the static link check. No ROS hardware or live robotics simulation was launched.

The new custom LPV-MPC experiment has 1,520 successful QP solves across three scenarios. Full-run position RMSE is 0.318 m (oval), 0.289 m (figure-eight), and 0.396 m (disturbed lane change), including startup error and disturbances. Five numerical tests pass, and every run checks commands, rates and sampled speed against configured limits. This is kinematic simulation with perfect state feedback, not hardware validation. The original six-state replay is preserved separately and is not used as a comparison benchmark.

To regenerate the custom data and website assets after editing the controller:

```sh
python code/custom_lpv_mpc/run.py
python tools/publish_custom_mpc.py
python tools/build_site.py
python tools/check_site.py
```

See `code/custom_lpv_mpc/README.md` for environment setup and the derivation. The publishing tool checks source hashes before copying results, so stale plots cannot be published as a run of changed source.
