# Visual Component Patterns

v2.7 introduces a richer but still template-safe visual baseline. The purpose is to avoid decks that look like repeated simple boxes while preserving the current corporate template, footer, logo area, and layout safety rules.

## Component selection rules

Use the component that matches the data structure:

| Content type | Preferred visual |
|---|---|
| topic candidates / scoring | score matrix |
| current-state comparison | compact comparison table |
| cause analysis | fishbone-style cause map |
| key factor confirmation | evidence table |
| key factor to countermeasure mapping | mapping matrix |
| implementation chain | arrow flow |
| safety controls | gate grid |
| evidence lifecycle | arrow flow |
| validation layers | vertical timeline |
| before/after metrics | statistical comparison table + KPI summary |
| standardization assets | vertical timeline |
| promotion plan / next steps | roadmap timeline |
| final summary | PDCA cycle |

## Guardrails

- Rich visuals must stay inside the safe content area.
- Do not introduce a competing background, footer, or logo.
- Do not shrink body text below the formal threshold to fit a complex visual.
- Split crowded content into multiple slides rather than compressing it.
- Tables and flows should prioritize readability over decoration.
- If the input data is too sparse for a complex visual, fall back to a clear table or card.

## Default posture

The default deck should look structured and presentation-ready, not like a raw list of cards. However, visual complexity must be earned by the data. Do not draw decorative diagrams that do not clarify the QCC logic.
