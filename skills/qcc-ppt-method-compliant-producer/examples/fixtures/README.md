# QCC Method-Compliance Fixtures

These fixtures are the regression guard for the v5.0 structural compliance check.

| Fixture | Purpose | Expected result |
|---|---|---|
| `keyword-only.qcc.pptx` | Decks that only show method names / placeholders | `NON-COMPLIANT`（含 WEAK / INCOMPLETE / MISSING） |
| `method-theater.qcc.pptx` | Method keywords complete but data logic broken (non-monotonic Pareto, target contradicting the formula, improvement worse than baseline) | `NON-COMPLIANT`（逻辑门拦截） |
| `data-complete.qcc.pptx` | The standard ten-step chain with data and conclusions | `PASS`（十步全部 `FOUND`） |
| `reports/keyword-only.report.md` | Expected report for the negative fixture | 不通过 |
| `reports/method-theater.report.md` | Expected report for the adversarial fixture | 不通过 |
| `reports/data-complete.report.md` | Expected report for the positive fixture | 通过 |

Regenerate and verify:

```bash
python scripts/make_qcc_method_fixtures.py --outdir examples/fixtures
python scripts/selftest_qcc_method_compliance.py --fixtures examples/fixtures
```
