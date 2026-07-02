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
