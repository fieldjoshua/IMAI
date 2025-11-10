# Commit Message Conventions

This document defines the commit message standards for the IMAI project, ensuring consistent and meaningful commit history.

## Format

```
<type>: <subject>

<body>

<footer>
```

### Components

1. **Type**: What kind of change (required)
2. **Subject**: Brief description (required, max 72 characters)
3. **Body**: Detailed explanation (optional)
4. **Footer**: References and breaking changes (optional)

## Types

### Primary Types

- **`feat`**: New feature
- **`fix`**: Bug fix
- **`test`**: Adding or updating tests
- **`docs`**: Documentation changes
- **`refactor`**: Code refactoring (no behavior change)
- **`chore`**: Maintenance tasks, dependencies, tooling
- **`style`**: Code style changes (formatting, whitespace)
- **`perf`**: Performance improvements
- **`ci`**: CI/CD changes
- **`build`**: Build system changes

### Examples

```bash
feat: add Claude AI processor for P.A.R.A. categorization
fix: handle rate limits in Notion API client
test: add integration tests for file watcher
docs: update PR workflow guide
refactor: extract file processing logic
chore: update dependencies in requirements.txt
style: format code with Black
perf: optimize database query performance
ci: add PR validation workflow
build: update Python version requirement
```

## Subject Line Rules

1. **Use imperative mood**: "add" not "added" or "adds"
2. **No period at end**: End with no punctuation
3. **Lowercase**: Start with lowercase (except proper nouns)
4. **Be specific**: Describe what changed, not why
5. **Max 72 characters**: Keep it concise

### Good Examples

```bash
feat: add Gmail integration for email processing
fix: handle missing API keys gracefully
test: add unit tests for para_classifier
docs: document PR versioning system
```

### Bad Examples

```bash
# Too vague
feat: updates

# Wrong mood
feat: added new feature

# Too long
feat: add comprehensive integration for Gmail API with OAuth authentication and email processing

# Period at end
feat: add file processor.

# Not imperative
feat: adds file processor
```

## Body (Optional)

Use body for:
- Detailed explanation of what and why
- Breaking changes
- Related issues

### Format

```bash
feat: add file watcher integration

Implement file system monitoring using watchdog library.
Monitors configured directories for new files and processes
them through the P.A.R.A. classification pipeline.

Closes #123
```

## Footer (Optional)

Use footer for:
- Breaking changes: `BREAKING CHANGE: description`
- Issue references: `Closes #123`, `Fixes #456`
- Co-authors: `Co-authored-by: Name <email>`

### Examples

```bash
fix: handle Notion API rate limits

Add exponential backoff retry logic for rate-limited requests.
Prevents immediate failures and improves reliability.

Fixes #42

---

feat: refactor configuration management

BREAKING CHANGE: Config class now requires explicit API keys.
Previously, keys were loaded from environment automatically.

Closes #78
```

## Multi-Line Format

```bash
<type>: <subject>

<body paragraph 1>

<body paragraph 2>

<footer>
```

## Pre-Commit Hook Validation

The pre-commit hook validates commit messages:

- ✅ Checks for conventional format (`type: description`)
- ⚠️ Warns if format doesn't match (allows override)
- ✅ Prevents commits without type prefix

### Bypassing Validation

If you need to bypass (not recommended):

```bash
git commit --no-verify -m "message"
```

## Branch Naming

Branches should match commit types:

- `feat/feature-name`
- `fix/bug-description`
- `test/add-tests`
- `docs/update-readme`
- `refactor/extract-logic`
- `chore/update-deps`

## Examples by Scenario

### New Feature

```bash
feat: add Google Calendar integration

Implement OAuth flow and event synchronization for Google Calendar.
Events are fetched and processed through the P.A.R.A. classifier.

Closes #15
```

### Bug Fix

```bash
fix: correct Notion database relation creation

Fix bug where relations weren't being created when para_link matched
an existing Project/Area/Resource. Now properly queries and links.

Fixes #23
```

### Test Addition

```bash
test: add integration tests for Gmail integration

Add tests marked with @pytest.mark.requires_api for Gmail OAuth
and email fetching. Tests use real API with test credentials.

Related to #18
```

### Documentation

```bash
docs: add PR workflow guide

Create comprehensive guide for creating and managing PRs according
to guardrail requirements. Includes versioning, testing, and
mandatory updates.

Closes #12
```

### Refactoring

```bash
refactor: extract AI processing into separate module

Move Claude AI processing logic from main.py into processors/
module for better organization and testability. No behavior changes.

Part of #20
```

### Dependency Update

```bash
chore: update anthropic package to 0.18.0

Update to latest version for improved error handling and new
API features. No breaking changes.

Updates trackers/dependencies.md
```

## Commit Message Best Practices

1. **Be Descriptive**: Explain what and why, not just what
2. **Reference Issues**: Link to related issues/PRs
3. **Group Related Changes**: One logical change per commit
4. **Write for Future You**: Clear messages help debugging
5. **Follow Format**: Consistency makes history searchable
6. **Keep It Focused**: One concern per commit
7. **Update Trackers**: Mention if trackers updated

## Common Mistakes

### ❌ Too Vague

```bash
fix: stuff
update: things
changes
```

### ❌ Wrong Mood

```bash
feat: added feature
fix: fixes bug
```

### ❌ Too Long Subject

```bash
feat: add comprehensive file processing system with support for PDF DOCX TXT MD CSV JSON images with OCR and ZIP archives
```

### ❌ Missing Type

```bash
add file processor
fix bug
update docs
```

### ✅ Good Examples

```bash
feat: add multi-format file processor
fix: handle missing file permissions
docs: update setup instructions
```

## Tools

### Commit Template

Create `.gitmessage` template:

```
# <type>: <subject>
#
# <body>
#
# <footer>
```

Use with:
```bash
git config commit.template .gitmessage
```

### Commit Message Validation

Pre-commit hook validates format automatically.

## References

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Angular Commit Guidelines](https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit)
- [PR Workflow Guide](PR_WORKFLOW.md)

