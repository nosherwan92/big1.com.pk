#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Multi-page build for the BIG1 / FilePak marketing site.

Carves the ordered _build/*.html fragments into shared partials (one head/CSS,
one nav, one footer, shared scripts) and per-page bodies, then emits:
  index.html         -> generic company home (lean)
  tax-filing.html    -> the FilePak tax-return product (all tax-specific content)
  calculators.html   -> the free tax calculators
(services.html is maintained separately, standalone.)

Run:  python build.py     (from C:\\bfiler\\website)
UTF-8 no BOM; asserts non-ascii == 0 per page.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
BLD  = os.path.join(ROOT, "_build")

def read(name):
    with io.open(os.path.join(BLD, name), encoding="utf-8") as f:
        return f.read()

def pull_style(text):
    """Return inner CSS of the first <style>..</style>, or '' if none."""
    m = re.search(r"<style>(.*?)</style>", text, re.S)
    return m.group(1) if m else ""

def section(text, start_sub, end="</section>"):
    """Extract from the FULL opening tag containing start_sub through the first `end` after it.
    start_sub may be a full tag ('<section class=\"hero\">') or an attribute fragment ('id=\"faq\"');
    either way we back up to the '<' that opens the tag."""
    k = text.index(start_sub)
    i = text.rindex("<", 0, k + 1)  # start of the opening tag
    j = text.index(end, k) + len(end)
    return text[i:j]

# ---- load fragments ----
F01 = read("01-head.html")
F02 = read("02-nav-hero.html")
F03 = read("03-trust-product-why.html")
F04 = read("04-comparison.html")
F05 = read("05-features-how-ai.html")
F06 = read("06-calculators.html")
F07 = read("07-audience-dashboard-security-practice.html")
F08 = read("08-testimonials-pricing-faq-cta-footer.html")
F09 = read("09-whatsapp-calc-script.html")
F10 = read("10-script.html")

# ---- combined stylesheet (preserve cascade order) ----
CSS = "\n".join(pull_style(f) for f in [F01, F03, F04, F05, F06, F07, F08, F10])

NEW_CSS = """
/* ---------- Home: hero + pillars (multi-page) ---------- */
.home-hero{position:relative;padding:clamp(56px,9vw,120px) 0 clamp(30px,5vw,60px);text-align:center;overflow:clip}
.home-hero .eyebrow{margin-bottom:20px}
.home-hero h1{font-size:clamp(2.1rem,5.4vw,3.7rem);letter-spacing:-.04em;line-height:1.04;max-width:16ch;margin:0 auto 20px}
.home-hero .lede{max-width:640px;margin:0 auto 30px}
.home-hero .hero-cta{justify-content:center}
.pillars{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:8px 0 8px}
.pillar{position:relative;display:flex;flex-direction:column;padding:26px;border-radius:var(--r-lg);
  border:1px solid var(--border);background:var(--surface-solid);text-decoration:none;color:inherit;overflow:hidden;
  transition:transform .4s var(--ease),box-shadow .4s var(--ease),border-color .4s var(--ease)}
.pillar::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;transform:scaleX(0);transform-origin:left;
  background:linear-gradient(90deg,var(--emerald-500),var(--blue-600));transition:transform .5s var(--ease)}
.pillar:hover{transform:translateY(-6px);box-shadow:var(--shadow-lg);border-color:var(--border-strong)}
.pillar:hover::after{transform:scaleX(1)}
.pillar .pic{width:46px;height:46px;border-radius:13px;display:grid;place-items:center;margin-bottom:18px;
  background:linear-gradient(135deg,rgba(6,95,70,.14),rgba(16,158,125,.1));color:var(--accent);border:1px solid var(--border)}
