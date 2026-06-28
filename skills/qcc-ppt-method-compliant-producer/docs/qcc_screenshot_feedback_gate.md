# QCC Screenshot Feedback Gate

## 1. Purpose

Rendered screenshots and user-provided screenshots are the delivery truth for QCC PPT formatting.

A slide can pass method coverage and object-level format audits but still fail formal review because of visual defects such as loose composition, crossing connector lines, awkward text wrapping, oversized whitespace, or weak method recognizability.

## 2. Mandatory workflow

When a screenshot defect is reported:

1. **Classify the defect** using the table below.
2. **Repair locally**: rebuild only the affected slide or component.
3. **Preserve the accepted framework**: page order, template, title system, footer, logo, and QCC method chain must remain stable.
4. **Render again** to PNG and inspect the repaired slide at full size.
5. **Update the Skill** with the defect pattern and repair rule.

## 3. Defect categories and repairs

| Screenshot symptom | Likely cause | Required repair |
|---|---|---|
| Cards float loosely across the page | Free-form placement without grid | Convert to grid, lane, or card board layout. |
| Connector lines cross the central text or pass through cards | Uncontrolled radial diagram | Remove connectors or route them outside text zones; prefer grid for formal review. |
| Large empty canvas around a method diagram | Method visual not using available content area | Add a topic anchor, group lane, or structured card region. |
| Title and content look disconnected | Body region starts too low or lacks visual anchor | Add a content heading or a left anchor panel. |
| Method page is technically correct but does not look like the method | Generic cards replaced method-specific form | Rebuild using the method visual pattern from `qcc_method_visual_patterns.md`. |
| Table is present but unreadable | Too many rows/columns or small font | Split, cardize, or reduce to key rows. |
| Bottom conclusion collides with legend/footer/logo | Callout y-position or content overflow | Move/shorten callout; keep footer and logo clearance. |
| TOP ranking card has vertical score wrapping | Score zone too narrow or font too large | Use fixed rank/topic/score zones and express score as `24分`; widen score zone instead of shrinking all fonts. |
| Ranking-card note overlaps the last row | Note placed inside the row stack | Move note below the row stack with a hard gap, or move the note to the bottom conclusion. |

## 4. Brainstorming page hard rule

For `主题评审｜头脑风暴`, prefer one of these formal-review-safe layouts:

1. **Idea-board grid**: left topic anchor + 2×3 or 3×2 candidate cards.
2. **Radial idea board**: only when connector lines do not cross text, cards, or conclusion callouts.
3. **Simple idea list**: when space is limited.

Avoid free-form radial layouts with long diagonal connector lines. They often look acceptable in object view but fail in rendered screenshots.

## 5. Acceptance gate

A repaired screenshot page passes only when:

- The method title is visible.
- The method form is recognizable.
- No connector line crosses text.
- No text overlaps or clips.
- All cards align to an obvious grid or intentional visual structure.
- The bottom callout and footer are separated.
- The slide remains editable PowerPoint shapes unless the user explicitly accepts image-only output.


## 6. Ranking summary card hard rule

For checklist, scoring matrix, Pareto, or topic-selection pages that contain a side `TOP` or `TOP 课题摘要` card:

- Use a list card, not a compressed nested table.
- Keep one row per ranked item.
- Use fixed zones: `rank badge` / `topic` / `score`.
- Never allow two-digit scores to wrap vertically.
- Never place explanatory notes over or inside the ranked-item rows.
- Prefer moving secondary explanation into the bottom conclusion if the side card is narrow.

Acceptance requires rendered screenshot inspection. Object-level layout coordinates are not enough because PowerPoint/LibreOffice may wrap text differently after export.
