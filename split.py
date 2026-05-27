#!/usr/bin/env python3
"""
Split Magnifica Humanitas raw.md into structured YAML data files.
"""

import re
import os

WORKSPACE = "/Users/jerieljan/workspace/4-playground/magnifica-humanitas"
RAW_PATH = os.path.join(WORKSPACE, "raw.md")
DATA_DIR = os.path.join(WORKSPACE, "data")

MAJOR_HEADINGS = {
    "INTRODUCTION",
    "CHAPTER ONE",
    "CHAPTER TWO",
    "CHAPTER THREE",
    "CHAPTER FOUR",
    "CHAPTER FIVE",
    "CONCLUSION",
}


def normalize_title(text):
    """Strip markdown bold/italic, remove links, collapse whitespace."""
    text = re.sub(r"\*+", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip("-")


def write_yaml_string(value):
    """Return a YAML-safe quoted string if needed, else plain."""
    if not value:
        return '""'
    if "\n" in value:
        lines = value.splitlines()
        indented = lines[0] + "\n" + "\n".join("      " + l for l in lines[1:])
        return f'"{indented.replace("\\", "\\\\").replace('"', '\\"')}"'
    if re.match(r"^[a-zA-Z0-9_\s.,;:!?()'-]+$", value) and not value.startswith(("*", "#", "[", "{", "|", ">", "'", '"')):
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def main():
    with open(RAW_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Split into chunks separated by blank lines
    chunks = [c.strip() for c in re.split(r"\n\s*\n", raw_text) if c.strip()]

    # 1. Frontmatter extraction (first chunk inside ---)
    frontmatter = {}
    if chunks[0].startswith("---"):
        fm_text = chunks[0].strip().lstrip("-").strip()
        for line in fm_text.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                frontmatter[k.strip()] = v.strip().strip('"').strip("'")

    # 2. Find start of body: first major heading chunk that is NOT a TOC link
    body_start_idx = None
    for i, chunk in enumerate(chunks):
        m = re.match(r"^\*\*(.+)\*\*$", chunk, re.DOTALL)
        if m:
            inner = m.group(1)
            if "](" in inner:
                continue  # skip TOC entries like **[INTRODUCTION](#url)**
            clean = normalize_title(inner)
            if clean in MAJOR_HEADINGS:
                body_start_idx = i
                break

    if body_start_idx is None:
        raise RuntimeError("Could not find INTRODUCTION heading")

    # 3. Parse body into sections
    sections_data = []
    current_section = None
    current_blocks = []
    current_subsections = []
    last_subheading = None
    first_para = None
    last_para = None
    last_para_for_sub = None

    def finish_section():
        if current_section:
            # Close last subsection
            if current_subsections and current_subsections[-1].get("paragraph_range")[1] is None:
                current_subsections[-1]["paragraph_range"][1] = last_para_for_sub
            sections_data.append({
                "title": current_section,
                "slug": slugify(current_section),
                "blocks": current_blocks,
                "subsections": current_subsections,
                "paragraph_range": [first_para, last_para] if first_para else [None, None],
            })

    heading_re = re.compile(r"^\*\*(.+)\*\*$", re.DOTALL)
    para_re = re.compile(r"^(\d+)\\\.\s+(.+)$", re.DOTALL)
    footnote_ref_re = re.compile(r"\[\^(\d+)\]")

    body_chunks = chunks[body_start_idx:]
    idx = 0
    while idx < len(body_chunks):
        chunk = body_chunks[idx]

        # Stop at footnotes separator
        if chunk == "---":
            tail = body_chunks[idx + 1: idx + 6]
            fn_like = sum(1 for c in tail if re.search(r"\[\^(\d+)\]", c) or re.search(r"\[\\\[(\d+)\\\]\]", c))
            if fn_like >= 2:
                break

        m = heading_re.match(chunk)
        if m:
            inner = m.group(1)
            # Skip any bold chunks that contain markdown links (TOC remnants)
            if "](" in inner:
                idx += 1
                continue
            clean = normalize_title(inner)
            if clean in MAJOR_HEADINGS:
                # Check if next chunk is a continuation title (bold all caps)
                next_title = None
                if idx + 1 < len(body_chunks):
                    next_chunk = body_chunks[idx + 1]
                    next_m = heading_re.match(next_chunk)
                    if next_m:
                        next_inner = next_m.group(1)
                        if "](" not in next_inner:
                            next_clean = normalize_title(next_inner)
                            if next_clean.isupper() and next_clean not in MAJOR_HEADINGS:
                                next_title = next_clean
                finish_section()
                if next_title:
                    current_section = f"{clean}: {next_title}"
                    current_blocks = [
                        {"type": "heading", "level": 2, "title": clean},
                        {"type": "heading", "level": 2, "title": next_title},
                    ]
                    idx += 1  # skip the next chunk since we consumed it
                else:
                    current_section = clean
                    current_blocks = [
                        {"type": "heading", "level": 2, "title": clean},
                    ]
                current_subsections = []
                first_para = None
                last_para = None
                last_para_for_sub = None
                idx += 1
                continue
            else:
                # Subheading
                if current_subsections and current_subsections[-1].get("paragraph_range")[1] is None:
                    current_subsections[-1]["paragraph_range"][1] = last_para_for_sub
                last_subheading = clean
                current_subsections.append({
                    "title": clean,
                    "slug": slugify(clean),
                    "paragraph_range": [None, None],
                })
                current_blocks.append({
                    "type": "subheading",
                    "level": 3,
                    "title": clean,
                    "slug": slugify(clean),
                })
                idx += 1
                continue

        m = para_re.match(chunk)
        if m:
            para_num = int(m.group(1))
            content = m.group(2)
            refs = footnote_ref_re.findall(content)
            if first_para is None:
                first_para = para_num
            last_para = para_num
            last_para_for_sub = para_num

            if current_subsections and current_subsections[-1].get("paragraph_range")[0] is None:
                current_subsections[-1]["paragraph_range"][0] = para_num

            current_blocks.append({
                "type": "paragraph",
                "number": para_num,
                "content": content,
                "footnote_refs": [int(r) for r in refs],
                "enrichment": {},
            })
            idx += 1
            continue

        # Unnumbered text (signature, dateline, etc.)
        current_blocks.append({
            "type": "text",
            "content": chunk,
        })
        idx += 1

    finish_section()

    # 4. Post-process subsections: fix paragraph ranges for any that are still open
    for sec in sections_data:
        paras = [b["number"] for b in sec["blocks"] if b["type"] == "paragraph"]
        for sub in sec["subsections"]:
            if sub["paragraph_range"][0] is None:
                sub["paragraph_range"][0] = paras[0] if paras else None
            if sub["paragraph_range"][1] is None:
                sub["paragraph_range"][1] = paras[-1] if paras else None

    # 5. Footnotes extraction
    footnote_area_start = None
    for i, chunk in enumerate(chunks):
        if chunk == "---":
            tail = chunks[i + 1: i + 6]
            fn_count = sum(1 for c in tail if re.search(r"\[\^(\d+)\]", c) or re.search(r"\[\\\[(\d+)\\\]\]", c))
            if fn_count >= 2:
                footnote_area_start = i + 1
                break

    raw_footnotes = []
    if footnote_area_start:
        for chunk in chunks[footnote_area_start:]:
            m = re.match(r"^\[\^(\d+)\]\s+(.*)$", chunk, re.DOTALL)
            if not m:
                m = re.match(r"^\[\\\[(\d+)\\\]\]\(.*?\)\s+(.*)$", chunk, re.DOTALL)
            if m:
                old_id = int(m.group(1))
                content = m.group(2).strip()
                raw_footnotes.append((old_id, content))

    # 6. Renumber footnotes
    body_to_new = {}
    footnotes_out = []
    next_new_id = 1

    for sec in sections_data:
        for block in sec["blocks"]:
            if block["type"] != "paragraph":
                continue
            content = block["content"]
            refs = footnote_ref_re.findall(content)
            new_refs = []
            for old_str in refs:
                old_id = int(old_str)
                if old_id not in body_to_new:
                    new_id = next_new_id
                    next_new_id += 1
                    body_to_new[old_id] = new_id
                    if new_id <= len(raw_footnotes):
                        fn_content = raw_footnotes[new_id - 1][1]
                    else:
                        fn_content = "[Footnote content missing]"
                    footnotes_out.append({
                        "id": new_id,
                        "content": fn_content,
                    })
                new_refs.append(body_to_new[old_id])

            def repl(m):
                return f"[^{body_to_new[int(m.group(1))]}]"
            block["content"] = footnote_ref_re.sub(repl, content)
            block["footnote_refs"] = new_refs

    # 7. Build manifest
    manifest = {
        "meta": {
            "title": "Magnifica Humanitas",
            "subtitle": "On Safeguarding the Human Person in the Time of Artificial Intelligence",
            "author": "Pope Leo XIV",
            "date": "2026-05-15",
            "source": frontmatter.get("source", ""),
            "total_paragraphs": 245,
        },
        "sections": [],
    }

    for i, sec in enumerate(sections_data, start=1):
        paras = [b["number"] for b in sec["blocks"] if b["type"] == "paragraph"]
        manifest["sections"].append({
            "title": sec["title"],
            "slug": sec["slug"],
            "file": f"{sec['slug']}.yaml",
            "order": i,
            "paragraph_range": [paras[0], paras[-1]] if paras else [None, None],
            "subsections": [
                {
                    "title": sub["title"],
                    "slug": sub["slug"],
                    "paragraph_range": sub["paragraph_range"],
                }
                for sub in sec["subsections"]
            ],
        })

    # 8. Write files
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(os.path.join(DATA_DIR, "manifest.yaml"), "w", encoding="utf-8") as f:
        f.write("# Auto-generated manifest for Magnifica Humanitas\n")
        f.write("meta:\n")
        for k, v in manifest["meta"].items():
            f.write(f"  {k}: {write_yaml_string(str(v))}\n")
        f.write("sections:\n")
        for sec in manifest["sections"]:
            f.write(f"  - title: {write_yaml_string(sec['title'])}\n")
            f.write(f"    slug: {sec['slug']}\n")
            f.write(f"    file: {sec['file']}\n")
            f.write(f"    order: {sec['order']}\n")
            f.write(f"    paragraph_range: [{sec['paragraph_range'][0]}, {sec['paragraph_range'][1]}]\n")
            f.write(f"    subsections:\n")
            for sub in sec["subsections"]:
                f.write(f"      - title: {write_yaml_string(sub['title'])}\n")
                f.write(f"        slug: {sub['slug']}\n")
                f.write(f"        paragraph_range: [{sub['paragraph_range'][0]}, {sub['paragraph_range'][1]}]\n")

    for sec in sections_data:
        path = os.path.join(DATA_DIR, f"{sec['slug']}.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"title: {write_yaml_string(sec['title'])}\n")
            f.write(f"slug: {sec['slug']}\n")
            f.write(f"part: {sec['slug']}\n")
            paras = [b["number"] for b in sec["blocks"] if b["type"] == "paragraph"]
            f.write(f"paragraph_range: [{paras[0] if paras else 'null'}, {paras[-1] if paras else 'null'}]\n")
            f.write("blocks:\n")
            for block in sec["blocks"]:
                f.write(f"  - type: {block['type']}\n")
                if block["type"] == "heading":
                    f.write(f"    level: {block['level']}\n")
                    f.write(f"    title: {write_yaml_string(block['title'])}\n")
                elif block["type"] == "subheading":
                    f.write(f"    level: {block['level']}\n")
                    f.write(f"    title: {write_yaml_string(block['title'])}\n")
                    f.write(f"    slug: {block['slug']}\n")
                elif block["type"] == "paragraph":
                    f.write(f"    number: {block['number']}\n")
                    f.write(f"    content: {write_yaml_string(block['content'])}\n")
                    f.write(f"    footnote_refs: {block['footnote_refs']}\n")
                    f.write(f"    enrichment: {{}}\n")
                elif block["type"] == "text":
                    f.write(f"    content: {write_yaml_string(block['content'])}\n")

    with open(os.path.join(DATA_DIR, "footnotes.yaml"), "w", encoding="utf-8") as f:
        f.write("footnotes:\n")
        for fn in footnotes_out:
            f.write(f"  - id: {fn['id']}\n")
            f.write(f"    content: {write_yaml_string(fn['content'])}\n")

    print(f"Done. Wrote {len(sections_data)} section files + manifest + footnotes to {DATA_DIR}")
    total_paras = sum(1 for s in sections_data for b in s["blocks"] if b["type"] == "paragraph")
    print(f"Total paragraphs processed: {total_paras}")
    print(f"Total footnotes mapped: {len(footnotes_out)}")
    if next_new_id - 1 > len(raw_footnotes):
        print(f"WARNING: {next_new_id - 1 - len(raw_footnotes)} footnotes had missing content in the raw list.")
    else:
        print("All footnotes mapped successfully.")


if __name__ == "__main__":
    main()
