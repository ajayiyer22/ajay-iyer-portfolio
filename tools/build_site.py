#!/usr/bin/env python3
"""Generate the static portfolio. Uses Python standard-library tools."""
from pathlib import Path
from hashlib import sha256
import json
from html import escape as e

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'data/projects.json').read_text())
PROFILE = json.loads((ROOT / 'data/profile.json').read_text())
RESUME_PATH = 'assets/documents/Ajay_Iyer_Resume.pdf'
RESUME_URL = RESUME_PATH + '?v=' + sha256((ROOT / RESUME_PATH).read_bytes()).hexdigest()[:12]


def head(title, description, prefix=''):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description)}">
<meta name="theme-color" content="#164f42"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/site.css"><script src="{prefix}assets/site.js" defer></script></head><body id="top">
<a class="skip" href="#main">Skip to content</a>'''


def header(prefix=''):
    home = prefix + 'index.html' if prefix else ''
    return f'''<header class="site-header"><div class="container header-inner">
<a class="brand" href="{home or '#top'}">AJAY IYER<span>Robotics Software & Autonomy</span></a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation">Menu</button>
<nav class="nav" id="navigation" aria-label="Main navigation"><a href="{home}#about">About</a><a href="{home}#portfolio">Work</a><a href="{home}#experience">Experience</a><a href="{home}#contact">Contact</a><a class="nav-resume" href="{prefix}assets/documents/Ajay_Iyer_Resume.pdf">Resume ↗</a></nav>
</div></header>'''


def footer(prefix=''):
    return '''<footer class="site-footer"><div class="container footer-inner"><p>© 2026 Ajay Ganesan Iyer · College Station, Texas</p><p>Original template by <a href="https://templateflip.com">TemplateFlip</a> · Portfolio updated October 2026</p></div></footer></body></html>'''


def tags(p):
    return '<ul class="tag-list" aria-label="Tools and methods">' + ''.join(f'<li>{e(s)}</li>' for s in p['stack']) + '</ul>'


def visual(p, prefix='', loading='lazy'):
    if 'image' in p:
        return f'<img src="{prefix}assets/images/{e(p["image"])}" alt="{e(p["imageAlt"])}" loading="{loading}" decoding="async">'
    data = {
        'welding': ('Robotic welding', ['Register the workpiece', 'Plan the torch motion', 'Execute & monitor'], 'UR10e · Miller · Python / ROS'),
        'miko': ('Physical robot control', ['Model the dynamics', 'Close the feedback loop', 'Test the motion'], 'Articulation · Balance · Interaction'),
        'mpc': ('Predictive control', ['Predict vehicle motion', 'Optimize within limits', 'Apply & repeat'], '4 states · 20-step horizon · Python'),
        'frontier': ('Research scope', ['Observe the scene', 'Map semantic value', 'Choose the next view'], 'ROS 2 · Husky + Jackal'),
        'needle': ('Needle-tip estimation', ['Extract visual features', 'Estimate the state', 'Compare with ground truth'], 'Ultrasound · Kalman filtering')
    }
    label, steps, note = data[p['visual']]
    return f'<div class="diagram-preview"><p class="diagram-title">{e(label)}</p>' + ''.join(f'<div class="flow-line"><span>0{i}</span>{e(s)}</div>' for i,s in enumerate(steps,1)) + f'<small>{e(note)}</small></div>'


def card(p):
    url=f'projects/{p["slug"]}.html'
    recognition=f'<p class="recognition-badge">{e(p["recognition"])}</p>' if p.get('recognition') else ''
    return f'''<article class="project-card" data-category="{p['category']}"><a class="card-image" href="{url}" aria-label="Explore {e(p['title'])}">{visual(p)}</a>{recognition}<div class="status">{e(p['status'])}</div><h3><a href="{url}">{e(p.get('shortTitle',p['title']))}</a></h3><p>{e(p['summary'])}</p><a class="text-link" href="{url}">View project <span aria-hidden="true">↗</span></a></article>'''


def homepage():
    w=PROJECTS[0]
    body=head('Ajay Iyer | Robotics Software & Autonomous Systems', 'Robotics software portfolio: C++17, ROS 2, multi-robot exploration, PyTorch CUDA perception, autonomous vehicles and motion control. Mechanical Engineering Ph.D. student at Texas A&M.')+header()
    body+='''<main id="main"><div class="container"><section class="hero" aria-labelledby="hero-title"><div>
