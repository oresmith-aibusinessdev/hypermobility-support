import json, glob, html as htmlmod, os, re, shutil

SCRATCH = os.path.dirname(os.path.abspath(__file__))
DRAFTS = os.path.normpath(os.path.join(SCRATCH, "..", "site-copy", "drafts"))
BUILD = f"{SCRATCH}/site_build"
DOMAIN = "https://hypermobilitysupport.com"
SITE_NAME = "Hypermobility Support"

ICON_URIS = json.load(open(f"{SCRATCH}/icon_data_uris.json"))
ICON_BG = json.load(open(f"{SCRATCH}/icon_bg_colors.json"))

def get_icon_img(slug, css_class="hub-icon-img"):
    uri = ICON_URIS.get(slug)
    if not uri:
        return ""
    return f'<img src="{uri}" class="{css_class}" alt="">'

def get_bg(slug, default="#F7F0E6"):
    return ICON_BG.get(slug, default)

# ---------------------------------------------------------------
# Product recommendations — Amazon Associates
# Every product here is named or evidenced in the page's own cited research;
# nothing below a 4.0-star / meaningful-review-count bar is included.
# ---------------------------------------------------------------
ASSOC_TAG = "hypermobil087-20"

AUTHOR_NAME = "Maren Voss"

def render_byline(p=None):
    updated = p.get("last_updated") if p else None
    updated_html = f'<span class="byline-sep">&middot;</span><span class="byline-updated">Last reviewed {esc(updated)}</span>' if updated else ""
    return f'''<div class="byline"><span>Researched and written by</span><span class="byline-name">{esc(AUTHOR_NAME)}</span><span class="byline-sep">&middot;</span><a href="/about/">How we source this</a>{updated_html}</div>'''

def amz(asin):
    return f"https://www.amazon.com/dp/{asin}?tag={ASSOC_TAG}"

