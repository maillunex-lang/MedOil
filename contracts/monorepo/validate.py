#!/usr/bin/env python3
"""Validate monorepo manifest and on-disk scaffold. No third-party dependencies."""
from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = pathlib.Path(__file__).resolve().parent / "manifest.json"
SCHEMA = pathlib.Path(__file__).resolve().parent / "manifest.schema.json"

MODULE_ID = re.compile(r"^[a-z][a-z0-9_]*$")
MODULE_PATH = re.compile(r"^[a-z][a-z0-9_]*$")
TASK_STREAM = re.compile(r"^(S0|[A-Z][0-9]?)$")


class ValidationError(Exception):
    pass


def _expect_type(value: Any, expected: type, path: str) -> None:
    if not isinstance(value, expected):
        raise ValidationError(f"{path}: expected {expected.__name__}, got {type(value).__name__}")


def _expect_keys(obj: dict[str, Any], required: set[str], path: str, *, extra_allowed: bool) -> None:
    missing = required - obj.keys()
    if missing:
        raise ValidationError(f"{path}: missing keys {sorted(missing)}")
    if not extra_allowed:
        extra = set(obj.keys()) - required
        if extra:
            raise ValidationError(f"{path}: unexpected keys {sorted(extra)}")


def validate_against_schema(manifest: dict[str, Any], schema: dict[str, Any]) -> None:
    if manifest.get("schema_version") != schema["properties"]["schema_version"].get("const"):
        raise ValidationError("schema_version must be 1")

    _expect_keys(
        manifest,
        set(schema["required"]),
        "manifest",
        extra_allowed=False,
    )

    _expect_type(manifest["schema_version"], int, "schema_version")
    _expect_type(manifest["project"], str, "project")
    _expect_type(manifest["repository"], str, "repository")
    if not manifest["project"].strip():
        raise ValidationError("project must be non-empty")
    if len(manifest["repository"]) < 3:
        raise ValidationError("repository too short")

    modules = manifest["modules"]
    _expect_type(modules, list, "modules")
    if len(modules) < schema["properties"]["modules"]["minItems"]:
        raise ValidationError(f"modules: need at least {schema['properties']['modules']['minItems']} entries")

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    module_def = schema["$defs"]["module"]
    req_mod = set(module_def["required"])

    for i, mod in enumerate(modules):
        p = f"modules[{i}]"
        _expect_type(mod, dict, p)
        _expect_keys(mod, req_mod, p, extra_allowed=False)
        mid, mpath = mod["id"], mod["path"]
        _expect_type(mid, str, f"{p}.id")
        _expect_type(mpath, str, f"{p}.path")
        if not MODULE_ID.fullmatch(mid):
            raise ValidationError(f"{p}.id invalid")
        if not MODULE_PATH.fullmatch(mpath):
            raise ValidationError(f"{p}.path invalid")
        if mid in seen_ids:
            raise ValidationError(f"duplicate module id {mid}")
        if mpath in seen_paths:
            raise ValidationError(f"duplicate module path {mpath}")
        seen_ids.add(mid)
        seen_paths.add(mpath)
        if not TASK_STREAM.fullmatch(mod["task_stream"]):
            raise ValidationError(f"{p}.task_stream invalid")
        if not mod["description"].strip():
            raise ValidationError(f"{p}.description empty")

    aux_def = schema["$defs"]["auxiliary"]
    req_aux = set(aux_def["required"])
    for i, aux in enumerate(manifest["auxiliary_paths"]):
        p = f"auxiliary_paths[{i}]"
        _expect_type(aux, dict, p)
        _expect_keys(aux, req_aux, p, extra_allowed=False)
        if not aux["path"].strip() or not aux["description"].strip():
            raise ValidationError(f"{p}: path and description required")

    for key in ("required_root_entries", "network_invariants", "economic_invariants"):
        arr = manifest[key]
        _expect_type(arr, list, key)
        if key == "required_root_entries" and not arr:
            raise ValidationError("required_root_entries must not be empty")
        for j, item in enumerate(arr):
            _expect_type(item, str, f"{key}[{j}]")
            if not item.strip():
                raise ValidationError(f"{key}[{j}] empty")

    if "no_float_for_money_or_inventory" not in manifest["economic_invariants"]:
        raise ValidationError("economic_invariants must include no_float_for_money_or_inventory")


def validate_filesystem(manifest: dict[str, Any], root: pathlib.Path = ROOT) -> None:
    for mod in manifest["modules"]:
        path = root / mod["path"]
        if not path.is_dir():
            raise ValidationError(f"missing module directory: {mod['path']}/")
    for aux in manifest["auxiliary_paths"]:
        path = root / aux["path"]
        if not path.exists():
            raise ValidationError(f"missing auxiliary path: {aux['path']}")
    for entry in manifest["required_root_entries"]:
        if not (root / entry).is_file():
            raise ValidationError(f"missing required root file: {entry}")


def load_manifest(path: pathlib.Path = MANIFEST) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def load_schema(path: pathlib.Path = SCHEMA) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest_document(manifest: dict[str, Any], schema: dict[str, Any] | None = None) -> None:
    schema = schema or load_schema()
    validate_against_schema(manifest, schema)


def validate_repository(root: pathlib.Path = ROOT) -> None:
    manifest = load_manifest()
    schema = load_schema()
    validate_against_schema(manifest, schema)
    validate_filesystem(manifest, root)


def main() -> int:
    try:
        validate_repository()
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("OK: monorepo manifest and scaffold")
    return 0


if __name__ == "__main__":
    sys.exit(main())