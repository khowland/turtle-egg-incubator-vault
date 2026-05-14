"""
=============================================================================
Module:        utils/wormd_export.py
Project:       Incubator Vault v8.1.0 — WINC (Clinical Sovereignty Edition)
Requirement:   §1.2 Bridge — Ad-hoc WormD-oriented export bundles (ISS-2)
Upstream:      vault_views/6_Reports.py
Downstream:    datetime, json, typing
Use Cases:     [Pending - Describe practical usage here]
Inputs:        Normalized clinical records (dicts from Supabase)
Outputs:       CSV string, JSON string (versioned intake bundle)
Description:   Builds flattened case-level CSV and selectable JSON payloads as a
               best-effort schema for external turtle intake systems (e.g. WormD).
=============================================================================
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

EXPORT_SPEC_VERSION = "wormd_intake_bundle_v1"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_flat_case_csv(rows: list[dict[str, Any]]) -> str:
    """
    One row per maternal case (intake). Column order is stable for spreadsheets
    and mail merge. `rows` must be pre-joined dicts (see Reports view builder).
    """
    if not rows:
        return ""
    columns = list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def build_wormd_intake_json_bundle(
    *,
    selection_criteria: dict[str, Any],
    clinical_origin: dict[str, Any] | list[dict[str, Any]],
    bins: list[dict[str, Any]] | None = None,
    eggs: list[dict[str, Any]] | None = None,
    egg_observations_summary: list[dict[str, Any]] | None = None,
    bin_observations_summary: list[dict[str, Any]] | None = None,
    hatchling_outcomes: list[dict[str, Any]] | None = None,
    audit_provenance: dict[str, Any] | None = None,
    include_flags: dict[str, bool] | None = None,
) -> str:
    """
    Versioned JSON envelope for machine import. Sections are omitted when
    include_flags[key] is False or when the corresponding list/dict is None.
    """
    flags = include_flags or {}
    bundle: dict[str, Any] = {
        "export_spec_version": EXPORT_SPEC_VERSION,
        "generated_at_utc": _utc_now_iso(),
        "vault_application": "Incubator Vault",
        "selection_criteria": selection_criteria,
        "wormd_intake_guess": {
            "intake_type": "salvage_egg_program_maternal_donor",
            "notes": (
                "Best-effort mapping for a new turtle / salvage intake record. "
                "Validate field names against the live WormD schema before automation."
            ),
        },
        "include": {
            "clinical_origin": flags.get("clinical_origin", True),
            "bins": flags.get("bins", True),
            "eggs": flags.get("eggs", True),
            "egg_observations_summary": flags.get("egg_observations_summary", False),
            "bin_observations_summary": flags.get("bin_observations_summary", False),
            "hatchling_outcomes": flags.get("hatchling_outcomes", False),
            "audit_provenance": flags.get("audit_provenance", True),
        },
    }
    if bundle["include"]["clinical_origin"]:
        bundle["clinical_origin"] = clinical_origin
    if bundle["include"]["bins"] and bins is not None:
        bundle["bins"] = bins
    if bundle["include"]["eggs"] and eggs is not None:
        bundle["eggs"] = eggs
    if (
        bundle["include"]["egg_observations_summary"]
        and egg_observations_summary is not None
    ):
        bundle["egg_observations_summary"] = egg_observations_summary
    if (
        bundle["include"]["bin_observations_summary"]
        and bin_observations_summary is not None
    ):
        bundle["bin_observations_summary"] = bin_observations_summary
    if bundle["include"]["hatchling_outcomes"] and hatchling_outcomes is not None:
        bundle["hatchling_outcomes"] = hatchling_outcomes
    if bundle["include"]["audit_provenance"] and audit_provenance is not None:
        bundle["audit_provenance"] = audit_provenance
    return json.dumps(bundle, indent=2, default=str)