PRODUCTS = {
    "joint-instability-subluxations": [
        {
            "name": "3-Point Products Oval-8 Finger Splints",
            "why": "Built specifically for small-joint hyperextension and lateral slip, the exact instability pattern described above for finger subluxation.",
            "rating": "4.1", "reviews": "3,400+",
            "url": amz("B00GK8XC6U"),
        },
        {
            "name": "Bauerfeind GenuTrain Knee Brace",
            "why": "General orthopedic bracing, not built for hEDS specifically, but a well-reviewed option in the same category the research above points to for larger-joint support.",
            "rating": "4.4", "reviews": "1,000+",
            "url": amz("B07ZYC2ZCZ"),
        },
        {
            "name": "TRIBE Resistance Bands Set",
            "why": "Matches the strength-based physical therapy approach described above. Real hEDS/HSD resistance-training evidence is cited in this section.",
            "rating": "4.7", "reviews": "10,000+",
            "url": amz("B07Q3ZX72W"),
        },
    ],
    "chronic-back-pain-spinal-instability": [
        {
            "name": "Cushion Lab Extra Dense Lumbar Pillow",
            "why": "A verified product built for lumbar support, fitting the ergonomic-seating approach described above for reducing unsupported spinal load.",
            "rating": "4.3", "reviews": "21,000+",
            "url": amz("B08TR9MKGS"),
        },
        {
            "name": "Lifepro CosmoPlate Vibration Plate",
            "why": "General-population evidence for whole-body vibration and low back pain is real (cited above); hEDS-specific evidence does not yet exist, so treat this as an unproven-but-plausible option, not a verified fix.",
            "rating": "4.5", "reviews": "1,000+",
            "url": amz("B0GKJ9VPFZ"),
        },
    ],
    "pots-adjacent-dizziness": [
        {
            "name": "JOBST Relief 20-30 mmHg Waist-High Compression Stockings",
            "why": "Matches the medical-grade, waist-high, 20-30+ mmHg compression range actually used in the trials cited above, not everyday shapewear.",
            "rating": "4.5", "reviews": "100+",
            "url": amz("B0C91W63HY"),
        },
    ],
    "foot-ankle-instability-gait": [
        {
            "name": "Brooks Adrenaline GTS 25 (stability running shoe)",
            "why": "Motion-control/stability footwear is the category recommended by the Ehlers-Danlos Society and specialty clinics referenced above.",
            "rating": "4.4", "reviews": "1,000+",
            "url": amz("B0DM36SKZG"),
        },
    ],
    "fatigue-post-exertional-crash": [
        {
            "name": "Oura Ring 4",
            "why": "Named directly in the research summary above as a wearable that could theoretically support pacing decisions. Oura itself states it is not a medical device, and no trial has tested it for this use.",
            "rating": "4.0", "reviews": "1,000+",
            "url": amz("B0D9WVKXLK"),
        },
    ],
    # Spoke-page entries below reuse the exact same vetted product as the hub page
    # they bridge to, only where the spoke's own text explicitly names that same
    # intervention category (strengthening, compression, stability footwear) —
    # no new products/ratings introduced without their own research pass.
    "why-do-i-keep-spraining-the-same-ankle": [
        {
            "name": "Brooks Adrenaline GTS 25 (stability running shoe)",
            "why": "Motion-control/stability footwear is the category recommended by the Ehlers-Danlos Society and specialty clinics for recurring ankle instability, covered in full on the Foot and Ankle Instability page this article bridges to.",
            "rating": "4.4", "reviews": "1,000+",
            "url": amz("B0DM36SKZG"),
        },
    ],
    "why-do-i-feel-dizzy-when-i-stand-up": [
        {
            "name": "JOBST Relief 20-30 mmHg Waist-High Compression Stockings",
            "why": "Matches the medical-grade, waist-high, 20-30+ mmHg compression range used in the trials on the POTS-Adjacent Dizziness page this article references.",
            "rating": "4.5", "reviews": "100+",
            "url": amz("B0C91W63HY"),
        },
    ],
    "muscle-cramps-weakness-hypermobility": [
        {
            "name": "TRIBE Resistance Bands Set",
            "why": "Matches the supervised, graded resistance-training approach this page names directly as having real evidence behind it for hEDS/HSD muscle symptoms.",
            "rating": "4.7", "reviews": "10,000+",
            "url": amz("B07Q3ZX72W"),
        },
    ],
    "tendinitis-bursitis-plantar-fasciitis-hypermobility": [
        {
            "name": "TRIBE Resistance Bands Set",
            "why": "Matches the targeted-strengthening approach this page names directly as part of managing recurring tendinitis, bursitis, and plantar fasciitis alongside joint protection technique.",
            "rating": "4.7", "reviews": "10,000+",
            "url": amz("B07Q3ZX72W"),
        },
    ],
}

def render_products(slug):
    items = PRODUCTS.get(slug)
    if not items:
        return ""
    cards = ""
    for it in items:
        cards += f'''
        <div class="product-card">
          <div class="product-top">
            <span class="product-name">{esc(it["name"])}</span>
            <span class="product-rating">&#9733; {esc(it["rating"])} <span class="product-reviews">({esc(it["reviews"])} ratings)</span></span>
          </div>
          <p class="product-why">{esc(it["why"])}</p>
          <a href="{esc_attr(it["url"])}" target="_blank" rel="sponsored noopener nofollow" class="product-link">View on Amazon &rarr;</a>
        </div>'''
    return f'''
        <div class="products">
          <p class="products-label">Related products mentioned in the research above</p>
          <p class="products-disclosure">We're an Amazon Associate and earn from qualifying purchases at no extra cost to you. Products are picked because they match what's discussed above, not the other way around. See our <a href="/affiliate-disclosure/">full disclosure</a>.</p>
          <div class="product-grid">{cards}</div>
        </div>'''

os.chdir(DRAFTS)
hub_pages = []
for f in sorted(glob.glob("pages_batch*_final.json")):
    hub_pages.extend(json.load(open(f)))

spoke_pages = []
for f in sorted(glob.glob("spokes_batch*_final.json")):
    spoke_pages.extend(json.load(open(f)))

beighton = json.load(open("beighton_score_page_final.json"))

