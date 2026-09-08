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
import io, os, re, sys, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
BLD  = os.path.join(ROOT, "_build")

def read(name):
    with io.open(os.path.join(BLD, name), encoding="utf-8") as f:
        return f.read()

def pull_style(text):
    """Return inner CSS of the first <style>..</style>, or '' if none."""
    m = re.search(r"<style>(.*?)</style>", text, re.S)
    return m.group(1) if m else ""

def _scope_sel(sel, P):
    """Scope a single selector under .P; drop bare global resets (:root,*,html,body,a)."""
    sel = sel.strip()
    if not sel:
        return None
    if sel in (":root", "*", "html", "body", "a"):
        return None
    if re.match(r"^(a|body|html)([:\s]|$)", sel) and not sel.startswith(("html[", "a.", "a#", "a[")):
        return None  # a{}, a:hover, body ..., html ... — global resets, shared head already has them
    if sel.startswith("html"):                     # html[data-theme=..] .x  ->  html[..] .P .x
        parts = sel.split(None, 1)
        return parts[0] + " " + P + " " + parts[1] if len(parts) == 2 else None
    return P + " " + sel

def scope_css(css, P):
    """Prefix every selector in `css` with `P` so it can't touch the shared nav/footer.
    Keeps @media/@supports (recurses) and @keyframes/@font-face (verbatim); drops global resets."""
    def block(s):
        out, i, n = "", 0, len(s)
        while i < n:
            at, br = s.find("@", i), s.find("{", i)
            if br == -1:
                break
            if at != -1 and at < br:                 # at-rule
                pre = s[at:br]; name = pre.split()[0] if pre.split() else pre
                depth, j = 1, br + 1
                while j < n and depth:
                    depth += (s[j] == "{") - (s[j] == "}"); j += 1
                inner = s[br + 1:j - 1]
                if name.startswith(("@keyframes", "@-webkit-keyframes", "@font-face")):
                    out += s[at:j]
                else:
                    out += pre + "{" + block(inner) + "}"
                i = j
            else:                                    # normal rule
                sel = s[i:br]
                depth, j = 1, br + 1
                while j < n and depth:
                    depth += (s[j] == "{") - (s[j] == "}"); j += 1
                decls = s[br + 1:j - 1]
                scoped = [x for x in (_scope_sel(p, P) for p in sel.split(",")) if x]
                if scoped:
                    out += ",".join(scoped) + "{" + decls + "}"
                i = j
        return out
    return block(css)

def standalone(src, cls, wrap_inner):
    """Import a standalone page: return (scoped_css, body, page_js) for build.py assembly."""
    t = read(src)
    css = scope_css(re.search(r"<style>(.*?)</style>", t, re.S).group(1), "." + cls)
    inner = re.search(r"<main[^>]*>(.*?)</main>", t, re.S).group(1)
    if wrap_inner:
        inner = '<div class="wrap">' + inner + "</div>"
    jm = re.search(r"<script>(.*?)</script>", t, re.S)
    body = ('<div class="%s">%s</div>' % (cls, inner)).replace("{{APP}}", APP_URL)
    return css, body, (jm.group(1) if jm else "")

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
/* home hero: reuses the shared .hero/.hero-grid; a generic compliance-overview mock on the right */
.hrow{display:flex;align-items:center;gap:11px;padding:10px 12px;border-radius:12px;border:1px solid var(--border);background:var(--bg-sub)}
.hrow .hi{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;flex-shrink:0;color:var(--accent);
  background:linear-gradient(135deg,rgba(6,95,70,.13),rgba(16,158,125,.1));border:1px solid var(--border)}
.hrow .hi svg{width:16px;height:16px}
.hrow .hl{flex:1;min-width:0}
.hrow .hl b{display:block;font-size:.82rem;font-weight:600;letter-spacing:-.01em}
.hrow .hl span{font-size:.67rem;color:var(--text-3)}
.hnext{margin-top:13px;padding:10px 13px;border-radius:12px;font-size:.77rem;color:var(--emerald-700);line-height:1.4;
  background:linear-gradient(120deg,rgba(16,185,129,.1),rgba(16,158,125,.06));border:1px solid rgba(16,185,129,.22)}
html[data-theme="dark"] .hnext{color:var(--emerald-300)}
/* clean floating card (distinct from the tax page's browser-window mock) */
.hcard{position:relative;background:var(--surface-solid);border:1px solid var(--border);border-radius:24px;padding:24px;box-shadow:var(--shadow-xl)}
.hcard-h{display:flex;align-items:center;gap:13px;margin-bottom:16px}
.hcard-h .hb{width:46px;height:46px;border-radius:14px;display:grid;place-items:center;color:#fff;flex-shrink:0;
  background:linear-gradient(140deg,var(--emerald-700),var(--emerald-500));box-shadow:0 12px 22px -10px rgba(6,95,70,.55)}
.hcard-h .hb svg{width:24px;height:24px}
.hcard-h b{display:block;font-size:1.02rem;letter-spacing:-.02em}
.hcard-h .s{font-size:.72rem;color:var(--text-3)}
.hcard-h .pill{margin-left:auto}
/* ---------- Rotating full-bleed hero (home) ---------- */
.rhero{position:relative;min-height:100svh;display:flex;align-items:center;overflow:hidden;isolation:isolate;background:var(--emerald-900)}
.rhero-slides{position:absolute;inset:0;z-index:-2}
.rslide{position:absolute;inset:0;background-size:cover;background-position:center;opacity:0;transform:scale(1.03);
  transition:opacity 1s ease;will-change:opacity,transform}
.rslide.on{opacity:1;animation:kenburns 5s ease-out forwards}
@keyframes kenburns{0%{transform:scale(1.03)}100%{transform:scale(1.15)}}
.rhero-ov{position:absolute;inset:0;z-index:-1;
  background:linear-gradient(100deg,rgba(3,24,18,.92) 0%,rgba(4,40,30,.76) 42%,rgba(4,30,22,.42) 78%,rgba(4,30,22,.24) 100%)}
