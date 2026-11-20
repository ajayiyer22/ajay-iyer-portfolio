#!/usr/bin/env python3
"""Generate the static portfolio. Uses Python standard-library tools."""
from pathlib import Path
from hashlib import sha256
import json
from html import escape as e

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = json.loads((ROOT / 'data/projects.json').read_text())
STYLE_VERSION = sha256((ROOT / 'assets/site.css').read_bytes()).hexdigest()[:12]
RESUME_PATH = 'assets/documents/Ajay_Iyer_Resume.pdf'
RESUME_URL = RESUME_PATH + '?v=' + sha256((ROOT / RESUME_PATH).read_bytes()).hexdigest()[:12]


def head(title, description, prefix=''):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description)}">
<meta name="theme-color" content="#164f42"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/site.css?v={STYLE_VERSION}"><script src="{prefix}assets/site.js" defer></script></head><body id="top">
<a class="skip" href="#main">Skip to content</a>'''


def header(prefix=''):
    home = prefix + 'index.html' if prefix else ''
    return f'''<header class="site-header"><div class="container header-inner">
<a class="brand" href="{home or '#top'}">Ajay Iyer</a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation">Menu</button>
<nav class="nav" id="navigation" aria-label="Main navigation"><a href="{home}#about">About</a><a href="{home}#portfolio">Work</a><a href="{home}#publications">Publications</a><a href="{home}#experience">Experience</a><a href="{home}#contact">Contact</a><a class="nav-resume" href="{prefix}assets/documents/Ajay_Iyer_Resume.pdf">Resume </a></nav>
</div></header>'''


def footer(prefix=''):
    return '''<footer class="site-footer"><div class="container footer-inner"><p>© 2026 Ajay Ganesan Iyer · College Station, Texas</p><p>Original template by <a href="https://templateflip.com">TemplateFlip</a> · Updated November 2026</p></div></footer></body></html>'''


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
    return f'''<article class="project-card" data-category="{p['category']}"><a class="card-image" href="{url}" aria-label="Explore {e(p['title'])}">{visual(p)}</a>{recognition}<div class="status">{e(p['status'])}</div><h3><a href="{url}">{e(p.get('shortTitle',p['title']))}</a></h3><p>{e(p['summary'])}</p><a class="text-link" href="{url}">View project <span aria-hidden="true"></span></a></article>'''


def project_entry(p):
    url=f'projects/{p["slug"]}.html'
    image=p.get('image')
    alt=p.get('imageAlt', '')
    if p['slug']=='frontier-exploration':
        image='jackal-lab.webp'
        alt='Physical Jackal robot with onboard display and LiDAR in the laboratory'
    picture=f'<img src="assets/images/{e(image)}" alt="{e(alt)}" loading="lazy" decoding="async">' if image else visual(p)
    notes={
        'frontier-exploration': 'Jackal hardware demonstration · Husky and Jackal team in simulation',
        'welding-automation': 'UR10e manipulator · CAD registration · Coordinated welding',
        'miko-robotics': 'Industry experience · Articulation, balance and audio-directed motion',
        'robot-swarm': 'Best Paper Award · IEEE ICECA 2019',
        'vehicle-platooning': 'Related publication · ACODS 2022',
        'vehicle-mpc': 'Simulation: 0.289–0.396 m position RMSE across three scenarios',
        'needle-tracking': 'Artificial-tissue position RMSE: 0.79 → 0.03 cm versus vision-only tracking',
    }
    note=f'<p class="project-result">{e(notes[p["slug"]])}</p>' if p['slug'] in notes else ''
    links=f'<a href="{url}">Project details</a>'
    if p.get('externalVideo'):links+=f'<a href="{e(p["externalVideo"]["url"])}" target="_blank" rel="noopener noreferrer">Video</a>'
    return f'''<article class="project-card" data-category="{e(p['category'])}"><a class="project-image" href="{url}" aria-label="{e(p['title'])}">{picture}</a><div class="project-copy"><p class="project-meta">{e(p['organization'])} · {e(p['date'])}</p><h3><a href="{url}">{e(p['title'])}</a></h3><p>{e(p['summary'])}</p>{note}<div class="project-links">{links}</div></div></article>'''


def homepage():
    body=head('Ajay Iyer | Robotics, Planning & Control', 'Ajay Ganesan Iyer, Mechanical Engineering Ph.D. student at Texas A&M. Robotics research and industry experience in autonomous navigation, perception and control.')+header()
    body+='''<main id="main"><section class="profile container" id="about" aria-labelledby="hero-title"><div class="profile-copy"><p class="profile-role">Ajay Ganesan Iyer</p><h1 id="hero-title">Hi, I’m Ajay.</h1>
