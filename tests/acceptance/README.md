# Acceptance suite

`baseline/` is a byte-for-byte snapshot of the hand-written site at the commit in
`baseline/COMMIT`. It is the oracle for the migration: the generated site must
reproduce it. These files are **checked in and never regenerated** — changing one
means deliberately accepting that the site now differs from what shipped.

Because the migration targets *visually identical* output rather than
byte-identical, the byte-diff safety net is gone. These five gates replace it.

```bash
.venv/bin/python build.py            # writes _site/
.venv/bin/python -m pytest tests/acceptance -q
```

Gates that need `_site/` skip until `build.py` produces it. The self-check tests
always run — they prove the comparators work (a one-word edit is detected; a
whitespace or entity change is not) so that a red gate later means a real
regression rather than a broken comparator.

| Gate | What it checks | Where |
|---|---|---|
| 1 | ids, hrefs, srcs, toggle targets, citation keys, nav tabs | `inventory.py` |
| 2 | prose, after whitespace/entity/class normalization; `tidy` clean | `normalize_html.py` |
| 3 | rendered screenshots + live behavior | manual, see below |
| 4 | CV extracted text, page count, page images | `compare_pdf.py` |
| 5 | permanent invariants (no duplicate ids, local links resolve, no build output committed) | `test_gates.py` |

Every deliberate deviation from the baseline is registered in
`expected_diffs.py` with a reason. An unregistered difference fails.

## Baseline bug pins

Two tests assert that defects present *today* are still present in the baseline.
They are documentation, not aspiration — when a fix lands, the pin and an
`expected_diffs.py` entry change together, which makes the fix a visible event.

- **`listAbstract` is duplicated** (`index.html:340` and `:544`). Clicking the
  `list` chevron on the Software tab opens the Writing tab's "Statistical
  analysis of list experiments" abstract.
- **`blair2025ice` is cited but never defined.** The ICE paper's Cite button is a
  console error and an empty modal.

## Gate 3 — screenshots and live behavior

Needs a browser, so it runs manually at the end of each content PR and again
against production right after cutover.

```bash
.venv/bin/python -m http.server 8801 --directory tests/acceptance/baseline &
.venv/bin/python -m http.server 8802 --directory _site &
```

For each of the 7 tabs at 375 / 768 / 1280 px, and a second pass with every
`.collapse` force-expanded (abstracts are hidden by default and would otherwise
never be compared):

1. Navigate to `http://localhost:PORT/#!<tab>`.
2. Before capturing, settle the page:
   ```js
   document.querySelectorAll('.collapse').forEach(e => e.classList.add('show'));
   document.head.insertAdjacentHTML('beforeend',
     '<style>*{transition:none!important;animation:none!important}</style>');
   await document.fonts.ready;
   ```
3. Screenshot both, then `compare_png.py a.png b.png --threshold 0.001 --out diff.png`.

Behavioral assertions, which matter more than the pixels:

- Zero console errors on the built site. The **baseline** will show
  `Missing "blair2025ice"` — that non-empty baseline is itself the proof the bug
  is real.
- Zero 404s in the network log on either side.
- Each nav tab click sets `location.hash` to `#!<tab>`.
- A cold load of `#!expert` leaves that pane `active show`.
- Each of the 26 Cite links opens `#citationModal` with non-empty
  `#citation-output` — the end-to-end check on the BibTeX → JSON → citation-js path.
- Each abstract chevron toggles `fa-arrow-alt-circle-down` ↔ `-up`.
