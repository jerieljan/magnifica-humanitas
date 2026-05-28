# Agent Guidelines — Magnifica Humanitas

## Project Overview

An Astro static site that presents Pope Leo XIV's encyclical *Magnifica Humanitas* as a structured, responsive web reader. The source text lives in `data/` as typed YAML blocks; the site renders them with a 3-column layout (sidebar, main text, annotation pane).

## Build & Development

- **Package manager:** Bun. Do not use npm or pnpm.
- **Commands:**
  - `bun install` — install dependencies
  - `bun run dev` — start Astro dev server
  - `bun run build` — static build to `dist/`
  - `bun run preview` — preview production build
- **Deployment:** Vercel, Astro v6 default static output. The `dist/` directory is the deploy artifact.
- **Do not commit `node_modules/`, `dist/`, or `.astro/`.** These are already in `.gitignore`.

## Project Structure

```
data/              # YAML source files (see Data Conventions below)
src/
  layouts/
    Layout.astro   # Root layout with fonts, meta, global styles
  pages/
    index.astro    # Homepage / landing
    [section].astro  # Dynamic route for each YAML section
    footnotes.astro  # Dedicated footnotes page
    404.astro      # Custom error page
  components/
    Sidebar.astro           # Left navigation panel
    ParagraphRow.astro      # Single paragraph + enrichment pane
    ParagraphScrubber.astro # Bottom navigation scrubber
  lib/
    data.js        # YAML loading helpers, manifest parsing
  styles/
    global.css     # Tailwind/custom styles, EB Garamond typography
public/            # Static assets (images, favicon, robots.txt)
split.py          # One-off script used to generate YAML from raw source
vercel.json       # Vercel deployment config (headers, redirects)
```

## Data Conventions

All encyclical content lives in `data/*.yaml`. Treat these files as the **single source of truth** for text content.

### Block types

| Type | Fields | Purpose |
|---|---|---|
| `heading` | `content` | Major section titles (e.g., `CHAPTER ONE`) |
| `subheading` | `content`, `level` | Bold sentence-case subsections; `level` matches original TOC depth |
| `paragraph` | `number`, `content`, `footnote_refs`, `enrichment` | Numbered paragraphs |
| `text` | `content` | Unnumbered elements (dateline, signature) |

### Rules for editing YAML

1. **Preserve paragraph numbering.** Paragraph numbers (`number:`) must stay sequential within a section and globally consistent with `manifest.yaml`.
2. **Do not change filenames.** Section slugs are hardcoded in `manifest.yaml` and referenced by `[section].astro`.
3. **Footnote references** (`footnote_refs`) are arrays of integers pointing into `footnotes.yaml`. When adding new references, ensure the target footnote exists and sequential numbering is maintained.
4. **Footnote content format** — use `[Footnote content missing]` as a placeholder for unrecovered footnotes so the renderer can style them distinctly.
5. **The `enrichment` field** on every paragraph is intentionally empty (`{}`). It is reserved for AI-generated metadata (summary, keywords, commentary, cross-references). Do not put human-written commentary there unless the user explicitly asks.
6. **Title case for chapter titles** — convert from ALL CAPS to Title Case in YAML `heading` blocks (this is already done; preserve it).
7. **Markdown in `content`** — inline Markdown is supported (emphasis, links). Use straight quotes; the renderer handles typography.

### manifest.yaml

This is the navigation index. If you add, remove, or rename sections, update:
- `sections` list (slug, title, paragraph range)
- `subsections` hierarchy (titles and levels)

`src/lib/data.js` parses this file at build time.

## UI/UX Conventions

- **Typography:** Body text is EB Garamond. Do not override the body font family without explicit user request.
- **3-column layout:**
  - Left: `Sidebar` — collapsible on mobile, fixed on desktop.
  - Center: main reading area — scrollable.
  - Right: enrichment pane — displays `ParagraphRow` enrichment data; hidden on mobile.
- **Mobile:** The enrichment pane is replaced by a bottom-anchored summary panel (`ParagraphScrubber`).
- **AI disclosure:** Any AI-generated content shown in the UI must be gated by the desktop disclosure toggle/modal or equivalent mobile disclosure.
- **Source attribution:** The Vatican source URL and publication date must remain visible in the site footer or an accessible credits area.

## Code Style

- Use Astro components (`.astro`) for markup; plain JS/TS (`.js`/`.ts`) for data utilities.
- Keep component props typed where possible; use standard HTML attributes for event delegation.
- Prefer CSS custom properties in `global.css` for theming values (colors, spacing, font sizes).

## Common Tasks

### Adding a new section
1. Create `data/<section-slug>.yaml` following the block schema above.
2. Add the section entry to `data/manifest.yaml` (slug, title, paragraph range, subsections).
3. The `[section].astro` dynamic route will pick it up automatically via `src/lib/data.js`.
4. Re-run `bun run build` and verify the sidebar links correctly.

### Updating paragraph enrichment
1. Edit the `enrichment` object inside the relevant paragraph block in the section YAML.
2. The UI renders enrichment in the right-hand pane (desktop) and bottom panel (mobile).
3. Rebuild to see changes; no layout files need editing for data-only updates.

### Recovering missing footnotes
1. Update the corresponding entry in `data/footnotes.yaml`.
2. Remove the `[Footnote content missing]` placeholder.
3. Verify that `footnote_refs` arrays across all sections still point to valid numbers.

## Notes

- `split.py` is a one-off data-migration script. You generally do not need to run it again unless re-processing a new raw source file.
- The site is content-heavy and text-focused. Keep additions lightweight; avoid heavy JS frameworks or large dependencies.
