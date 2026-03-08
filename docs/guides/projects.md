# Projects

Projects in Agent Zero provide **isolated workspaces** for your agents. Each project has its own memory store, instructions, and secrets—perfect for multi-client setups, separate research domains, or simply keeping contexts clean.

## Key Concepts
- **Isolation**: Memory, uploaded files, and project-specific prompts are never shared across projects.
- **Project Config**: Stored under `a0/usr/projects/<name>/.a0proj` containing instructions and config.
- **Switching**: Change the active project via the Web UI (top-right selector) or programmatically using the API.

## Creating a Project
Projects can be created on the fly. The first time you switch to a non-existent project, Agent Zero will initialize it with default instructions.

### Via UI
1. Click the project dropdown in the top navigation.
2. Select "Create new project".
3. Provide a name and optional description.

### Via API
```bash
curl -X POST http://localhost:50080/api/project \
  -H 'Content-Type: application/json' \
  -d '{"name":"client-a","instructions":"You are a specialized assistant for Client A."}'
```

## Project Structure
On disk, each project lives at `a0/usr/projects/<name>/` with:
- `.a0proj/` – JSON/YAML configuration
- `workdir/` – working files for that project

## Use Cases
- Separate agents for different clients or companies
- Distinct environments (dev vs. prod)
- Isolate sensitive data per domain

---

## Best Practices
- Use clear, descriptive project names.
- Keep project-specific instructions concise and in the project config.
- Backup `a0/usr/projects/` regularly.

See also: [Usage Guide](./usage.md)
