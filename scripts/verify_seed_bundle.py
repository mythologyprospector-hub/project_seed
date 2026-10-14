#!/usr/bin/env python3
"""Check that a Project Seed bundle or propagated snapshot is structurally complete.

This checks file presence and bundle wiring. It does not prove that an AI agent
will follow instructions, nor that project-specific AGENTS.md was adapted well.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_FILES = (
    "AGENTS.md",
    "DOCS.md",
    "HUMAN.md",
    "MACHINE.md",
    "ORGANS.md",
    "README.md",
)
SNAPSHOT_FILES = ROOT_FILES + ("WORKTREE_LIFECYCLE.md",)


def missing_files(base: Path, files: tuple[str, ...]) -> list[str]:
    return [name for name in files if not (base / name).is_file()]


def check_source(root: Path) -> list[str]:
    problems: list[str] = []
    missing = missing_files(root, ROOT_FILES + ("WORKTREE_LIFECYCLE.md", "SEED_SYNC.md"))
    if missing:
        problems.append("Canonical Seed is missing required files: " + ", ".join(missing))
        return problems

    readme = (root / "README.md").read_text(encoding="utf-8")
    for name in ROOT_FILES:
        if name not in readme:
            problems.append(f"README.md does not document required bundle file {name}")

    human = (root / "HUMAN.md").read_text(encoding="utf-8")
    required_phrases = (
        "regular, full-size Markdown fenced code block",
        "Never use compact command bars",
    )
    for phrase in required_phrases:
        if phrase not in human:
            problems.append(f"HUMAN.md is missing terminal-format rule: {phrase!r}")

    workflow_path = root / ".github" / "workflows" / "project-seed-sync.yml"
    if not workflow_path.is_file():
        problems.append("Missing .github/workflows/project-seed-sync.yml")
    else:
        workflow = workflow_path.read_text(encoding="utf-8")
        for name in SNAPSHOT_FILES:
            if f'cp "seed/{name}" "target/.project_seed/seed/{name}"' not in workflow:
                # The workflow uses a loop for the copy, so confirm the manifest
                # loop includes each expected file instead of expecting a literal cp.
                loop_start = 'for file in '
                loop_lines = [line for line in workflow.splitlines() if line.strip().startswith(loop_start)]
                if not loop_lines or not any(name in line for line in loop_lines):
                    problems.append(f"Sync workflow does not include {name} in its snapshot manifest")
    return problems


def check_target(target: Path) -> list[str]:
    problems: list[str] = []
    snapshot = target / ".project_seed" / "seed"
    if snapshot.is_dir():
        missing = missing_files(snapshot, SNAPSHOT_FILES)
        if missing:
            problems.append("Seed reference snapshot is incomplete: " + ", ".join(missing))
        if not (target / "AGENTS.md").is_file():
            problems.append("Target repository has no active root AGENTS.md")
    else:
        missing = missing_files(target, ROOT_FILES)
        if missing:
            problems.append("Root Seed bundle is incomplete: " + ", ".join(missing))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, help="check a target repository's installed Seed files")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="canonical Seed repository root (defaults to this checkout)")
    args = parser.parse_args()

    problems = check_target(args.target.resolve()) if args.target else check_source(args.root.resolve())
    if problems:
        print("Project Seed verification FAILED:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("Project Seed verification passed.")
    if args.target:
        print("File presence was checked; instruction-following and project-specific adaptation require review.")
    else:
        print("Canonical bundle, terminal-format rule, and sync manifest are structurally consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
