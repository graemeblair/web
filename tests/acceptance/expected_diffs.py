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

KNOWN BLIND SPOT, measured, not theoretical. A "text" key matches as a
substring of a whole diff line, so it excuses that line entirely -- not just the
fragment it names. Publication entries are single lines of 300+ characters, so
"Ellen Chapin" (registered for a contributor-list change) also covers a wrong
publisher or a typo'd page range in the same entry. Checked: with the current
registrations, changing a journal issue from 377(6602) to 377(6603) passes the
suite; dropping a coauthor from a line with no registered key still fails.

The fix is to require the registered keys to account for the whole difference --
mask every key occurrence on both sides and demand the remainders match. That
was tried here and works, but the 60 existing registrations were written for
substring matching and do not tile their changes, so it currently reports about
thirty already-agreed changes as unexplained. Rewriting them to tile is real
work and belongs in its own change, not smuggled into a content PR.
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
    (
        "text",
        "UCLA_PS179_Syllabus.pdf",
        "Removal side of the syllabus rename. Registered as text as well as "
        "href because Gate 2 reads the rendered link and only consults text "
        "keys, while Gate 1 compares the href set.",
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
        "Luke Sonnet, and Neal Fultz",
        "estimatr had the same omission, in both the site and the CV: only the "
        "deleted content/citations.bib credited Neal Fultz, and folding that "
        "file into content/software.yml is what surfaced it. Owner confirmed he "
        "should be listed. NOTE: this line was already excused by the '}, with "
        "Jasper Cooper' key above, so the suite did not fail on it -- the "
        "blind spot described at the top of this file. Registered anyway, "
        "because the reason on that key is about \\href nesting and would not "
        "tell a reader an author had been added.",
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
        "Macartan Humphreys, and Luke Sonnet",
        "Continuation line of the old estimatr entry, before Neal Fultz -- the "
        "same wrap-tail as fabricatr's above. Visible only in the typeset "
        "comparison, which is why CI's PDF gate caught it while the local "
        "suite (which skips the PDF gates without XeLaTeX) stayed green.",
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
        "Advances in Experimental Political Science",
        "The site called the volume the site's Blair-McClendon chapter sits in "
        "the 'Handbook of Experimental Political Science'. The CV and "
        "content/citations.bib both name it 'Advances in Experimental Political "
        "Science', which is the book Druckman and Green edited. The site gains "
        "the correct title. The CV also regains the chapter's editors, year and "
        "publisher, which a duplicate `kind:` key in the YAML had silently "
        "dropped -- Gate 5 lints for that now.",
    ),
    (
        "text",
        "Handbook of Experimental Political Science",
        "Removal side of the volume-title correction above.",
    ),
    # ---- titles, six of which the two sources disagreed on ------------------
    (
        "text",
        "Poverty and Support for Militant Politics: Evidence from Pakistan",
        "The CV said 'Survey Evidence from Pakistan'; the AJPS title is "
        "'Evidence from Pakistan'.",
    ),
    (
        "text",
        "Poverty and Support for Militant Politics: Survey Evidence from Pakistan",
        "Removal side of the Pakistan title correction.",
    ),
    (
        "text",
        "Immigration and Customs Enforcement Individual-Level Administrative Data",
        "The CV omitted 'administrative' from the ICE data paper's title; the "
        "site and citations.bib both have it.",
    ),
    (
        "text",
        "Immigration and Customs Enforcement individual-level data",
        "Removal side of the ICE-data title correction.",
    ),
    (
        "text",
        "Accessing Justice for Survivors of Violence against Women",
        "The CV said 'Improving Access to Justice for Survivors of Violence "
        "Against Women'; the site and citations.bib say 'Accessing justice ...', "
        "which is what Science published. The CV was stale.",
    ),
    (
        "text",
        "Improving Access to Justice for Survivors of Violence Against Women",
        "Removal side of the help-desks title correction.",
    ),
    (
        "text",
        "Evidence Needed for Ethical Social Science",
        "The CV said 'Evidence required ...'; the published title is 'Evidence "
        "needed ...'.",
    ),
    (
        "text",
        "Evidence required for ethical social science",
        "Removal side of the ethics-piece title correction.",
    ),
    (
        "text",
        "Design and Analysis of the Randomized Response Technique",
        "The CV said 'Statistical Analysis of ...'; JASA published 'Design and "
        "Analysis of ...'.",
    ),
    (
        "text",
        "Statistical Analysis of the Randomized Response Technique",
        "Removal side of the randomized-response title correction.",
    ),
    (
        "text",
        "Community Policing Does Not Build Citizen Trust in Police or Reduce Crime",
        "The CV carried the working title 'Does Community Policing Build Trust "
        "in Police and Reduce Crime? Evidence from Six Coordinated Field "
        "Experiments in the Global South'. Science published the finding as a "
        "statement, not a question.",
    ),
    (
        "text",
        "Does Community Policing Build Trust in Police and Reduce Crime?",
        "Removal side of the community-policing title correction.",
    ),
    (
        "text",
        "Where and Why Does Oil Cause Armed Conflict in Africa?",
        "The CV's title omitted 'in Africa', and the paper has moved from "
        "forthcoming to accepted at the Journal of Politics.",
    ),
    (
        "text",
        "Where and why does oil cause armed conflict?",
        "Removal side of the point-of-attack title change.",
    ),
    ("text", "Accepted, \\textit{Journal of Politics}", "See above -- forthcoming to accepted."),
    (
        "text",
        "Forthcoming, \\textit{Journal of Politics}",
        "Removal side of the forthcoming-to-accepted change.",
    ),
    (
        "text",
        "2022. ``How Does Armed Conflict Shape Investment?",
        "The mining paper was listed as 2020 on the CV and 2022 on the site. It "
        "appeared in the Journal of Politics in 2022; 2020 was the working-paper "
        "year. One year now feeds both targets.",
    ),
    (
        "text",
        "2020. ``How does armed conflict shape investment?",
        "Removal side of the mining-paper year correction.",
    ),
    (
        "text",
        "2022. “How Does Armed Conflict Shape Investment?",
        "Quote-mark-free form of the mining-paper year correction, for the PDF "
        "comparison: the source writes the opening quote as ``, the typeset text "
        "as a curly quote, so a key with one never matches the other.",
    ),
    (
        "text",
        "2020. “How does armed conflict shape investment?",
        "Removal side of the above, in typeset form.",
    ),
    # Codebooks and reports were the only publication titles the CV left in
    # sentence case. Titles are stored in sentence case and Title Cased for the
    # CV, so these now match their neighbours. Registered individually rather
    # than as one "Codebook" key, which would whitelist any future codebook.
    (
        "text",
        "ICE Detention Facilities Codebook",
        "Title Cased with every other CV title. Removal side is the sentence-case form.",
    ),
    ("text", "ICE detention facilities codebook", "Removal side of the above."),
    (
        "text",
        "ICE Field Offices and Areas of Responsibility Codebook",
        "Title Cased with every other CV title.",
    ),
    ("text", "ICE field offices and areas of responsibility codebook", "Removal side of the above."),
    ("text", "EOIR Processed Case Data Codebook", "Title Cased with every other CV title."),
    ("text", "EOIR processed case data codebook", "Removal side of the above."),
    ("text", "EOIR Case Dataset Codebook", "Title Cased with every other CV title."),
    ("text", "EOIR case dataset codebook", "Removal side of the above."),
    (
        "text",
        "One Year of Immigration Enforcement under the Second Trump Administration",
        "Title Cased with every other CV title.",
    ),
    (
        "text",
        "One year of immigration enforcement under the second Trump administration",
        "Removal side of the above.",
    ),
    (
        "text",
        "Immigration Enforcement in the First Nine Months of the Second Trump Administration",
        "Title Cased with every other CV title.",
    ),
    (
        "text",
        "Immigration enforcement in the first nine months of the second Trump administration",
        "Removal side of the above.",
    ),
    # ---- paper links, which the two targets pointed at differently ----------
    #
    # The CV's link for an entry is now the same `links:` row the site renders,
    # so the two cannot point at different copies of one paper. They did on
    # three, and five more were linked over http.
    (
        "text",
        "graemeblair.com/papers/mkiv.pdf",
        "The CV linked the community-policing paper to its Science landing page, "
        "the site to the PDF. The site's link wins: it reaches the paper "
        "without a paywall.",
    ),
    (
        "text",
        "science.org/doi/10.1126/science.abd3446",
        "Removal side of the community-policing link change.",
    ),
    (
        "text",
        "science.org/doi/pdf/10.1126/sciadv.aau5175",
        "The CV linked a local copy of the Nollywood paper, the site the "
        "publisher's open-access PDF. Science Advances is open access, so the "
        "publisher's copy is the better target.",
    ),
    (
        "text",
        "graemeblair.com/papers/nollywood.pdf",
        "Removal side of the Nollywood link change.",
    ),
    (
        "text",
        "https://declaredesign.org/paper.pdf",
        "The CV linked declaredesign.org/declare.pdf and the site "
        "declaredesign.org/paper.pdf for the same paper. The site's is the live "
        "one.",
    ),
    (
        "text",
        "https://declaredesign.org/declare.pdf",
        "Removal side of the DeclareDesign link change.",
    ),
    (
        "text",
        "https://graemeblair.com/papers/randresp.pdf",
        "Five CV paper links were http://. Upgraded to https, matching the site "
        "-- the same change already made to the two sensitivequestions.org "
        "software links.",
    ),
    (
        "text",
        "https://graemeblair.com/papers/listendorse.pdf",
        "As above -- http:// to https://.",
    ),
    (
        "text",
        "https://graemeblair.com/papers/pakistan.pdf",
        "As above -- http:// to https://.",
    ),
    ("text", "http://graemeblair.com/papers/randresp.pdf", "Removal side of the https upgrade."),
    ("text", "http://graemeblair.com/papers/listendorse.pdf", "Removal side of the https upgrade."),
    ("text", "http://graemeblair.com/papers/pakistan.pdf", "Removal side of the https upgrade."),
    (
        "text",
        "{\\it Social Psychological and Personality Science} 8(4): 424-433",
        "The audio-check entry was the one article whose volume followed a "
        "period after the journal name. Every other entry runs the two together.",
    ),
    (
        "text",
        "{\\it Social Psychological and Personality Science}. 8(4): 424-433",
        "Removal side of the stray-period fix above.",
    ),
    (
        "text",
        "Personality Science 8(4): 424-433",
        "Brace-free form of the audio-check stray-period fix, for the PDF "
        "comparison, which reads typeset text rather than LaTeX.",
    ),
    (
        "text",
        "Personality Science. 8(4): 424-433",
        "Removal side of the above, brace-free.",
    ),
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
        "text-exact",
        "#text .",
        "Removal side of the ICE byline move: the text node after the venue was "
        "a bare period, and now carries the coauthors. Registered as an exact "
        "match because '.' as a substring would whitelist the whole document.",
    ),
    (
        "text",
        "Forthcoming,",
        "Addition side of the ICE byline move -- its coauthors now follow the "
        "venue, as every other paper's do.",
    ),
    (
        "text",
        "With Rebecca Littman, Elizabeth Nugent",
        "Removal side of the PNAS author-list correction.",
    ),
    (
        "text",
        "With Christine Fair",
        "Removal side of the C. Christine Fair correction.",
    ),
    (
        "text",
        "With Nicholas Owsley.",
        "Removal side: the extractor had collapsed the field-experiments "
        "paper's Ⓡ-separated names into a single string, leaving one coauthor.",
    ),
    # Bylines are rendered by one filter now, so they punctuate consistently.
    # The hand-written page did not: some lists had a serial "and" before the
    # last name and a closing period, some had neither.
    (
        "text",
        "and Macartan Humphreys.",
        "Byline punctuation normalized -- the site omitted the serial 'and' and "
        "the closing period here.",
    ),
    (
        "text",
        "Alexander Coppock, Macartan Humphreys",
        "Removal side of the byline punctuation normalization.",
    ),
    (
        "text",
        "With Kosuke Imai and Yang-Yang Zhou.",
        "Byline punctuation normalized -- see above.",
    ),
    (
        "text",
        "With Kosuke Imai, Yang-Yang Zhou.",
        "Removal side of the byline punctuation normalization.",
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
    # ---- expert work, reorganized by case (site only) ------------------------
    #
    # VISIBLE PRESENTATION CHANGE, owner requested. The Expert work tab used to
    # list every filing as its own bullet, so a case that moved through the
    # courts appeared two or three times -- Mahdawi twice, Khalil twice under
    # two captions. Each case now appears once inside its legal-theory section,
    # with its postures traced beneath it: a muted court-and-date line, then the
    # role and document links. The CV is untouched -- its flat reverse-
    # chronological list renders byte-identically from the same data.
    #
    # Every entry line changed shape, so each old text node and its replacement
    # is registered below, almost all as text-exact so no key can excuse more
    # than the node it names. Three matters' lines (Pablo Sequen, D.N.N.,
    # Stanford Daily) are already excused by the district-court continuation
    # keys registered further up.
    #
    # The old "role, case, date, court (docs)" nodes, one per matter:
    ("text-exact", "#text , June 2026, U.S. District Court for the Southern District of Indiana (", "Sarsour's old one-line entry."),
    ("text-exact", "#text , March 2026, U.S. District Court for the Southern District of Ohio", "Peralta's old one-line entry."),
    ("text-exact", "#text , October 2025, U.S. Court of Appeals for the Fourth Circuit (with David Hausman) (", "Khan Suri's old one-line entry."),
    ("text-exact", "#text , September 2025, U.S. Court of Appeals for the Third Circuit (with David Hausman) (", "The old Khalil v. Trump entry, now the appellate stage of the Khalil case."),
    ("text-exact", "#text , August 2025, U.S. Court of Appeals for the Second Circuit (with David Hausman) (", "The old second Mahdawi entry, now the appellate stage of the Mahdawi case."),
    ("text-exact", "#text , August 2025, U.S. District Court for the Central District of California", "Vasquez Perdomo's old one-line entry."),
    ("text-exact", "#text , July 2025, U.S. Court of Appeals for the Ninth Circuit", "Calderon's old one-line entry."),
    ("text-exact", "#text , April 2025, U.S. District Court for the District of Vermont (with David Hausman) (", "The old first Mahdawi entry, now the district stage of the Mahdawi case."),
    ("text-exact", "#text , March 2025, U.S. District Court for the Southern District of New York (with David Hausman) (", "Chung's old one-line entry."),
    ("text-exact", "#text , March 2025, U.S. District Court for the District of New Jersey (with David Hausman) (", "The old Khalil v. Joyce entry, now the district stage of the Khalil case."),
    # The new court-and-date line each stage renders instead:
    ("text-exact", "#text U.S. District Court for the Southern District of Indiana · June 2026", "Sarsour's stage line."),
    ("text-exact", "#text U.S. District Court for the Southern District of Ohio · March 2026", "Peralta's stage line."),
    ("text-exact", "#text U.S. Court of Appeals for the Fourth Circuit · October 2025", "Khan Suri's stage line."),
    ("text-exact", "#text U.S. Court of Appeals for the Third Circuit · September 2025", "Khalil's appellate stage line."),
    ("text-exact", "#text U.S. Court of Appeals for the Second Circuit · August 2025", "Mahdawi's appellate stage line."),
    ("text-exact", "#text U.S. District Court for the Central District of California · August 2025", "Vasquez Perdomo's stage line."),
    ("text-exact", "#text U.S. Court of Appeals for the Ninth Circuit · July 2025", "Calderon's stage line."),
    ("text-exact", "#text U.S. District Court for the District of Vermont · April 2025", "Mahdawi's district stage line."),
    ("text-exact", "#text U.S. District Court for the Southern District of New York · March 2025", "Chung's stage line."),
    ("text-exact", "#text U.S. District Court for the District of New Jersey · March 2025 · as Khalil v. Joyce et al.", "Khalil's district stage line, noting the caption the case carried there."),
    ("text-exact", "#text Khalil v. Joyce et al.", "The old entry's italicized caption text; it now sits unitalicized inside the stage line above."),
    # The role, which led the old line and now sits under the court line. The
    # trailing comma is the old form, the em dash (before document links) or
    # bare form the new one:
    ("text-exact", "#text Declaration,", "Old role prefix, nine matters."),
    ("text-exact", "#text Declaration —", "New role line, Sarsour and Pablo Sequen."),
    ("text-exact", "#text Declaration (with David Hausman) —", "New role line, the seven matters with David Hausman."),
    ("text-exact", "#text Consulting,", "Old role prefix, Peralta."),
    ("text-exact", "#text Consulting", "New role line, Peralta (no documents, so no dash)."),
    ("text-exact", "#text Expert report,", "Old role prefix, D.N.N."),
    ("text-exact", "#text Expert report —", "New role line, D.N.N."),
    ("text-exact", "#text Brief of amicus curiae,", "Old role prefix, Calderon."),
    ("text-exact", "#text Brief of amicus curiae", "New role line, Calderon (no documents)."),
    ("text-exact", "#text Declarations (for motion to certify class and reply in support of motion to certify class),", "Old role prefix, Vasquez Perdomo."),
    ("text-exact", "#text Declarations (for motion to certify class and reply in support of motion to certify class)", "New role line, Vasquez Perdomo (no documents)."),
    # Punctuation nodes around the document links: the old form wrapped them in
    # parentheses and joined with commas, the new form joins with middots.
    ("text-exact", "#text )", "Closing paren of an old document-link list, ten matters."),
    ("text-exact", "#text ,", "Comma between two old document links."),
    ("text-exact", "#text ·", "Middot between two document links in the new form."),
    # Structure: two matters merged into the case entry they belong to.
    ("text-exact", "<li>", "Thirteen matter bullets became eleven case entries: Khalil's and Mahdawi's second filings merged into their cases."),
    ("text-exact", "<i>", "The thirteen <i> wrappers the old matter bullets carried are gone: each case name is now the heading of its entry, italicized by the case-name class, which this gate does not track."),
    ("text-exact", "#text Mahdawi v. Trump et al.", "Mahdawi's name appeared in each of its two entries and now appears once, as the case name."),
    (
        "text",
        ".jumbotron { min-height: 300px; }",
        "site.css gains the case-list and stage-timeline styles for the "
        "reorganized Expert work tab. The inlined stylesheet is a single "
        "canonical text line, so this key names a stable fragment present on "
        "both sides of the change.",
    ),
    # ---- Khalil's Supreme Court stage, added August 2026 ---------------------
    #
    # NEW CONTENT, owner requested. The Khalil case gains its Supreme Court
    # posture: an expert declaration for the forthcoming amicus brief, with
    # David Hausman. No document is linked yet -- the Third Circuit stayed its
    # mandate and the certiorari deadline was extended to September 21, 2026
    # (No. 26A90) -- so the entry carries no URL until the brief is docketed.
    ("text-exact", "#text U.S. Supreme Court · August 2026", "The new stage's court line on the site."),
    ("text-exact", "#text Declaration (with David Hausman)", "The new stage's role line on the site -- no dash, because there are no documents to link yet."),
    (
        "text",
        "Khalil v. Trump et al.}, August 2026",
        "The new CV line, in LaTeX source form.",
    ),
    (
        "text",
        "Khalil v. Trump et al., August 2026",
        "The new CV line as typeset, in the brace-free form the PDF comparison "
        "reads. Covers the first line of the entry however it wraps -- nothing "
        "can wrap before 'August 2026', two-thirds of the way to the margin.",
    ),
    (
        "text",
        "Hausman)",
        "The typeset continuation of the new CV line. The entry is long enough "
        "to wrap and the wrap point depends on font metrics this suite cannot "
        "reproduce without XeLaTeX, so the key is the fragment every possible "
        "continuation ends with. Broader than its neighbours: it would also "
        "excuse a future diff line ending '(with ... Hausman)' -- accepted, "
        "because any real change to those lines still trips on its other words.",
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

    changed = [
        line
        for line in diff.splitlines()
        if line.startswith(("+", "-"))
        and not line.startswith(("+++", "---"))
        and line[1:].strip()
    ]

    # A line that appears as both a removal and an addition moved; it did not
    # change. difflib re-pairs surrounding context whenever a neighbour changes
    # length, so a regenerated section reports its unchanged chevrons and
    # wrappers as -/+ pairs. Cancelling them out leaves only real edits.
    #
    # Safe because it is symmetric: a line that is genuinely deleted has no
    # matching addition and still fails.
    from collections import Counter

    # Compare stripped, so a line that merely shifted indentation -- because a
    # wrapper above it was dropped -- still cancels as moved.
    removed = Counter(line[1:].strip() for line in changed if line.startswith("-"))
    added = Counter(line[1:].strip() for line in changed if line.startswith("+"))
    # Both sides of a moved line must be skippable, so each sign gets its own
    # allowance. Sharing one pool let the removals exhaust it and reported every
    # addition as unexplained.
    shared = removed & added  # multiset intersection
    budget = {"-": Counter(shared), "+": Counter(shared)}

    # "text" keys match as substrings; "text-exact" keys must be the whole line.
    # The exact form exists for fragments too short to be safe as substrings --
    # a bare "." would otherwise whitelist most of the document.
    exact = {v for k, v, _ in EXPECTED_DIFFS if k == "text-exact"}

    unexplained = []
    for line in changed:
        body = line[1:]
        stripped = body.strip()
        pool = budget[line[0]]
        if pool.get(stripped):
            pool[stripped] -= 1
            continue
        if stripped in exact:
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
