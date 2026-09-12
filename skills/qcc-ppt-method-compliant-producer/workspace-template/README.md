# qcc-workspace for Visual Enhancer

Place task-specific files here, not in the Skill directory.

```text
qcc-workspace/
├── input/
│   ├── qcc-min-data.yaml       # 原始事实（向导或扫描草稿补全后）
│   ├── qcc-data.yaml           # 推导后的完整十步数据
│   ├── qcc-baseline.pptx       # 可选：增强模式
│   └── render/
│       └── montage.png
├── template/
│   └── company-template.pptx   # optional
├── output/
└── reports/
    ├── data-scan-report.md         # 数据目录扫描报告（使用者给文件夹时）
    ├── data-scan-evidence.json     # 证据索引（交给模型抽取）
    ├── data-derive-report.md       # 推导算式（改善重点/目标值/达成率/进步率/p 值）
    ├── data-readiness.md           # 还缺哪些字段
    ├── qcc-statistics-report.md    # 统计复算
    └── pipeline-summary.md         # 一次流水线各阶段 PASS/FAIL/GAP
```

使用者的原始资料（Excel / Word / PPT / PDF / CSV）**不要**放进这里，
保持原目录不动，用 `--dir` 指向它即可：

```bash
python scripts/qcc_pipeline.py --dir "D:/QCC资料" --workspace qcc-workspace
```