RAW_CONFIDENCE = {
    "joint-instability-subluxations": "Medium",
    "chronic-migraines-headaches": "High",
    "chronic-back-pain-spinal-instability": "Medium",
    "fatigue-post-exertional-crash": "Medium",
    "pots-adjacent-dizziness": "Medium-High",
    "foot-ankle-instability-gait": "High",
    "digestive-issues-gi-dysmotility": "Medium-High",
    "skin-fragility-easy-bruising": "Medium",
    "anxiety-mood-dysautonomia-linked": "Medium",
    "neck-instability-cervical-pain": "Low-Medium",
    "chronic-widespread-pain-central-sensitization": "Medium-High",
    "menstrual-hormonal-health-heavy-bleeding-iron": "Medium",
    "pregnancy-pelvic-girdle-pain-postpartum": "High",
    "pelvic-organ-prolapse": "Low-Medium",
    "heds-pots-mcas-trifecta": "Medium",
    "beighton-score-self-assessment": "High",
}
def conf_bucket(slug):
    raw = RAW_CONFIDENCE.get(slug, "Medium")
    if raw in ("High", "Medium-High"):
        return ("High confidence", "var(--conf-high)")
    if raw in ("Low-Medium", "Low"):
        return ("Emerging / limited", "var(--conf-low)")
    return ("Medium confidence", "var(--conf-medium)")

hub_title = {p["slug"]: p["title"] for p in hub_pages}
hub_title["beighton-score-self-assessment"] = beighton["title"]

SPOKE_TO_HUB = {
    "tension-headaches-that-wont-go-away": ["neck-instability-cervical-pain", "chronic-migraines-headaches"],
    "why-do-i-bruise-so-easily": ["skin-fragility-easy-bruising"],
    "why-do-i-feel-dizzy-when-i-stand-up": ["pots-adjacent-dizziness"],
    "chronic-fatigue-that-doesnt-improve-with-rest": ["fatigue-post-exertional-crash"],
    "why-do-i-keep-spraining-the-same-ankle": ["foot-ankle-instability-gait"],
    "why-dont-my-pain-medications-work": ["chronic-widespread-pain-central-sensitization"],
    "anxiety-that-doesnt-respond-to-treatment": ["anxiety-mood-dysautonomia-linked"],
    "pelvic-pressure-or-bulging-feeling": ["pelvic-organ-prolapse"],
    "why-are-my-periods-so-heavy": ["menstrual-hormonal-health-heavy-bleeding-iron"],
    "always-been-double-jointed-is-that-real": ["beighton-score-self-assessment", "joint-instability-subluxations"],
    "jaw-pain-tmj-hypermobility": ["joint-instability-subluxations", "chronic-migraines-headaches"],
    "child-growing-pains-hypermobility": ["joint-instability-subluxations", "beighton-score-self-assessment"],
    "high-palate-crowded-teeth-hypermobility": ["beighton-score-self-assessment"],
    "unexplained-stretch-marks-hypermobility": ["skin-fragility-easy-bruising"],
    "early-varicose-veins-hypermobility": ["joint-instability-subluxations"],
    "dizzy-standing-not-pots-orthostatic-intolerance": ["pots-adjacent-dizziness"],
    "tendinitis-bursitis-plantar-fasciitis-hypermobility": ["joint-instability-subluxations"],
    "muscle-cramps-weakness-hypermobility": ["joint-instability-subluxations"],
    "celiac-disease-hypermobility-link": ["digestive-issues-gi-dysmotility"],
    "keratosis-pilaris-hypermobility": ["skin-fragility-easy-bruising"],
    "swallowing-difficulty-hoarse-voice-hypermobility": ["digestive-issues-gi-dysmotility"],
    "why-does-my-ear-feel-blocked-or-plugged": ["asthma-allergies-airway-hypermobility"],
    "recurrent-hernias-and-hypermobility": ["joint-instability-subluxations"],
    "cold-discolored-hands-feet-raynauds-hypermobility": ["pots-adjacent-dizziness"],
    "local-anesthetic-doesnt-work-dentist-hypermobility": ["pain-treatments-actually-used-hypermobility"],
    "blue-tinted-eye-whites-hypermobility": ["eye-vision-signs-hypermobility"],
    "numb-tingling-hands-ulnar-nerve-hypermobility": ["neck-instability-cervical-pain"],
    "gum-recession-inflammation-hypermobility": ["skin-fragility-easy-bruising"],
    "elongated-uvula-hypermobility": ["skin-fragility-easy-bruising"],
    "scoliosis-spine-curvature-hypermobility": ["chronic-back-pain-spinal-instability"],
}

