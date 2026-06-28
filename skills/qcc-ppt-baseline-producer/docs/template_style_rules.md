# Template Style Rules

The deck must follow the supplied light 16:9 enterprise template.

## Fixed style

- White background.
- Large black title.
- Short red underline below title.
- Grey subtitle.
- Footer with page number, `Huawei Confidential`, and logo area.
- Red as the primary accent, with orange/green/blue/purple only for data grouping.
- No dark-blue technology-style theme.
- No independent title boxes on the cover that visually fight the original background.

## Cover rules

- Use template-like white cover.
- Title should sit directly on the background, not inside a separate opaque text box.
- Metadata should be placed in the template's lower-left information area.

## Agenda rules

- Use clean, sparse agenda layout.
- Do not over-design with dashboard-like blocks.

## Footer rules

- Footer must be consistent.
- Do not place content in the footer safety area.
- Keep a bottom safe zone of at least 0.62in.

## Bottom conclusion bar rules

- Do not mechanically add conclusion bars to every slide.
- At most one bottom conclusion bar per slide.
- No conclusion bars on cover, agenda, or circle-profile pages.
- If a slide title is already a strong conclusion, usually remove the bar.
- The bar must contain only one short page conclusion, not method explanation.
- Height should not exceed 0.28in.
- Text should normally be 20-35 Chinese characters.

## Template safety-zone rules added in v2.1

Corporate templates often already contain logo, confidentiality text, page footer, and decorative bottom-right elements. The generator must treat those as template-owned areas.

### Hard rules

- If the template already contains a logo, do not add any `HUAWEI` text or logo mark.
- If the template already contains a footer, use `--footer-mode none`.
- If the template contains only a logo but no page metadata, use `--footer-mode minimal`.
- Never place normal body text in the bottom-right logo safe zone.
- Never place conclusion bars over template footer or logo areas.
- Never add an extra decorative red block as a logo placeholder.

### Reserved areas for 16:9 Huawei-light template

| Area | Rule |
|---|---|
| bottom 0.62in | footer/template safe zone; no normal content |
| bottom-right x>10.80in, y>6.72in | logo safe zone; generator must not add text here |
| cover / agenda / circle profile | no bottom conclusion bar |

### Footer modes

`build_qcc_ppt.py` supports three footer modes:

- `none`: template fully owns footer and logo.
- `minimal`: generator adds page number and confidentiality text only. Default.
- `full`: generator adds full footer. Use only for blank templates without any logo/footer.


## V2.2 强模板驱动规则

- 必须先识别模板页类型：封面、目录、正文/图表、结束页。
- 正文页必须使用正文/图表 layout，禁止使用结束页 layout。
- 生成器只能填充内容安全区，不能重画模板背景、页脚、品牌层。
- 模板已有 logo/footer 时，`--footer-mode` 必须为 `none`。
- 禁止通过 `min(6, len(slide_layouts)-1)` 或类似兜底逻辑选择 layout。
- 禁止在读取模板后直接退化为空白页自绘模式。


## Placeholder handling

The template may contain editable placeholders for manual authoring. The generator must remove unused slide-level placeholders immediately after slide creation. Template-owned master elements, background images, footer lines and logos must remain.

Blocking defects:

- `单击此处添加标题` or `单击此处添加文本` visible in edit mode.
- A generated textbox overlaps an unused placeholder.
- A body/content placeholder remains on a generated slide.
