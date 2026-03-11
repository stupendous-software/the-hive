# Skills System

Skills are plug‑and‑play packages that extend clone with new tools, commands, and UI components. Whether you need PDF parsing, web search, or custom integrations, the skill marketplace and local development workflow make it easy.

## What is a Skill?
A skill follows the **agentskills.io** standard and includes:
- `SKILL.md` – documentation and usage
- `scripts/` – executable tools (python, node, shell)
- `prompts/` – optional system/user message templates

## Installing Skills
### From Marketplace
```bash
a0_skill install <skill-id>
```
### Local Development
Place the skill folder under `a0/usr/skills/` and clone will automatically load it on restart (or hot‑reload if enabled).


## Developing a Skill
1. Create a new skill using the wizard: `a0_skill create`
2. Implement your scripts in `scripts/` – they can call any agent tool.
3. Document usage in `SKILL.md`.
4. Test locally, then share or publish.

## Security Considerations
- Skills run with the same permissions as the clone process. Restrict skill installation to trusted sources.
- Secrets accessed by skill scripts are injected via the secure vault.

---

## Popular Skills
- `smtp-email-sender` – Send emails via SMTP
- `pdf_editing` – Extract text, convert to images, manipulate PDFs
- `web_search` – Perform Google searches and return results

Explore the full list in your instance’s Skills page or via `a0_skill list`.

