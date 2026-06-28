# Workspace and Template Boundary

## Principle

The Skill is a capability package, not a project data container.

## Skill may contain

- default PPT template;
- complete empty QCC PPT template;
- scripts;
- rules;
- example data schema.

## Skill must not contain

- real project data;
- real evidence files;
- generated final PPT outputs;
- task-specific reports.

## Workspace must contain

- qcc-data.yaml;
- evidence-index.yaml;
- source materials;
- optional custom template;
- output PPT and reports.

## No-data behavior

If no `qcc-data.yaml` is provided, the Skill must generate a complete empty QCC PPT template with placeholders. It must not infer, fabricate, or reuse sample business content.
