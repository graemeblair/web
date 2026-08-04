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

A second instance, same cause: Gate 2 emits one line per node, so a role label
in a table cell has nothing on its line identifying whose row it is. Moving a
person between two roles already in use passes. Names, links, photos and
placements are each checked, so this is bounded to the role column.

Keys do at least match on word boundaries now -- "Jihae Hong" no longer matches
"Jihae Hongg", which it did, and which meant a typo in a name passed.

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
    # ---- people, moved into content/people.yml ------------------------------
    #
    # The site's Research group tab and the CV's "Advisees and placement" are
    # one list now. Nine people appeared in one and not the other, and eight
    # placements were worded differently. Owner confirmed one list, everyone in
    # both, and settled the two status questions.
    (
        "text",
        "Jiyoung Kim (dissertation committee): Assistant Professor",
        "BUG FIX. The CV line read 'Jiyoung Kim (dissertation committee, "
        "Assistant professor, Michigan State University' -- an unclosed "
        "parenthesis, and a comma where its eleven siblings use '):'. It "
        "typeset that way in the published PDF. The rendering is generated from "
        "one template now, so a line cannot be punctuated differently from its "
        "neighbours.",
    ),
    (
        "text",
        "Jiyoung Kim (dissertation committee, Assistant professor",
        "Removal side of the unclosed-parenthesis fix.",
    ),
    (
        "text",
        "Alfredo Trejo III (dissertation committee)\\\\",
        "OWNER DECISION. The CV said 'ongoing'; the site listed him under "
        "Alumni. Owner confirmed he has finished. No placement is recorded -- "
        "left blank rather than invented.",
    ),
    (
        "text",
        "Alfredo Trejo III (dissertation committee, ongoing)",
        "Removal side of the Trejo status correction.",
    ),
    (
        "text",
        "Daniel Carnahan",
        "OWNER DECISION. On the site as a current dissertation student and "
        "absent from the CV. Owner confirmed the CV was stale; he is now listed "
        "in both, dissertation committee, ongoing.",
    ),
    (
        "text",
        "Brigid Morris",
        "As above -- current on the site, missing from the CV, now in both.",
    ),
    (
        "text",
        "Current research assistants",
        "Five current undergraduate researchers (Omar Elamri, Belle Ho, Jason "
        "Leland, Jarod Ngo, Ophelia Sin) were in the CV and nowhere on the "
        "site, which had no section for a current researcher without a "
        "placement -- only 'Current dissertation students' and 'Alumni'. Owner "
        "chose one list for both targets, so the site gains the section.",
    ),
    (
        "text",
        "Omar Elamri, Belle Ho, Jason Leland, Jarod Ngo, Ophelia Sin",
        "The five names in that new section -- see above.",
    ),
    (
        "text",
        "Graduate student researchers",
        "Aaron Rudkin and Luke Sonnet were on the site as graduate student "
        "researchers and in neither of the CV's three subsections. The CV gains "
        "a fourth rather than filing them under 'Staff researchers', which is "
        "not what they were.",
    ),
    ("text", "Aaron Rudkin: Postdoctoral fellow, MIT", "See above."),
    ("text", "Luke Sonnet: Lead data scientist, GrowthBook", "See above."),
    (
        "text",
        "Jihae Hong",
        "On the site's alumni table, absent from the CV. Now in both.",
    ),
    (
        "text",
        "Neal Fultz: Independent data science consultant",
        "On the site's alumni table, absent from the CV. Now in both. (He was "
        "already in the CV's software list as a fabricatr author.)",
    ),
    (
        "text",
        "Sofía Granados",
        "Her name, link and photo were on the site only inside a large "
        "commented-out card block, so they reached no reader. She is in the "
        "CV's staff researchers, so she now appears in both.",
    ),
    (
        "href",
        "https://co.linkedin.com/in/dankat-sofia-granados-sotelo",
        "Sofía Granados's link, previously only inside commented-out markup.",
    ),
    (
        "src",
        "img/group-sofia.webp",
        "Sofía Granados's photo, previously only inside commented-out markup.",
    ),
    ("text", "Saloni Majmudar", "In the CV's undergraduate list, absent from the site. Now in both."),
    ("text", "Jacquelyn Nguyen", "In the CV's undergraduate list, absent from the site. Now in both."),
    # Placements the two sources worded differently. The site's wording is used
    # in each case: it is the one being maintained, and in every instance it is
    # the more specific or more recent of the two.
    (
        "text",
        "Cesar B. Martinez-Alvarez",
        "The CV wrote 'Cesar Martinez Alvarez' and listed 'Assistant professor, "
        "UCSB; Postdoc, Yale'; the site has the hyphenated name with the middle "
        "initial and the two positions in chronological order. One value now "
        "feeds both.",
    ),
    ("text", "Cesar Martinez Alvarez", "Removal side of the name and placement correction."),
    (
        "text",
        "Ph.D. student, UCSB Bren School",
        "The CV said 'Ph.D. student, Bren School of the Environment, UCSB'.",
    ),
    (
        "text",
        "Ph.D. student, Bren School of the Environment, UCSB",
        "Removal side of the Fatiq Nadeem placement wording.",
    ),
    (
        "text",
        "J. Sebastián Leiva M.",
        "The CV wrote 'J. Sebasti\\'an Leiva'; the site has the full name. Also "
        "settles 'M.P.P student' (site, missing a period) against 'M.P.P. "
        "student' (CV) in favour of the CV.",
    ),
    ("text", "M.P.P student, Princeton", "Removal side of the missing-period fix above."),
    (
        "text",
        "Jasmine Miller: Researcher, Give Directly",
        "The CV said 'Research manager'; the site says 'Researcher'.",
    ),
    ("text", "Jasmine Miller: Research manager, Give Directly", "Removal side of the above."),
    (
        "text",
        "Safa Saleem: Legal assistant, law firm",
        "The CV recorded no placement for her; the site does.",
    ),
    (
        "text",
        "Quantitative research assistant, RAND Corporation",
        "The CV said 'Research assistant, RAND Corporation'.",
    ),
    (
        "text",
        "Research assistant, RAND Corporation",
        "Removal side of the Emily Allendorf placement wording.",
    ),
    (
        "text",
        "Ph.D. student in biomedical data science, Stanford",
        "The CV said 'biomedical informatics'; the site says 'biomedical data "
        "science', which is the name of the Stanford programme.",
    ),
    (
        "text",
        "Ph.D. student in biomedical informatics, Stanford",
        "Removal side of the Min Woo Sun placement correction.",
    ),
    (
        "text",
        "Assistant Professor of Political Science, University of Nevada, Reno",
        "The CV abbreviated the title to 'Assistant professor'; the site gives "
        "it in full, as it does for every other placement.",
    ),
    (
        "text",
        "Assistant professor, University of Nevada, Reno",
        "Removal side of the Ryan Baxter-King title wording.",
    ),
    ("text", "Jacquelyn Nguyen: Medical school", "Sentence-cased with its neighbours."),
    ("text", "Jacquelyn Nguyen: medical school", "Removal side of the above."),
    # Markup that reached no reader, dropped with the section it lived in.
    (
        "text",
        "%\\begin{minipage}{\\linewidth}",
        "Commented-out LaTeX at the head of the advisees block, dropped with "
        "the hand-written section it introduced.",
    ),
    (
        "text",
        "%{\\large\\item UCLA}",
        "As above -- commented-out heading.",
    ),
    (
        "text",
        "%Avery Do:",
        "A commented-out staff researcher with no placement recorded. Dropped "
        "rather than carried into the YAML as a person with no content; git "
        "history has it if it was a placeholder for someone real.",
    ),
    # Table scaffolding for the rows added above. The cells' contents are each
    # registered separately, and Gate 1 compares every href and src exactly, so
    # what these admit is an empty row -- not a row with anything in it.
    ("text-exact", "<tr>", "Scaffolding of an added alumni row -- see the names above."),
    ("text-exact", "<td>", "As above."),
    ("text-exact", "<td/>", "An added alumni row's empty photo cell (no photo on file)."),
    ("text-exact", "<h1>", "The 'Current research assistants' heading element."),
    # Gate 2 emits one line per node, so a role label sits on a line of its own
    # with nothing tying it to the person whose row it is. These keys therefore
    # admit "some alumni row says this role" and no more: every name, link,
    # photo and placement on those rows is checked separately. What slips
    # through is a person's role changing between two labels already in use --
    # measured, and noted in the blind-spot section at the top of this file.
    (
        "text-exact",
        "#text Undergraduate research assistant",
        "Role label on the rows added for Saloni Majmudar and Jacquelyn Nguyen.",
    ),
    (
        "text-exact",
        "#text Staff researcher",
        "Role label on the row added for Sofía Granados.",
    ),
    (
        "text",
        "Postdoctoral fellow, Yale; Assistant Professor of Political Science, UCSB",
        "Cesar Martinez-Alvarez's two positions were split by a <br> on the "
        "site and joined by a semicolon in the CV. One value feeds both, so the "
        "site's cell is now one string.",
    ),
    ("text", "Ph.D. student, UCLA", "Sofía Granados's placement, on her added row."),
    ("text", "M.P.P. student, Princeton", "J. Sebastián Leiva's placement -- see the name entry above."),
    ("text", "M.P.P. student, Princeton\\\\", "LaTeX form of the above, which carries a line-break macro."),
    (
        "text",
        "J. Sebasti{\\'a}n Leiva M.",
        "LaTeX form of the Leiva name correction. Registered separately because "
        "the CV source spells the accent as {\\'a} and the site as a literal á, "
        "so one key cannot match both.",
    ),
    (
        "text",
        "J. Sebasti{\\'a}n Leiva:",
        "Removal side of the above, in LaTeX form.",
    ),
    # Spacing that moved because membership did. The wider \\[.9em] marks a
    # boundary between groups within a subsection, so it follows whoever is last
    # in a group -- and both groups gained or lost a member above.
    (
        "text",
        "Emily Ortiz (dissertation committee, ongoing)",
        "Now last among the ongoing committee members, because Alfredo Trejo "
        "moved to the finished group, so the group-boundary gap follows her.",
    ),
    (
        "text",
        "Ophelia Sin",
        "Now last among current undergraduate researchers, because Safa Saleem "
        "moved to the placed group.",
    ),
    (
        "text",
        "Valerie Wirtschafter (dissertation committee): Data analyst, Brookings Institution\\end{indnt}",
        "The last line of a subsection no longer carries a trailing line break, "
        "so \\end{indnt} follows it directly rather than starting its own line. "
        "A trailing \\\\ before \\end{indnt} adds vertical space the "
        "hand-written CV did not have.",
    ),
    (
        "text-exact",
        "\\end{indnt}\\vspace{1em}",
        "Removal side of the line-break change above: the bare \\end{indnt} "
        "line that each subsection used to start.",
    ),
    (
        "text-exact",
        "\\begin{indnt}\\vspace{-.35em}",
        "Opening of the added 'Graduate student researchers' subsection.",
    ),
    (
        "text",
        "img/group-sofia.webp",
        "Sofía Granados's photo element. Registered as text as well as src "
        "because Gate 2 reads the rendered markup and consults only text keys, "
        "while Gate 1 compares the src set.",
    ),
    (
        "text",
        "co.linkedin.com/in/dankat-sofia-granados-sotelo",
        "Her link element, for the same reason.",
    ),
    ("text-exact", "#text Postdoctoral fellow, Yale", "Removal side of the Cesar placement join."),
    (
        "text-exact",
        "#text Assistant Professor of Political Science, UCSB",
        "Removal side of the Cesar placement join.",
    ),
    ("text-exact", "<br/>", "The <br> that separated Cesar's two positions -- now a semicolon."),
    ("text", "Associate consultant, Bain", "Saloni Majmudar's placement, on her added row."),
    ("text-exact", "#text Medical school", "Jacquelyn Nguyen's placement, on her added row."),
    (
        "text",
        "Valerie Wirtschafter (dissertation committee): Data analyst, Brookings Institution",
        "Removal side of the trailing-line-break change: her line used to end "
        "the subsection with \\end{indnt} on the next line.",
    ),
    (
        "text",
        "Safa Saleem",
        "Moves from the current undergraduate researchers to the placed ones, "
        "because the site records a placement for her and the CV did not.",
    ),
    ("text-exact", "\\end{indnt}", "Removal side of the trailing-line-break change above."),
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
        if not any(_matches(key, body) for key in keys):
            unexplained.append(line)
    return unexplained


def _matches(key: str, body: str) -> bool:
    """Is `key` present in `body` as a whole word rather than a fragment?

    Plain `in` is too weak for a key that is somebody's name. "Jihae Hong" is
    registered because she was added to the CV -- and it also matches "Jihae
    Hongg", so a typo in a name would have passed the suite. Measured: it did.

    A match is rejected when the character butting up against either end of the
    key is alphanumeric and the key's own end character is too. Keys that
    deliberately stop mid-phrase are unaffected, because they end in
    punctuation or a space.
    """
    start = body.find(key)
    while start != -1:
        end = start + len(key)
        before = body[start - 1] if start else ""
        after = body[end] if end < len(body) else ""
        clean_start = not (key[:1].isalnum() and before.isalnum())
        clean_end = not (key[-1:].isalnum() and after.isalnum())
        if clean_start and clean_end:
            return True
        start = body.find(key, start + 1)
    return False


def reason(kind: str, key: str) -> str | None:
    for k, v, why in EXPECTED_DIFFS:
        if k == kind and v == key:
            return why
    return None


def describe(kind: str, key: str) -> str:
    why = reason(kind, key)
    return f"{kind} {key!r}: {why}" if why else f"{kind} {key!r}: UNREGISTERED"
