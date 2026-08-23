# Insights content

Each article is one Markdown file in `content/insights/`. Add a file, push to
`main`, and the site rebuilds itself (GitHub Action `.github/workflows/build.yml`)
— it appears on the homepage (latest 3) and on `insights.html`, with its own page.

## File name

Use the date and a short slug, e.g. `2026-09-01-budget-2026-highlights.md`.
The part after the date becomes the page URL: `insight-<slug>.html`.

## Format

```markdown
---
title: Your headline here
category: Income Tax        # or Registrations / Intellectual Property / Corporate
date: 2026-09-01            # YYYY-MM-DD (newest sorts first)
excerpt: One line shown on the card and under the title.
# image: assets/insights/your-image.jpg   # optional; omit for a gradient tile
# link: https://external-url               # optional; if set, the card links out
                                            # instead of generating an article page
---

Write the article body in Markdown below the front-matter.

## A heading

A paragraph. You can use **bold**, *italic*, and [links](services.html).

- Bullet points
- Work too
```

## Notes

- No special characters needed — the build converts them automatically.
- Keep tax/legal claims general; a disclaimer is added to every article.
- To add a photo: drop it in `assets/insights/` and set `image:` above.