.rhero-inner{position:relative;z-index:1;color:#fff;padding-top:calc(var(--nav-h) + 24px);padding-bottom:46px}
.rhero .eyebrow{color:#eafff5;background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.24)}
.rhero .eyebrow .dot{background:var(--emerald-300)}
.rtexts{position:relative;margin:22px 0 0;min-height:236px}
.rtext{position:absolute;inset:0;opacity:0;transform:translateY(10px);transition:opacity .7s ease,transform .7s ease;pointer-events:none;max-width:700px}
.rtext.on{opacity:1;transform:none;position:relative;pointer-events:auto}
.rtext h1{font-size:clamp(2.2rem,4.7vw,3.5rem);letter-spacing:-.035em;line-height:1.06;color:#fff;margin-bottom:16px;text-shadow:0 2px 30px rgba(0,0,0,.22)}
.rtext p{font-size:clamp(.98rem,1.5vw,1.14rem);color:rgba(255,255,255,.9);line-height:1.6;max-width:560px}
.rhero-cta{display:flex;flex-wrap:wrap;gap:14px;margin-top:6px}
.rhero-cta .btn-glass{background:rgba(255,255,255,.13);border-color:rgba(255,255,255,.32);color:#fff}
.rhero-cta .btn-glass:hover{background:rgba(255,255,255,.22);border-color:rgba(255,255,255,.5)}
.rdots{display:flex;gap:9px;margin-top:34px}
.rdot{width:30px;height:4px;border-radius:4px;background:rgba(255,255,255,.35);border:0;padding:0;cursor:pointer;transition:.3s}
.rdot.on{background:#fff;width:46px}
/* light nav while over the dark hero (home, before scroll) */
html.has-hero .nav:not(.stuck) .nav-links a{color:rgba(255,255,255,.85)}
html.has-hero .nav:not(.stuck) .nav-links a:hover{color:#fff;background:rgba(255,255,255,.15)}
html.has-hero .nav:not(.stuck) .brand .tag{color:#fff;border-color:rgba(255,255,255,.45)}
html.has-hero .nav:not(.stuck) .bmark{background:none;-webkit-text-fill-color:#fff;color:#fff}
html.has-hero .nav:not(.stuck) .theme-btn{color:#fff;border-color:rgba(255,255,255,.45);background:rgba(255,255,255,.12)}
html.has-hero .nav:not(.stuck) .nav-toggle{color:#fff;border-color:rgba(255,255,255,.45)}
@media (prefers-reduced-motion:reduce){.rslide,.rslide.on{animation:none;transition:opacity .5s ease;transform:none}}
@media (max-width:640px){.rtexts{min-height:300px}}
.pillars{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px;margin:8px 0 8px}
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
.what-tools{text-align:center;margin-top:24px;font-size:.92rem;color:var(--text-2)}
.what-tools a{color:var(--accent);font-weight:650}
/* photographs on the pillar / two-ways cards (Pexels licence; credits in assets/PHOTO-CREDITS.txt) */
.pillar .shot{display:block;width:100%;height:auto;aspect-ratio:16/10;object-fit:cover;border-radius:14px;
  border:1px solid var(--border);margin:-6px 0 16px;background:var(--bg-sub);
  filter:saturate(.9) contrast(1.02);transition:filter .3s var(--ease),transform .3s var(--ease)}
.pillar:hover .shot{filter:saturate(1);transform:translateY(-2px)}
#two-ways .pillar .shot{aspect-ratio:16/9}
/* "See it working" framed product screens (tax page) + demo walkthrough (demo.html) */
.shots{display:grid;gap:28px;max-width:1120px;margin:0 auto}
.shotrow{display:grid;grid-template-columns:1.15fr 1fr;gap:36px;align-items:center;padding:10px 0}
.shotrow.rev .shot-img{order:2}
.shot-img{background:linear-gradient(135deg,rgba(6,95,70,.10),rgba(16,185,129,.06));border:1px solid var(--border);border-radius:22px;padding:14px}
.shot-img img{display:block;width:100%;height:auto;border-radius:12px;box-shadow:0 18px 40px -22px rgba(6,95,70,.45)}
.shot-copy h3{font-size:1.35rem;letter-spacing:-.02em;line-height:1.2;margin:10px 0 8px}
.shot-copy p{color:var(--text-2);line-height:1.6;font-size:.95rem}
@media (max-width:860px){.shotrow{grid-template-columns:1fr;gap:16px}.shotrow.rev .shot-img{order:0}}
.demo-steps{display:grid;gap:36px;max-width:900px;margin:0 auto}
.demo-step{display:grid;grid-template-columns:52px 1fr;gap:16px;align-items:start}
.demo-n{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;font-weight:800;color:#fff;
  background:linear-gradient(140deg,var(--emerald-700),var(--emerald-500));box-shadow:0 10px 20px -9px rgba(6,95,70,.5)}
.demo-step h3{font-size:1.15rem;letter-spacing:-.015em;margin:6px 0 4px}
.demo-step p{color:var(--text-2);line-height:1.55;font-size:.93rem}
.demo-step img{display:block;width:100%;height:auto;border-radius:14px;border:1px solid var(--border);margin-top:12px;box-shadow:0 18px 40px -24px rgba(6,95,70,.45)}
.hero-trust{margin-top:14px;font-size:.8rem;color:var(--text-3);max-width:560px;line-height:1.5}
.rhero .hero-trust{color:rgba(255,255,255,.78)}
.foot-trust{display:block;font-size:.74rem;color:var(--text-3);max-width:640px;line-height:1.5;margin-bottom:6px}
@media (max-width:980px){.pillars{grid-template-columns:repeat(2,1fr)}}
@media (max-width:560px){.pillars{grid-template-columns:1fr;max-width:460px;margin-inline:auto}}
/* calculators page header */
.page-hero{padding:clamp(46px,7vw,88px) 0 clamp(10px,2vw,24px);text-align:center}
.page-hero h1{font-size:clamp(1.9rem,4.4vw,3rem);letter-spacing:-.035em;line-height:1.08;margin:16px 0 14px}
.page-hero .lede{max-width:620px;margin-inline:auto}
/* insights (news / articles) */
.insights-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}
@media (max-width:900px){.insights-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width:600px){.insights-grid{grid-template-columns:1fr;max-width:440px;margin-inline:auto}}
.insight{display:flex;flex-direction:column;text-decoration:none;color:inherit;border-radius:var(--r-lg);overflow:hidden;
  border:1px solid var(--border);background:var(--surface-solid);transition:transform .3s var(--ease),box-shadow .3s var(--ease),border-color .3s var(--ease)}
.insight:hover{transform:translateY(-5px);box-shadow:var(--shadow-lg);border-color:var(--border-strong)}
.insight-img{aspect-ratio:16/10;background-size:cover;background-position:center;
  background-image:linear-gradient(135deg,var(--emerald-700),var(--blue-600))}
.insight-body{padding:17px 20px 20px;display:flex;flex-direction:column;gap:7px;flex:1}
.insight-cat{font-size:.64rem;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:var(--accent)}
.insight-t{font-size:1.02rem;font-weight:650;letter-spacing:-.02em;line-height:1.32}
.insight-ex{font-size:.83rem;color:var(--text-2);line-height:1.55}
.insight-date{margin-top:auto;font-size:.72rem;color:var(--text-3);padding-top:6px}
/* article page */
.article{max-width:740px;margin-inline:auto}
.article h2{font-size:clamp(1.25rem,2.3vw,1.6rem);letter-spacing:-.02em;margin:26px 0 10px}
.article h3{font-size:1.08rem;margin:20px 0 8px}
.article p{font-size:.97rem;color:var(--text-2);line-height:1.75;margin-bottom:14px}
.article ul{margin:0 0 16px;padding-left:20px;display:grid;gap:7px}
.article li{font-size:.95rem;color:var(--text-2);line-height:1.6}
.article a{color:var(--accent);font-weight:600}
.article-hero{max-width:760px;margin-inline:auto}
.article-back{display:inline-flex;gap:6px;align-items:center;font-size:.83rem;font-weight:650;color:var(--accent);text-decoration:none;margin-top:32px}
.article-note{max-width:740px;margin:22px auto 0;font-size:.78rem;color:var(--text-3);border-left:2px solid var(--border-strong);padding-left:12px;line-height:1.55}
"""

# ---- head / body-open (shared) ----
HEAD_RAW = F01[:F01.index("</head>") + len("</head>")]
BODY_OPEN = F01[F01.index("</head>") + len("</head>"):].strip("\n")  # <body> + skip + scrollbar

def head_for(title, desc, canonical, extra_css=""):
    h = HEAD_RAW
    h = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, h, flags=re.S)
    h = re.sub(r'(<meta name="description" content=").*?(" />)', lambda m: m.group(1)+desc+m.group(2), h, flags=re.S)
    h = re.sub(r'(<meta property="og:title" content=").*?(" />)', lambda m: m.group(1)+title+m.group(2), h, flags=re.S)
    h = re.sub(r'(<meta property="og:description" content=").*?(" />)', lambda m: m.group(1)+desc+m.group(2), h, flags=re.S)
    h = re.sub(r'(<meta property="og:url" content=").*?(" />)', lambda m: m.group(1)+"https://big1.com.pk/"+canonical+m.group(2), h, flags=re.S)
    h = re.sub(r'(<link rel="canonical" href=").*?(" />)', lambda m: m.group(1)+"https://big1.com.pk/"+canonical+m.group(2), h, flags=re.S)
    h = re.sub(r"<style>.*?</style>", "<style>\n" + CSS + "\n" + NEW_CSS + "\n" + extra_css + "\n</style>", h, flags=re.S, count=1)
    # Meta (Facebook) domain verification for big1.com.pk — must stay in a STATIC <head> permanently;
    # Meta re-checks periodically and un-verifies if it disappears, so it lives in the shared head, not
    # one page. Public token, safe to commit. Added on every page's <head> before the closing tag.
    h = h.replace("</head>",
                  '<meta name="facebook-domain-verification" content="pq059rmb39z0t76ve40w2312t7hxni" />\n</head>')
    return h

# ---- shared nav (cross-page links + active state) ----
NAVLINKS = [("home","index.html","Home"),("tax","tax-filing.html","Tax filing"),
            ("services","services.html","Services"),("insights","insights.html","Insights"),
            ("calc","calculators.html","Calculators")]
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
      <a class="btn btn-primary btn-sm btn-cta" href="%s" data-start>Get started <svg class="arw" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></a>
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

# ---- the FilePak application URL. Live on Cloud Run. Pages use the {{APP}} token; when the branded
#      domain (e.g. app.big1.com.pk) is mapped in front of Cloud Run, swap this one line.
APP_URL = "https://app.big1.com.pk"

# ---- FEES: single source of truth = the FilePak backend rate card (GET /api/v1/pricing, which serves
# backend/app/payments/pricing.py -- the same table the app and the WhatsApp bot use). At build time we
# fetch it and bake the numbers in ({{FEE:kind}} tokens + window.BIG1_FEES); pricing.json is the last
# good snapshot used when the API is unreachable. At runtime the page re-fetches and refreshes [data-fee].
import json as _json, urllib.request as _urlreq
_FEES_SNAPSHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pricing.json")

def _load_fees():
    try:
        # Cloudflare in front of the app rejects the default Python user-agent (403) -- identify as a browser.
        req = _urlreq.Request(APP_URL + "/api/v1/pricing",
                              headers={"User-Agent": "Mozilla/5.0 (big1.com.pk site build)", "Accept": "application/json"})
        with _urlreq.urlopen(req, timeout=10) as r:
            data = _json.loads(r.read().decode("utf-8"))
        fees = {k: int(v) for k, v in (data.get("fees") or {}).items() if int(v) > 0}
        if fees:
            with io.open(_FEES_SNAPSHOT, "w", encoding="utf-8", newline="\n") as f:
                _json.dump({"currency": "PKR", "fees": fees}, f, indent=2, sort_keys=True)
            print("  fees: %d kinds from the live rate card" % len(fees))
            return fees
    except Exception as e:  # noqa: BLE001
        sys.stderr.write("  fees: live rate card unavailable (%s) -- using pricing.json snapshot\n" % e)
    try:
        with io.open(_FEES_SNAPSHOT, "r", encoding="utf-8") as f:
            return {k: int(v) for k, v in _json.load(f)["fees"].items()}
    except Exception:  # noqa: BLE001
        sys.stderr.write("  fees: NO snapshot either -- fee tokens will render as '?'\n")
        return {}

FEES = _load_fees()

def fee_txt(kind):
    v = FEES.get(kind)
    return "{:,}".format(v) if v else "?"

def _apply_fees(html):
    html = re.sub(r"\{\{FEE:([a-z_]+)\}\}", lambda m: fee_txt(m.group(1)), html)
    script = "<script>window.BIG1_FEES=%s;</script>" % _json.dumps({"currency": "PKR", "fees": FEES}, sort_keys=True)
    return html.replace(BODY_OPEN, BODY_OPEN + "\n" + script, 1) if BODY_OPEN in html else html

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
HOME_HERO = '''<!-- ============================== HOME HERO (rotating) ============================== -->
<section class="rhero" id="rhero">
  <div class="rhero-slides" aria-hidden="true">
    <div class="rslide on" style="background-image:url(\'assets/hero-1-tax.jpg\')"></div>
    <div class="rslide" style="background-image:url(\'assets/hero-2-register.jpg\')"></div>
    <div class="rslide" style="background-image:url(\'assets/hero-3-corporate.jpg\')"></div>
    <div class="rslide" style="background-image:url(\'assets/hero-4-team.jpg\')"></div>
  </div>
  <div class="rhero-ov" aria-hidden="true"></div>
  <div class="wrap rhero-inner">
    <span class="eyebrow"><span class="dot"></span>Tax, registration &amp; corporate services &middot; Pakistan</span>
    <div class="rtexts">
      <div class="rtext on" data-cta="File your taxes" data-href="tax-filing.html" data-start="1">
        <h1>File correctly.<br />Down to the last rupee.</h1>
        <p>Guided income-tax filing &mdash; computed to the rupee and filed through an authorized FBR e-intermediary.</p>
      </div>
      <div class="rtext" data-cta="Start a registration" data-href="services.html" data-start="0">
        <h1>Register, incorporate,<br />comply.</h1>
        <p>NTN, sales tax, trademark and company registration &mdash; the exact documents listed up front.</p>
      </div>
      <div class="rtext" data-cta="Explore corporate services" data-href="services.html" data-start="0">
        <h1>Built for<br />Pakistani business.</h1>
        <p>From company formation to SECP compliance &mdash; handled end to end.</p>
      </div>
      <div class="rtext" data-cta="Get started" data-href="services.html" data-start="0">
        <h1>A real team behind<br />an intelligent platform.</h1>
        <p>Filed by people who know Pakistani tax &mdash; in English or&nbsp;&#1575;&#1585;&#1583;&#1608;.</p>
      </div>
    </div>
    <div class="rhero-cta">
      <a class="btn btn-primary btn-lg" id="rheroCta" href="tax-filing.html" data-start>File your taxes
        <svg class="arw" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></a>
      <a class="btn btn-glass btn-lg" href="services.html">Explore all services</a>
    </div>
    <div class="rdots" role="group" aria-label="Choose hero slide">
      <button class="rdot on" type="button" data-i="0" aria-label="Slide 1"></button>
      <button class="rdot" type="button" data-i="1" aria-label="Slide 2"></button>
      <button class="rdot" type="button" data-i="2" aria-label="Slide 3"></button>
      <button class="rdot" type="button" data-i="3" aria-label="Slide 4"></button>
    </div>
  </div>
</section>'''

PILLARS = '''<!-- ============================== PILLARS ============================== -->
<section class="sec" id="what" style="padding-top:clamp(34px,3.8vw,54px)">
  <div class="wrap">
    <div class="sec-head center" data-reveal>
      <span class="eyebrow"><span class="dot"></span>What we do</span>
      <h2 class="h1">One firm for tax, registration<br /><span class="serif">and everything after.</span></h2>
      <p class="lede">From your income-tax return to trademarks, company formation and advisory &mdash; handled under one roof, by a real team.</p>
    </div>
  </div>
  <div class="wrap wrap-wide">
    <div class="pillars">
      <a class="pillar" data-reveal href="tax-filing.html">
        <span class="pic"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h9l5 5v13H6z"/><path d="M14 3v6h6"/><path d="M9.5 13h5M9.5 16.5h5"/></svg></span>
        <img class="shot" src="assets/img-income-tax.webp" width="1200" height="800" loading="lazy" decoding="async" alt="Preparing an income-tax return with a calculator and documents" />
        <h3>Income tax</h3>
        <p>Guided returns computed to the rupee, prior-year filing, notices and tax advisory &mdash; filed through an authorized FBR e-intermediary.</p>
        <span class="go">File your taxes <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></span>
      </a>

      <a class="pillar" data-reveal style="--d:80ms" href="services.html#taxation">
        <span class="pic"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18M5 21V9l7-4 7 4v12"/><path d="M9.5 21v-5h5v5"/></svg></span>
        <img class="shot" src="assets/img-registrations.webp" width="1200" height="800" loading="lazy" decoding="async" alt="Stamping an official registration document" />
        <h3>Registrations</h3>
        <p>NTN, Sales Tax (GST) and Provincial Sales Tax &mdash; with the exact documents for your case listed up front.</p>
        <span class="go">Get registered <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></span>
      </a>

      <a class="pillar" data-reveal style="--d:160ms" href="services.html#ip">
        <span class="pic"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9V6z"/><path d="M9.3 12l1.8 1.8L15 10"/></svg></span>
        <img class="shot" src="assets/img-ip.webp" width="1200" height="800" loading="lazy" decoding="async" alt="A designer sketching a brand logo on a tablet" />
        <h3>Intellectual property</h3>
        <p>Trademark, copyright, patent and design registration with IPO&nbsp;Pakistan &mdash; protect your brand and your ideas.</p>
        <span class="go">Protect your brand <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></span>
      </a>

      <a class="pillar" data-reveal style="--d:240ms" href="services.html#corporate">
        <span class="pic"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M3 12h18"/></svg></span>
        <img class="shot" src="assets/img-corporate.webp" width="1200" height="800" loading="lazy" decoding="async" alt="Aerial view of Karachi's business district" />
        <h3>Corporate &amp; advisory</h3>
        <p>Company incorporation, SECP compliance, and corporate &amp; business advisory &mdash; structure and run your company right.</p>
        <span class="go">Explore corporate <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></span>
      </a>
    </div>
    <p class="what-tools" data-reveal>Just exploring? <a href="calculators.html">Try the free tax calculators &rarr;</a></p>
  </div>
</section>'''

# Two ways to file — mirrors the app's "File your Income Tax Return" chooser (Services → Taxation).
# Prices are the app's rate card (Self-Filing 3,900 · Priority 8,000 / 10,000 estimates); keep in sync with
# backend/app/payments/pricing.py. Deep links open the chosen way directly after sign-in.
TWO_WAYS = '''<!-- ============================== TWO WAYS TO FILE ============================== -->
<section class="sec" id="two-ways" style="padding-top:clamp(28px,3.2vw,46px)">
  <div class="wrap">
    <div class="sec-head center" data-reveal>
      <span class="eyebrow"><span class="dot"></span>File your income tax return</span>
      <h2 class="h1">Two ways to file.<br /><span class="serif">Same profile, your choice of effort.</span></h2>
      <p class="lede">Prepare it yourself with FilePak&rsquo;s guided steps, or hand us your documents and let the BIG1 team prepare and file it for you.</p>
    </div>
  </div>
  <div class="wrap wrap-wide">
    <div class="pillars" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr));max-width:980px;margin:0 auto">
      <a class="pillar" data-reveal href="{{APP}}/?service=self_filing" target="_blank" rel="noopener noreferrer">
        <img class="shot" src="assets/img-income-tax.webp" width="1200" height="800" loading="lazy" decoding="async" alt="Preparing an income-tax return with a calculator and documents" />
        <span class="pic"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h9l5 5v13H6z"/><path d="M14 3v6h6"/><path d="M9 13h6M9 17h6"/></svg></span>
        <h3>Self-Filing &middot; Rs <span data-fee="income_tax_return">{{FEE:income_tax_return}}</span></h3>
        <p>You prepare your return yourself with step-by-step guidance &mdash; automatic tax calculation, wealth reconciliation, IRIS-format summary and Excel export. Pay at the end, before filing.</p>
        <span class="go">Start Self-Filing <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></span>
      </a>
      <a class="pillar" data-reveal style="--d:80ms" href="{{APP}}/?service=priority" target="_blank" rel="noopener noreferrer">
        <img class="shot" src="assets/img-assisted.webp" width="1200" height="800" loading="lazy" decoding="async" alt="An adviser going through figures with a client" />
        <span class="pic"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 3 14h8l-1 8 10-12h-8z"/></svg></span>
        <h3>Assisted Filing &middot; from Rs <span data-fee="priority_filing_salary">{{FEE:priority_filing_salary}}</span></h3>
        <p>Don&rsquo;t know how to prepare your return? Tick what applies, upload what you have &mdash; nothing is mandatory &mdash; and our team prepares and files it. Salary-only Rs <span data-fee="priority_filing_salary">{{FEE:priority_filing_salary}}</span> &middot; business or multiple incomes Rs <span data-fee="priority_filing_complex">{{FEE:priority_filing_complex}}</span> (estimates; you pay when it&rsquo;s ready).</p>
        <span class="go">Start Assisted Filing <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></span>
      </a>
    </div>
    <p class="what-tools" data-reveal>Either way, nothing is filed without your approval &mdash; and no need to send last year&rsquo;s return, we retrieve it from IRIS.</p>
  </div>
</section>'''
# {{APP}} is only substituted for standalone pages (see standalone()); inline home/tax blocks resolve it here.
TWO_WAYS = TWO_WAYS.replace("{{APP}}", APP_URL)

# ---- "See it working": framed FilePak screenshots (demo profile, fictitious data) with one idea each.
#      Screens: assets/app-*.webp, captured from the app with a demo profile ("Ahmed Khan", fake CNIC).
def _shot(img, w, h, eyebrow, title, body, rev=False, alt=""):
    return '''
      <div class="shotrow%s" data-reveal>
        <div class="shot-img"><img src="assets/%s" width="%d" height="%d" loading="lazy" decoding="async" alt="%s" /></div>
        <div class="shot-copy"><span class="eyebrow"><span class="dot"></span>%s</span><h3>%s</h3><p>%s</p></div>
      </div>''' % (" rev" if rev else "", img, w, h, alt, eyebrow, title, body)

SHOTS = '''<!-- ============================== SEE IT WORKING ============================== -->
<section class="sec" id="see-it-working">
  <div class="wrap">
    <div class="sec-head center" data-reveal>
      <span class="eyebrow"><span class="dot"></span>See it working</span>
      <h2 class="h1">This is FilePak.<br /><span class="serif">Real screens, not promises.</span></h2>
      <p class="lede">Every screen below is the actual product, shown with a demo profile. <a href="demo.html">Walk through the whole flow &rarr;</a></p>
    </div>
    <div class="shots">''' + _shot("app-self.webp", 1100, 515, "Self-Filing", "Guided steps with your live tax position",
        "Answer plain questions, one income source at a time. The engine recomputes your taxable income, tax charge and tax already paid as you type &mdash; no spreadsheet, no guessing.",
        alt="FilePak guided income step with the live tax summary") + _shot("app-assisted.webp", 620, 680, "Assisted Filing", "Tick what applies. Upload what you have.",
        "Nothing is mandatory. Tick the items that apply to you, attach the documents you already have, and the BIG1 team prepares the return and follows up for the rest.", rev=True,
        alt="FilePak Assisted Filing document checklist") + _shot("app-iris.webp", 660, 752, "Before filing", "An IRIS-format summary you can read",
        "Your return laid out exactly as FBR structures it &mdash; income heads, codes and computations &mdash; so you review the real thing before anything is filed. Download it to Excel any time.",
        alt="FilePak IRIS-format return summary") + _shot("app-dashboard.webp", 1100, 515, "Your account", "Every request and return, in one place",
        "Returns, registrations and trademark work show their live status on one dashboard. You can still edit a submitted return until our team starts on it.", rev=True,
        alt="FilePak dashboard showing services and a submitted return") + '''
    </div>
  </div>
</section>'''

# ---- demo.html: a no-login walkthrough of the real product (the "Launch demo" idea, without exposing the app) ----
def _step(n, img, w, h, title, body, alt=""):
    return '''
      <div class="demo-step" data-reveal>
        <div class="demo-n">%d</div>
        <div><h3>%s</h3><p>%s</p><img src="assets/%s" width="%d" height="%d" loading="lazy" decoding="async" alt="%s" /></div>
      </div>''' % (n, title, body, img, w, h, alt)

DEMO_BODY = '''<!-- ============================== DEMO WALKTHROUGH ============================== -->
<section class="sec" id="demo" style="padding-top:calc(var(--nav-h) + 96px)">
  <div class="wrap">
    <div class="sec-head center" data-reveal>
      <span class="eyebrow"><span class="dot"></span>See how it works</span>
      <h1 class="h1">Filing a return in FilePak,<br /><span class="serif">start to finish.</span></h1>
      <p class="lede">A read-only walkthrough of the real product using a demo profile. Nothing here is a mock-up; every screen is what you get after signing in.</p>
    </div>
    <div class="demo-steps">''' + _step(1, "app-chooser.webp", 620, 390, "Choose how you want to file",
        "Two ways, same profile. Self-Filing if you want to prepare it yourself with guidance; Assisted Filing if you would rather hand us your documents. Fees are shown up front; Assisted Filing is paid last, when the return is ready.",
        "FilePak filing chooser") + _step(2, "app-self.webp", 1100, 515, "Self-Filing: guided, one source at a time",
        "Salary, savings, property, business &mdash; each in its own step with plain-language questions. Your live position updates on the left as you go.",
        "FilePak guided income step") + _step(3, "app-assisted.webp", 620, 680, "Assisted Filing: tick, upload, done",
        "Tick what applies to you and upload what you have. Nothing is mandatory &mdash; the BIG1 team prepares the return from your documents and contacts you for anything missing. No need for last year&rsquo;s return; we retrieve it from IRIS.",
        "FilePak Assisted Filing checklist") + _step(4, "app-iris.webp", 660, 752, "Review the return in IRIS format",
        "Before anything is filed you see the return exactly as FBR structures it &mdash; income heads, codes, computations, and the wealth reconciliation. Export to Excel with one click.",
        "FilePak IRIS-format summary") + _step(5, "app-dashboard.webp", 1100, 515, "Track everything from one dashboard",
        "Your returns, registrations and trademark requests show their live status. A submitted return stays editable until our team starts work on it; after that, one tap reaches an agent.",
        "FilePak dashboard") + '''
    </div>
    <div class="cta-btns" data-reveal style="justify-content:center;margin-top:36px">
      <a class="btn btn-primary btn-lg" href="''' + APP_URL + '''/?service=self_filing" target="_blank" rel="noopener noreferrer">Start Self-Filing &middot; Rs {{FEE:income_tax_return}}</a>
      <a class="btn btn-lg" style="border:1px solid var(--border)" href="''' + APP_URL + '''/?service=priority" target="_blank" rel="noopener noreferrer">Start Assisted Filing &middot; from Rs {{FEE:priority_filing_salary}}</a>
    </div>
    <p class="what-tools" data-reveal>BIG1 is a chartered accountancy firm. Returns are filed through an authorised FBR e-intermediary &mdash; we never ask for or store your IRIS password. Demo profile: fictitious data.</p>
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
      <h2 data-reveal style="--d:80ms">One team for tax, registration<br /><span class="grad-text">and corporate services.</span></h2>
      <p class="lede" data-reveal style="--d:160ms">File your return, register a business, protect a brand, or answer a
        notice &mdash; start on WhatsApp and a real person picks it up.</p>
      <div class="cta-btns" data-reveal style="--d:240ms">
        <a class="btn btn-primary btn-lg" href="tax-filing.html" data-start>File your taxes
          <svg class="arw" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></a>
        <a class="btn btn-glass btn-lg" href="''' + WA_START + '''" target="_blank" rel="noopener noreferrer">Chat on WhatsApp</a>
      </div>
      <p class="cta-fine" data-reveal style="--d:360ms">Filed through an authorized FBR e-intermediary &middot; English &amp; &#1575;&#1585;&#1583;&#1608;</p>
    </div>
  </div>
</section>'''

TRUST_HOME = '''<!-- ============================== HOME TRUST BAND ============================== -->
<section class="trust" aria-label="BIG1 at a glance">
  <div class="wrap wrap-wide">
    <div class="trust-in">
      <div class="stat" data-reveal>
        <div class="v tnum" data-count="20" data-suffix="+">0</div>
        <div class="l">Services across tax, registration &amp; corporate &mdash; handled under one roof.</div>
      </div>
      <div class="stat" data-reveal style="--d:80ms">
        <div class="v tnum" data-count="3">0</div>
        <div class="l">Authorities we file with &mdash; FBR, IPO&nbsp;Pakistan and SECP.</div>
      </div>
      <div class="stat" data-reveal style="--d:160ms">
        <div class="v tnum" data-count="10" data-suffix=" yrs">0</div>
        <div class="l">Of prior income-tax returns you can still file &mdash; back to 2016.</div>
      </div>
      <div class="stat" data-reveal style="--d:240ms">
        <div class="v tnum" style="font-size:clamp(1.6rem,3vw,2.1rem)">EN&nbsp;/&nbsp;&#1575;&#1585;&#1583;&#1608;</div>
        <div class="l">Every step available in English and Urdu.</div>
      </div>
    </div>
  </div>
  <div class="marquee" aria-hidden="true">
    <ul>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> Income-tax filing</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> NTN registration</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> Sales tax (GST) &amp; PST</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> Trademark &mdash; IPO Pakistan</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> Company incorporation &mdash; SECP</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> Authorized FBR e-intermediary</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> AES-256 encryption</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> English &amp; &#1575;&#1585;&#1583;&#1608;</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> Income-tax filing</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> NTN registration</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> Sales tax (GST) &amp; PST</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> Trademark &mdash; IPO Pakistan</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> Company incorporation &mdash; SECP</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> Authorized FBR e-intermediary</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> AES-256 encryption</li>
      <li><svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="4"/></svg> English &amp; &#1575;&#1585;&#1583;&#1608;</li>
    </ul>
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
def page(title, desc, canonical, active, body, calc=False, extra_css="", extra_js=""):
    parts = [head_for(title, desc, canonical, extra_css), BODY_OPEN, nav_for(active), body,
             "</main>", FOOTER, WA_FAB]
    if calc:
        parts.append(CALC_ENGINE)
    if extra_js:
        parts.append("<script>\n" + extra_js + "\n</script>")
    parts.append(GEN_SCRIPT)
    return "\n".join(parts)

# ==================== INSIGHTS (content/insights/*.md -> cards + pages) ====================
_MONTHS = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def _esc(s):
    """HTML-escape and convert any non-ASCII char to a numeric entity (keeps the ascii==0 guard happy)."""
    o = []
    for ch in (s or ""):
        c = ord(ch)
        if ch == "&": o.append("&amp;")
        elif ch == "<": o.append("&lt;")
        elif ch == ">": o.append("&gt;")
        elif c > 127: o.append("&#%d;" % c)
        else: o.append(ch)
    return "".join(o)

def _inline(s):
    """Minimal inline markdown: [text](url), **bold**, *italic*."""
    links = []
    def cap(m):
        links.append((m.group(1), m.group(2))); return "\x01%d\x01" % (len(links) - 1)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", cap, s)
    s = _esc(s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    s = re.sub("\x01(\\d+)\x01", lambda m: '<a href="%s">%s</a>' % (_esc(links[int(m.group(1))][1]), _esc(links[int(m.group(1))][0])), s)
    return s

def _render_md(md):
    """Block-level markdown: ## / ### headings, - lists, paragraphs."""
    lines = (md or "").replace("\r", "").split("\n"); out = []; i, n = 0, len((md or "").replace("\r", "").split("\n"))
    while i < n:
        st = lines[i].strip()
        if not st: i += 1; continue
        if st.startswith("### "): out.append("<h3>" + _inline(st[4:]) + "</h3>"); i += 1
        elif st.startswith("## "): out.append("<h2>" + _inline(st[3:]) + "</h2>"); i += 1
        elif st.startswith("# "): out.append("<h2>" + _inline(st[2:]) + "</h2>"); i += 1
        elif st.startswith("- "):
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append("<li>" + _inline(lines[i].strip()[2:]) + "</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
        else:
            buf = []
            while i < n and lines[i].strip() and not lines[i].strip().startswith(("#", "- ")):
                buf.append(lines[i].strip()); i += 1
            out.append("<p>" + _inline(" ".join(buf)) + "</p>")
    return "\n".join(out)

def _fmt_date(d):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", d or "")
    return "%s %d, %s" % (_MONTHS[int(m.group(2))], int(m.group(3)), m.group(1)) if m else _esc(d or "")

def _frontmatter(text):
    meta, body = {}, text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1); meta[k.strip().lower()] = v.strip()
            body = text[end + 4:].lstrip("\n")
    return meta, body

def load_insights():
    items = []
    d = os.path.join(ROOT, "content", "insights")
    if os.path.isdir(d):
        for path in glob.glob(os.path.join(d, "*.md")):
            meta, body = _frontmatter(io.open(path, encoding="utf-8").read())
            meta["slug"] = os.path.splitext(os.path.basename(path))[0]
            meta["body"] = body
            items.append(meta)
    items.sort(key=lambda m: m.get("date", ""), reverse=True)
    return items

INSIGHTS = load_insights()

def _insight_card(it):
    img = it.get("image", "")
    style = ' style="background-image:url(%s)"' % _esc(img) if img else ""
    href = it.get("link") or ("insight-%s.html" % it["slug"])
    return ('<a class="insight" href="%s"><span class="insight-img"%s></span>'
            '<span class="insight-body"><span class="insight-cat">%s</span>'
            '<span class="insight-t">%s</span><span class="insight-ex">%s</span>'
            '<span class="insight-date">%s</span></span></a>') % (
        _esc(href), style, _esc(it.get("category", "Insight")), _esc(it.get("title", "")),
        _esc(it.get("excerpt", "")), _fmt_date(it.get("date", "")))

def _insights_home():
    if not INSIGHTS: return ""
    cards = "\n".join(_insight_card(it) for it in INSIGHTS[:3])
    return ('''<!-- ============================== INSIGHTS ============================== -->
<section class="sec frame-sub" id="insights">
  <div class="wrap">
    <div class="sec-head center" data-reveal>
      <span class="eyebrow"><span class="dot"></span>Insights</span>
      <h2 class="h1">Tax &amp; business<br /><span class="serif">insights.</span></h2>
      <p class="lede">Plain-language updates on FBR, SECP and IPO&nbsp;Pakistan &mdash; deadlines, changes, and what they mean for you.</p>
    </div>
    <div class="insights-grid" data-reveal>%s</div>
    <div style="text-align:center;margin-top:32px"><a class="btn btn-primary btn-lg" href="insights.html">View all insights <svg class="arw" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg></a></div>
  </div>
</section>''') % cards

INSIGHTS_HOME = _insights_home()

def _insights_page_body():
    cards = "\n".join(_insight_card(it) for it in INSIGHTS) or '<p class="lede" style="text-align:center">New insights are on the way.</p>'
    return ('''<section class="page-hero">
  <div class="wrap">
    <span class="eyebrow" data-reveal><span class="dot"></span>Insights</span>
    <h1 data-reveal style="--d:80ms">Tax &amp; business insights.</h1>
    <p class="lede" data-reveal style="--d:160ms">Plain-language updates on FBR, SECP and IPO&nbsp;Pakistan &mdash; and what they mean for individuals and businesses in Pakistan.</p>
  </div>
</section>
<section class="sec" style="padding-top:clamp(18px,2.6vw,32px)">
  <div class="wrap"><div class="insights-grid">%s</div></div>
</section>''') % cards

def _article_body(it):
    img = it.get("image", "")
    hero_img = ('<div class="insight-img" style="max-width:740px;margin:24px auto 0;border-radius:var(--r-lg);background-image:url(%s)"></div>' % _esc(img)) if img else ""
    return ('''<section class="page-hero">
  <div class="wrap article-hero" style="text-align:center">
    <span class="eyebrow" data-reveal><span class="dot"></span>%s</span>
    <h1 data-reveal style="--d:80ms">%s</h1>
    <p class="lede" data-reveal style="--d:160ms">%s</p>
    <p class="insight-date" style="margin-top:2px">%s</p>
  </div>
</section>
%s
<section class="sec" style="padding-top:clamp(14px,2vw,26px)">
  <div class="wrap">
    <div class="article">%s</div>
    <p class="article-note">This is general information, not tax advice for your particular situation. Figures, rates and deadlines change &mdash; confirm your case with us before you act.</p>
    <div style="max-width:740px;margin-inline:auto"><a class="article-back" href="insights.html"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H6M12 5l-7 7 7 7"/></svg> All insights</a></div>
  </div>
</section>''') % (_esc(it.get("category", "Insight")), _esc(it.get("title", "")), _esc(it.get("excerpt", "")),
                 _fmt_date(it.get("date", "")), hero_img, _render_md(it.get("body", "")))

TAX_BODY = "\n\n".join([HERO_TAX, TWO_WAYS, SHOTS, TRUST, COMPARE, FEATURES, HOW, BEYOND, DASH, SECURITY, FAQ, CTA])
# these sections moved to their own pages, so their in-page anchors become cross-page links
TAX_BODY = TAX_BODY.replace('href="#services"', 'href="services.html"').replace('href="#calculators"', 'href="calculators.html"')

PAGES = {
    "index.html": page(
        "BIG1 &mdash; Tax Filing, Registration &amp; Corporate Services in Pakistan",
        "BIG1 helps individuals and businesses in Pakistan file income tax, register (NTN, sales tax, company, trademark) and stay compliant &mdash; a real team behind an intelligent platform.",
        "", "home",
        "\n\n".join([HOME_HERO, TRUST_HOME, PILLARS, TWO_WAYS, INSIGHTS_HOME, STORIES, FAQ_HOME, CTA_HOME])),
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

# ---- standalone content pages, now sharing the same head/nav/footer ----
_SVC_CSS, _SVC_BODY, _SVC_JS = standalone("services-src.html", "pgsvc", wrap_inner=True)
_ABT_CSS, _ABT_BODY, _ABT_JS = standalone("about-src.html", "pgabout", wrap_inner=False)
PAGES["demo.html"] = page(
    "See how FilePak works &mdash; a walkthrough of filing your return | BIG1",
    "A read-only walkthrough of FilePak with a demo profile: choose Self-Filing or Assisted Filing, answer guided steps or upload documents, review the IRIS-format summary, track it on your dashboard.",
    "demo.html", "tax", DEMO_BODY)
PAGES["services.html"] = page(
    "Services &mdash; NTN, Sales Tax, Trademark &amp; Company Registration in Pakistan | BIG1",
    "Assisted tax, IP and corporate services in Pakistan with the exact documents each one needs: NTN, sales tax (GST) and PST registration, IRIS updates, FBR notices, trademark, copyright, patent, design, SECP incorporation and compliance.",
    "services.html", "services", _SVC_BODY, extra_css=_SVC_CSS, extra_js=_SVC_JS)
PAGES["about.html"] = page(
    "About &amp; Contact &mdash; BIG1 / FilePak",
    "BIG1 is a Pakistani tax and corporate-services firm behind FilePak: income-tax filing, registrations, IP and SECP compliance. What we do, how we work, and how to reach us.",
    "about.html", "about", _ABT_BODY, extra_css=_ABT_CSS, extra_js=_ABT_JS)

# ---- insights: listing page + one page per article ----
PAGES["insights.html"] = page(
    "Insights &mdash; Tax, Registration &amp; Corporate Updates in Pakistan | BIG1",
    "Plain-language tax and business insights for Pakistan from BIG1 &mdash; FBR, SECP and IPO Pakistan updates, deadlines and guides for individuals and businesses.",
    "insights.html", "insights", _insights_page_body())
for _it in INSIGHTS:
    PAGES["insight-%s.html" % _it["slug"]] = page(
        _esc(_it.get("title", "Insight")) + " &mdash; BIG1 Insights",
        _esc(_it.get("excerpt", "")),
        "insight-%s.html" % _it["slug"], "insights", _article_body(_it))

def build():
    for name, html in PAGES.items():
        html = _apply_fees(html)          # bake the live rate card ({{FEE:kind}} + window.BIG1_FEES)
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
