# qcc-ppt-method-compliant-producer v5.0

This Skill produces or enhances QCC (品管圈) PPT decks that satisfy the **standard
ten-step QCC method** — not just decks that show method names.

## v5.0: from "method names" to "analysis chain"

v4.x judged compliance by keyword presence: if a slide title contained `柏拉图`
or `根因验证`, the deck could pass even without data. v5.0 replaces that with a
structural check of the standard ten-step chain:

```text
1  主题选定     主题评价矩阵（维度/权重/评分/排序/选定理由）
2  活动计划     甘特图 + PDCA + 负责人
3  现状把握     现状流程图 + 查检表 + 数据汇总 + 层别 + 柏拉图（累计% / 80% 改善重点）
4  目标设定     现况值 -（现况值 × 改善重点 × 圈能力）= 目标值 + 目标柱状图
5  解析         鱼骨图（5M1E/6M）→ 要因评价 → 真因验证（数据验证，未通过回退）
6  对策拟定     对策评价矩阵 + 5W1H + 对策↔已验证真因
7  对策实施      PDCA 实施跟踪 + 过程数据 + 困难与调整
8  效果确认     有形成果（改善前后/目标达成率/进步率）+ 无形成果（雷达图）
9  标准化       标准化文件 + 日常稽核 + 教育训练与推广
10 检讨与改进   优点/不足/残余问题/下期主题
```

The compliance report now emits `FOUND / WEAK / MISSING / INCOMPLETE` per step:

- `FOUND` — inputs, analysis evidence and conclusions are present;
- `WEAK` — the method page exists but required evidence is missing;
- `MISSING` — the step/page is absent;
- `INCOMPLETE` — required data is still a `待补充` / `待验证` placeholder.

A deck is compliant only when all ten steps are `FOUND`.

## Three gates

1. **Method chain** — `docs/qcc_methodology.md`, `docs/qcc_page_contract.md`,
   `docs/qcc_method_compliance_protocol.md`.
2. **Structural compliance check** — `scripts/check_qcc_method_compliance.py`.
3. **Rendered quality + screenshot feedback** — `docs/qcc_format_diagnosis_and_repair.md`,
   `docs/qcc_screenshot_feedback_gate.md`.

## Typical flow

```bash
python scripts/check_qcc_method_compliance.py qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/qcc-method-compliance-report.md

python scripts/audit_qcc_ppt_format.py qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/qcc-format-audit-report.md

python scripts/audit_qcc_visual_heuristics.py qcc-workspace/output/qcc-review-ready.pptx \
  --report qcc-workspace/reports/qcc-visual-heuristics-report.md
```

Then render to PNG and inspect the montage. User-provided screenshots are authoritative
over object-level audits (`docs/qcc_screenshot_feedback_gate.md`).

## Data intake (v5.5)

```bash
python scripts/init_qcc_data.py --out qcc-workspace/input/qcc-data.yaml           # blank template
python scripts/init_qcc_data.py --out qcc-workspace/input/qcc-data.yaml --sample  # filled example
python scripts/validate_qcc_data.py --data qcc-workspace/input/qcc-data.yaml      # missing-field checklist
python scripts/verify_qcc_statistics.py --data qcc-workspace/input/qcc-data.yaml  # recompute p-value
python scripts/check_qcc_method_compliance.py deck.pptx --data qcc-workspace/input/qcc-data.yaml
```

See `docs/qcc_data_intake.md` for the per-step field checklist, CSV column conventions
and the data-quality rules.

## Fixture self-check

```bash
python scripts/make_qcc_method_fixtures.py --outdir examples/fixtures
python scripts/selftest_qcc_method_compliance.py --fixtures examples/fixtures
```

Expected result:

- `examples/fixtures/keyword-only.qcc.pptx` → `NON-COMPLIANT` (WEAK/INCOMPLETE/MISSING)
- `examples/fixtures/data-complete.qcc.pptx` → `PASS` (ten steps `FOUND`)

This is the regression guard against "method theater" decks.

## What changed vs v4.3

- Compliance is now structural/logical, not keyword-based.
- 查检表 moved from 主题评审 to 现状把握; SIPOC no longer replaces 现状把握.
- Added 主题评价、活动计划、目标设定、效果确认、标准化文件、检讨与改进.
- 鱼骨图 must be followed by 要因评价 and data-based 真因验证.
- 5W upgraded to 对策评价矩阵 + 5W1H + 对策↔真因映射.
