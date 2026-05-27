# Magnifica Humanitas

Date Created: 2026-05-27 11:52

## Description

First Encyclical Letter of His Holiness Leo XIV Magnifica Humanitas

## Data Structure

The encyclical has been split into structured YAML files under the `data/` directory for easy consumption by static site generators (e.g., Astro, Hugo) and further processing.

### Files

| File | Description |
|---|---|
| `manifest.yaml` | Navigation index. Contains metadata and a list of all sections with their paragraph ranges and subsections. |
| `introduction.yaml` | §1–16 (Introduction) |
| `chapter-one-a-dynamic-approach-faithful-to-the-gospel.yaml` | §17–45 (Chapter One) |
| `chapter-two-foundations-and-principles-of-the-social-doctrine-of-the-church.yaml` | §46–89 (Chapter Two) |
| `chapter-three-technology-and-dominance.yaml` | §90–130 (Chapter Three) |
| `chapter-four-safeguarding-humanity-at-a-time-of-transformation.yaml` | §131–181 (Chapter Four) |
| `chapter-five-the-culture-of-power-and-the-civilization-of-love.yaml` | §182–228 (Chapter Five) |
| `conclusion.yaml` | §229–245 (Conclusion) |
| `footnotes.yaml` | All endnotes, sequentially renumbered. |

### YAML Schema (per section)

Each section file contains an ordered list of **blocks**:

- `heading` — Major section titles (e.g., `CHAPTER ONE`)
- `subheading` — Bold sentence-case subsections
- `paragraph` — Numbered paragraphs with footnote references and an empty `enrichment:` object
- `text` — Unnumbered elements (e.g., dateline, signature)

Example paragraph block:

```yaml
  - type: paragraph
    number: 1
    content: "Humanity, created by God in all its grandeur..."
    footnote_refs: [1, 2]
    enrichment: {}
```

### Footnotes

Footnotes were renumbered sequentially (Option B) to match the order of first appearance in the text. 210 of 224 footnotes were recovered from the raw source; the remaining 14 are marked with `[Footnote content missing]`.

### Enrichment

The `enrichment:` field on every paragraph is intentionally left empty. It is designed for future data such as AI-generated summaries, commentary, keywords, or cross-references that can be rendered in a right-hand annotation pane.

## Source

This text is sourced from the [Vatican website](https://www.vatican.va/content/leo-xiv/en/encyclicals/documents/20260515-magnifica-humanitas.html), published on 15 May 2026.

## Credits

- AI icon by [humbleicons](https://github.com/zraly/humbleicons) (MIT License)
