"""Economic type validation (stdlib only)."""
from __future__ import annotations

import json
import pathlib
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[2]
KINDS_PATH = pathlib.Path(__file__).resolve().parent / "quantity-kinds.json"

INT64_MIN = -9223372036854775808
INT64_MAX = 9223372036854775807


class TypeValidationError(Exception):
    pass


def load_kinds(path: pathlib.Path = KINDS_PATH) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise TypeValidationError("quantity-kinds schema_version must be 1")
    lookup: dict[str, dict[str, Any]] = {}
    for entry in data["kinds"]:
        kid = entry["id"]
        if kid in lookup:
            raise TypeValidationError(f"duplicate kind {kid}")
        lookup[kid] = entry
    return lookup


def validate_amount_for_kind(kind: str, amount: Any, kinds: dict[str, dict[str, Any]] | None = None) -> int:
    kinds = kinds or load_kinds()
    if kind not in kinds:
        raise TypeValidationError(f"unknown quantity kind: {kind}")
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeValidationError(f"{kind}: amount must be integer, not float")
    if isinstance(amount, float):
        raise TypeValidationError(f"{kind}: float forbidden")
    spec = kinds[kind]
    if amount < spec["min"] or amount > spec["max"]:
        raise TypeValidationError(f"{kind}: amount {amount} out of range")
    if not spec["signed"] and amount < 0:
        raise TypeValidationError(f"{kind}: amount must be non-negative")
    return amount


def validate_quantity(obj: Any, kinds: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise TypeValidationError("quantity must be object")
    extra = set(obj.keys()) - {"kind", "amount"}
    if extra:
        raise TypeValidationError(f"unexpected quantity fields: {sorted(extra)}")
    if "kind" not in obj or "amount" not in obj:
        raise TypeValidationError("quantity requires kind and amount")
    kind = obj["kind"]
    if not isinstance(kind, str):
        raise TypeValidationError("kind must be string")
    amount = validate_amount_for_kind(kind, obj["amount"], kinds)
    return {"kind": kind, "amount": amount}


def validate_rational(obj: Any) -> dict[str, int]:
    if not isinstance(obj, dict):
        raise TypeValidationError("rational must be object")
    extra = set(obj.keys()) - {"numerator", "denominator"}
    if extra:
        raise TypeValidationError(f"unexpected rational fields: {sorted(extra)}")
    num, den = obj.get("numerator"), obj.get("denominator")
    if isinstance(num, bool) or not isinstance(num, int):
        raise TypeValidationError("numerator must be integer")
    if isinstance(den, bool) or not isinstance(den, int):
        raise TypeValidationError("denominator must be integer")
    if den < 1:
        raise TypeValidationError("denominator must be >= 1")
    if num < INT64_MIN or num > INT64_MAX or den < INT64_MIN or den > INT64_MAX:
        raise TypeValidationError("rational components out of int64 range")
    return {"numerator": num, "denominator": den}


def reject_float_leaves(value: Any, path: str = "$") -> None:
    """Walk JSON-like structure and forbid float nodes."""
    if isinstance(value, float):
        raise TypeValidationError(f"float forbidden at {path}")
    if isinstance(value, dict):
        for k, v in value.items():
            reject_float_leaves(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            reject_float_leaves(v, f"{path}[{i}]")