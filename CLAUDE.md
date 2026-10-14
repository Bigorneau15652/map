# Grist custom widgets — lessons learned

This repo hosts self-contained Grist custom widgets (one HTML file per widget
folder, no build step, served via GitHub Pages). Notes below are things that
have gone wrong in practice and must be checked for every new/edited widget.

## Alert / warning banners must always be readable, not just on hover

A widget shipped with warning banners that were unreadable until the user
hovered over them inside a Grist widget panel. Root cause was never fully
isolated (Grist can embed custom widgets in narrow/short panels, and
`position: sticky` toolbars combined with such panels are a suspect), but the
fix that resolved it was:

- Do not use `position: sticky` for in-widget toolbars/headers — use normal
  static positioning.
- Alert/banner text must have a strong, solid background/text contrast (no
  near-white-on-white palettes), a font-size of at least 13px, and explicit
  `white-space: normal; overflow-wrap: anywhere;` — never rely on default
  wrapping alone.
- Never use `overflow: hidden`, `text-overflow: ellipsis`, fixed/max-height,
  or opacity tricks on any element that carries user-facing text.
- Before shipping, screenshot-test the widget at a **narrow viewport**
  (~340px wide, not just a full 1280px desktop width) — Grist widget panels
  are frequently much narrower than a full page. A layout that looks fine at
  1280px can still hide content at panel widths users actually use.

## Form controls (select/button/input) need an explicit `color`, not just `background`

A widget's toolbar `<select>` and `<button>` elements had an explicit white
`background` but no explicit `color`. In a browser/OS running in dark mode,
this rendered as invisible white-on-white text — the background stayed
white (author-specified) while the text used the browser's dark-mode UA
default (light), because `color` was left unspecified. Regular elements
(divs, headings) aren't affected the same way since author-specified
background+color together always win over UA dark-mode styling — it's
specifically form controls where an unstyled sub-part can pick up the OS
theme's default independently. Two things fix this, do both:
- Add `color-scheme: light;` on `:root` (or `html`) to opt the whole page
  out of UA dark-mode form-control styling.
- Still set an explicit `color` on every `select`/`button`/`input` alongside
  its `background`, never one without the other.

Test by emulating a dark color scheme (Playwright: `newPage({ colorScheme:
'dark' })`) before shipping — this bug is invisible when testing in a
normally-light dev browser/tool.

## Don't build features the host already provides

Before adding UI chrome like a fullscreen/expand button, check whether Grist
itself already exposes it — Grist's own widget panel header has a native
expand icon. A widget-drawn equivalent is redundant, and worse, may not even
work: the Fullscreen API can be blocked inside Grist's iframe embedding,
producing a button that visibly fails. Prefer leaving host-chrome
responsibilities (fullscreen, drag-resize, etc.) to the host.

## Data-quality banners must be actionable, not just a count

When a widget flags a data-quality issue (e.g. "N rows excluded"), always:
- state unambiguously which table/column the user should go check ("vérifiez
  la colonne Site dans BDD_Salles"), not just an abstract count;
- give concrete example identifiers (room numbers, row ids) so the user can
  actually find the offending rows, capped to a handful with "et N autres";
- be explicit about what a count does *not* mean — e.g. clarify that "N
  rows share the same value" is about a genuine duplicate, not simply "this
  building has several floors" (an unclear message caused exactly that
  confusion once).

## Mirroring a reference document (PDF, existing report, …)

When a widget is meant to reproduce a specific reference document:
- Reuse the **exact wording** of section titles, table headers and field
  labels from the source document — do not paraphrase, shorten, or invent
  extra indicators/sections beyond what's in the reference, unless the user
  explicitly asks for additions.
- Use `pdfplumber`'s `extract_tables()` (not raw `pdftotext`/`pdfminer` text
  flow) to recover a PDF's actual table structure — flat text extraction
  scrambles column order in multi-column layouts and will lead to
  misreading the source document.
- Structure the HTML in clearly named, stable sections/ids matching the
  reference document's own sections (e.g. `#sec-surfaces-totales`). This lets
  future change requests reference "page 2, table X" precisely, and keeps
  layout positions stable across revisions as requested by the user.
- If the reference document is meant to be printed on a specific number of
  pages, add an explicit `@media print` stylesheet (smaller font, hidden
  interactive-only elements like on-screen charts/toolbars, `break-before:
  page` at the right spots) and verify the page count by rendering to PDF
  (e.g. Playwright `page.pdf()` + `pypdf` page count) — do not assume the
  on-screen layout will print acceptably.

## Verifying Grist data-derived logic before shipping

- Cross-check computed totals against a known-correct reference (a PDF, a
  prior report) at the same granularity (e.g. per floor, not just per
  building) — aggregate-only checks can hide a metric that's inflated on
  every floor by the same bug.
- A "3x (or more) too high" discrepancy against a trusted reference is a
  strong signal of a join/filter bug (e.g. a missing `Site=$Site` guard
  letting mismatched rows leak in), not a legitimate data difference.
- When a Grist table has sibling formula columns that already implement a
  filter (e.g. `Site=$Site`) and a new/changed column omits it, that's a bug
  by omission — check for this kind of inconsistency explicitly when adding
  or editing formulas in a table that has similar existing columns.

## SI Patrimoine reference documentation (read before any audit or change)

A private repository named Grist-SIPI-informations holds the reference note of the Grist document "Bac à sable SIPI" (data model, formulas, relations, pages, widgets, known anomalies, change journal). The main file is Note_reference_Grist_Bac_a_sable_SIPI.md. If a model state file or a change journal exists in that repository, read them too: they take precedence over the note where they differ.

To find it, search for a folder named Grist-SIPI-informations in the working environment. If it is not available, ask the user to add the repository to the session (or to attach the file). Never continue without it for a task that depends on table or column names.

Rules:
- Before auditing or modifying any widget, read the note. Never guess table or column names.
- The note is dated. If it conflicts with the widget code or with what the user says, point out the conflict instead of choosing silently.
- This repository is public. Never copy content from the private note into this repository (README files, code comments, commit messages, pull requests). Table structure, formula logic, anomaly lists and internal service names stay private.
- When a change alters which tables or columns a widget expects, tell the user to add an entry to the change journal of the private repository.
- For performance audits, measure first. Check Grist-side causes before touching widget code: heavy summary tables, full-document access reads of large tables such as BDD_Salles, duplicated calculations between a Grist formula and the widget.
- In JavaScript, write every string with template literals (backticks), without exception, because French apostrophes cause "Unexpected token, expected ;" errors.
- The user does not master code or GitHub. Communicate in French, in a didactic and factual tone, ask the necessary questions before programming, and give GitHub steps one by one.
