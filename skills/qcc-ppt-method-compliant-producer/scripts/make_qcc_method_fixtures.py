#!/usr/bin/env python3
"""Generate QCC method-compliance fixtures.

Two decks are produced:

* ``keyword-only.qcc.pptx`` — method titles with little or no data. It must be
  rejected by ``check_qcc_method_compliance.py``.
* ``data-complete.qcc.pptx`` — the standard ten-step chain with evidence. It
  must pass.

Run:
    python scripts/make_qcc_method_fixtures.py --outdir examples/fixtures
"""
from __future__ import annotations

import argparse
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt


def add_text_slide(prs: Presentation, title: str, lines: list[str]):
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title
    body = slide.shapes.add_textbox(Inches(0.6), Inches(1.6), Inches(9.0), Inches(4.6))
    frame = body.text_frame
    frame.word_wrap = True
    for index, line in enumerate(lines):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = line
        paragraph.font.size = Pt(14)
    return slide


def add_table_slide(
    prs: Presentation,
    title: str,
    headers: list[str],
    rows: list[list[str]],
    lines: list[str] | None = None,
):
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = title
    shape = slide.shapes.add_table(
        len(rows) + 1,
        len(headers),
        Inches(0.5),
        Inches(1.5),
        Inches(9.0),
        Inches(0.4) * (len(rows) + 1),
    )
    table = shape.table
    for column, header in enumerate(headers):
        table.cell(0, column).text = header
    for row_index, row in enumerate(rows, start=1):
        for column, value in enumerate(row):
            table.cell(row_index, column).text = value
    if lines:
        body = slide.shapes.add_textbox(Inches(0.5), Inches(4.2), Inches(9.0), Inches(2.0))
        frame = body.text_frame
        frame.word_wrap = True
        for index, line in enumerate(lines):
            paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            paragraph.text = line
    return slide


