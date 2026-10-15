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
- `assets/downloads/`: attributed MPC source bundle and replay measurements.

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
- MPC applies reference LPV-MPC theory. The supplied Python files credit Mark Misin; those notices are preserved in the downloadable source bundle and plot attribution. The replay uses the supplied default circuit configuration and does not modify the controller/model. The bundled UAV thesis belongs to the reference author and is not published as Ajay's work.
- Ongoing semantic exploration work is labeled as research in progress.
- EKF-SLAM simulation and embedded SPARK-V navigation are described separately.
- The local drone video and existing Google Drive links are retained from the original website. Drive videos open directly in a new tab to avoid blank embedded players; access depends on their external sharing settings.
- Original template credit and license files are retained.

## Verification

The generated site was checked for local link and anchor integrity, image descriptions, served assets, project filters, mobile navigation, and desktop/mobile layout. All ten pages and local file targets passed the static link check. No ROS hardware or live robotics simulation was launched.

The MPC circuit replay is a separate numerical simulation: 154 simulation seconds, 7,701 samples, 1.01035 m Euclidean position RMSE, 5.04749 m peak error, and 22.6237° maximum absolute steering command. These are simulated results for that configuration, not real-time or hardware-performance measurements.