def esc(s):
    return htmlmod.escape(s, quote=False)

def esc_attr(s):
    return htmlmod.escape(s, quote=True)

def paras(items):
    return "\n".join(f"<p>{esc(t)}</p>" for t in items)

def meta_desc(intro_list, limit=155):
    text = " ".join(intro_list)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "..."

def render_stats(stats, style):
    if not stats:
        return ""
    if style == "single" and len(stats) == 1:
        s = stats[0]
        return f'''<div class="single-stat">
          <span class="stat-num">{esc(s["num"])}</span>
          <span class="stat-text">{esc(s["label"])}<span class="stat-source" style="display:block;margin-top:0.4rem;">{esc(s["source"])}</span></span>
        </div>'''
    rows = "\n".join(
        f'''<div class="stat">
          <span class="stat-num">{esc(s["num"])}</span>
          <span class="stat-label">{esc(s["label"])}</span>
          <span class="stat-source">{esc(s["source"])}</span>
        </div>''' for s in stats
    )
    return f'<div class="stat-row">{rows}</div>'

def render_sources(sources):
    items = []
    for i, s in enumerate(sources, start=1):
        text = s["text"] if isinstance(s, dict) else s
        url = s.get("url") if isinstance(s, dict) else None
        n = f"{i:02d}"
        if url:
            items.append(f'<li><span class="n">{n}</span><span><a href="{esc(url)}" target="_blank" rel="noopener">{esc(text)}</a></span></li>')
        else:
            items.append(f'<li><span class="n">{n}</span><span>{esc(text)} <em class="unlinked">(link not yet sourced)</em></span></li>')
    return "\n".join(items)

# ---------------------------------------------------------------
# Page shell (real HTML document per page)
# ---------------------------------------------------------------
def page_shell(slug, title, description, body_html, json_ld, og_type="article"):
    url = DOMAIN if slug == "" else f"{DOMAIN}/{slug}/"
    full_title = title if slug == "" else f"{title} | {SITE_NAME}"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','GTM-BDJ349M9');</script>
<!-- End Google Tag Manager -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc_attr(description)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{esc_attr(full_title)}">
<meta property="og:description" content="{esc_attr(description)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{esc_attr(SITE_NAME)}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{esc_attr(full_title)}">
<meta name="twitter:description" content="{esc_attr(description)}">
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">{json.dumps(json_ld)}</script>
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-BDJ349M9"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
<div class="site">
  <div class="topbar">
    <span class="topbar-mark"><a href="/">A Working Reference</a></span>
    <span class="topbar-tag">Hypermobility Research</span>
  </div>
  <div class="shell wide" id="app-root">
    {body_html}
  </div>
  <div class="site-footer">
    <span>&copy; {SITE_NAME}. Not medical advice.</span>
    <a href="/about/">About &amp; sourcing standards</a>
    <a href="/affiliate-disclosure/">Affiliate disclosure</a>
  </div>
