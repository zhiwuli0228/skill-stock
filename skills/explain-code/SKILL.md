---
name: explain-code
description: Use when the user asks to explain, understand, or walk through a piece of code, file, or function
allowed-tools: Read, Grep, Glob
argument-hint: [file-path or function-name]
---

# Explain Code

## Overview

Provide a clear, structured explanation of code — what it does, how it works, and why it's designed that way.

## When to Use

- User says "explain this code", "what does this do", "walk me through this"
- User points at a file or function and wants to understand it
- User is onboarding to a new codebase

**Do NOT use when:**
- User wants to modify or fix the code (use direct editing instead)
- User wants a code review (use `/code-review` instead)

## Steps

1. Read the target file or function
2. Identify the purpose and high-level flow
3. Break down key logic sections with plain-language explanations
4. Note any non-obvious patterns, edge cases, or design decisions
5. Provide a concise summary

## Output Format

- Start with a one-line summary of what the code does
- Break down into logical sections (not line-by-line)
- Use bullet points for clarity
- Call out dependencies and side effects
- End with any caveats or things to watch out for
