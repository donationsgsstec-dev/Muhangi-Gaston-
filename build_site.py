#!/usr/bin/env python3
"""Build the single-file professional profile page for Muhangi Gaston / GSS LLP.

Writes ./site/index.html with the official logo embedded as base64 so the page is
fully self-contained and works from any host.
"""
import base64
import io
import pathlib

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE / "site"
SITE.mkdir(exist_ok=True)

# The source logo is 1070 px wide and is displayed at most 190 px, so ship a 2x
# rendition. WebP keeps the file small; the favicon is a separate tiny PNG.
_src = Image.open(HERE.parent / "qr_build" / "logo.png").convert("RGB")
_h = round(420 * _src.height / _src.width)
_buf = io.BytesIO()
_src.resize((420, _h), Image.LANCZOS).save(_buf, format="WEBP", quality=88, method=6)
logo_b64 = base64.b64encode(_buf.getvalue()).decode()

_fav = io.BytesIO()
_src.resize((64, round(64 * _src.height / _src.width)), Image.LANCZOS).save(
    _fav, format="PNG", optimize=True)
favicon_b64 = base64.b64encode(_fav.getvalue()).decode()
print(f"embedded logo: 420x{_h} WebP {len(_buf.getvalue())/1024:.0f} KB | "
      f"favicon {len(_fav.getvalue())/1024:.1f} KB")

SERVICES = [
    ("Artificial intelligence &amp; machine learning",
     "Models and pipelines applied to real business problems."),
    ("Custom software &amp; application development",
     "Web, mobile and desktop systems built to your workflow."),
    ("AI integrations &amp; intelligent assistants",
     "Assistants and copilots embedded into existing tools."),
    ("WhatsApp business automation",
     "Ordering, support and notifications on the channel customers already use."),
    ("API development &amp; system integrations",
     "Connecting platforms, payments and internal services."),
    ("Cloud hosting &amp; application deployment",
     "Reliable deployment, scaling and uptime for production systems."),
    ("Database design &amp; workflow automation",
     "Structured data and automated processes that remove manual work."),
    ("Network monitoring &amp; infrastructure intelligence",
     "Visibility into networks, uptime and infrastructure health."),
    ("Technical consulting &amp; software architecture",
     "Guidance on architecture, tooling and delivery strategy."),
]

PRODUCTS = [
    ("UGA BUILD", "AI-assisted software development.",
     "Turn a description into working software with an AI build pipeline."),
    ("UGA HOST", "Website &amp; application hosting and deployment.",
     "Get projects online quickly, with managed deployment."),
    ("GSS Connect", "WhatsApp-based commerce &amp; business automation.",
     "Sell, confirm and support customers directly on WhatsApp."),
    ("GSS Network Intelligence", "Network &amp; infrastructure monitoring.",
     "Know what is up, what is slow and what is failing."),
    ("WetGuard Uganda", "Environmental monitoring &amp; pollution-risk awareness.",
     "Track environmental signals and surface pollution risk early."),
]

INTERESTS = ["Artificial intelligence", "Machine learning", "Backend &amp; full-stack engineering",
             "Cloud infrastructure", "API integrations", "Software architecture",
             "Technology entrepreneurship"]

service_cards = "\n".join(
    f'''      <article class="card">
        <div class="card-mark"></div>
        <h3>{t}</h3>
        <p>{d}</p>
      </article>''' for t, d in SERVICES)

product_cards = "\n".join(
    f'''      <article class="product">
        <div class="product-head"><h3>{n}</h3><span>{tag}</span></div>
        <p>{d}</p>
      </article>''' for n, tag, d in PRODUCTS)

chips = "\n".join(f'      <li>{i}</li>' for i in INTERESTS)