<p class="eyebrow">Mechanical Engineering Ph.D. student · Texas A&M</p><h1 id="hero-title">Ajay Ganesan Iyer</h1>
<p class="intro">I build robotics software that connects perception, planning and control to physical machines. My work spans autonomous navigation, robotic welding and interactive robots, with industry experience as a Robotics Engineer at MIKO.</p>
<a class="hero-recognition" href="#publications"><strong>Best Paper Award</strong><span>IEEE ICECA 2019 · Three-robot cooperative search</span></a><p class="availability">__OPPORTUNITY__</p>
<div class="actions"><a class="button" href="#portfolio">Explore projects <span aria-hidden="true">↘</span></a><a class="button secondary" href="assets/documents/Ajay_Iyer_Resume.pdf">View resume ↗</a></div></div>
<figure class="hero-portrait"><img src="assets/images/ajay-iyer.webp" width="1000" height="750" alt="Ajay Iyer outdoors overlooking a canyon" fetchpriority="high"><figcaption class="photo-note"><span>Ajay Ganesan Iyer</span><span>College Station, TX</span></figcaption></figure></section>
<div class="credentials"><span><strong>Texas A&M</strong> · Doctoral research</span><span><strong>MIKO</strong> · Robotics Engineer, 2021–2023</span><span><strong>IIT Roorkee</strong> · Systems & Control</span><span><strong>NIT Trichy</strong> · Instrumentation & Control</span></div></div>
<section class="section about-band" id="about"><div class="container about-layout"><div><p class="eyebrow">About</p><h2>About me</h2></div><div class="about-copy" id="skill">
<p class="lead">My work has taken me from a team of small robots searching for light to industrial welding, interactive robots and autonomous navigation. Across these projects, I have worked on the same practical question: how do we turn sensor measurements into useful robot motion?</p>
<p>At NIT Tiruchirappalli, I worked on a three-robot system that shared light measurements to find the brightest region in an arena. Our <a href="projects/robot-swarm.html">particle swarm search project</a> led to a paper that received a <strong>Best Paper Award at IEEE ICECA 2019</strong>. During my master’s in Systems and Control at IIT Roorkee, I studied robust vehicle platooning, with related work published at ACODS 2022, and combined image processing with Kalman filtering to improve ultrasound needle tracking.</p>
<p>As a <a href="projects/miko-robotics.html">Robotics Engineer at MIKO</a>, I brought that controls background to physical prototypes. I modeled mechanisms, developed expressive head motion, tuned a self-balancing robot and connected audio direction estimates to turning behavior. Working with the hardware meant testing how the models, sensors and controllers behaved together.</p>
<p>At Texas A&amp;M, my Ph.D. work has included <a href="projects/welding-automation.html">CAD-guided welding with a UR10e</a> and <a href="projects/autonomous-vehicles.html">perception and trajectory planning for rural roads</a>. These projects connected geometry, camera and LiDAR processing, motion planning and hardware interfaces in working robotics workflows.</p>
<p>I recently joined Dr. Srikanth Saripalli’s lab, where I am building on <a href="projects/frontier-exploration.html">Jackal hardware exploration and multi-robot simulation</a>. The research scope is efficient exploration of unknown outdoor environments through task allocation based on each robot’s mobility and sensing capabilities.</p>
</div></div></section>
<section class="section" id="portfolio"><div class="container"><div class="section-heading"><div><p class="eyebrow">Selected work</p><h2>Selected projects</h2></div><p>Research and engineering projects in autonomous systems, robotic manipulation, state estimation, and feedback control.</p></div>'''
    body+='''<div class="evidence-grid" aria-label="Selected project results"><a class="evidence-item" href="projects/needle-tracking.html"><strong>0.79 → 0.03 cm</strong><span>Needle-tip position RMSE</span><small>Image processing + Kalman filtering, tested in artificial tissue against an electromagnetic reference.</small></a><a class="evidence-item" href="projects/vehicle-mpc.html"><strong>1,520 successful solves</strong><span>Constrained vehicle tracking</span><small>Three simulation scenarios, with 0.289–0.396 m position RMSE including startup recovery.</small></a><a class="evidence-item" href="projects/frontier-exploration.html#demo"><strong>Physical robot deployment</strong><span>Autonomous Jackal exploration</span><small>LiDAR mapping, frontier selection and Nav2 navigation demonstrated on hardware.</small></a></div>'''
    body+=f'''<article class="featured"><a class="feature-visual" href="projects/{w['slug']}.html" aria-label="Explore multi-robot autonomy">{visual(w)}</a><div class="feature-content"><p class="eyebrow">Multi-robot autonomy</p><h3>{e(w['title'])}</h3><p>{e(w['summary'])}</p>{tags(w)}<a class="text-link" href="projects/{w['slug']}.html">View project ↗</a></div></article><div class="feature-bottom">'''
    for i,p in enumerate(PROJECTS[1:3],2):
        body+=f'''<article class="compact-feature"><span class="number">0{i}</span><p class="eyebrow">{e(p['eyebrow'])}</p><h3>{e(p.get('shortTitle',p['title']))}</h3><p>{e(p['summary'])}</p><a class="text-link" href="projects/{p['slug']}.html">View project ↗</a></article>'''
    body+='''</div><div class="section-heading" style="margin-top:32px"><div><p class="eyebrow">Project archive</p><h2>Project archive</h2></div><p>Project objectives, technical contributions and experimental results.</p></div>
