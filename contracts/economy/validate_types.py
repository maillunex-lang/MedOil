#!/usr/bin/env python3
"""CLI: validate Quantity / Rational JSON files."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from econ_types import TypeValidationError, reject_float_leaves, validate_quantity, validate_rational


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, help="JSON file with quantity or rational root object")
    parser.add_argument(
        "--mode",
        choices=("auto", "quantity", "rational"),
        default="auto",
        help="validation mode (auto uses keys present)",
    )
    args = parser.parse_args()
    try:
        data = json.loads(args.file.read_text(encoding="utf-8"))
        reject_float_leaves(data)
        mode = args.mode
        if mode == "auto":
            if "kind" in data and "amount" in data:
                mode = "quantity"
            elif "numerator" in data and "denominator" in data:
                mode = "rational"
            else:
                raise TypeValidationError("cannot infer mode; use --mode")
        if mode == "quantity":
            validate_quantity(data)
        else:
            validate_rational(data)
    except (TypeValidationError, json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())