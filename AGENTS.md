# Working in this repository

**The website and the CV are generated. Edit `content/*.yml`.**

There is no `index.html` and no `GraemeBlair-CV.tex` in this repository. They are
built from YAML by `build.py`, along with the CV PDF, and published straight to
GitHub Pages from a workflow run. If you create either file, CI will fail — and
if you somehow got one into the tree, the next build would discard your edit
without telling anyone.

That is the whole point of the arrangement. The site and the CV used to state
the same facts separately, and they drifted: paper titles diverged, a course had
two different numbers, a coauthor appeared in one and not the other, a Cite
button pointed at a citation that did not exist.

## Where things live

| To change | Edit |
|---|---|
| A paper, book, or abstract | `content/publications.yml` |
| Bibliographic detail (volume, pages, publisher) | `content/citations.bib` |
| A court case or declaration | `content/expert.yml` |
| An R package | `content/software.yml` |
| A course | `content/teaching.yml` |
| A student or advisee | `content/people.yml` |
| A dataset | `content/datasets.yml` |
| Grants, talks, service, awards — CV only | `content/cv.yml` |
| Page chrome, nav, CDN pins | `content/site.yml` |
| CRAN download counts | run `tools/update_cran_counts.py`; never by hand |
| Layout and markup | `templates/` |

One-off prose that appears in exactly one place and never in the CV — the bio
modal, the "For students" tab, the DeclareDesign card — lives in the template,
not in YAML. Rule of thumb: repeated, structured, or shared with the CV → YAML;
one-off site-only prose → template.

## Build and check

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python build.py
.venv/bin/python -m pytest tests/acceptance -q
```

`build.py` writes `_site/`, which is gitignored.

## The acceptance gates

`tests/acceptance/baseline/` is a frozen snapshot of the hand-written site as it
shipped. The gates compare what you built against it: structure (ids, links,
toggle targets, citation keys), prose, the CV's source and typeset PDF, and a set
of standing invariants.

**A gate failing means your change altered something. That is usually the bug,
not the gate.** When a change is deliberate, add an entry to
`tests/acceptance/expected_diffs.py` with a reason a reader can evaluate — a
rename needs both its old and new value registered, so neither side of the diff
passes unexplained. Do not widen a key until a failure goes away; a key broad
enough to whitelist a whole page proves nothing.

Do not edit `tests/acceptance/baseline/`. It is the oracle.

## Two things that will bite

**URLs must not go through the LaTeX escaper.** Use `| tex_url`. hyperref reads
`\href` arguments almost verbatim, so escaping the `_` in a courtlistener URL
puts a literal backslash in the link target. The PDF still compiles; the link
just quietly goes nowhere.

**The LaTeX templates use `<<< >>>` and `<<% %>>`, not `{{ }}`.** Parenthesis
delimiters were tried and are a trap: CV prose is full of literal parentheses,
so `((( x )))` beside a "(graduate)" annotation parses as `(((` plus the
expression `( x )`, and the parentheses vanish silently from the PDF.
