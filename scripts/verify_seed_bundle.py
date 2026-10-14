#!/usr/bin/env python3
"""Check that a Project Seed bundle or propagated snapshot is structurally complete.

This checks file presence and bundle wiring. It does not prove that an AI agent
will follow instructions, nor that project-specific AGENTS.md was adapted well.
"""
from __future__ import annotations

import argparse
import shlex
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
SNAPSHOT_COPY = 'cp "seed/$file" "target/.project_seed/seed/$file"'


def missing_files(base: Path, files: tuple[str, ...]) -> list[str]:
    return [name for name in files if not (base / name).is_file()]


def snapshot_manifest(workflow: str) -> tuple[set[str], bool, bool]:
    """Return files listed by the loop that actually performs the snapshot copy."""
    lines = workflow.splitlines()
    copied_files: set[str] = set()
    found_copy = False
    parse_failed = False
    index = 0

    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped.startswith("for file in "):
            index += 1
            continue

        manifest = stripped[len("for file in "):].split(";", 1)[0].strip()
        body: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip() != "done":
            body.append(lines[index].strip())
            index += 1

        if SNAPSHOT_COPY in body:
            found_copy = True
            try:
                copied_files.update(shlex.split(manifest))
            except ValueError:
                parse_failed = True
        index += 1

    return copied_files, found_copy, parse_failed


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
        manifest_files, found_copy, parse_failed = snapshot_manifest(workflow)
        if parse_failed:
            problems.append("Could not parse the sync workflow snapshot manifest")
        for name in SNAPSHOT_FILES:
            if name not in manifest_files:
                problems.append(
                    f"Sync workflow does not include {name} in the snapshot-copy loop manifest"
                )
        if not found_copy:
            problems.append("Sync workflow does not copy manifest files into the reference snapshot")
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
