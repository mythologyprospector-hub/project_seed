# Universal Project Seed

This directory contains the portable operating constitution for projects built with Jimmy and the assistant.

The seed is intentionally **not** a project architecture.

It carries the stable relationship, workflow, communication, truth, verification, and machine conventions that should survive from one repository to the next.

## Installation

Copy the contents of this seed into a new repository.

Install the complete seed bundle:

```text
AGENTS.md
DOCS.md
HUMAN.md
MACHINE.md
ORGANS.md
README.md
```

`AGENTS.md` is the entry-point operating constitution, but it relies on the supporting references. The complete bundle preserves the owner's working relationship and Genie Principle (`HUMAN.md`), machine constants (`MACHINE.md`), documentation rules (`DOCS.md`), and Organs integration contract (`ORGANS.md`). Do not install only `AGENTS.md` and assume the full operating model is present.

### Verify an installation

Run the structural verifier from the Project Seed checkout:

```bash
python3 scripts/verify_seed_bundle.py --target /path/to/target-repository
```

It checks for the six root bundle files in a fresh installation, or the complete reference snapshot and active `AGENTS.md` in a repository that receives synchronized Seed snapshots. GitHub Actions also checks that this repository's bundle and propagation manifest remain structurally consistent.

**Limit:** this verifies file presence and wiring, not whether an assistant follows the instructions or whether project-specific adaptation is correct. Those still require review and real-world observation.

## What does not belong here

Do not put these in the universal seed:

- project-specific architecture;
- project-specific roadmap;
- project-specific APIs;
- project-specific canon;
- project-specific tests;
- current project status;
- temporary decisions;
- repository-specific dependencies.

Those belong to the project itself.

## The intended bootstrap

```text
New repository
    ↓
Install Project Seed
    ↓
Point assistant at repository
    ↓
Human: "We're building ______."
    ↓
Assistant inspects repository
    ↓
Assistant establishes / discovers project canon
    ↓
Assistant drives the work
```

The Seed should make the relationship work without requiring the human to re-explain it.