<p>I’m a Ph.D. student in Mechanical Engineering at Texas A&amp;M University, working with Dr. Srikanth Saripalli. I’m interested in how robots use what they sense to decide where to go and how to move.</p>
<p>I recently started working on <a href="projects/frontier-exploration.html">cooperative robot exploration</a>: how a team can efficiently explore an unknown outdoor environment by assigning tasks according to each robot’s capabilities. My work so far includes frontier exploration on a physical Jackal and a multi-robot simulation with a Husky and two Jackals.</p>
<p>Before this, I worked on <a href="projects/autonomous-vehicles.html">perception and planning for rural roads</a> and <a href="projects/welding-automation.html">robotic welding</a> at Texas A&amp;M. Previously, I was a <a href="projects/miko-robotics.html">Robotics Engineer at MIKO</a>, where I developed motion control for expressive and self-balancing robot prototypes. I earned my master’s in Systems and Control from IIT Roorkee and my bachelor’s in Instrumentation and Control from NIT Tiruchirappalli.</p>
<div class="profile-links"><a href="assets/documents/Ajay_Iyer_Resume.pdf">Resume</a><a href="mailto:ajayiyer2397@tamu.edu">Email</a><a href="https://scholar.google.com/citations?user=XCSeehYAAAAJ&amp;hl=en">Google Scholar</a><a href="https://www.linkedin.com/in/ajay-iyer-792299116/">LinkedIn</a></div></div>
<figure class="profile-photo"><img src="assets/images/ajay-iyer.webp" width="1000" height="750" alt="Ajay Ganesan Iyer" fetchpriority="high"><figcaption>College Station, Texas</figcaption></figure></section>
<div class="container">
  <aside class="recognition-note" aria-label="Research recognition">
    <span class="recognition-label">Recognition</span>
    <p><strong>Best Paper Award · IEEE ICECA 2019.</strong> I co-authored the paper based on our undergraduate research at NIT Tiruchirappalli. We implemented particle swarm optimization on three LEGO NXT robots that shared light readings to find the brightest spot in an arena. <a href="projects/robot-swarm.html">See the robot swarm project</a>.</p>
  </aside>
