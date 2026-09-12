#!/usr/bin/env python3
"""Build a messy "raw data folder" that exercises qcc_scan_inputs.py.

The folder mimics what a QCC circle actually hands over: a few Excel exports, a
hand-made CSV, a Word project note, a legacy .xls that cannot be parsed and a
photo. Category counts are deliberately NOT sorted, and several ten-step fields
are deliberately absent, so the scan report must flag them as missing instead of
inventing them.

    python scripts/make_qcc_scan_fixture.py --outdir examples/scan-fixture
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def build(root: Path) -> list[Path]:
    root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    counts = root / "查检表-1月汇总.csv"
    write_csv(
        counts,
        ["类别", "频次", "判定标准", "收集期间", "样本量", "责任人"],
        [
            ["校验异常", 60, "结果校验不通过", "2026-01-01..2026-01-31", 300, "张三"],
            ["记录缺失", 70, "关键字段为空", "2026-01-01..2026-01-31", 300, "张三"],
            ["流程等待", 126, "等待超 2 小时", "2026-01-01..2026-01-31", 300, "张三"],
            ["标注错误", 30, "标注与规则不符", "2026-01-01..2026-01-31", 300, "张三"],
            ["其他", 14, "其余零星异常", "2026-01-01..2026-01-31", 300, "张三"],
            ["合计", 300, "", "", "", ""],
        ],
    )
    written.append(counts)

    strata = root / "层别-班别.csv"
    write_csv(
        strata,
        ["班别", "异常数"],
        [["A 班", 46], ["B 班", 38], ["C 班", 41]],
    )
    written.append(strata)

    effect = root / "改善前后对比.csv"
    write_csv(
        effect,
        ["阶段", "期间", "异常例数", "样本量"],
        [
            ["改善前", "2026-01-01..2026-01-31", 126, 300],
            ["改善后", "2026-03-01..2026-03-31", 41, 300],
        ],
    )
    written.append(effect)

    measures = root / "对策实施表.csv"
    write_csv(
        measures,
        ["对策", "真因", "责任人", "环节", "时间", "做法", "可行性", "效益性", "经济性", "圈能力"],
        [
            ["补齐校验规则", "校验规则缺失", "李四", "结果校验环节", "第 4 周", "新增 12 条规则并回归验证", 5, 5, 4, 5],
            ["统一字段定义", "字段定义不统一", "王五", "数据录入环节", "第 4 周", "发布字段字典并培训", 5, 4, 5, 4],
            ["优化校验工具", "校验工具版本旧", "李四", "工具链", "第 5 周", "升级工具版本并配置规则", 4, 4, 4, 4],
        ],
    )
    written.append(measures)

    causes = root / "真因验证.csv"
    write_csv(
        causes,
        ["真因", "数据来源", "验证", "结论"],
        [
            ["校验规则缺失", "查检表 300 例", "按规则缺失分类统计", "关联异常 98 例（77.8%）"],
            ["字段定义不统一", "查检表 300 例 + 字段字典", "对比字段口径差异", "关联异常 36 例（28.6%）"],
            ["培训不到位", "访谈 20 人次", "访谈核查", "8 人次未受训（40%）"],
            ["校验工具版本旧", "工具清单核对", "版本比对", "3 个环节仍用旧版本"],
        ],
    )
    written.append(causes)

    try:
        from openpyxl import Workbook

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "主题评价"
        sheet.append(["候选主题", "上级政策", "重要性", "迫切性", "可行性", "圈能力"])
        sheet.append(["降低处理异常率", 5, 5, 4, 5, 4])
        sheet.append(["缩短处理时长", 4, 4, 3, 4, 4])
        sheet.append(["减少返工次数", 3, 4, 3, 3, 3])
        second = workbook.create_sheet("成本效益")
        second.append(["项目", "数值"])
        second.append(["投入人时", "24 小时"])
        second.append(["投入费用", "0.4 万元"])
        second.append(["年化节省工时", "312 小时"])
        second.append(["年化节省费用", "5.2 万元"])
        second.append(["回收期", "1 个月内"])
        second.append(["圈能力", "80%"])
        xlsx = root / "主题评价与效益.xlsx"
        workbook.save(xlsx)
        written.append(xlsx)
    except ImportError:
        pass

    try:
        import docx

        document = docx.Document()
        for line in (
            "课题：降低处理异常率",
            "圈组：精益圈",
            "圈长：张三",
            "活动周期：2026-01-01..2026-03-31",
            "指标：处理异常率（越低越好）",
            "优点：数据驱动定位改善重点",
            "不足：工具兼容性评估不足",
            "残余问题：抽样标准仍未统一",
            "下期主题：降低记录缺失率",
        ):
            document.add_paragraph(line)
        docx_path = root / "项目说明.docx"
        document.save(docx_path)
        written.append(docx_path)
    except ImportError:
        pass

    legacy = root / "去年查检表.xls"
    legacy.write_bytes(b"legacy-binary")
    written.append(legacy)

    photo = root / "现场查检表照片.png"
    photo.write_bytes(b"\x89PNG\r\n\x1a\n")
    written.append(photo)

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a messy raw-data folder for the QCC scan test.")
    parser.add_argument("--outdir", type=Path, default=Path("examples/scan-fixture"))
    args = parser.parse_args()
    written = build(args.outdir)
    for path in written:
        print(f"written: {path}")
    print(f"{len(written)} files in {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
