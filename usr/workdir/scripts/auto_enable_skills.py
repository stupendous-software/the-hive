#!/usr/bin/env python3
import json, os, re, sys

SETTINGS = '/a0/usr/settings.json'

# Known skill roots (match clone discovery)
SKILL_ROOTS = [
    '/a0/usr/workdir',
    '/a0/usr/skills',
    '/a0/skills',
]

# Load settings
try:
    with open(SETTINGS, 'r') as f:
        settings = json.load(f)
except Exception as e:
    print(f'[auto-enable] Failed to load settings: {e}', file=sys.stderr)
    sys.exit(1)

# Allow disabling via settings
if settings.get('skills_auto_enable') is False:
    print('[auto-enable] Disabled via settings.')
    sys.exit(0)

# Existing skills: preserve order, dedupe, and clean names (strip quotes/whitespace)
raw = settings.get('skills', [])
existing_norm = set()
existing = []
for s in raw:
    clean = s.strip().strip('"\'')
    norm = clean.lower()
    if norm and norm not in existing_norm:
        existing_norm.add(norm)
        existing.append(clean)

# Discover skills: find SKILL.md under each root (non-hidden)
discovered = []
for root in SKILL_ROOTS:
    if not os.path.isdir(root):
        continue
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if not os.path.isdir(path):
            continue
        md = os.path.join(path, 'SKILL.md')
        if not os.path.isfile(md):
            continue
        # Extract name from frontmatter
        name = None
        try:
            with open(md, 'r', encoding='utf-8', errors='ignore') as f:
                in_fm = False
                for line in f:
                    line = line.strip()
                    if line == '---':
                        if in_fm:
                            break
                        else:
                            in_fm = True
                        continue
                    if in_fm:
                        m = re.match(r'^name:\s*(.+)$', line)
                        if m:
                            name = m.group(1).strip()
                            break
        except Exception:
            pass
        if not name:
            name = entry
        clean_name = name.strip().strip('"\'')
        discovered.append(clean_name)

# Normalize discovered and filter new ones
new = []
for name in discovered:
    norm = name.lower()
    if norm and norm not in existing_norm:
        new.append(name)
        existing_norm.add(norm)

if not new:
    print('[auto-enable] All skills already enabled.')
    sys.exit(0)

print(f'[auto-enable] Enabling {len(new)} new skills: {new}')

settings['skills'] = existing + new
with open(SETTINGS, 'w') as f:
    json.dump(settings, f, indent=2)

print('[auto-enable] Updated settings.json.')
print('[auto-enable] Done.')
