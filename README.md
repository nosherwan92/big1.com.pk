# FilePak — official website

A single self-contained HTML page. No build step, no dependencies, no external requests
(no CDN, no web fonts, no analytics) — open `index.html` and it runs.

```
C:\bfiler\website\
├─ index.html          ← the site (this is the deliverable, ~190 KB)
├─ README.md           ← this file
├─ .claude\launch.json ← dev-server config for the preview pane
└─ _build\             ← the source parts index.html is assembled from
```

## Running it

Straight from disk: double-click `index.html`.

Or serve it (needed if you want to test as it will behave when hosted):

```bash
python -m http.server 5310 --directory C:/bfiler/website
```

Then open <http://localhost:5310/index.html>.

## Editing

`index.html` is the file to edit. `_build\*.html` are the ordered fragments it was
assembled from and are kept only so the page can be regenerated or split later:

```powershell
$d='C:\bfiler\website'
$parts = Get-ChildItem "$d\_build\*.html" | Sort-Object Name
$out = ($parts | ForEach-Object { [System.IO.File]::ReadAllText($_.FullName,[System.Text.Encoding]::UTF8) }) -join "`n"
[System.IO.File]::WriteAllText("$d\index.html",$out,(New-Object System.Text.UTF8Encoding($false)))
```

**Encoding:** always read/write UTF-8 explicitly as above. PowerShell 5.1's default
`Get-Content` decodes as ANSI and will corrupt every em-dash on the page.

## What's on the page

Nav · Hero · Trust band · Product showcase (4 tabs) · Why FilePak (bento) ·
**Tax calculators (5)** · Features (4 editorial rows) · How it works (6-step scroll journey) ·
AI Tax Intelligence · Designed for everyone (8 cards) · Dashboard showcase (4 views) · Security ·
Professional practice · Testimonials · Pricing (4 plans) · FAQ · Final CTA · Footer.
Plus a persistent WhatsApp button on every screen.

Every product image is live HTML/CSS, not a screenshot — so the mockups restyle
themselves in dark mode and stay sharp at any resolution.

### Design system

Tokens live in the `:root` block at the top of `index.html`.

| | |
|---|---|
| Primary | Deep emerald `#065F46` → `#0B7A5B`, professional blue `#1E40AF` → `#2563EB` |
| Accent | Soft cyan `#22D3EE`, gold `#E9B949`, graphite `#05070A` |
| Type | System display/sans stack, serif accents for pull phrases, tabular numerals for all money |
| Theme | Follows the OS by default; the header toggle overrides and persists to `localStorage` |

### Behaviour

Scroll-progress bar · sticky glass nav · IntersectionObserver reveals ·
count-up metrics · mouse-parallax hero with 3D tilt · pointer-tracking card glow ·
tabbed showcase with a sliding indicator and arrow-key support · dashboard view switcher ·
scroll-linked journey line · accordion FAQ · in-view animation gating so nothing
animates off-screen.

Accessibility: skip link, semantic landmarks, one `h1`, ARIA tabs/accordion,
visible focus rings, keyboard-operable everywhere, and a full
`prefers-reduced-motion` path. Verified: no duplicate IDs, no unlabelled controls,
no horizontal overflow at 390 / 834 / 1440 px.

## Tax calculators

Five live calculators in the `#calculators` section: **salary**, **rental income**,
**capital gain — property**, **capital gain — securities**, **business & freelance**.
All vanilla JS, all recompute as you type.

**Rates are tax year 2026 (Finance Act 2025)**, verified against
[PwC Worldwide Tax Summaries — Pakistan](https://taxsummaries.pwc.com/pakistan/individual/taxes-on-personal-income).
They are **not** the backend's `seeds.py` slabs, which are explicitly marked
`PLACEHOLDER — NOT REAL LAW`. The tables live at the top of the calculator script
(`_build/08-whatsapp-calc-script.html`):

| Table | Contents |
|---|---|
| `SAL_SLABS` | Salaried: 0 / 1% / 11% / 23% / 30% / 35%, plus 9% surcharge above Rs 10m |
| `NONSAL_SLABS` | Non-salaried & AOP: 0 / 15% / 20% / 30% / 40% / 45%, plus 10% surcharge above Rs 10m |
| `CGT_PROP_TAPER` | s.37 holding-period taper by property type, pre-1-Jul-2024 acquisitions |
| `CGT_SEC_TAPER` | s.37A securities taper |

Every result was hand-checked against the slab arithmetic before shipping, including the
surcharge, the taper, and the non-filer "slab rates but not less than 15%" floor.

**When the Finance Act changes, edit those four tables and nothing else.**

Deliberately not modelled, and flagged on-page: tax credits, allowances, exempt income,
minimum tax u/s 113, and the concessional final rate on IT/IT-enabled exports. The
securities calculator shows the 15% ceiling for pre-July-2024 acquisitions rather than
guessing the taper step, and says so.

## Brand

The nav and footer render a `BIG1` wordmark in the site's own typography as a fallback.
To use the real artwork, drop the logo file at:

```
C:\bfiler\website\assets\big1-logo.png
```

It appears automatically — the markup already references it, and the text fallback hides
itself when the image loads (and reappears if the file is missing, so nothing ever breaks).
An SVG is better than a PNG if you have one; change the `src` in
`_build/02-nav-hero.html` and `_build/07-testimonials-pricing-faq-cta-footer.html`.

**Open question:** the site is currently branded BIG1 (company) in the logo with FilePak
(product) in all the copy. If FilePak is being retired in favour of BIG1, the body copy
needs a rename pass.

## WhatsApp

`+92 339 9999611` → `https://wa.me/923399999611`, in three places: the floating button
(collapses to icon-only under 560px), the footer social row, and a visible number under the
footer blurb. To change it, search the file for `923399999611`.

## Before this goes live — needs your sign-off

These are placeholders written to be credible, not verified facts:

1. **Pricing** — Rs 2,900 / Rs 5,900 / Rs 1,200 per return / Enterprise custom.
   Positioned deliberately below Befiler's Rs 3,900 / 5,500 / 14,500.
2. **Trust-band statistics** — 18-minute median, 61 validation rules, 7 years of
   retained rulesets. Every one of these is a public claim; make them true or change them.
3. **Testimonials** — clearly labelled as illustrative on the page. Replace after the
   first filing season.
4. **Legal pages** — Privacy, Terms, Careers, Contact, Documentation and the salary
   calculator are `href="#"` stubs.
5. **Regulatory copy** — the e-intermediary and "we never store your IRIS password"
   claims are load-bearing. They must match what the platform actually does at launch.
6. **Domain and contact** — social links are stubs; `app.filepak.pk` appears in the
   mockup chrome.

## Note on the stack

The brief listed React / Next.js / Tailwind / Framer Motion. This is delivered as
hand-written HTML + CSS + vanilla JS instead, per the "(in HTML)" instruction — which
also means zero dependencies, no hydration cost and nothing to keep patched. The
markup is already organised into component-shaped blocks, so porting each section to a
React component is mechanical if you want the Next.js version for a marketing CMS later.
