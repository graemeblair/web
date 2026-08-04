"""Generator for graemeblair.com and the CV.

`content/*.yml` is the single source of truth. `build.py` renders it, through
the templates in `templates/`, into `_site/index.html`, `_site/GraemeBlair-CV.tex`,
and the citation data -- then copies `static/` over the top.

Nothing under `_site/` is ever committed. See AGENTS.md.
"""
