import fs from 'node:fs';
import path from 'node:path';
import yaml from 'js-yaml';

const DATA_DIR = path.join(process.cwd(), 'data');

export function getManifest() {
  const file = fs.readFileSync(path.join(DATA_DIR, 'manifest.yaml'), 'utf8');
  return yaml.load(file);
}

export function getSection(slug) {
  const manifest = getManifest();
  const sectionMeta = manifest.sections.find((s) => s.slug === slug);
  if (!sectionMeta) return null;
  const file = fs.readFileSync(path.join(DATA_DIR, sectionMeta.file), 'utf8');
  const data = yaml.load(file);
  return { ...data, meta: sectionMeta };
}

export function getFootnotes() {
  const file = fs.readFileSync(path.join(DATA_DIR, 'footnotes.yaml'), 'utf8');
  const data = yaml.load(file);
  return data.footnotes || [];
}

export function getAllSections() {
  const manifest = getManifest();
  return manifest.sections.map((s) => {
    const file = fs.readFileSync(path.join(DATA_DIR, s.file), 'utf8');
    return yaml.load(file);
  });
}

export function getFootnoteBacklinks() {
  const sections = getAllSections();
  const backlinks = {};
  sections.forEach((sec) => {
    const sectionSlug = sec.slug || sec.part;
    sec.blocks?.forEach((block) => {
      if (block.type === 'paragraph' && block.footnote_refs) {
        block.footnote_refs.forEach((id) => {
          if (!backlinks[id]) backlinks[id] = [];
          backlinks[id].push({
            sectionSlug,
            sectionTitle: sec.title,
            paragraphNumber: block.number,
          });
        });
      }
    });
  });
  return backlinks;
}