def build_data_complete(path: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    add_text_slide(prs, "封面", ["QCC 主题活动：降低处理异常率", "圈组：精益圈", "日期：2026-01-31"])

    add_table_slide(
        prs,
        "主题选定｜主题评价",
        ["候选主题", "上级政策", "重要性", "迫切性", "圈能力", "总分"],
        [
            ["降低处理异常率", "5", "5", "4", "4", "18"],
            ["缩短处理时长", "4", "4", "3", "4", "15"],
            ["减少返工次数", "3", "4", "3", "3", "13"],
        ],
        ["评价规则：5 分制，圈员独立打分取平均，权重相同。",
         "排序：1 降低处理异常率，2 缩短处理时长，3 减少返工次数。",
         "选定主题：降低处理异常率；理由：得分最高且数据可得。"],
    )

    add_text_slide(
        prs,
        "活动计划｜甘特图",
        [
            "阶段：P 计划（第1-2周） / D 实施（第3-5周） / C 检查（第6周） / A 处理（第7周）",
            "第1周 主题选定；第2周 现状把握；第3周 目标设定；第4-5周 对策实施；第6周 效果确认；第7周 标准化与检讨",
            "负责人：张三（计划）、李四（实施）、王五（检查）",
            "计划 vs 实际：前 4 周按计划完成，第 5 周延期 1 天，完成率 95%。",
        ],
    )

    add_text_slide(
        prs,
        "现状把握｜现状流程图",
        ["开始 → 接收任务 → 执行处理 → 数据记录 → 结果校验 → 结束",
         "异常点：结果校验环节异常率最高（42%）。"],
    )

    add_text_slide(
        prs,
        "现状把握｜查检表",
        [
            "判定标准：结果校验不通过即判定为异常。",
            "收集期间：2026-01-01 至 2026-01-31。",
            "样本量：300 例。",
            "收集方法：查检表逐例记录；责任人：李四。",
            "类别与频次：校验异常 126，记录缺失 70，流程等待 60，标注错误 30，其他 14。",
        ],
    )

    add_table_slide(
        prs,
        "现状把握｜数据汇总与层别分析",
        ["问题类别", "频次", "占比", "累计占比"],
        [
            ["校验异常", "126", "42.0%", "42.0%"],
            ["记录缺失", "70", "23.3%", "65.3%"],
            ["流程等待", "60", "20.0%", "85.3%"],
            ["标注错误", "30", "10.0%", "95.3%"],
            ["其他", "14", "4.7%", "100.0%"],
        ],
        ["层别分析：按班别分层，A 班异常率 46%，B 班 38%。"],
    )

    add_text_slide(
        prs,
        "现状把握｜柏拉图：识别关键 80% 改进项",
        [
            "问题类别按频次降序排列：校验异常 126、记录缺失 70、流程等待 60、标注错误 30、其他 14。",
            "累计百分比：42.0% / 65.3% / 85.3% / 95.3% / 100.0%。",
            "80%（85.3%）改善重点：校验异常、记录缺失、流程等待三类，属关键少数问题。",
        ],
    )

    add_text_slide(
        prs,
        "目标设定",
        [
            "现况值：42.0%；改善重点：85.3%；圈能力：80%。",
            "目标值 = 现况值 -（现况值 × 改善重点 × 圈能力）= 42.0% - (42.0% × 85.3% × 80%) = 13.3%。",
            "目标柱状图：现况 42.0% → 目标 13.3%。",
            "合理性说明：基于数据可得性与圈能力测算，目标可达成。",
        ],
    )

    add_text_slide(
        prs,
        "解析｜特性要因图（鱼骨图）",
        [
            "主干问题：结果校验异常率高。",
            "人：新人不熟练；机：校验工具版本旧；料：字段定义不统一；法：校验规则缺失；环：任务高峰集中；测：抽样标准不明确。",
        ],
    )

    add_text_slide(
        prs,
        "解析｜要因评价",
        [
            "要因评价矩阵图：对候选要因按影响度、频次、可控性评分。",
            "评分：校验规则缺失 27 分，字段定义不统一 21 分，抽样标准不明确 18 分。",
            "总分排序后筛选出要因：校验规则缺失、字段定义不统一。",
        ],
    )

    add_table_slide(
        prs,
        "解析｜真因验证",
        ["要因", "数据来源", "验证方法", "验证结果", "结论"],
        [
            ["校验规则缺失", "查检表 300 例 + 现场记录", "按规则缺失分类统计", "关联异常 98 例（77.8%）", "真因成立"],
            ["字段定义不统一", "查检表 300 例 + 字段字典", "对比字段口径差异", "关联异常 36 例（28.6%）", "真因成立"],
            ["抽样标准不明确", "抽检记录 60 例", "重抽对比判定差异", "差异 < 5%，不显著", "不成立，回退"],
        ],
        ["真因验证数据来源、结果与结论齐备；不成立项已回退。"],
    )

    add_table_slide(
        prs,
        "对策拟定｜对策评价矩阵",
        ["对策", "可行性", "效益性", "经济性", "圈能力", "总分"],
        [
            ["补齐校验规则", "5", "5", "4", "5", "19"],
            ["统一字段定义", "5", "4", "5", "4", "18"],
            ["优化校验工具", "4", "4", "3", "4", "15"],
        ],
        ["采纳：补齐校验规则、统一字段定义；对应真因：校验规则缺失、字段定义不统一。"],
    )

    add_table_slide(
        prs,
        "对策拟定｜5W1H",
        ["What", "Why", "Who", "Where", "When", "How"],
        [
            ["补齐校验规则", "真因1 校验规则缺失", "李四", "校验环节", "第4周", "新增 12 条规则并验证"],
            ["统一字段定义", "真因2 字段定义不统一", "王五", "数据录入", "第4周", "发布字段字典并培训"],
        ],
        ["对策与已验证真因一一映射。"],
    )

    add_text_slide(
        prs,
        "对策实施与检讨",
        [
            "阶段：D 实施与 C 检查。时间：第4-6周。责任人：李四、王五。",
            "进展：完成 12 条校验规则上线，字段字典发布完成。",
            "跟踪数据：异常率由 42.0% 降至 16.5%。",
            "困难与调整：工具兼容性问题导致延期 2 天，已调整实施顺序。",
        ],
    )

    add_text_slide(
        prs,
        "效果确认｜有形成果",
        [
            "改善前：42.0%；改善后：13.6%；目标值：13.3%。",
            "目标达成率：99.0%；进步率：67.6%。",
            "改善后收集期间：2026-03-01 ~ 03-31；样本量：300 例。",
            "改善前后对比图（柏拉图）：异常率显著下降。",
        ],
    )

    add_text_slide(
        prs,
        "效果确认｜无形成果",
        [
            "无形成果雷达图：问题意识、数据分析、团队协作、表达沟通。",
            "评价量表：1–5 分制；维度：问题意识、数据分析、团队协作、表达沟通、工具应用。",
            "圈员能力评分：活动前 3.1 分，活动后 4.2 分。",
            "成长：数据分析能力提升最明显。",
        ],
    )

    add_text_slide(
        prs,
        "标准化",
        [
            "标准化文件名称：《结果校验作业标准书》，编号 QCC-STD-001，版本 V1.0，生效日期 2026-04-01。",
            "日常稽核：责任人张三，每月 1 次，按检查表逐项稽核；稽核结果回写班组看板。",
            "教育训练与推广：新员工入职培训纳入本标准，向二线班组推广。",
            "效果维持：连续 3 个月复查达标。",
        ],
    )

    add_text_slide(
        prs,
        "检讨与改进",
        [
            "优点：数据分析驱动，措施可验证。",
            "不足：工具兼容性评估不足。",
            "残余问题：抽样标准仍未统一，列入持续跟踪。",
            "下期主题：降低记录缺失率。",
        ],
    )

    prs.save(str(path))


def build_keyword_only(path: Path) -> None:
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    add_text_slide(prs, "封面", ["QCC 主题活动（示例）"])
    add_text_slide(
        prs,
        "主题选定｜主题评价",
        ["待补充：候选主题与评价维度。"],
    )
    add_text_slide(prs, "活动计划｜甘特图", ["（未排期）"])
    add_text_slide(
        prs,
        "现状把握｜柏拉图：识别关键 80% 改进项",
        ["待补充：类别、频次、累计百分比。"],
    )
    add_text_slide(prs, "目标设定", ["待补充：现况值与目标值。"])
    add_text_slide(prs, "解析｜真因验证", ["待验证：数据来源与验证结果。"])
    add_text_slide(prs, "对策拟定｜5W1H", ["（只有方法名称）"])
    add_text_slide(prs, "效果确认｜有形成果", ["待补充：改善前后数据。"])
    add_text_slide(prs, "标准化", ["待补充：标准化文件。"])
    add_text_slide(prs, "检讨与改进", ["待补充：优点与不足。"])

    prs.save(str(path))


METHOD_THEATER_REPLACEMENTS = (
    # Pareto data: non-monotonic counts and an inconsistent improvement focus
    ("126", "26"),
    ("记录缺失 70", "记录缺失 170"),
    ("校验异常、记录缺失、流程等待三类", "校验异常、记录缺失二类"),
    # True-cause verification with trivial evidence
    ("关联异常 98 例（77.8%）", "关联异常 3 例（2.4%）"),
    ("查检表 300 例 + 现场记录", "查检表 3 例 + 口头说明"),
    # Target value contradicts the stated formula
    ("= 13.3%。", "= 60.0%。"),
    ("目标值：13.3%", "目标值：60.0%"),
    # Effect confirmation is worse than baseline with impossible rates
    ("改善前：42.0%；改善后：13.6%", "改善前：13.6%；改善后：42.0%"),
    ("目标达成率：99.0%", "目标达成率：150.0%"),
    ("进步率：67.6%", "进步率：-208.8%"),
)


def build_method_theater(path: Path, source: Path) -> None:
    """Corrupt analytical logic while keeping every method keyword."""
    prs = Presentation(str(source))
    for slide in prs.slides:
        for shape in slide.shapes:
            frames = []
            if getattr(shape, "has_text_frame", False):
                frames.append(shape.text_frame)
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    for cell in row.cells:
                        frames.append(cell.text_frame)
            for frame in frames:
                for paragraph in frame.paragraphs:
                    for run in paragraph.runs:
                        text = run.text
                        for old, new in METHOD_THEATER_REPLACEMENTS:
                            text = text.replace(old, new)
                        run.text = text
    prs.save(str(path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate QCC compliance fixtures.")
    parser.add_argument("--outdir", type=Path, default=Path("examples/fixtures"))
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    build_keyword_only(args.outdir / "keyword-only.qcc.pptx")
    complete = args.outdir / "data-complete.qcc.pptx"
    build_data_complete(complete)
    build_method_theater(args.outdir / "method-theater.qcc.pptx", complete)
    print(f"fixtures written to {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
