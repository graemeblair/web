# Rolling back the Pages cutover

The site is published by `.github/workflows/build-deploy.yml` from the `main`
branch. Before the cutover it was served directly from the `gh-pages` branch,
which still holds the exact bytes that shipped that day — including the last
hand-committed CV PDF. Nothing was deleted.

To go back, ~60 seconds:

```bash
gh api -X PUT repos/graemeblair/web/pages \
  -f build_type=legacy -f 'source[branch]=gh-pages' -f 'source[path]=/'
gh api -X PATCH repos/graemeblair/web -f default_branch=gh-pages
gh api -X DELETE repos/graemeblair/web/branches/gh-pages/protection
```

`pages-config-before-cutover.json` is the API response captured immediately
before the change, in case any field needs restoring by hand.

## What changed at cutover

| | Before | After |
|---|---|---|
| Pages source | `gh-pages` branch | GitHub Actions artifact |
| Default branch | `gh-pages` | `main` |
| `gh-pages` | live | locked, retained |
| `index.html`, `GraemeBlair-CV.tex`, `.pdf` | committed | generated per build, in no branch |

The `github-pages` environment had custom branch policies enabled with **no
policies listed**, so no branch could deploy. `main` was added; that is why the
first deploy failed instantly with an empty step list.