</div>
<section class="section container" id="portfolio"><div class="section-heading"><h2>Research &amp; engineering projects</h2><p>Implemented systems, hardware demonstrations and simulation studies.</p></div>
<div class="project-filters" role="group" aria-label="Filter projects"><button class="filter" data-filter="all" aria-pressed="true">All projects</button><button class="filter" data-filter="autonomy" aria-pressed="false">Autonomy</button><button class="filter" data-filter="automation" aria-pressed="false">Automation</button><button class="filter" data-filter="controls" aria-pressed="false">Control &amp; estimation</button></div><p id="filter-status" class="filter-status" role="status" aria-live="polite">9 projects shown</p><div class="project-list">'''
    order=['frontier-exploration','autonomous-vehicles','welding-automation','miko-robotics','vehicle-platooning','robot-swarm','vehicle-mpc','needle-tracking','ekf-slam']
    by_slug={p['slug']:p for p in PROJECTS}
    body+=''.join(project_entry(by_slug[slug]) for slug in order)
    body+='''</div></section><section class="section" id="experience"><div class="container"><div class="section-heading"><h2>Experience</h2><a href="assets/documents/Ajay_Iyer_Resume.pdf">Full resume</a></div>'''
    rows=[
      ('Aug 2026 – Present','Graduate Researcher','Texas A&M · Dr. Srikanth Saripalli','Developing cooperative target search from a physical Jackal exploration pipeline and a Husky-and-two-Jackal simulation. Connected SLAM scan matching and platform odometry to LiDAR mapping, frontier selection and Nav2 navigation. The research scope investigates efficient exploration of unknown outdoor environments through task allocation based on robot mobility and sensing capabilities.','frontier-exploration'),
      ('Aug 2025 – Jul 2026','Graduate Research Assistant','Texas A&M · Dr. Reza Langari','Developed ROS 2 perception and Frenet trajectory planning for rural roads, integrating camera, LiDAR and radar processing. Built a separate OpenStreetMap driver-assistance prototype and analyzed visual-feature redundancy in driving models.','autonomous-vehicles'),
      ('Aug 2024 – Aug 2025','Graduate Research Assistant','Texas A&M · Dr. Prabhakar Pagilla','Developed a workflow from part registration to planned torch motion and synchronized welding. Later work connected infrared monitoring to process feedback.','welding-automation'),
      ('Jun 2021 – Jun 2023','Robotics Engineer','MIKO · Mumbai, India','Applied system identification and feedback control to expressive articulation and self-balancing robots, and connected audio direction estimates to yaw control.','miko-robotics')]
    for date,title,role,desc,slug in rows:
        body+=f'<article class="timeline-row"><div class="timeline-date">{date}</div><div><h3>{title}</h3><p class="role">{role}</p><p>{desc}</p><a href="projects/{slug}.html">Related work </a></div></article>'
    body+='''<details class="extra-work" id="earlier-experience"><summary>Earlier internships · 2016–2018</summary><div class="extra-grid"><article><h3>Technical University of Berlin</h3><p>May–Jul 2018 · Simulation and control of absorption heat transformers using Siemens TIA Portal, PID and ON–OFF control, and communication between LabVIEW and PLC systems.</p></article><article><h3>Indian Institute of Technology, Bombay</h3><p>Jun–Jul 2017 · EKF-SLAM simulation in MATLAB and embedded obstacle-avoiding navigation on a SPARK-V robot.</p><a href="projects/ekf-slam.html">Read the project </a></article><article><h3>NITIE · Seat stabilization</h3><p>Dec 2017 · A PID-controlled seat-stabilization prototype and physiological monitoring using heart-rate and accelerometer sensors.</p></article><article><h3>NITIE · AGV study</h3><p>Dec 2016–Jan 2017 · Study of automated guided vehicles, sensor classifications, and embedded sensing for interaction systems.</p></article></div></details>