</div>
</body>
</html>
'''

def breadcrumbs(title, slug):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": title, "item": f"{DOMAIN}/{slug}/"},
        ],
    }

# ---------------------------------------------------------------
# Hub page
# ---------------------------------------------------------------
def render_hub(p):
    bg = get_bg(p["slug"])
    sections_html = ""
    for sec in p["sections"]:
        sections_html += f'<h2>{esc(sec["heading"])}</h2>\n'
        sections_html += paras(sec["body"]) + "\n"
        sections_html += render_stats(sec.get("stats"), sec.get("stat_style"))
    hero = ""
    body = f'''
    <article class="page is-active" data-page="{p["slug"]}">
      <a href="/" class="back-link">&larr; All topics</a>
      {hero}
      <p class="eyebrow">{esc(p["eyebrow"])}</p>
      <h1 class="title">{esc(p["title"])}</h1>
      <div class="note">{paras(p["intro"])}</div>
      <div class="body">
        {sections_html}
        <div class="action-box" style="background:{bg};">
          <h2>{esc(p["action_title"])}</h2>
          {paras(p["action_body"])}
        </div>
        {render_products(p["slug"])}
        <div class="sources">
          <p class="sources-label">Sources referenced on this page</p>
          <ol>{render_sources(p["sources"])}</ol>
        </div>
        {render_byline(p)}
      </div>
    </article>'''
    desc = meta_desc(p["intro"])
    json_ld = {
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": p["title"],
        "headline": p["title"],
        "description": desc,
        "url": f"{DOMAIN}/{p['slug']}/",
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": DOMAIN + "/"},
        "about": {"@type": "MedicalCondition", "name": p["title"]},
        "audience": {"@type": "PatientsAudience", "audienceType": "Patients with hypermobility, hEDS, or HSD"},
        "specialty": "https://health-lifesci.schema.org/Rheumatology",
    }
    return page_shell(p["slug"], p["title"], desc, body, [json_ld, breadcrumbs(p["title"], p["slug"])])

# ---------------------------------------------------------------
# Spoke page
# ---------------------------------------------------------------
def render_spoke(p):
    sections_html = ""
    for sec in p["sections"]:
        sections_html += f'<h2>{esc(sec["heading"])}</h2>\n'
        sections_html += paras(sec["body"]) + "\n"
    hub_slugs = SPOKE_TO_HUB.get(p["slug"], [])
    if hub_slugs:
        links = " &middot; ".join(f'<a href="/{s}/">{esc(hub_title.get(s, s))}</a>' for s in hub_slugs)
        bridge_html = f'<div class="bridge-box"><p class="bridge-label">Read more on the hub page</p><p>{links}</p></div>'
    else:
        bridge_html = f'<div class="bridge-box"><p class="bridge-label">Related topic</p><p>{esc(p.get("bridge_to_hub",""))}. Not yet published as its own page.</p></div>'
    body = f'''
    <article class="page spoke is-active" data-page="{p["slug"]}">
      <a href="/" class="back-link">&larr; All topics</a>
      <p class="eyebrow">{esc(p["eyebrow"])}</p>
      <h1 class="title">{esc(p["title"])}</h1>
      <div class="note">{paras(p["intro"])}</div>
      <div class="body">
        {sections_html}
        {bridge_html}
        <div class="action-box" style="background:#F1EAD6;">
          <h2>{esc(p["action_title"])}</h2>
          {paras(p["action_body"])}
        </div>
        {render_products(p["slug"])}
        <div class="sources">
          <p class="sources-label">Sources referenced on this page</p>
          <ol>{render_sources(p["sources"])}</ol>
        </div>
        {render_byline(p)}
      </div>
    </article>'''
    desc = meta_desc(p["intro"])
    json_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": p["title"],
        "description": desc,
        "url": f"{DOMAIN}/{p['slug']}/",
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": DOMAIN + "/"},
    }
    return page_shell(p["slug"], p["title"], desc, body, [json_ld, breadcrumbs(p["title"], p["slug"])])

# ---------------------------------------------------------------
# Beighton tool page
# ---------------------------------------------------------------
def render_beighton(p):
    bg = get_bg(p["slug"])
    sections_html = ""
    for sec in p["sections"]:
        sections_html += f'<h2>{esc(sec["heading"])}</h2>\n'
        sections_html += paras(sec["body"]) + "\n"
    hero = ""
    body = f'''
    <article class="page tool is-active" data-page="{p["slug"]}">
      <a href="/" class="back-link">&larr; All topics</a>
      {hero}
      <p class="eyebrow">{esc(p["eyebrow"])}</p>
      <h1 class="title">{esc(p["title"])}</h1>
      <div class="note">{paras(p["intro"])}</div>
      <div class="body">
        {sections_html}
        <div class="action-box" style="background:{bg};">
          <h2>{esc(p["action_title"])}</h2>
          {paras(p["action_body"])}
        </div>
        <div class="sources">
          <p class="sources-label">Sources referenced on this page</p>
          <ol>{render_sources(p["sources"])}</ol>
        </div>
      </div>
    </article>'''
    desc = meta_desc(p["intro"])
    json_ld = {
        "@context": "https://schema.org",
        "@type": "MedicalWebPage",
        "name": p["title"],
        "headline": p["title"],
        "description": desc,
        "url": f"{DOMAIN}/{p['slug']}/",
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": DOMAIN + "/"},
        "about": {"@type": "MedicalTest", "name": "Beighton Score"},
        "audience": {"@type": "PatientsAudience", "audienceType": "Patients with hypermobility, hEDS, or HSD"},
    }
    return page_shell(p["slug"], p["title"], desc, body, [json_ld, breadcrumbs(p["title"], p["slug"])])

# ---------------------------------------------------------------
# Home page
# ---------------------------------------------------------------
def render_card(slug, title, eyebrow, sub):
    icon = get_icon_img(slug, "card-icon-img")
    bg = get_bg(slug)
    conf_label, conf_color = conf_bucket(slug)
    return f'''
        <a class="card" style="background:{bg};" href="/{slug}/">
          <div class="card-art">{icon}</div>
          <div class="card-body">
            <span class="card-conf"><span class="legend-dot" style="background:{conf_color};"></span>{esc(eyebrow)}</span>
            <h3 class="card-title">{esc(title)}</h3>
            <p class="card-sub">{esc(sub)}</p>
          </div>
        </a>'''

def render_home():
    cards = render_card(
        beighton["slug"], beighton["title"], beighton["eyebrow"], "Self-assessment tool"
    )
    for p in hub_pages:
        cards += render_card(p["slug"], p["title"], p["eyebrow"], f'{len(p["sources"])} sources')

    spoke_rows = ""
    for p in spoke_pages:
        spoke_rows += f'''
        <a class="spoke-row" href="/{p["slug"]}/">
          <span class="spoke-row-title">{esc(p["title"])}</span>
          <span class="spoke-row-arrow">&rarr;</span>
        </a>'''

    body = f'''
    <article class="page home is-active" data-page="home">
      <div class="hero-row">
        <div class="hero-title-block">
          <h1 class="board-title">Hypermobility Support</h1>
          <p class="board-tag">Hypermobility Research</p>
          <p class="board-kicker">A working reference on hypermobility</p>
        </div>
      </div>

      <section>
        <p class="sec-label">Start with the core topics</p>
        <div class="card-grid">
          {cards}
        </div>
      </section>

      <section>
        <p class="sec-label">Common questions that connect back to hypermobility</p>
        <div class="spoke-list">
          {spoke_rows}
        </div>
      </section>

      <div class="bottom-note">
        <h2>What this actually is</h2>
        <p>We're not doctors, and none of this is medical advice. It's what we found when we went looking: real studies on hEDS and HSD symptoms, one page per topic, every claim linked back to where it came from. Some of it is well-established. Some of it is one small study that hasn't been repeated yet. We say which is which.</p>
        <div class="legend">
          <span class="legend-item"><span class="legend-dot" style="background:var(--conf-high);"></span>High confidence</span>
          <span class="legend-item"><span class="legend-dot" style="background:var(--conf-medium);"></span>Medium confidence</span>
          <span class="legend-item"><span class="legend-dot" style="background:var(--conf-low);"></span>Emerging / limited</span>
        </div>
      </div>
    </article>'''

    title = "Hypermobility Support: Evidence-Based Hypermobility & hEDS/HSD Research"
    desc = "A free, evidence-linked reference on hypermobility, hEDS, and HSD symptoms and treatments, plus a Beighton Score self-assessment tool. Not medical advice; every claim is sourced."
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": SITE_NAME,
        "url": DOMAIN + "/",
        "description": desc,
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": DOMAIN + "/"},
    }
    return page_shell("", title, desc, body, [json_ld], og_type="website")

# ---------------------------------------------------------------
# Build
# ---------------------------------------------------------------
if os.path.exists(BUILD):
    shutil.rmtree(BUILD)
os.makedirs(f"{BUILD}/assets")

shutil.copy(f"{SCRATCH}/assets_style.css", f"{BUILD}/assets/style.css")

with open(f"{BUILD}/index.html", "w") as f:
    f.write(render_home())

all_page_slugs = []
for p in hub_pages:
    os.makedirs(f"{BUILD}/{p['slug']}", exist_ok=True)
    open(f"{BUILD}/{p['slug']}/index.html", "w").write(render_hub(p))
    all_page_slugs.append(p["slug"])

for p in spoke_pages:
    os.makedirs(f"{BUILD}/{p['slug']}", exist_ok=True)
    open(f"{BUILD}/{p['slug']}/index.html", "w").write(render_spoke(p))
    all_page_slugs.append(p["slug"])

os.makedirs(f"{BUILD}/{beighton['slug']}", exist_ok=True)
open(f"{BUILD}/{beighton['slug']}/index.html", "w").write(render_beighton(beighton))
all_page_slugs.append(beighton["slug"])

# ---------------------------------------------------------------
# About / sourcing-standards page
# ---------------------------------------------------------------
about_body = f'''
    <article class="page is-active" data-page="about">
      <a href="/" class="back-link">&larr; All topics</a>
      <p class="eyebrow">About this site</p>
      <h1 class="title">About &amp; Sourcing Standards</h1>
      <div class="note"><p>{SITE_NAME} is an independent research reference, not a medical practice. Nothing here is medical advice, and nothing here is written or reviewed by a doctor. What it is: one place where the actual peer-reviewed research on hEDS/HSD symptoms is read, summarized honestly, and linked back to its source.</p></div>
      <div class="body">
        <h2>Who's behind this</h2>
        <p>This site is researched and written by {AUTHOR_NAME}, as the supportive partner of someone living with hEDS/HSD. That's the honest origin of this project: watching someone navigate symptoms that took years to get named, and finding that a lot of the real research on them was scattered, paywalled, or buried under forum threads and anecdotes. This site exists to put the actual studies in one place, in plain language, without overstating what they show.</p>
        <h2>What "evidence-based" means here</h2>
        <p>Every claim on every page is tied to a specific cited source &mdash; visible at the bottom of the page, not just referenced vaguely. Where the evidence is strong, we say so. Where it's a single small study that hasn't been replicated, we say that too. The confidence legend on the homepage (high / medium / emerging) reflects that distinction on every topic page.</p>
        <h2>What this site doesn't do</h2>
        <p>No fabricated claims, no invented statistics, no citations that don't check out. No pretending non-clinical research adds up to a diagnosis or a treatment plan. If something belongs in front of a doctor rather than on a page, the page says so directly instead of implying otherwise.</p>
        <h2>Corrections</h2>
        <p>If a citation is wrong, outdated, or misread, that's worth fixing immediately. Corrections can be sent via the contact details on the <a href="/affiliate-disclosure/">affiliate disclosure page</a>.</p>
        <div class="sources">
          <p class="sources-label">Related</p>
          <ol><li><span class="n">01</span><span><a href="/affiliate-disclosure/">Affiliate disclosure</a> &mdash; how product recommendations work and what does not influence them.</span></li></ol>
        </div>
      </div>
    </article>'''
about_desc = f"Who researches and writes {SITE_NAME}, and the sourcing standard every page is held to: real peer-reviewed citations only, no fabricated claims."
os.makedirs(f"{BUILD}/about", exist_ok=True)
open(f"{BUILD}/about/index.html", "w").write(
    page_shell("about", "About & Sourcing Standards", about_desc, about_body, [{
        "@context": "https://schema.org", "@type": "AboutPage", "name": "About & Sourcing Standards",
        "url": f"{DOMAIN}/about/", "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": DOMAIN + "/"},
    }], og_type="website")
)
all_page_slugs.append("about")

# ---------------------------------------------------------------
# Affiliate disclosure page (FTC requirement, not a hub/spoke page)
# ---------------------------------------------------------------
disclosure_body = f'''
    <article class="page is-active" data-page="affiliate-disclosure">
      <a href="/" class="back-link">&larr; All topics</a>
      <p class="eyebrow">Site policy</p>
      <h1 class="title">Affiliate Disclosure</h1>
      <div class="note"><p>The short version: we link to some products, and if you buy through those links, we may earn a small commission. It costs you nothing extra. It never changes what we say about the research.</p></div>
      <div class="body">
        <h2>How this works</h2>
        <p>{SITE_NAME} is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by linking to Amazon.com. When you click certain product links on this site and make a purchase, we may earn a commission, at no additional cost to you.</p>
        <h2>What this does not change</h2>
        <p>Products are selected because they match what the cited research on that page actually discusses, not the other way around. We do not accept payment for placement, we do not let commission rates influence which products appear, and we say plainly when a product's evidence is weak, general-population-only, or entirely absent. Our full evidence-confidence rating system is explained on the homepage and applies regardless of whether a page contains a product link.</p>
        <h2>What we don't do</h2>
        <p>We do not use health-condition-based ad retargeting. We do not monetize genetic-testing referrals. We are not doctors, and nothing on this site is medical advice. See the note on every page.</p>
        <div class="sources">
          <p class="sources-label">Contact</p>
          <ol><li><span class="n">01</span><span>Questions about this policy can be sent to the site owner via the contact details on the homepage.</span></li></ol>
        </div>
      </div>
    </article>'''
disclosure_desc = "How affiliate links and product recommendations work on this site, including what does and doesn't influence what we recommend."
os.makedirs(f"{BUILD}/affiliate-disclosure", exist_ok=True)
open(f"{BUILD}/affiliate-disclosure/index.html", "w").write(
    page_shell("affiliate-disclosure", "Affiliate Disclosure", disclosure_desc, disclosure_body, [{
        "@context": "https://schema.org", "@type": "WebPage", "name": "Affiliate Disclosure",
        "url": f"{DOMAIN}/affiliate-disclosure/", "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": DOMAIN + "/"},
    }], og_type="website")
)
all_page_slugs.append("affiliate-disclosure")

# ---------------------------------------------------------------
# robots.txt
# ---------------------------------------------------------------
robots = f"""# Traditional search engines
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: DuckDuckBot
Allow: /

User-agent: Yandex
Allow: /

User-agent: Applebot
Allow: /

User-agent: Baiduspider
Allow: /

# AI / LLM crawlers (training + live retrieval)
User-agent: GPTBot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: CCBot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: meta-externalagent
Allow: /

User-agent: Bytespider
Allow: /

User-agent: Diffbot
Allow: /

User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
"""
open(f"{BUILD}/robots.txt", "w").write(robots)

# ---------------------------------------------------------------
# sitemap.xml
# ---------------------------------------------------------------
urls = [""] + all_page_slugs
sitemap_entries = "\n".join(
    f"  <url><loc>{DOMAIN}/{s}{'/' if s else ''}</loc><changefreq>monthly</changefreq><priority>{'1.0' if s=='' else '0.7'}</priority></url>"
    for s in urls
)
sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{sitemap_entries}
</urlset>
'''
open(f"{BUILD}/sitemap.xml", "w").write(sitemap)

# ---------------------------------------------------------------
# llms.txt
# ---------------------------------------------------------------
llms_lines = [
    f"# {SITE_NAME}",
    "",
    "> A free, evidence-linked reference on hypermobility, hEDS (hypermobile Ehlers-Danlos Syndrome), and HSD (Hypermobility Spectrum Disorder). Every page cites its sources and states an evidence-confidence level. This is not medical advice and the site is not written or reviewed by medical professionals. It is a citation-linked collection of what published research says.",
    "",
    "## Core topics",
]
for p in hub_pages:
    llms_lines.append(f"- [{p['title']}]({DOMAIN}/{p['slug']}/): {meta_desc(p['intro'], 140)}")
llms_lines.append(f"- [{beighton['title']}]({DOMAIN}/{beighton['slug']}/): {meta_desc(beighton['intro'], 140)}")
llms_lines.append("")
llms_lines.append("## Common questions")
for p in spoke_pages:
    llms_lines.append(f"- [{p['title']}]({DOMAIN}/{p['slug']}/)")
open(f"{BUILD}/llms.txt", "w").write("\n".join(llms_lines) + "\n")

print("Built", len(all_page_slugs) + 1, "pages into", BUILD)
