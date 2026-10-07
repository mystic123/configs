---
name: creating-skills
description: Creates and refines SKILL.md files following Anthropic's official skill authoring best practices. Use when asked to create a new skill, improve an existing skill, review a skill for quality, or convert knowledge into skill format.
---

# Creating Skills

Build well-structured SKILL.md files that Claude discovers and uses effectively.

## Skill Structure

```
skill-name/
├── SKILL.md              # Main instructions (UNDER 500 lines)
├── reference/            # Detailed content loaded on demand
│   ├── api-guide.md
│   └── examples.md
├── scripts/              # Executable code (run, not read)
│   └── validate.py
└── assets/               # Templates, fonts, icons
    └── template.md
```

## Frontmatter Rules

```yaml
---
name: kebab-case-name
description: What it does in third person. Use when [specific trigger phrases].
---
```

- `name`: kebab-case, max 64 chars, no spaces/capitals/underscores
- `description`: max 1024 chars, MUST include WHAT + WHEN, third person
- No XML tags (`<` `>`) in frontmatter
- No "claude" or "anthropic" in name (reserved)
- No README.md inside skill folder
- File must be exactly `SKILL.md` (case-sensitive)

## Core Principles

### Claude is already smart
Only add what Claude doesn't already know. Challenge every line:
- "Does Claude need this explanation?" — probably not
- "Does this justify its token cost?" — be ruthless

### Match freedom to fragility
- **Low freedom** (exact scripts, specific numbers): fragile operations, critical sequences
- **Medium freedom** (pseudocode, parameters): preferred patterns with acceptable variation
- **High freedom** (text guidelines): context-dependent decisions, multiple valid approaches

### Progressive disclosure
- **Level 1** (frontmatter): always loaded — just name + description for discovery
- **Level 2** (SKILL.md body): loaded when relevant — core instructions
- **Level 3** (reference files): loaded on demand — detailed data, examples, API docs

## Writing the Description

The description is how Claude decides whether to load the skill. Get this right.

**Structure:** [What it does] + [When to use it] + [Key capabilities]

Good:
```yaml
description: Extracts text and tables from PDF files, fills forms, merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

Bad:
```yaml
description: Helps with documents.
```

**Rules:**
- Third person ("Processes..." not "I process..." or "You can use this to...")
- Include trigger phrases users would actually say
- Mention relevant file types if applicable
- Be specific enough to avoid over-triggering

## Writing Instructions

### Be specific and actionable

Good (50 tokens):
````markdown
## Extract PDF text
Use pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

Bad (150 tokens):
```markdown
## Extract PDF text
PDF files are a common format containing text and images.
To extract text, you'll need a library. There are many options
but pdfplumber is recommended because...
```

### Use progressive disclosure in practice

Keep SKILL.md as an overview. Detailed content goes in reference files.

```markdown
## Advanced features
**Form filling**: See [reference/forms.md](reference/forms.md)
**API reference**: See [reference/api.md](reference/api.md)
```

References must be **one level deep**. Never: SKILL.md → ref-a.md → ref-b.md.

### Provide workflows for complex tasks

Break into steps. For critical workflows, include a checklist:

````markdown
## Deployment workflow

```
Progress:
- [ ] Step 1: Run tests
- [ ] Step 2: Build artifacts
- [ ] Step 3: Deploy to staging
- [ ] Step 4: Verify
- [ ] Step 5: Deploy to production
```

**Step 1: Run tests**
...
````

### Include feedback loops

```markdown
## Edit process
1. Make changes
2. Validate: `python scripts/validate.py`
3. If validation fails → fix issues → go to step 2
4. Only proceed when validation passes
```

## Anti-Patterns

**Don't explain what Claude knows.** Skip "A PDF is a file format..." or "Python is a programming language..."

**Don't offer too many options.** Pick one default approach. Mention alternatives only when they serve a different use case.

**Don't use vague instructions.** "Validate properly" → "Run `python scripts/validate.py --strict`"

**Don't nest references.** One level deep from SKILL.md only.

**Don't include time-sensitive content.** No "as of March 2026" — use an "old patterns" section instead.

**Don't use Windows paths.** Always forward slashes: `reference/guide.md`, not `reference\guide.md`.

**Don't use magic numbers in scripts.** Document why: `TIMEOUT = 30  # HTTP requests typically complete within 30s`

## Quality Checklist

Before finalizing any skill:

- [ ] Name: kebab-case, max 64 chars
- [ ] Description: WHAT + WHEN, third person, under 1024 chars
- [ ] SKILL.md body: under 500 lines
- [ ] No unnecessary explanations of things Claude knows
- [ ] Specific and actionable instructions
- [ ] References one level deep
- [ ] No time-sensitive content
- [ ] Consistent terminology
- [ ] Tested triggering (loads on relevant queries, doesn't load on irrelevant ones)
- [ ] Freedom level matches task fragility