<div class="project-filters" role="group" aria-label="Filter projects"><button class="filter" data-filter="all" aria-pressed="true">All work</button><button class="filter" data-filter="automation" aria-pressed="false">Automation</button><button class="filter" data-filter="autonomy" aria-pressed="false">Autonomy</button><button class="filter" data-filter="controls" aria-pressed="false">Controls & estimation</button></div><p id="filter-status" class="filter-status" role="status" aria-live="polite">9 projects shown</p><div class="project-grid">'''
    body+=''.join(card(p) for p in PROJECTS)
    body+='''</div><details class="extra-work"><summary>Earlier projects & demonstrations</summary><div class="extra-grid"><div><h3>UAV modeling and control</h3><p>A 2019 control-systems course project exploring UAV dynamics and control in MATLAB. The original simulation demonstration is available below.</p><a class="text-link" href="https://drive.google.com/file/d/1HM16QL9dJMWermskILlDSCBvRlfYO1c8/view">Open drone-control demonstration ↗</a></div><div><h3>Industrial and embedded control</h3><p>Earlier internships included PID and ON–OFF control for an absorption heat transformer at TU Berlin, PLC–LabVIEW communication, and a seat-stabilization prototype at NITIE.</p><a class="text-link" href="#earlier-experience">See earlier experience ↓</a></div></div><figure class="media-demo"><video controls preload="none" aria-label="UAV control simulation"><source src="images/drone_control%20(1080p).mp4" type="video/mp4">Your browser does not support video. <a href="images/drone_control%20(1080p).mp4">Download the demonstration.</a></video><figcaption>UAV control simulation · 2019 course project.</figcaption></figure></details></div></section>
