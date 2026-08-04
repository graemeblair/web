"""Pre-registered, deliberate deviations from the frozen baseline.

The acceptance suite compares the built site against `baseline/`, which is a
byte-for-byte snapshot of the hand-written site at the commit recorded in
`baseline/COMMIT`. Any difference fails -- unless it is listed here.

The rule: a deviation gets an entry BEFORE the change lands, with a reason a
reader can evaluate. Nothing is fixed silently. Several of these are visible
behavior changes, not cosmetic cleanups, and the owner has to agree to each one.

Each entry is (kind, key, reason):
  kind  "id" | "citation" | "href" | "src" | "toggle"  -- Gate 1, exact match
        "text"                                         -- Gate 2 and the CV
                                                          source, substring match
  key   the value that differs (a distinctive fragment, for "text")
"""

from __future__ import annotations

EXPECTED_DIFFS: list[tuple[str, str, str]] = [
    (
        "id",
        "listPkgAbstract",
        "VISIBLE BEHAVIOR CHANGE. `listAbstract` was used twice in the baseline "
        "(index.html:340 for the list-experiments paper, :544 for the `list` R "
        "package), so the Software tab's chevron expanded the Writing tab's "
        "abstract instead of its own. The R package's collapse is renamed; the "
        "paper keeps `listAbstract`. Clicking that chevron now does something "
        "different -- and correct.",
    ),
    # ---- teaching, moved into content/teaching.yml -------------------------
    (
        "text",
        "170A",
        "One course number now feeds both targets. UCLA renumbered PS 179 to "
        "170A; the site had the new number, the CV still had the old one, and "
        "the syllabus PDF (renamed to UCLA_PS170A_Syllabus.pdf) had the old one "
        "while being linked from the line showing the new one. Owner confirmed "
        "170A is current.",
    ),
    (
        "text",
        "Research Design for Social Science",
        "The site abbreviated PS 292B to 'Research Design'; the CV had the full "
        "title. One title now feeds both. Owner confirmed.",
    ),
    (
        "text",
        "240A-B",
        "The site wrote PS 240a/b, the CV 240A-B. One number now feeds both. "
        "Owner confirmed.",
    ),
    (
        "text",
        "Statistical Programming for Social Science",
        "PS 200X was the only course on the site in sentence case, and carried "
        "a stray trailing period. Titles are stored in sentence case and "
        "title-cased for the site, so it now matches its neighbours.",
    ),
    (
        "text",
        "179",
        "The removal side of the PS 179 -> 170A renumbering above. A rename "
        "registers both the old and the new value, so neither side of the diff "
        "passes unexplained.",
    ),
    (
        "href",
        "teaching/UCLA_PS170A_Syllabus.pdf",
        "Syllabus renamed alongside the course renumbering so the filename and "
        "the displayed number agree. A Gate 5 lint enforces that from now on.",
    ),
    (
        "href",
        "teaching/UCLA_PS179_Syllabus.pdf",
        "Replaced by UCLA_PS170A_Syllabus.pdf -- see above.",
    ),
    (
        "text",
        "UCLA_PS170A_Syllabus.pdf",
        "Syllabus renamed alongside the course renumbering.",
    ),
    # The removal side of each teaching rename. Keys are deliberately specific
    # so each retires exactly one old string and cannot whitelist a future edit.
    (
        "text",
        "292B: Research Design (Ph.D.",
        "Removal side of the PS 292B title change.",
    ),
    ("text", "240a/b", "Removal side of the PS 240A-B renumbering."),
    (
        "text",
        "Statistical programming for social science.",
        "Removal side of the PS 200X title-casing.",
    ),
    # LaTeX comments in the teaching block held historical notes. They moved to
    # comments in content/teaching.yml, next to the course they describe,
    # instead of living in generated output. Listed individually rather than as
    # a blanket "%" key, which would whitelist every future comment change.
    ("text", "%. Winter 2017; Winter 2018", "Historical note, moved to teaching.yml."),
    ("text", "% Fall 2016 (as PS 209); Winter 2018", "Historical note, moved to teaching.yml."),
    ("text", "%Fall 2016 -- Winter 2017", "Historical note, moved to teaching.yml."),
    ("text", "% Politics 572 (Preceptor).", "Historical note, moved to teaching.yml."),
    # ---- software, moved into content/software.yml -------------------------
    #
    # Three changes to the CV's software list, all of them normalizations the
    # site already had right. The site's own rendering is unchanged.
    (
        "text",
        "}, with Jasper Cooper",
        "The \\href now covers the package name and description only; the "
        "coauthor list sits outside it. The hand-written CV did this both ways "
        "-- DeclareDesign, estimatr and fabricatr wrapped coauthors inside the "
        "link, rr and list left them out.",
    ),
    ("text", "research designs, with Jasper Cooper", "Removal side of the above (DeclareDesign)."),
    ("text", "social scientists, with Jasper Cooper", "Removal side of the above (estimatr)."),
    ("text", "collected, with Jasper Cooper", "Removal side of the above (fabricatr)."),
    (
        "text",
        "Aaron Rudkin, and Neal Fultz",
        "fabricatr's author list disagreed: the site credited Neal Fultz, the "
        "CV did not. One list now feeds both, and it includes him.",
    ),
    (
        "text",
        "https://rr.sensitivequestions.org",
        "The CV linked http:// for both sensitivequestions.org packages while "
        "the site already used https://.",
    ),
    (
        "text",
        "https://list.sensitivequestions.org",
        "As above -- http:// to https://.",
    ),
    ("text", "http://rr.sensitivequestions.org", "Removal side of the https upgrade."),
    ("text", "http://list.sensitivequestions.org", "Removal side of the https upgrade."),
    (
        "text",
        "R statistical package for analysis of survey",
        "The CV's software list is now in the site's order -- DeclareDesign, "
        "estimatr, fabricatr, then list, rr, which is alphabetical within each "
        "group. The CV had DeclareDesign, fabricatr, estimatr, rr, list, with "
        "no evident rule. One list feeds both targets, so it needs one order. "
        "This moves the `list` entry across a page break, which is what the "
        "page-image comparison flagged.",
    ),
    (
        "text",
        "R statistical package for analysis of randomized response",
        "Removal/addition sides of the reordering above (the `rr` entry).",
    ),
    # pdftotext wraps long entries, so a change or a move shows up on the
    # continuation lines too. These are the tails of entries already registered
    # above -- listed rather than papered over with a broad key.
    (
        "text",
        "Macartan Humphreys, and Aaron Rudkin",
        "Continuation line of the old fabricatr entry, before Neal Fultz.",
    ),
    (
        "text",
        "answers to sensitive questions, with Yang-Yang Zhou",
        "Continuation line of the `rr` entry, moved by the reordering.",
    ),
    (
        "text",
        "questions, with Kosuke Imai",
        "Continuation line of the `list` entry, moved by the reordering.",
    ),
    (
        "text",
        "District Court for the District of Maryland",
        "Continuation line of the D.N.N. stray-period fix. Only that matter is "
        "in Maryland, so this cannot cover anything else.",
    ),
    (
        "text",
        "District Court for the Northern District of California",
        "Continuation line of the Stanford Daily change (parentheses and David "
        "Hausman). Pablo Sequen is also in this district but its line is "
        "unchanged, so it never reaches the diff.",
    ),
    # ---- expert work, moved into content/expert.yml -------------------------
    (
        "text",
        "Expert declaration for amicus brief,",
        "Stanford Daily was the one matter of twelve written without the "
        "parentheses its siblings all had. Roles are a controlled vocabulary "
        "now, so each phrasing is written once and every matter with the same "
        "role reads identically.",
    ),
    (
        "text",
        "gov.uscourts.cand.454120",
        "Stanford Daily's CV line gains its amicus-brief link, and gains David "
        "Hausman -- the site credited him, the CV did not.",
    ),
    (
        "text",
        "D.N.N. et al. v. Liggins et al.}, December 2025",
        "This was the only expert-work line ending in a stray period before its "
        "line break.",
    ),
    # The CV linked three of fourteen expert-work entries with no evident rule.
    # Every matter with a public amicus brief now links it, which is the rule
    # the site already followed. These keys match both sides of the diff -- the
    # unlinked line and the same line wrapped in \href -- because that pairing
    # IS the registered change.
    (
        "text",
        "Mahdawi v. Trump et al.}, August 2025",
        "CV line gains its amicus-brief link (2d Cir.).",
    ),
    (
        "text",
        "Mahdawi v. Trump et al.}, April 2025",
        "CV line gains its amicus-brief link (D. Vt.).",
    ),
    (
        "text",
        "Chung v. Trump}, March 2025",
        "CV line gains its amicus-brief link (S.D.N.Y.).",
    ),
    # These keys exist for the PDF text comparison, which sees typeset prose
    # rather than LaTeX source -- so keys containing braces or macros never
    # match there. Each matches both sides of its change.
    (
        "text",
        "Stanford Daily Publishing Corporation",
        "In the typeset CV this line gains its parentheses and David Hausman "
        "-- see the two entries above. Registered again in a brace-free form "
        "because the PDF comparison reads text, not LaTeX.",
    ),
    (
        "text",
        "D.N.N. et al. v. Liggins",
        "Brace-free form of the stray-period fix above, for the PDF comparison.",
    ),
    # ---- publications, moved into content/publications.yml -----------------
    #
    # Titles are stored once in sentence case and the CV's Title Case derived,
    # which resolves the six titles the two sources disagreed on. In every one
    # the site and content/citations.bib agreed and the CV was stale, so the CV
    # gains the current title. Those changes surface in the CV comparison only.
    (
        "text",
        "Ellen Chapin",
        "The policing book's contributor list differed. The CV credited Ellen "
        "Chapin, Ahsan Farooqui, Zulfiqar Hameed, Andrew Miller and Fatiq "
        "Nadeem; the site did not, and credited Lily Tsai instead -- it was "
        "reusing the Science article's author list for the book. Owner "
        "confirmed the CV's 25-name list is the book's.",
    ),
    (
        "text",
        "Ben Kachero, Dorothy Kronick, Benjamin Morse, Robert Muggah, Matthew Nanes",
        "Removal side of the book contributor change above.",
    ),
    (
        "text",
        "Elizabeth R. Nugent",
        "The PNAS paper's author list on the site omitted Rebecca Wolfe "
        "entirely and abbreviated Elizabeth R. Nugent. One list feeds both "
        "targets now, and it is the CV's -- a journal's author list is a matter "
        "of record.",
    ),
    (
        "text",
        "Rebecca Wolfe, Mohammed Bukar",
        "Rebecca Wolfe restored to the PNAS author list -- see above.",
    ),
    (
        "text",
        "Mohammed Bukar, Benjamin Crisman",
        "Removal side of the PNAS author-list change.",
    ),
    (
        "text",
        "C. Christine Fair",
        "The site dropped the initial from C. Christine Fair's name. One list "
        "feeds both targets.",
    ),
    (
        "text",
        "With David Hausman and Phil Neff",
        "The ICE paper put its coauthors before the venue while every other "
        "paper puts them after. Uniform now.",
    ),
    (
        "text",
        "Ⓡ",
        "The Global South field-experiments paper has a randomized author "
        "order, and the two sources disagreed on both the order and several "
        "names (the site had 'Nicholas Owlsley', 'Alex Dyzenhaus', 'Ken "
        "Opalo'; the CV has 'Nicholas Owsley', 'Alex P. Dyzenhaus', 'Ken "
        "Ochieng' Opalo'). Randomized order is part of the published record, so "
        "the CV's list and order are used.",
    ),
    (
        "text",
        "Biz Herman",
        "Both sides of the randomized-order author list above.",
    ),
    (
        "text",
        "<p/>",
        "The Expert work tab had a bare <p></p> after two of its five case "
        "lists and not the other three, so section spacing was uneven. The "
        "sections render uniformly now. (normalize_html.py renders an empty "
        "element as `<p/>`, so this key cannot whitelist a paragraph that has "
        "content.)",
    ),
]


def is_expected(kind: str, key: str) -> bool:
    return any(k == kind and v == key for k, v, _ in EXPECTED_DIFFS)


def unexplained_diff_lines(diff: str) -> list[str]:
    """Diff lines not covered by a registered "text" entry.

    Substring rather than exact match, because a text change is registered by
    the distinctive fragment that changed, not by the whole surrounding line --
    a diff line carries indentation and neighbouring words that are noise.
    """
    keys = [v for k, v, _ in EXPECTED_DIFFS if k == "text"]
    unexplained = []
    for line in diff.splitlines():
        if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue
        body = line[1:]
        if not body.strip():
            continue
        if not any(key in body for key in keys):
            unexplained.append(line)
    return unexplained


def reason(kind: str, key: str) -> str | None:
    for k, v, why in EXPECTED_DIFFS:
        if k == kind and v == key:
            return why
    return None


def describe(kind: str, key: str) -> str:
    why = reason(kind, key)
    return f"{kind} {key!r}: {why}" if why else f"{kind} {key!r}: UNREGISTERED"
