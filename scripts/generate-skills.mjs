#!/usr/bin/env node
// Generate the shared rules blocks in canonical persona entrypoints.
// The fork keeps Pi adapter generation in generate-pi-skills.mjs.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = path.resolve(fileURLToPath(new URL('../', import.meta.url)));
export const COMPATIBILITY_CONTEXT = fs.readFileSync(new URL('../templates/harness-compatibility.md', import.meta.url), 'utf8');
export const SHARED_START = '<!-- BEGIN SHARED PERSONA RULES -->';
export const SHARED_END = '<!-- END SHARED PERSONA RULES -->';
export const DIRECT_PERSONAS = ['ask', 'implementer', 'researcher', 'reviewer', 'staffer'];
const NON_PERSONA_SKILLS = new Set(['jobs', 'lead']);

// Canonical SKILL.md files are installed directly by Claude Code and Codex.
// Only their marked block is generated; everything outside stays hand-written.
export function generateCanonicalSkills({ root = ROOT, check = false } = {}) {
  const skills = path.join(root, 'skills');
  const sharedPath = path.join(root, 'templates/persona-skill-rules.md');
  if (!fs.existsSync(sharedPath)) throw new Error('Missing shared persona rules source: templates/persona-skill-rules.md');
  const shared = fs.readFileSync(sharedPath, 'utf8').trim();
  if (!shared || shared.includes(SHARED_START) || shared.includes(SHARED_END)) {
    throw new Error('Invalid shared persona rules source');
  }
  const allSkillFiles = filesUnder(skills); // Reject symlinks before writing sources.
  for (const file of allSkillFiles) {
    if (!file.endsWith('.md')) continue;
    const relative = path.relative(root, file);
    const skillName = path.basename(path.dirname(file));
    const isDirectPersonaEntry = path.basename(file) === 'SKILL.md'
      && path.dirname(path.dirname(file)) === skills
      && !NON_PERSONA_SKILLS.has(skillName);
    if (!isDirectPersonaEntry) {
      const text = fs.readFileSync(file, 'utf8');
      if (text.includes(SHARED_START) || text.includes(SHARED_END)) {
        throw new Error(`Unexpected shared persona rules block in ${relative}`);
      }
    }
  }
  const entryPaths = new Set(DIRECT_PERSONAS.map(name => path.join(skills, name, 'SKILL.md')));
  for (const file of allSkillFiles) {
    if (path.basename(file) === 'SKILL.md' && path.dirname(path.dirname(file)) === skills) {
      const text = fs.readFileSync(file, 'utf8');
      if (text.includes(SHARED_START) || text.includes(SHARED_END)) entryPaths.add(file);
    }
  }
  const entries = [...entryPaths].sort().map(output => {
    const relative = path.relative(root, output);
    if (!fs.existsSync(output)) throw new Error(`Missing expected persona skill: ${relative}`);
    return { output, relative, source: fs.readFileSync(output, 'utf8') };
  });
  const block = `${SHARED_START}\n<!-- Generated from templates/persona-skill-rules.md; run npm run generate:skills. Do not edit this block. -->\n${shared}\n${SHARED_END}`;
  const outputs = [];
  for (const { output, relative, source } of entries) {
    const start = source.indexOf(SHARED_START);
    const end = source.indexOf(SHARED_END);
    if (start < 0 || end < start || source.indexOf(SHARED_START, start + 1) !== -1 || source.indexOf(SHARED_END, end + 1) !== -1) {
      throw new Error(`Expected exactly one ordered shared rules block in ${relative}`);
    }
    const dispatchExample = source.indexOf('## Locating the companion');
    if (dispatchExample === -1 || start > dispatchExample) {
      throw new Error(`Shared rules block must appear before dispatch example in ${relative}`);
    }
    const content = source.slice(0, start) + block + source.slice(end + SHARED_END.length);
    if (content !== source) outputs.push({ relative, output, content });
  }
  if (check && outputs.length) {
    throw new Error(`Stale canonical persona rules; edit templates/persona-skill-rules.md and run npm run generate:skills:\n${outputs.map(item => item.relative).join('\n')}`);
  }
  for (const { output, content } of outputs) fs.writeFileSync(output, content);
  return { changed: outputs.map(item => item.relative) };
}

function filesUnder(dir) {
  if (!fs.existsSync(dir)) return [];
  if (fs.lstatSync(dir).isSymbolicLink()) throw new Error(`Do not generate through symlinks: ${dir}`);
  return fs.readdirSync(dir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name)).flatMap(entry => {
    const target = path.join(dir, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`Do not generate through symlinks: ${target}`);
    return entry.isDirectory() ? filesUnder(target) : [target];
  });
}

