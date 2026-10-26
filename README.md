# Reynardo's Website

Source for [reynardo-tjhin.github.io](https://reynardo-tjhin.github.io/) — notes on my projects and the problems I run into at work. Built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) and deployed to GitHub Pages.

![deploy](https://github.com/reynardo-tjhin/reynardo-tjhin.github.io/actions/workflows/ci.yml/badge.svg)

## Local development

Requires Python 3.13 (pinned in `.python-version`) and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                       # installs from pyproject.toml + uv.lock into .venv
uv run mkdocs serve           # http://127.0.0.1:8000
uv run mkdocs build --strict  # check links (see note below)
```

Always go through `uv run`: there is no global mkdocs and `.venv` has no pip. Note that `--strict` still exits 0 when links are bad — this install logs orphan pages and broken links as `INFO`, so read the build output instead of trusting the exit code.

## Layout

| Path                                   | What it is                                                    |
| -------------------------------------- | ------------------------------------------------------------- |
| `docs/`                                | all content; `docs/blog/posts/` holds the posts                |
| `mkdocs.yml`                           | config; **`nav:` is manual** — a new page is invisible until added |
| `overrides/partials/comments.html`     | giscus block, rendered only for pages with `comments: true`    |
| `docs/javascripts/`                    | KaTeX and MathJax render hooks                                 |
| `.github/workflows/ci.yml`             | deploy on push to `main`                                       |

## Writing a post

Add a file to `docs/blog/posts/` — the blog plugin picks it up, so do not add posts to
`nav:`.

```markdown
---
title: Post title
slug: post-slug
date: 2026-10-26
categories:
  - Web
description: One line, used in the post list and the social card
comments: true
---

Intro paragraph.

<!-- more -->
```

A post is served at `/blog/<year>/<month>/<day>/<slug>/`, so changing its `date` or `slug` silently breaks links from other posts.

## Deploy

Pushing to `main` runs `ci.yml`, which publishes with `mkdocs gh-deploy --force` to the `gh-pages` branch. That branch is generated — never edit it by hand.

## License

[MIT](LICENSE)
