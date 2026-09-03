# Refreshing CRAN download counts

The Software tab shows an approximate download total per R package. The numbers
live in `content/cran_downloads.yml` and are written by a script, never by hand.

```bash
python3 tools/update_cran_counts.py
python build.py
git add content/cran_downloads.yml && git commit
```

`--dry-run` prints the file instead of writing it.

The script fetches from `cranlogs.r-pkg.org`, falling back to METACRAN, and
refuses to write unless every package resolved — a partial write would drop a
package from the file and then fail the build on a missing key, which is a
confusing way to find out that one API call timed out.

## The numbers in the file today are estimates, not measurements

The counts currently shown (DeclareDesign ~85,000, estimatr ~220,000, fabricatr
~95,000, list ~180,000, rr ~65,000) were never fetched from an API. The previous
version of this document described them plainly as conservative estimates based
on "package age and maturity, typical R package adoption patterns, growth since
last update".

So the first real run will move them, possibly by a lot. **Land that run as its
own commit**, so the movement is visible and reviewable rather than buried in a
change about something else.

## What changed

This script used to rewrite `index.html` with a regex and leave a
`.backup.<timestamp>` copy of the page in the repo root.

`index.html` is generated from `content/` now, so editing it directly would be
discarded by the next build — and until then would desync the page from
`content/software.yml`. The backups are gone too: git already does that job,
and those copies would now be published as part of the site.

## The packages

| Package | Since | What it does |
|---|---|---|
| DeclareDesign | 2016 | Research design declaration and diagnosis |
| estimatr | 2018 | Fast estimators for design-based inference |
| fabricatr | 2018 | Data simulation before collection |
| list | 2010 | Item count technique and list experiments |
| rr | 2015 | Randomized response technique |
