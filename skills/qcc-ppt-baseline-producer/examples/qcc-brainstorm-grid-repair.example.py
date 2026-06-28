"""Example: repair a loose brainstorming page.

Pattern: left topic anchor + 2x3 candidate idea grid + bottom output callout.
This avoids free-form connector clutter while keeping the QCC brainstorming form.
"""
# Use python-pptx to rebuild only the affected slide.
# 1. Clear the slide body.
# 2. Re-add template title/footer/logo.
# 3. Add a left topic anchor: 发散主题 / 不评分 / 不排序 / 先发散.
# 4. Add candidate ideas as 2x3 editable cards.
# 5. Add a bottom 发散输出 callout.
# 6. Render and inspect slide-XX.png before delivery.