<div class="education"><article><p class="eyebrow">Aug 2024 – Present</p><h3>Ph.D. · Mechanical Engineering</h3><p>Texas A&M University<br>College Station, Texas</p></article><article><p class="eyebrow">Completed June 2021</p><h3>M.Tech. · Systems and Control</h3><p>Indian Institute of Technology, Roorkee<br>India</p></article><article><p class="eyebrow">Completed May 2019</p><h3>B.Tech. · Instrumentation and Control</h3><p>National Institute of Technology, Tiruchirappalli<br>India</p></article></div></div></section>
<section class="section about-band" id="publications"><div class="container"><div class="section-heading"><div><h2>Publications</h2></div><a class="text-link" href="https://scholar.google.com/citations?user=XCSeehYAAAAJ&hl=en">Google Scholar </a></div>
<article class="publication"><div class="year">2019</div><div><p class="paper-award">Best Paper Award · IEEE ICECA 2019</p><h3>Particle Swarm Optimization Algorithm for Finding the Brightest Spot in an Arena</h3><p>M. Adharsh, <strong>Ajay G. Iyer</strong>, Abhinav G. Athrey, Ashwin V., Venkatesh V. G.</p><p>3rd IEEE International Conference on Electronics, Communication and Aerospace Technology (ICECA)</p><a class="text-link" href="projects/robot-swarm.html">Robot setup and experiments </a></div></article><article class="publication"><div class="year">2022</div><div><h3>Sliding Mode Control Using Power Rate Exponential Reaching Law for Urban Platooning</h3><p><strong>A. G. Iyer</strong>, J. Samantaray, S. Ghosh, A. Dey, S. Chakrabarty</p><p>7th International Conference on Advances in Control and Optimization of Dynamical Systems (ACODS)</p><a class="text-link" href="projects/vehicle-platooning.html">Related thesis and results </a></div></article>
</div></section>
'''
    body+='''<section class="section contact" id="contact"><div class="container"><h2>Get in touch</h2><div class="contact-links"><a href="mailto:ajayiyer2397@tamu.edu">ajayiyer2397@tamu.edu</a><a href="mailto:ajay.iyer79@gmail.com">ajay.iyer79@gmail.com</a><a href="assets/documents/Ajay_Iyer_Resume.pdf">Download resume</a></div></div></section></main>'''
    (ROOT/'index.html').write_text((body+footer()).replace(RESUME_PATH,RESUME_URL))


def casepage(p, next_p):
    prefix='../'
    challenge_title=e(p.get('challengeTitle', 'The problem'))
    outcome_title=e(p.get('outcomeTitle', 'Results & scope'))
    body=head(p['title']+' | Ajay Iyer',p['summary'],prefix)+header(prefix)
    recognition=f'<p class="recognition-badge">{e(p["recognition"])}</p>' if p.get('recognition') else ''
    body+=f'''<main id="main"><div class="container"><header class="case-header"><a class="back-link" href="../index.html#portfolio"> All projects</a><p class="eyebrow">{e(p['eyebrow'])}</p><h1>{e(p['title'])}</h1>{recognition}<p class="dek">{e(p['summary'])}</p><div class="case-meta"><div><strong>Organization</strong>{e(p['organization'])}</div><div><strong>Role & period</strong>{e(p['role'])}<br>{e(p['date'])}</div><div><strong>Project context</strong>{e(p['status'])}</div></div>{tags(p)}</header><figure class="case-cover">{visual(p,prefix,'eager')}'''
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
                body+=f'<li><a href="{e(url)}">{e(title)} </a></li>'
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
            body+=f'<a class="demo-preview" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{e(video["title"])} (opens in a new tab)"><img loading="lazy" src="../assets/images/{e(video["preview"])}" alt="{e(video["previewAlt"])}"><span aria-hidden="true">▶ Watch demonstration </span></a>'
        body+=f'<p><a class="text-link" href="{url}" target="_blank" rel="noopener noreferrer">{e(video["title"])} </a></p></section>'
    if p.get('video'):
        vid=p['video'];title=e(p['videoTitle'])
        body+=f'''<section id="demo"><h2>Watch the system</h2><div class="video-shell"><a class="video-button" href="https://drive.google.com/file/d/{vid}/view" target="_blank" rel="noopener noreferrer">▶ Watch {title.lower()} </a></div><p class="video-fallback">Opens the video on Google Drive in a new tab.</p></section>'''
    if p.get('resources'):
        body+=f'<section class="resources" id="resources"><h2>{e(p.get("resourcesTitle", "Read more"))}</h2><ul class="resource-list">'
        for title,url in p['resources']:
            link=url if url.startswith('https://') else prefix+url
            body+=f'<li><a href="{e(link)}">{e(title)} </a></li>'
        body+='</ul>'
        if p.get('sourceNote'):body+=f'<p class="source-note">{e(p["sourceNote"])}</p>'
        body+='</section>'
    elif p.get('sourceNote'):
        body+=f'<p class="source-note">{e(p["sourceNote"])}</p>'
    if p.get('methodReferences'):
        body+='<details class="method-references"><summary>Method references</summary><ul class="resource-list">'
        for title,url in p['methodReferences']:
            body+=f'<li><a href="{e(url)}">{e(title)} </a></li>'
        body+='</ul></details>'
    body+=f'</div></div><div class="next-project"><a href="../index.html#portfolio"> Back to all work</a><div><p>Explore next</p><a href="{next_p["slug"]}.html">{e(next_p.get("shortTitle",next_p["title"]))} →</a></div></div></div></main>'
    (ROOT/'projects'/f'{p["slug"]}.html').write_text((body+footer(prefix)).replace(RESUME_PATH, RESUME_URL))


if __name__=='__main__':
    homepage()
    for i,p in enumerate(PROJECTS):casepage(p,PROJECTS[(i+1)%len(PROJECTS)])
    print(f'Built homepage and {len(PROJECTS)} project pages.')