html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Muhangi Gaston — Founder &amp; Software Engineer | Gaston Software Solutions LLP</title>
<meta name="description" content="Muhangi Gaston, Founder &amp; Software Engineer at Gaston Software Solutions LLP, Kampala, Uganda. Software engineering, artificial intelligence, business automation and cloud platforms.">
<meta property="og:title" content="Muhangi Gaston — Gaston Software Solutions LLP">
<meta property="og:description" content="Innovation Today. Transformation Tomorrow. Software engineering, AI, automation and cloud platforms from Kampala, Uganda.">
<meta property="og:type" content="profile">
<link rel="icon" href="data:image/png;base64,{favicon_b64}">
<style>
  :root{{
    --navy-deep:#081428; --navy:#0C2242; --navy-light:#14345E;
    --blue:#2E6FB7; --accent:#9EC1E8; --silver:#C6D0DD; --silver-dim:#8A9AB0;
    --line:rgba(198,208,221,.22);
    --logo:url("data:image/webp;base64,{logo_b64}");
  }}
  *{{box-sizing:border-box}}
  html{{scroll-behavior:smooth}}
  body{{
    margin:0; background:var(--navy-deep); color:#fff;
    font-family:"Inter",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    line-height:1.65; -webkit-font-smoothing:antialiased;
  }}
  .wrap{{max-width:1080px; margin:0 auto; padding:0 24px}}

  /* ---------- header ---------- */
  header{{
    position:sticky; top:0; z-index:50;
    background:rgba(8,20,40,.88); backdrop-filter:blur(12px);
    border-bottom:1px solid var(--line);
  }}
  .nav{{display:flex; align-items:center; justify-content:space-between; gap:20px; height:70px}}
  .nav .brand{{width:120px; height:38px; background:var(--logo) center/contain no-repeat}}
  .nav ul{{display:flex; gap:26px; list-style:none; margin:0; padding:0}}
  .nav a{{color:var(--silver); text-decoration:none; font-size:13px; letter-spacing:1.6px;
          text-transform:uppercase; transition:color .15s}}
  .nav a:hover{{color:#fff}}
  @media(max-width:760px){{.nav ul{{display:none}}}}

  /* ---------- hero ---------- */
  .hero{{
    position:relative; overflow:hidden;
    background:radial-gradient(110% 130% at 20% 0%,var(--navy-light) 0%,var(--navy) 42%,var(--navy-deep) 100%);
    border-bottom:1px solid var(--line); padding:84px 0 78px;
  }}
  .hero::after{{
    content:""; position:absolute; inset:0; pointer-events:none;
    background-image:linear-gradient(rgba(158,193,232,.05) 1px,transparent 1px),
                     linear-gradient(90deg,rgba(158,193,232,.05) 1px,transparent 1px);
    background-size:52px 52px; -webkit-mask-image:radial-gradient(70% 70% at 50% 40%,#000,transparent);
    mask-image:radial-gradient(70% 70% at 50% 40%,#000,transparent);
  }}
  .hero-grid{{position:relative; display:grid; grid-template-columns:1fr auto; gap:48px; align-items:center}}
  @media(max-width:860px){{.hero-grid{{grid-template-columns:1fr; text-align:center; justify-items:center}}}}
  .eyebrow{{font-size:12px; letter-spacing:4px; color:var(--accent); text-transform:uppercase;
            margin:0 0 18px; font-weight:600}}
  h1{{font-family:"Montserrat",Inter,sans-serif; font-size:clamp(34px,5.4vw,58px); font-weight:800;
      letter-spacing:2.5px; margin:0 0 14px; line-height:1.1}}
  .role{{font-size:clamp(15px,1.9vw,19px); color:var(--silver); letter-spacing:2.6px;
         text-transform:uppercase; margin:0 0 8px; font-weight:500}}
  .company{{font-size:15px; color:var(--accent); letter-spacing:1px; margin:0 0 26px}}
  .slogan{{font-family:"Montserrat",Inter,sans-serif; font-size:17px; letter-spacing:1.2px;
           color:#fff; border-left:3px solid var(--blue); padding-left:16px; margin:0 0 30px}}
  @media(max-width:860px){{.slogan{{border:0; padding:0}}}}
  .hero-actions{{display:flex; gap:14px; flex-wrap:wrap}}
  @media(max-width:860px){{.hero-actions{{justify-content:center}}}}
  .btn{{display:inline-flex; align-items:center; gap:9px; padding:13px 26px; border-radius:9px;
        text-decoration:none; font-size:13.5px; font-weight:600; letter-spacing:.6px;
        transition:transform .15s,background .15s,border-color .15s}}
  .btn:hover{{transform:translateY(-2px)}}
  .btn-primary{{background:var(--blue); color:#fff}}
  .btn-primary:hover{{background:#3a7fc9}}
  .btn-ghost{{border:1px solid rgba(198,208,221,.42); color:var(--silver)}}
  .btn-ghost:hover{{border-color:var(--accent); color:#fff}}
  .portrait{{width:190px; height:190px; border-radius:50%; background:#04101f var(--logo) center/72% no-repeat;
             border:3px solid rgba(158,193,232,.4); box-shadow:0 18px 46px rgba(0,0,0,.5); padding:8px}}
  @media(max-width:860px){{.portrait{{width:150px; height:150px}}}}

  /* ---------- sections ---------- */
  section{{padding:74px 0}}
  .alt{{background:linear-gradient(180deg,#0A1B34,#0C2242)}}
  .sec-head{{margin:0 0 40px}}
  .sec-kicker{{font-size:11.5px; letter-spacing:4px; color:var(--accent); text-transform:uppercase;
               margin:0 0 12px; font-weight:600}}
  h2{{font-family:"Montserrat",Inter,sans-serif; font-size:clamp(24px,3.2vw,34px); font-weight:700;
      letter-spacing:1px; margin:0}}
  .sec-rule{{width:72px; height:3px; background:linear-gradient(90deg,var(--blue),var(--accent));
             border-radius:2px; margin:18px 0 0}}
  .lede{{font-size:16.5px; color:var(--silver); max-width:76ch; margin:0}}
  .lede + .lede{{margin-top:16px}}

  .chips{{display:flex; flex-wrap:wrap; gap:11px; list-style:none; margin:30px 0 0; padding:0}}
  .chips li{{padding:8px 17px; border-radius:999px; font-size:13px; color:var(--silver);
             background:rgba(46,111,183,.16); border:1px solid rgba(158,193,232,.28)}}

  .grid{{display:grid; grid-template-columns:repeat(auto-fit,minmax(288px,1fr)); gap:20px}}
  .card{{background:rgba(12,34,66,.6); border:1px solid var(--line); border-radius:15px;
         padding:26px 24px 24px; position:relative; overflow:hidden;
         transition:border-color .18s,transform .18s}}
  .card:hover{{border-color:rgba(158,193,232,.5); transform:translateY(-3px)}}
  .card-mark{{position:absolute; top:0; left:0; width:100%; height:2px;
              background:linear-gradient(90deg,var(--blue),var(--accent),transparent)}}
  .card h3{{font-size:16px; margin:0 0 9px; letter-spacing:.3px; font-weight:600}}
  .card p{{margin:0; font-size:14px; color:var(--silver-dim); line-height:1.7}}

  .product{{background:rgba(12,34,66,.6); border:1px solid var(--line); border-radius:15px;
            padding:26px 24px; transition:border-color .18s,transform .18s}}
  .product:hover{{border-color:rgba(158,193,232,.5); transform:translateY(-3px)}}
  .product-head{{display:flex; align-items:baseline; justify-content:space-between; gap:14px;
                 flex-wrap:wrap; margin-bottom:10px}}
  .product-head h3{{font-family:"Montserrat",Inter,sans-serif; font-size:17px; margin:0;
                    letter-spacing:1.4px; color:#fff}}
  .product-head span{{font-size:12px; color:var(--accent); letter-spacing:.4px}}
  .product p{{margin:0; font-size:14px; color:var(--silver-dim); line-height:1.7}}

  .edu{{display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:20px; margin-top:34px}}
  .edu-item{{border-left:3px solid var(--blue); padding:6px 0 6px 20px}}
  .edu-item h3{{font-size:15.5px; margin:0 0 6px; font-weight:600}}
  .edu-item p{{margin:0; font-size:13.5px; color:var(--silver-dim)}}

  .callout{{background:rgba(46,111,183,.14); border:1px solid rgba(158,193,232,.3);
            border-radius:15px; padding:26px 28px; margin-top:34px}}
  .callout p{{margin:0; font-size:15px; color:var(--silver)}}

  /* ---------- contact ---------- */
  .contact-grid{{display:grid; grid-template-columns:repeat(auto-fit,minmax(258px,1fr)); gap:18px}}
  .contact-card{{display:block; text-decoration:none; color:#fff; padding:24px;
                 background:rgba(12,34,66,.6); border:1px solid var(--line); border-radius:15px;
                 transition:border-color .18s,transform .18s,background .18s}}
  .contact-card:hover{{border-color:var(--accent); transform:translateY(-3px); background:rgba(46,111,183,.22)}}
  .contact-card .label{{font-size:11px; letter-spacing:2.6px; text-transform:uppercase;
                        color:var(--silver-dim); margin:0 0 9px}}
  .contact-card .value{{font-size:15.5px; font-weight:600; word-break:break-word; margin:0}}

  footer{{background:#061020; border-top:1px solid var(--line); padding:44px 0 38px; text-align:center}}
  footer .brand{{width:170px; height:52px; margin:0 auto 18px; background:var(--logo) center/contain no-repeat}}
  footer .slogan-line{{font-family:"Montserrat",Inter,sans-serif; font-size:14px; letter-spacing:1.1px;
                       color:var(--accent); margin:0 0 16px}}
  footer p{{margin:6px 0; font-size:13px; color:var(--silver-dim)}}
  footer a{{color:var(--silver); text-decoration:none}}
  footer a:hover{{color:#fff}}
</style>
</head>
<body>

<header>
  <div class="wrap nav">
    <div class="brand" role="img" aria-label="Gaston Software Solutions LLP"></div>
    <nav><ul>
      <li><a href="#about">About</a></li>
      <li><a href="#services">Services</a></li>
      <li><a href="#products">Products</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul></nav>
  </div>
</header>

<div class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="eyebrow">Kampala, Uganda</p>
      <h1>MUHANGI GASTON</h1>
      <p class="role">Founder &amp; Software Engineer</p>
      <p class="company">Gaston Software Solutions LLP</p>
      <p class="slogan">Innovation Today. Transformation Tomorrow.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="mailto:info@gss-tec.com">Email me</a>
        <a class="btn btn-ghost" href="https://wa.me/256755274944">WhatsApp</a>
        <a class="btn btn-ghost" href="https://www.linkedin.com/in/muhangi-gaston-490030261">LinkedIn</a>
      </div>
    </div>
    <div class="portrait" role="img" aria-label="Gaston Software Solutions LLP logo"></div>
  </div>
</div>

<section id="about">
  <div class="wrap">
    <div class="sec-head">
      <p class="sec-kicker">Profile</p>
      <h2>About</h2>
      <div class="sec-rule"></div>
    </div>
    <p class="lede">Muhangi Gaston is a Ugandan software engineer, AI innovator and entrepreneur,
      and the founder of Gaston Software Solutions LLP. He develops practical software solutions,
      AI-powered applications, intelligent automation systems and cloud-based technology platforms.</p>
    <p class="lede">His work focuses on turning real operational problems into working systems —
      from AI assistants and WhatsApp commerce to network intelligence and hosted platforms.</p>
    <ul class="chips">
{chips}
    </ul>

    <div class="edu">
      <div class="edu-item">
        <h3>Diploma in Computer Science</h3>
        <p>Metropolitan International University</p>
      </div>
      <div class="edu-item">
        <h3>Certificate in AI &amp; Machine Learning</h3>
        <p>Refactory Academy, 2025</p>
      </div>
    </div>

    <div class="callout">
      <p>Open to technology partnerships, client projects, innovation programmes, pilot projects
        and opportunities to scale African technology.</p>
    </div>
  </div>
</section>

<section id="services" class="alt">
  <div class="wrap">
    <div class="sec-head">
      <p class="sec-kicker">What we do</p>
      <h2>Services</h2>
      <div class="sec-rule"></div>
    </div>
    <div class="grid">
{service_cards}
    </div>
  </div>
</section>

<section id="products">
  <div class="wrap">
    <div class="sec-head">
      <p class="sec-kicker">Our work</p>
      <h2>Products &amp; initiatives</h2>
      <div class="sec-rule"></div>
    </div>
    <div class="grid">
{product_cards}
    </div>
  </div>
</section>

<section id="company" class="alt">
  <div class="wrap">
    <div class="sec-head">
      <p class="sec-kicker">The company</p>
      <h2>Gaston Software Solutions LLP</h2>
      <div class="sec-rule"></div>
    </div>
    <p class="lede">Gaston Software Solutions LLP is a Ugandan technology company focused on
      software engineering, artificial intelligence, business automation, cloud platforms and
      digital transformation.</p>
    <p class="lede">We build systems that organisations actually run on — designed around the
      workflow, deployed on reliable infrastructure, and supported as they grow.</p>
  </div>
</section>

<section id="contact">
  <div class="wrap">
    <div class="sec-head">
      <p class="sec-kicker">Get in touch</p>
      <h2>Contact</h2>
      <div class="sec-rule"></div>
    </div>
    <div class="contact-grid">
      <a class="contact-card" href="mailto:info@gss-tec.com">
        <p class="label">Email</p><p class="value">info@gss-tec.com</p></a>
      <a class="contact-card" href="tel:+256755274944">
        <p class="label">Phone / WhatsApp</p><p class="value">+256 755 274 944</p></a>
      <a class="contact-card" href="https://www.linkedin.com/in/muhangi-gaston-490030261">
        <p class="label">LinkedIn</p><p class="value">muhangi-gaston-490030261</p></a>
      <a class="contact-card" href="https://www.gss-tec.com">
        <p class="label">Website</p><p class="value">gss-tec.com</p></a>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <div class="brand" role="img" aria-label="Gaston Software Solutions LLP"></div>
    <p class="slogan-line">Innovation Today. Transformation Tomorrow.</p>
    <p><a href="mailto:info@gss-tec.com">info@gss-tec.com</a> &nbsp;|&nbsp;
       <a href="tel:+256755274944">+256 755 274 944</a> &nbsp;|&nbsp;
       <a href="https://www.gss-tec.com">gss-tec.com</a></p>
    <p>Gaston Software Solutions LLP &nbsp;|&nbsp; Kampala, Uganda</p>
  </div>
</footer>

</body>
</html>
'''

(SITE / "index.html").write_text(html, encoding="utf-8")
print("wrote", SITE / "index.html", f"({len(html.encode())/1024:.1f} KB)")
