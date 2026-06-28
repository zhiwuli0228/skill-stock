#!/usr/bin/env python3
"""Validate QCC data contract before PPT generation.

Default mode is formal: the script fails on placeholder data, oral-only evidence,
missing quantitative before/after data, or evidence_status: missing in core pages.
Use --allow-draft only for an intermediate data-gap report.
"""
from __future__ import annotations
import argparse, re, sys, yaml
from pathlib import Path
from typing import Any

REQUIRED_TOP = ["meta", "circle", "qcc_process", "results", "standardization", "promotion"]
PLACEHOLDER_PATTERNS = ["待补充", "待确认", "TBD", "TODO", "N/A", "未知", "未提供", "缺失", "用户口述"]
QUALITATIVE_ONLY_PATTERNS = ["显著", "较好", "稳定", "提升", "降低", "优化", "可控", "良好", "半年"]
ACCEPTABLE_FORMAL_EVIDENCE_TYPES = {
    "experiment_report", "test_report", "performance_report", "operation_log", "production_monitoring_report",
    "release_record", "incident_record", "inspection_record", "code_commit", "audit_record", "metrics_export", "risk_report",
}
ORAL_EVIDENCE_TYPES = {"user_statement", "user_provided_production_summary", "oral_summary", "interview", "conversation_summary"}


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def flatten(obj: Any, prefix: str = "") -> list[tuple[str, Any]]:
    out: list[tuple[str, Any]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.extend(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj, 1):
            out.extend(flatten(v, f"{prefix}[{i}]"))
    else:
        out.append((prefix, obj))
    return out


def is_placeholder(v: Any) -> bool:
    if v is None:
        return True
    s = str(v).strip()
    if not s:
        return True
    return any(p.lower() in s.lower() for p in PLACEHOLDER_PATTERNS)


def contains_number(v: Any) -> bool:
    return bool(re.search(r"\d", str(v)))


def looks_qualitative_only(v: Any) -> bool:
    s = str(v)
    return not contains_number(s) and any(p in s for p in QUALITATIVE_ONLY_PATTERNS)


def evidence_index(evidence_path: Path | None) -> dict[str, dict]:
    if not evidence_path or not evidence_path.exists():
        return {}
    data = load_yaml(evidence_path)
    return {str(item.get("id")): item for item in data.get("evidence_index", []) if item.get("id")}


def has_evidence(obj: dict) -> bool:
    return bool(obj.get("evidence_ids") or obj.get("evidence_ref") or obj.get("evidence_status") == "missing")


def evidence_quality(obj: dict, ids: dict[str, dict]) -> tuple[bool, list[str]]:
    """Return (has_formal_evidence, notes)."""
    notes: list[str] = []
    if obj.get("evidence_status") == "missing":
        notes.append("evidence_status is missing")
        return False, notes
    if obj.get("evidence_ref"):
        ref = str(obj.get("evidence_ref"))
        if any(p in ref for p in ["用户口述", "口述", "conversation", "聊天"]):
            notes.append("evidence_ref appears to be oral/conversation summary")
            return False, notes
        return True, notes
    ev_ids = obj.get("evidence_ids", []) or []
    if not ev_ids:
        notes.append("no evidence_ids/evidence_ref")
        return False, notes
    formal = False
    for eid in ev_ids:
        item = ids.get(str(eid))
        if not item:
            notes.append(f"unknown evidence id: {eid}")
            continue
        etype = str(item.get("type", "")).strip()
        desc = f"{item.get('file','')} {item.get('description','')}"
        if etype in ORAL_EVIDENCE_TYPES or "用户口述" in desc or "口述" in desc:
            notes.append(f"oral-only evidence id: {eid}")
            continue
        if etype in ACCEPTABLE_FORMAL_EVIDENCE_TYPES:
            formal = True
        else:
            notes.append(f"non-standard evidence type for formal mode: {eid}:{etype}")
    return formal, notes


def require_field(obj: dict, key: str, path: str, errors: list[str]) -> None:
    if key not in obj or is_placeholder(obj.get(key)):
        errors.append(f"{path}.{key} is required and must not be placeholder")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("qcc_data", type=Path)
    ap.add_argument("--evidence", type=Path, default=None)
    ap.add_argument("--report", type=Path, default=Path("data-quality-report.md"))
    ap.add_argument("--allow-draft", action="store_true", help="Allow placeholders/missing evidence; still produces a data-gap report.")
    args = ap.parse_args()

    data = load_yaml(args.qcc_data)
    ids = evidence_index(args.evidence)
    errors, warnings = [], []
    formal = not args.allow_draft

    for k in REQUIRED_TOP:
        if k not in data:
            errors.append(f"Missing top-level section: {k}")

    if formal:
        for path, value in flatten(data):
            if is_placeholder(value):
                errors.append(f"formal mode forbids placeholder at {path}: {value}")

    circle = data.get("circle", {})
    for k in ["name", "topic", "activity_period", "department", "leader", "members"]:
        require_field(circle, k, "circle", errors if formal else warnings)
    if formal:
        for i, m in enumerate(circle.get("members", []) or [], 1):
            for k in ["name", "role", "responsibility"]:
                require_field(m, k, f"circle.members[{i}]", errors)

    qcc = data.get("qcc_process", {})
    for k in ["topic_selection", "current_state", "target_setting", "cause_analysis", "key_factor_confirmation", "countermeasures"]:
        if k not in qcc:
            errors.append(f"qcc_process.{k} is required")

    candidates = qcc.get("topic_selection", {}).get("candidates", [])
    if len(candidates) < 2:
        (errors if formal else warnings).append("topic_selection must include at least two candidates")

    problems = qcc.get("current_state", {}).get("problems", []) or []
    if formal and len(problems) < 3:
        errors.append("formal mode requires at least three current_state problems")
    for i, p in enumerate(problems, 1):
        for k in ["scenario", "symptom", "current_response", "impact"]:
            require_field(p, k, f"current_state.problems[{i}]", errors if formal else warnings)

    for i, t in enumerate(qcc.get("target_setting", {}).get("targets", []), 1):
        for k in ["metric", "baseline", "target", "rationale"]:
            require_field(t, k, f"target[{i}]", errors if formal else warnings)
        if formal and (not contains_number(t.get("baseline")) or not contains_number(t.get("target"))):
            errors.append(f"target[{i}] baseline and target must contain measurable numbers")
        ok, notes = evidence_quality(t, ids)
        if not ok:
            (errors if formal else warnings).append(f"target[{i}] lacks formal evidence: {'; '.join(notes)}")

    factors = {f.get("cause") for f in qcc.get("key_factor_confirmation", {}).get("factors", [])}
    for i, f in enumerate(qcc.get("key_factor_confirmation", {}).get("factors", []), 1):
        for k in ["cause", "verification_method", "evidence"]:
            require_field(f, k, f"key_factor[{i}]", errors if formal else warnings)
        ok, notes = evidence_quality(f, ids)
        if not ok:
            (errors if formal else warnings).append(f"key_factor[{i}] lacks formal evidence: {'; '.join(notes)}")

    for i, c in enumerate(qcc.get("countermeasures", {}).get("items", []), 1):
        for k in ["key_factor", "countermeasure", "implementation", "validation"]:
            require_field(c, k, f"countermeasure[{i}]", errors if formal else warnings)
        if c.get("key_factor") not in factors:
            (errors if formal else warnings).append(f"countermeasure[{i}] key_factor does not exactly match a confirmed factor: {c.get('key_factor')}")

    results = data.get("results", {})
    validation = results.get("validation", {})
    for k in ["test_total", "test_passed", "test_failed", "experiment_count"]:
        require_field(validation, k, "results.validation", errors if formal else warnings)
        if formal and not contains_number(validation.get(k)):
            errors.append(f"results.validation.{k} must be numeric or contain a numeric value")
    ok, notes = evidence_quality(validation, ids)
    if not ok:
        (errors if formal else warnings).append(f"results.validation lacks formal evidence: {'; '.join(notes)}")

    before_after = results.get("before_after", []) or []
    if formal and len(before_after) < 3:
        errors.append("formal mode requires at least three before_after metrics")
    for i, item in enumerate(before_after, 1):
        for k in ["metric", "before", "after", "improvement"]:
            require_field(item, k, f"before_after[{i}]", errors if formal else warnings)
        if formal:
            if not contains_number(item.get("before")) or not contains_number(item.get("after")):
                errors.append(f"before_after[{i}] before and after must contain quantitative values; do not use qualitative-only wording")
            if looks_qualitative_only(item.get("improvement")):
                errors.append(f"before_after[{i}].improvement is qualitative-only; provide a numeric delta or explicit count")
        ok, notes = evidence_quality(item, ids)
        if not ok:
            (errors if formal else warnings).append(f"before_after[{i}] lacks formal evidence: {'; '.join(notes)}")

    risk_items = results.get("risk_closure", []) or []
    if formal and len(risk_items) < 4:
        errors.append("formal mode requires at least four risk_closure items")
    for i, risk in enumerate(risk_items, 1):
        for k in ["concern", "experiment", "result", "conclusion"]:
            require_field(risk, k, f"risk_closure[{i}]", errors if formal else warnings)
        if formal and not contains_number(risk.get("result")):
            errors.append(f"risk_closure[{i}].result must contain quantitative experiment/operation result")
        ok, notes = evidence_quality(risk, ids)
        if not ok:
            (errors if formal else warnings).append(f"risk_closure[{i}] lacks formal evidence: {'; '.join(notes)}")

    lines = ["# QCC 数据质量报告", "", f"- mode: {'draft' if args.allow_draft else 'formal'}", "", "## Errors"]
    lines += [f"- {e}" for e in errors] or ["- None"]
    lines += ["", "## Warnings"]
    lines += [f"- {w}" for w in warnings] or ["- None"]
    lines += ["", "## Evidence Type Policy"]
    lines += ["- Formal mode requires operation logs, monitoring reports, test reports, experiment reports, release records, incident records, audit records, code commits, or metrics exports."]
    lines += ["- User oral summaries are allowed only in draft mode and must be converted to formal evidence before PPT generation."]
    lines += ["", "## Summary", f"- errors: {len(errors)}", f"- warnings: {len(warnings)}"]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines), encoding="utf-8")

    print(f"Validation report written: {args.report}")
    if errors:
        print("FAILED")
        return 1
    print("PASSED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