<section class="section" id="experience"><div class="container"><div class="section-heading"><div><p class="eyebrow">Experience</p><h2>Experience</h2></div><a class="text-link" href="assets/documents/Ajay_Iyer_Resume.pdf">Read the full resume ↗</a></div>'''
    rows=[
      ('Aug 2026 – Present','Graduate Researcher','Texas A&M · Dr. Srikanth Saripalli','Developing cooperative target search from a physical Jackal exploration pipeline and a Husky-and-two-Jackal simulation. Integrated AMCL for map-based localization, EKF fusion of wheel encoder odometry and IMU measurements, shared mapping and Hungarian frontier allocation. The research scope investigates efficient exploration of unknown outdoor environments through task allocation based on robot mobility and sensing capabilities.','frontier-exploration'),
      ('Aug 2025 – Jul 2026','Graduate Research Assistant','Texas A&M · Dr. Reza Langari','Developed ROS 2 perception and Frenet trajectory planning for rural roads, integrating camera, LiDAR and radar processing. Built a separate OpenStreetMap driver-assistance prototype and analyzed visual-feature redundancy in driving models.','autonomous-vehicles'),
      ('Aug 2024 – Aug 2025','Graduate Research Assistant','Texas A&M · Dr. Prabhakar Pagilla','Developed a workflow from part registration to planned torch motion and synchronized welding. Later work connected infrared monitoring to process feedback.','welding-automation'),
      ('Jun 2021 – Jun 2023','Robotics Engineer','MIKO · Mumbai, India','Applied system identification and feedback control to expressive articulation and self-balancing robots, and connected audio direction estimates to yaw control.','miko-robotics')]
    for date,title,role,desc,slug in rows:
        body+=f'<article class="timeline-row"><div class="timeline-date">{date}</div><div><h3>{title}</h3><p class="role">{role}</p><p>{desc}</p><a href="projects/{slug}.html">Related work ↗</a></div></article>'
    body+='''<details class="extra-work" id="earlier-experience"><summary>Earlier internships · 2016–2018</summary><div class="extra-grid"><article><h3>Technical University of Berlin</h3><p>May–Jul 2018 · Simulation and control of absorption heat transformers using Siemens TIA Portal, PID and ON–OFF control, and communication between LabVIEW and PLC systems.</p></article><article><h3>Indian Institute of Technology, Bombay</h3><p>Jun–Jul 2017 · EKF-SLAM simulation in MATLAB and embedded obstacle-avoiding navigation on a SPARK-V robot.</p><a href="projects/ekf-slam.html">Read the project ↗</a></article><article><h3>NITIE · Seat stabilization</h3><p>Dec 2017 · A PID-controlled seat-stabilization prototype and physiological monitoring using heart-rate and accelerometer sensors.</p></article><article><h3>NITIE · AGV study</h3><p>Dec 2016–Jan 2017 · Study of automated guided vehicles, sensor classifications, and embedded sensing for interaction systems.</p></article></div></details>
