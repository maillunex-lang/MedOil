#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

from econ_types import (
    TypeValidationError,
    load_kinds,
    reject_float_leaves,
    validate_amount_for_kind,
    validate_quantity,
    validate_rational,
)


class EconomicTypesTests(unittest.TestCase):
    def test_kinds_registry_covers_schema_enum(self) -> None:
        kinds = load_kinds()
        schema = json.loads((Path(__file__).parent / "quantity.schema.json").read_text(encoding="utf-8"))
        enum = set(schema["properties"]["kind"]["enum"])
        self.assertEqual(enum, set(kinds.keys()))

    def test_money_signed_negative_allowed(self) -> None:
        validate_amount_for_kind("money_kopeks", -100)

    def test_mass_rejects_negative(self) -> None:
        with self.assertRaises(TypeValidationError):
            validate_amount_for_kind("mass_grams", -1)

    def test_rejects_bool_as_amount(self) -> None:
        with self.assertRaises(TypeValidationError):
            validate_amount_for_kind("count_pieces", True)

    def test_rejects_float_in_tree(self) -> None:
        with self.assertRaises(TypeValidationError):
            reject_float_leaves({"a": 1.5})

    def test_quantity_valid(self) -> None:
        q = validate_quantity({"kind": "volume_milliliters", "amount": 500})
        self.assertEqual(q["amount"], 500)

    def test_quantity_unknown_kind(self) -> None:
        with self.assertRaises(TypeValidationError):
            validate_quantity({"kind": "float_liters", "amount": 1})

    def test_rational_valid(self) -> None:
        r = validate_rational({"numerator": 150, "denominator": 10000})
        self.assertEqual(r["denominator"], 10000)

    def test_rational_denominator_min(self) -> None:
        with self.assertRaises(TypeValidationError):
            validate_rational({"numerator": 1, "denominator": 0})


if __name__ == "__main__":
    unittest.main()