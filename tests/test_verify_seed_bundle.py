"""Regression tests for the Project Seed structural verifier."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.verify_seed_bundle import ROOT_FILES, SNAPSHOT_FILES, check_source, check_target


class VerifySeedBundleTests(unittest.TestCase):
    def make_source(self, root: Path) -> None:
        for name in ROOT_FILES + ("WORKTREE_LIFECYCLE.md", "SEED_SYNC.md"):
            (root / name).write_text(
                "\n".join(ROOT_FILES) if name == "README.md" else "seed content",
                encoding="utf-8",
            )
        (root / "HUMAN.md").write_text(
            "regular, full-size Markdown fenced code block\n"
            "Never use compact command bars\n",
            encoding="utf-8",
        )
        workflow = root / ".github" / "workflows" / "project-seed-sync.yml"
        workflow.parent.mkdir(parents=True)
        workflow.write_text(
            "for file in " + " ".join(SNAPSHOT_FILES) + "; do\n"
            '  cp "seed/$file" "target/.project_seed/seed/$file"\n'
            "done\n",
            encoding="utf-8",
        )

    def test_valid_source_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_source(root)
            self.assertEqual(check_source(root), [])

    def test_source_detects_missing_snapshot_file_in_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_source(root)
            workflow = root / ".github" / "workflows" / "project-seed-sync.yml"
            workflow.write_text(
                "for file in " + " ".join(SNAPSHOT_FILES[:-1]) + "; do\n"
                '  cp "seed/$file" "target/.project_seed/seed/$file"\n'
                "done\n",
                encoding="utf-8",
            )
            self.assertTrue(any("WORKTREE_LIFECYCLE.md in the snapshot-copy loop manifest" in p
                                for p in check_source(root)))

    def test_source_does_not_accept_similarly_named_manifest_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_source(root)
            workflow = root / ".github" / "workflows" / "project-seed-sync.yml"
            workflow.write_text(
                "for file in " + " ".join(SNAPSHOT_FILES[:-1])
                + " WORKTREE_LIFECYCLE.md.backup; do\n"
                + '  cp "seed/$file" "target/.project_seed/seed/$file"\n'
                + "done\n",
                encoding="utf-8",
            )
            self.assertTrue(any("WORKTREE_LIFECYCLE.md in the snapshot-copy loop manifest" in p
                                for p in check_source(root)))

    def test_source_detects_missing_snapshot_copy_operation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_source(root)
            workflow = root / ".github" / "workflows" / "project-seed-sync.yml"
            workflow.write_text(
                "for file in " + " ".join(SNAPSHOT_FILES) + "; do\n"
                '  echo "seed/$file"\n'
                "done\n",
                encoding="utf-8",
            )
            self.assertTrue(any("does not copy manifest files" in p for p in check_source(root)))

    def test_source_ignores_manifest_in_unrelated_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_source(root)
            workflow = root / ".github" / "workflows" / "project-seed-sync.yml"
            workflow.write_text(
                "for file in " + " ".join(SNAPSHOT_FILES) + "; do\n"
                '  echo "listed elsewhere only"\n'
                "done\n"
                "for file in " + " ".join(SNAPSHOT_FILES[:-1]) + "; do\n"
                '  cp "seed/$file" "target/.project_seed/seed/$file"\n'
                "done\n",
                encoding="utf-8",
            )
            self.assertTrue(any("WORKTREE_LIFECYCLE.md in the snapshot-copy loop manifest" in p
                                for p in check_source(root)))

    def test_source_detects_removed_terminal_rule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_source(root)
            (root / "HUMAN.md").write_text("general guidance only", encoding="utf-8")
            self.assertTrue(any("terminal-format rule" in p for p in check_source(root)))

    def test_fresh_install_passes_with_complete_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for name in ROOT_FILES:
                (target / name).write_text("installed", encoding="utf-8")
            self.assertEqual(check_target(target), [])

    def test_fresh_install_detects_missing_bundle_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for name in ROOT_FILES[:-1]:
                (target / name).write_text("installed", encoding="utf-8")
            self.assertTrue(any("README.md" in p for p in check_target(target)))

    def test_synchronized_target_passes_with_complete_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            snapshot = target / ".project_seed" / "seed"
            snapshot.mkdir(parents=True)
            for name in SNAPSHOT_FILES:
                (snapshot / name).write_text("installed", encoding="utf-8")
            (target / "AGENTS.md").write_text("project instructions", encoding="utf-8")
            self.assertEqual(check_target(target), [])

    def test_synchronized_target_detects_incomplete_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            snapshot = target / ".project_seed" / "seed"
            snapshot.mkdir(parents=True)
            for name in SNAPSHOT_FILES[:-1]:
                (snapshot / name).write_text("installed", encoding="utf-8")
            (target / "AGENTS.md").write_text("project instructions", encoding="utf-8")
            self.assertTrue(any("Seed reference snapshot is incomplete" in p
                                for p in check_target(target)))

    def test_synchronized_target_requires_active_root_instructions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            snapshot = target / ".project_seed" / "seed"
            snapshot.mkdir(parents=True)
            for name in SNAPSHOT_FILES:
                (snapshot / name).write_text("installed", encoding="utf-8")
            self.assertTrue(any("no active root AGENTS.md" in p for p in check_target(target)))


if __name__ == "__main__":
    unittest.main()