<div class="education"><article><p class="eyebrow">Aug 2024 – Present</p><h3>Ph.D. · Mechanical Engineering</h3><p>Texas A&M University<br>College Station, Texas</p></article><article><p class="eyebrow">Completed June 2021</p><h3>M.Tech. · Systems and Control</h3><p>Indian Institute of Technology, Roorkee<br>India</p></article><article><p class="eyebrow">Completed May 2019</p><h3>B.Tech. · Instrumentation and Control</h3><p>National Institute of Technology, Tiruchirappalli<br>India</p></article></div></div></section>
<section class="section about-band" id="publications"><div class="container"><div class="section-heading"><div><p class="eyebrow">Publications & recognition</p><h2>Publications & recognition</h2></div><a class="text-link" href="https://scholar.google.com/citations?user=XCSeehYAAAAJ&hl=en">Google Scholar ↗</a></div>
<article class="publication"><div class="year">2019</div><div><p class="recognition-badge">Best Paper Award · IEEE ICECA 2019</p><h3>Particle Swarm Optimization Algorithm for Finding the Brightest Spot in an Arena</h3><p>M. Adharsh, Ajay G. Iyer, Abhinav G. Athrey, Ashwin V., Venkatesh V. G.</p><p>3rd IEEE International Conference on Electronics, Communication and Aerospace Technology (ICECA)</p><a class="text-link" href="projects/robot-swarm.html">Robot setup and experiments ↗</a></div></article><article class="publication"><div class="year">2022</div><div><h3>Sliding Mode Control Using Power Rate Exponential Reaching Law for Urban Platooning</h3><p>A. G. Iyer, J. Samantaray, S. Ghosh, A. Dey, S. Chakrabarty</p><p>7th International Conference on Advances in Control and Optimization of Dynamical Systems (ACODS)</p><a class="text-link" href="projects/vehicle-platooning.html">Related thesis and results ↗</a></div></article>
</div></section>
<section class="contact" id="contact"><div class="container contact-layout"><div><p class="eyebrow">Get in touch</p><h2>Contact</h2><p>Available for 2027 internships in robotics software, autonomous vehicles, perception integration, motion planning, and simulation.</p></div><div class="contact-links"><a href="mailto:ajay.iyer79@gmail.com">ajay.iyer79@gmail.com ↗</a><a href="mailto:ajayiyer2397@tamu.edu">ajayiyer2397@tamu.edu ↗</a><a href="https://www.linkedin.com/in/ajay-iyer-792299116/">LinkedIn ↗</a><a href="assets/documents/Ajay_Iyer_Resume.pdf" download>Download resume ↓</a></div></div></section></main>'''
    body = body.replace('__OPPORTUNITY__', e(PROFILE['opportunity']))
    (ROOT/'index.html').write_text((body+footer()).replace(RESUME_PATH, RESUME_URL))


def casepage(p, next_p):
    prefix='../'
    challenge_title=e(p.get('challengeTitle', 'The problem'))
    outcome_title=e(p.get('outcomeTitle', 'Results & scope'))
    body=head(p['title']+' | Ajay Iyer',p['summary'],prefix)+header(prefix)
    recognition=f'<p class="recognition-badge">{e(p["recognition"])}</p>' if p.get('recognition') else ''
    body+=f'''<main id="main"><div class="container"><header class="case-header"><a class="back-link" href="../index.html#portfolio">← All projects</a><p class="eyebrow">{e(p['eyebrow'])}</p><h1>{e(p['title'])}</h1>{recognition}<p class="dek">{e(p['summary'])}</p><div class="case-meta"><div><strong>Organization</strong>{e(p['organization'])}</div><div><strong>Role & period</strong>{e(p['role'])}<br>{e(p['date'])}</div><div><strong>Project context</strong>{e(p['status'])}</div></div>{tags(p)}</header><figure class="case-cover">{visual(p,prefix,'eager')}'''
    if p.get('imageCaption'):body+=f'<figcaption>{e(p["imageCaption"])}</figcaption>'
    body+=f'</figure><div class="case-layout"><nav class="case-nav" aria-label="On this page"><h2>In this project</h2><a href="#challenge">{challenge_title}</a>'
    body+='<a href="#contributions">Approach & implementation</a>'
    body+=f'<a href="#outcome">{outcome_title}</a>'

    if p.get('researchScope'):body+='<a href="#research-scope">Research scope</a>'
    if p.get('benchmark'):body+=f'<a href="#evaluation">{e(p["benchmark"]["title"])}</a>'
    if p.get('gallery'):body+='<a href="#gallery">Project images</a>'
    if p.get('video') or p.get('externalVideo'):body+='<a href="#demo">Demonstration</a>'
    if p.get('resources'):body+='<a href="#resources">Read more</a>'
    body+='</nav><div class="case-body">'
    body+=f'<section id="challenge"><h2>{challenge_title}</h2><p>{e(p["challenge"])}</p>'
    if p.get('steps'):body+='<ol class="process" aria-label="System workflow">'+''.join(f'<li>{e(step)}</li>' for step in p['steps'])+'</ol>'
    body+='</section>'
    body+='<section id="contributions"><h2>Approach & implementation</h2><ul class="contribution-list">'
    for title, text in p.get('contributions', []):
        body+=f'<li><strong>{e(title)}.</strong> {e(text)}</li>'
    body+='</ul></section>'
    body+=f'<section id="outcome"><h2>{outcome_title}</h2><p>{e(p["outcome"])}</p>'
    if p.get('resultsTable'):
        t=p['resultsTable']
        body+='<div class="results-scroll" role="region" aria-label="Simulation results" tabindex="0"><table class="results-table"><caption>'+e(t['caption'])+'</caption><thead><tr>'
        body+=''.join(f'<th scope="col">{e(h)}</th>' for h in t['headers'])+'</tr></thead><tbody>'
        for row in t['rows']:
            body+=f'<tr><th scope="row">{e(row[0])}</th>'+''.join(f'<td>{e(v)}</td>' for v in row[1:])+'</tr>'
        body+='</tbody></table></div>'
    body+='</section>'
    if p.get('researchScope'):
        scope=p['researchScope']
        body+=f'<section id="research-scope"><h2>Research scope</h2><p>{e(scope["overview"])}</p>'
        if scope['directions']:body+='<ul class="contribution-list">'
        for title, text in scope['directions']:
            body+=f'<li><strong>{e(title)}.</strong> {e(text)}</li>'
        if scope['directions']:body+='</ul>'
        body+='</section>'
    if p.get('benchmark'):
        b=p['benchmark']
        body+=f'<section id="evaluation"><h2>{e(b["title"])}</h2><p>{e(b["text"])}</p>'
        if b.get('references'):
            body+='<ul class="resource-list">'
            for title,url in b['references']:
                body+=f'<li><a href="{e(url)}">{e(title)} ↗</a></li>'
            body+='</ul>'
        body+='</section>'
    if p.get('gallery'):
        gallery_class='gallery gallery-wide' if p.get('wideGallery') else 'gallery'
        body+=f'<section id="gallery"><h2>A closer look</h2><div class="{gallery_class}">'
        for file,alt,caption in p['gallery']:
            body+=f'<figure><a href="../assets/images/{e(file)}" aria-label="View full-size image: {e(alt)}"><img loading="lazy" src="../assets/images/{e(file)}" alt="{e(alt)}"></a><figcaption>{e(caption)}</figcaption></figure>'
        body+='</div></section>'
    if p.get('externalVideo'):
        video=p['externalVideo']
        url=e(video['url'])
        body+='<section id="demo"><h2>Jackal hardware demonstration</h2>'
        if p.get('videoDescription'):body+=f'<p>{e(p["videoDescription"])}</p>'
        if video.get('youtubeId'):
            body+=f'<div class="demo-player"><iframe loading="lazy" src="https://www.youtube-nocookie.com/embed/{e(video["youtubeId"])}" title="{e(video["title"])}" referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>'
        elif video.get('preview'):
            body+=f'<a class="demo-preview" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{e(video["title"])} (opens in a new tab)"><img loading="lazy" src="../assets/images/{e(video["preview"])}" alt="{e(video["previewAlt"])}"><span aria-hidden="true">▶ Watch demonstration ↗</span></a>'
        body+=f'<p><a class="text-link" href="{url}" target="_blank" rel="noopener noreferrer">{e(video["title"])} ↗</a></p></section>'
    if p.get('video'):
        vid=p['video'];title=e(p['videoTitle'])
        body+=f'''<section id="demo"><h2>Watch the system</h2><div class="video-shell"><a class="video-button" href="https://drive.google.com/file/d/{vid}/view" target="_blank" rel="noopener noreferrer">▶ Watch {title.lower()} ↗</a></div><p class="video-fallback">Opens the video on Google Drive in a new tab.</p></section>'''
    if p.get('resources'):
        body+=f'<section class="resources" id="resources"><h2>{e(p.get("resourcesTitle", "Read more"))}</h2><ul class="resource-list">'
        for title,url in p['resources']:
            link=url if url.startswith('https://') else prefix+url
            body+=f'<li><a href="{e(link)}">{e(title)} ↗</a></li>'
        body+='</ul>'
        if p.get('sourceNote'):body+=f'<p class="source-note">{e(p["sourceNote"])}</p>'
        body+='</section>'
    elif p.get('sourceNote'):
        body+=f'<p class="source-note">{e(p["sourceNote"])}</p>'
    if p.get('methodReferences'):
        body+='<details class="method-references"><summary>Method references</summary><ul class="resource-list">'
        for title,url in p['methodReferences']:
            body+=f'<li><a href="{e(url)}">{e(title)} ↗</a></li>'
        body+='</ul></details>'
    body+=f'</div></div><div class="next-project"><a href="../index.html#portfolio">← Back to all work</a><div><p>Explore next</p><a href="{next_p["slug"]}.html">{e(next_p.get("shortTitle",next_p["title"]))} →</a></div></div></div></main>'
    (ROOT/'projects'/f'{p["slug"]}.html').write_text((body+footer(prefix)).replace(RESUME_PATH, RESUME_URL))


if __name__=='__main__':
    homepage()
    for i,p in enumerate(PROJECTS):casepage(p,PROJECTS[(i+1)%len(PROJECTS)])
    print(f'Built homepage and {len(PROJECTS)} project pages.')
