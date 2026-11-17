#!/usr/bin/env python3
import copy
import json
import tempfile
import unittest
from pathlib import Path

from validate import (
    ValidationError,
    load_manifest,
    load_schema,
    validate_against_schema,
    validate_filesystem,
    validate_manifest_document,
)


class MonorepoManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_manifest()
        self.schema = load_schema()

    def test_manifest_matches_schema(self) -> None:
        validate_manifest_document(self.manifest, self.schema)

    def test_all_module_paths_unique(self) -> None:
        paths = [m["path"] for m in self.manifest["modules"]]
        self.assertEqual(len(paths), len(set(paths)))

    def test_repository_matches_tasks_json(self) -> None:
        tasks = json.loads(
            (Path(__file__).resolve().parents[2] / "tasks" / "tasks.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.manifest["repository"], tasks["repository"])

    def test_rejects_duplicate_module_id(self) -> None:
        bad = copy.deepcopy(self.manifest)
        bad["modules"].append(copy.deepcopy(bad["modules"][0]))
        with self.assertRaises(ValidationError) as ctx:
            validate_against_schema(bad, self.schema)
        self.assertIn("duplicate", str(ctx.exception).lower())

    def test_rejects_wrong_schema_version(self) -> None:
        bad = copy.deepcopy(self.manifest)
        bad["schema_version"] = 99
        with self.assertRaises(ValidationError):
            validate_against_schema(bad, self.schema)

    def test_rejects_missing_money_invariant(self) -> None:
        bad = copy.deepcopy(self.manifest)
        bad["economic_invariants"] = [x for x in bad["economic_invariants"] if x != "no_float_for_money_or_inventory"]
        with self.assertRaises(ValidationError):
            validate_against_schema(bad, self.schema)

    def test_filesystem_scaffold_on_repo_root(self) -> None:
        root = Path(__file__).resolve().parents[2]
        validate_filesystem(self.manifest, root)

    def test_filesystem_negative_missing_module(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("# x", encoding="utf-8")
            (root / "AGENTS.md").write_text("# x", encoding="utf-8")
            for mod in self.manifest["modules"]:
                if mod["id"] != "server":
                    (root / mod["path"]).mkdir()
            for aux in self.manifest["auxiliary_paths"]:
                (root / aux["path"]).mkdir()
            with self.assertRaises(ValidationError) as ctx:
                validate_filesystem(self.manifest, root)
            self.assertIn("server", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()