.pillar h3{font-size:1.2rem;letter-spacing:-.025em;margin-bottom:8px}
.pillar p{font-size:.86rem;color:var(--text-2);line-height:1.6;margin-bottom:16px}
.pillar ul{list-style:none;display:grid;gap:7px;margin-bottom:20px}
.pillar li{display:flex;gap:8px;align-items:flex-start;font-size:.8rem;color:var(--text-2)}
.pillar li .d{width:5px;height:5px;border-radius:50%;background:var(--emerald-500);margin-top:7px;flex-shrink:0}
.pillar .go{margin-top:auto;font-size:.84rem;font-weight:650;color:var(--accent);display:inline-flex;align-items:center;gap:7px}
.pillar:hover .go svg{transform:translateX(3px)}
.pillar .go svg{transition:transform .3s var(--ease)}
@media (max-width:900px){.pillars{grid-template-columns:1fr;max-width:520px;margin-inline:auto}}
/* calculators page header */
.page-hero{padding:clamp(46px,7vw,88px) 0 clamp(10px,2vw,24px);text-align:center}
.page-hero h1{font-size:clamp(1.9rem,4.4vw,3rem);letter-spacing:-.035em;line-height:1.08;margin:16px 0 14px}
.page-hero .lede{max-width:620px;margin-inline:auto}
"""

# ---- head / body-open (shared) ----
HEAD_RAW = F01[:F01.index("</head>") + len("</head>")]
BODY_OPEN = F01[F01.index("</head>") + len("</head>"):].strip("\n")  # <body> + skip + scrollbar

def head_for(title, desc, canonical):
    h = HEAD_RAW
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, h, flags=re.S)
    h = re.sub(r'(<meta name="description" content=").*?(" />)', lambda m: m.group(1)+desc+m.group(2), h, flags=re.S)
    h = re.sub(r'(<meta property="og:title" content=").*?(" />)', lambda m: m.group(1)+title+m.group(2), h, flags=re.S)
    h = re.sub(r'(<meta property="og:description" content=").*?(" />)', lambda m: m.group(1)+desc+m.group(2), h, flags=re.S)
    h = re.sub(r'(<meta property="og:url" content=").*?(" />)', lambda m: m.group(1)+"https://big1.com.pk/"+canonical+m.group(2), h, flags=re.S)
    h = re.sub(r'(<link rel="canonical" href=").*?(" />)', lambda m: m.group(1)+"https://big1.com.pk/"+canonical+m.group(2), h, flags=re.S)
    h = re.sub(r"<style>.*?</style>", "<style>\n" + CSS + "\n" + NEW_CSS + "\n</style>", h, flags=re.S, count=1)
    return h

# ---- shared nav (cross-page links + active state) ----
NAVLINKS = [("home","index.html","Home"),("tax","tax-filing.html","Tax filing"),
            ("services","services.html","Services"),("calc","calculators.html","Calculators")]
def nav_for(active):
    links = "\n".join(
        '      <a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if key==active else "", label)
        for key,href,label in NAVLINKS)
    return '''<!-- ============================== NAV ============================== -->
<header class="nav" id="nav">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="BIG1 &mdash; home">
      <img class="logo-img" src="assets/big1-logo.png" alt="BIG1" onerror="this.remove()" />
      <span class="bmark" aria-hidden="true">B<i>1</i>G</span>
      <span class="tag">FilePak</span>
    </a>

    <nav class="nav-links" id="navlinks" aria-label="Primary">
%s
    </nav>

    <div class="nav-right">
      <button class="theme-btn" id="themeBtn" aria-label="Switch colour theme" title="Switch theme">
        <svg class="sun" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
        <svg class="moon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
      </button>
      <a class="btn btn-primary btn-sm btn-cta" href="%s">Get started <svg class="arw" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></a>
      <button class="nav-toggle" id="navToggle" aria-expanded="false" aria-controls="navlinks" aria-label="Open menu">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
      </button>
    </div>
  </div>
</header>

<main id="main">
<span id="top"></span>''' % (links, WA_START)

# ---- interim "start" target: app not deployed yet -> WhatsApp ----
WA = "https://wa.me/923399999611"
WA_START = WA + "?text=Assalam%20o%20Alaikum%2C%20I%27d%20like%20to%20get%20started."

# ---- shared footer + whatsapp float + scripts ----
FOOTER = section(F08, '<footer class="foot">', "</footer>")
# repoint footer links from in-page anchors to cross-page
_footer_map = {
    'href="#features"':'href="tax-filing.html#features"',
    'href="#beyond"':'href="tax-filing.html#beyond"',
    'href="#intelligence"':'href="tax-filing.html#intelligence"',
    'href="#dashboard"':'href="tax-filing.html#dashboard"',
    'href="#calculators"':'href="calculators.html"',
    'href="#who"':'href="tax-filing.html#who"',
    'href="#faq"':'href="tax-filing.html#faq"',
    'href="#top"':'href="index.html"',
}
for a,b in _footer_map.items():
    FOOTER = FOOTER.replace(a,b)

WA_FAB = section(F09, '<a class="wa-fab"', "</a>")
CALC_ENGINE = section(F09, "<script>", "</script>")
GEN_SCRIPT = F10[F10.index("<script>"):]  # <script>..</script></body></html>

# ---- sections ----
HERO_TAX   = section(F02, '<section class="hero">')
TRUST      = section(F03, '<section class="trust"')
COMPARE    = section(F04, 'id="compare"')
FEATURES   = section(F05, 'id="features"')
HOW        = section(F05, 'id="how"')
INTEL      = section(F05, 'id="intelligence"')
BEYOND     = section(F05, 'id="beyond"')
CALC       = section(F06, 'id="calculators"')
WHO        = section(F07, 'id="who"')
DASH       = section(F07, 'id="dashboard"')
SECURITY   = section(F07, 'id="security"')
STORIES    = section(F08, 'id="stories"')
FAQ        = section(F08, 'id="faq"')
CTA        = section(F08, 'id="cta"')

# repoint the tax-page hero primary CTA + who-card etc. stay in-page (same page now)

# ---- NEW home content ----
HOME_HERO = '''<!-- ============================== HOME HERO ============================== -->
<section class="home-hero">
  <div class="hero-bg" aria-hidden="true">
    <div class="aurora a1"></div><div class="aurora a2"></div><div class="aurora a3"></div><div class="grid-lines"></div>
  </div>
  <div class="wrap">
    <span class="eyebrow" data-reveal><span class="dot"></span>Tax, registration &amp; corporate services &middot; Pakistan</span>
    <h1 class="h-display" data-reveal style="--d:80ms">Your tax and compliance,<br /><span class="grad-text">handled end to end.</span></h1>
    <p class="lede" data-reveal style="--d:160ms">BIG1 helps individuals and businesses across Pakistan file their taxes,
      register with the authorities, and stay compliant &mdash; a real team behind an intelligent platform, in English or&nbsp;&#1575;&#1585;&#1583;&#1608;.</p>
    <div class="hero-cta" data-reveal style="--d:240ms">
      <a class="btn btn-primary btn-lg" href="tax-filing.html">File your taxes
        <svg class="arw" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></a>
      <a class="btn btn-glass btn-lg" href="services.html">Explore all services</a>
    </div>
  </div>
</section>'''

PILLARS = '''<!-- ============================== PILLARS ============================== -->
<section class="sec" id="what" style="padding-top:clamp(20px,3vw,40px)">
  <div class="wrap wrap-wide">
    <div class="pillars">
      <a class="pillar" data-reveal href="tax-filing.html">
        <span class="pic"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h9l5 5v13H6z"/><path d="M14 3v6h6"/><path d="M9.5 13h5M9.5 16.5h5"/></svg></span>
        <h3>File your taxes</h3>
        <p>Guided income-tax filing for salaried people, freelancers and businesses &mdash; computed to the rupee and filed through an authorized FBR e-intermediary.</p>
        <ul>
          <li><span class="d"></span>Reads your documents, finds tax you overpaid</li>
          <li><span class="d"></span>Wealth statement that reconciles before you file</li>
          <li><span class="d"></span>File any year back to 2016 to get on the ATL</li>
        </ul>
        <span class="go">Go to tax filing <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></span>
      </a>

      <a class="pillar" data-reveal style="--d:80ms" href="services.html">
        <span class="pic"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V7l7-4 7 4v14"/><path d="M9 9h.01M15 9h.01M9 13h.01M15 13h.01M9 17h6"/></svg></span>
        <h3>Register &amp; comply</h3>
        <p>Every registration and filing a person or business needs &mdash; with the exact documents listed up front and a tracked reference to completion.</p>
        <ul>
          <li><span class="d"></span>NTN, sales tax (GST) &amp; provincial sales tax</li>
          <li><span class="d"></span>Trademark, copyright, patent &amp; design (IPO Pakistan)</li>
          <li><span class="d"></span>Company incorporation &amp; SECP compliance</li>
        </ul>
        <span class="go">Explore services <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></span>
      </a>

      <a class="pillar" data-reveal style="--d:160ms" href="calculators.html">
        <span class="pic"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="3" width="16" height="18" rx="2.4"/><path d="M8 7h8M8 11h8M8 15h4"/></svg></span>
        <h3>Free tax tools</h3>
        <p>Estimate what you owe in seconds &mdash; salary, rental, capital gains and business tax, on the current Finance Act rates.</p>
        <ul>
          <li><span class="d"></span>Salary &amp; business income tax</li>
          <li><span class="d"></span>Capital gains &mdash; property &amp; securities</li>
          <li><span class="d"></span>Rental income tax</li>
        </ul>
        <span class="go">Open calculators <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></span>
      </a>
    </div>
  </div>
</section>'''

# a short, GENERIC home FAQ (filing-specific FAQ stays on the tax page)
FAQ_HOME = '''<!-- ============================== HOME FAQ ============================== -->
<section class="sec frame-sub" id="faq">
  <div class="wrap">
    <div class="sec-head center" data-reveal>
      <span class="eyebrow"><span class="dot"></span>Questions</span>
      <h2 class="h1">The things people<br />actually ask.</h2>
    </div>
    <div class="faq" data-reveal>
      <div class="qa"><button aria-expanded="false"><span>What does BIG1 do?</span>
        <span class="qi" aria-hidden="true"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></span></button>
        <div class="ans"><div><p>BIG1 is a Pakistani tax and corporate-services firm. We file income-tax returns through
          FilePak, our own platform, and we handle the registrations and filings that go with running your affairs &mdash;
          NTN, sales tax, trademarks, company incorporation and SECP compliance, plus notices and advisory.</p></div></div></div>
      <div class="qa"><button aria-expanded="false"><span>Are you authorized to file with FBR?</span>
        <span class="qi" aria-hidden="true"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></span></button>
        <div class="ans"><div><p>Yes. Returns are filed through an authorized FBR e-intermediary channel &mdash; and we never
          ask for or store the IRIS password that belongs to you and FBR alone.</p></div></div></div>
      <div class="qa"><button aria-expanded="false"><span>Is my data safe?</span>
        <span class="qi" aria-hidden="true"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></span></button>
        <div class="ans"><div><p>Encrypted in transit and at rest, scoped per client, accessible only under role-based
          permission with the reason recorded. We do not sell your data or market off your return.</p></div></div></div>
      <div class="qa"><button aria-expanded="false"><span>How do I get started?</span>
        <span class="qi" aria-hidden="true"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg></span></button>
        <div class="ans"><div><p>Pick what you need &mdash; <a href="tax-filing.html">file your taxes</a>,
          <a href="services.html">request a service</a>, or message us on WhatsApp at +92&nbsp;339&nbsp;9999611 and a
          person will guide you from there.</p></div></div></div>
    </div>
  </div>
</section>'''

# generic closing CTA for the home page
CTA_HOME = '''<!-- ============================== HOME CTA ============================== -->
<section class="cta-sec" id="cta">
  <div class="wrap">
    <div class="cta-inner">
      <span class="eyebrow" data-reveal><span class="dot"></span>BIG1 &middot; FilePak</span>
      <h2 data-reveal style="--d:80ms">One team for your<br /><span class="grad-text">tax and compliance.</span></h2>
      <p class="lede" data-reveal style="--d:160ms">File your return, register a business, protect a brand, or answer a
        notice &mdash; start on WhatsApp and a real person picks it up.</p>
      <div class="cta-btns" data-reveal style="--d:240ms">
        <a class="btn btn-primary btn-lg" href="tax-filing.html">File your taxes
          <svg class="arw" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></a>
        <a class="btn btn-glass btn-lg" href="''' + WA_START + '''" target="_blank" rel="noopener noreferrer">Chat on WhatsApp</a>
      </div>
      <p class="cta-fine" data-reveal style="--d:360ms">Filed through an authorized FBR e-intermediary &middot; English &amp; &#1575;&#1585;&#1583;&#1608;</p>
    </div>
  </div>
</section>'''

CALC_HERO = '''<!-- ============================== CALC HERO ============================== -->
<section class="page-hero">
  <div class="wrap">
    <span class="eyebrow" data-reveal><span class="dot"></span>Free tools &middot; Tax Year 2025&ndash;26</span>
    <h1 data-reveal style="--d:80ms">Pakistan tax calculators.</h1>
    <p class="lede" data-reveal style="--d:160ms">Estimate your tax in seconds on the current Finance Act rates &mdash; salary,
      rental, capital gains and business income. No sign-up.</p>
  </div>
</section>'''

# ---- page assembly ----
def page(title, desc, canonical, active, body, calc=False):
    parts = [head_for(title, desc, canonical), BODY_OPEN, nav_for(active), body,
             "</main>", FOOTER, WA_FAB]
    if calc:
        parts.append(CALC_ENGINE)
    parts.append(GEN_SCRIPT)
    return "\n".join(parts)

TAX_BODY = "\n\n".join([HERO_TAX, COMPARE, FEATURES, HOW, INTEL, BEYOND, WHO, DASH, SECURITY, FAQ, CTA])
# these sections moved to their own pages, so their in-page anchors become cross-page links
TAX_BODY = TAX_BODY.replace('href="#services"', 'href="services.html"').replace('href="#calculators"', 'href="calculators.html"')

PAGES = {
    "index.html": page(
        "BIG1 &mdash; Tax Filing, Registration &amp; Corporate Services in Pakistan",
        "BIG1 helps individuals and businesses in Pakistan file income tax, register (NTN, sales tax, company, trademark) and stay compliant &mdash; a real team behind an intelligent platform.",
        "", "home",
        "\n\n".join([HOME_HERO, PILLARS, TRUST, STORIES, FAQ_HOME, CTA_HOME])),
    "tax-filing.html": page(
        "Tax Filing in Pakistan &mdash; FilePak by BIG1",
        "FilePak files your Pakistani income-tax return correctly to the last rupee: reads your documents, reconciles your wealth statement, matches withholding, and files through an authorized FBR e-intermediary.",
        "tax-filing.html", "tax", TAX_BODY),
    "calculators.html": page(
        "Free Pakistan Tax Calculators &mdash; Salary, Rental, Capital Gains &amp; Business",
        "Free income-tax calculators for Pakistan on current Finance Act rates: salary, rental income, capital gains on property and securities, and business income.",
        "calculators.html", "calc",
        "\n\n".join([CALC_HERO, CALC]), calc=True),
}

def build():
    for name, html in PAGES.items():
        na = len(re.findall(r"[^\x00-\x7F]", html))
        with io.open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        status = "OK" if na == 0 else "!! NON-ASCII %d" % na
        print("  %-20s %6d bytes  non-ascii:%s" % (name, len(html.encode("utf-8")), status))
        if na:
            for ch in re.findall(r"[^\x00-\x7F]", html)[:5]:
                sys.stderr.write("   U+%04X %r\n" % (ord(ch), ch))
            sys.exit(1)

if __name__ == "__main__":
    build()
    print("built.")
