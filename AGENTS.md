# AI Agent Instructions & Repository Guidelines

## Critical Context for AI Agents

**IMPORTANT**: This project uses specific patterns that must be followed:
1. **Build Command**: Use `uv run python -m ia_writer_templates.main` (NOT `uv run build` - that doesn't work)
2. **Dark Mode**: Use `html.night-mode` class, NOT `@media (prefers-color-scheme: dark)`
3. **CSS Structure**: Single unified `style.css` file, not separate light/dark files
4. **Python Version**: Requires Python 3.13+ (this is non-negotiable)

## Project Structure & Module Organization
- `src/ia_writer_templates/main.py` scans the `templates/` directory and builds an `.iatemplate` for each subdirectory
- Shared fragments (Info.plist, title, header, footer, document) live in `src/fragments/`; place overrides inside `templates/<template_name>/`
- Templates use unified `style.css` with light mode as default and `html.night-mode` for dark mode
- Never edit files in `dist/` by hand—always rebuild

## Build, Test, and Development Commands
- `uv sync --extra dev` prepares the environment with all dependencies
- `uv run python -m ia_writer_templates.main` builds all templates (primary command)
- `uv run pytest tests/` runs the test suite
- `uv run ruff format src` and `uv run ruff check src` for code quality

## Coding Style & Naming Conventions
- Follow standard PEP 8 for Python (4-space indentation, lowercase `snake_case` functions, constants in `UPPER_SNAKE_CASE`).
- Inside HTML/CSS fragments, keep indentation at two spaces and prefer semantic class names like `template-header` over positional names.
- Template directories use underscores (e.g., `neon_flux/`), bundle names use hyphens (e.g., `Neon-Flux.iatemplate`)
- Info.plist bundle IDs should stay reverse-DNS (e.g., `com.pravin.templates.neonflux`)

## Testing Guidelines
- Run `uv run python -m ia_writer_templates.main` after any change to rebuild templates
- Diff regenerated files (`git diff dist/templates`) to confirm expected HTML/CSS deltas only; document notable visual changes in the PR.
- Install the bundle in [iA Writer](https://ia.net/writer) and verify both appearance modes plus PDF export (`File → Export → PDF`) before shipping.

## Commit & Pull Request Guidelines
- Use imperative, scope-aware commit subjects like `Add cobalt variant preset` or `Refine PDF contrast`; squash trivial commits before opening a PR.
- Describe the problem, the solution, and impacted templates in the PR body; attach screenshots or PDFs captured from iA Writer when visual output changes.
- Link issues when available and call out any manual post-merge steps (e.g., `uv run build`) in a dedicated checklist.

## Template Packaging Tips
- Keep metadata in `bundle.json`; add new themes by cloning an existing directory under `templates/` and adjusting the JSON
- Use single `style.css` with `html.night-mode` for dark mode - DO NOT create separate light/dark CSS files
- List all assets in `bundle.json` under the `assets` key (including HTML fragments if customized)
- Validate after building—incorrect CSS selectors or Info.plist keys break iA Writer installation

## Known Issues & Solutions

### Light/Dark Mode Not Working
**Problem**: Template stays dark or doesn't switch
**Solution**:
- Remove ANY `@media (prefers-color-scheme: dark)` rules
- Ensure light mode is the default (no class needed)
- Dark mode ONLY activates with `html.night-mode` class
- Set explicit colors on `html` element for both modes

### Build Command Fails
**Problem**: `uv run build` doesn't work
**Solution**: Use `uv run python -m ia_writer_templates.main`

### PDF Export Issues
**Problem**: Headers have unwanted backgrounds, gradients don't show
**Solution**:
- Use `@media print` to override styles
- Provide solid color fallbacks for gradients
- Remove backdrop-filter and other unsupported properties

## Current Template Status

### GitHub Template
- Reference implementation from official iA Writer Templates
- Used for testing build accuracy
- DO NOT modify unless matching upstream changes

### Neon Flux Template
- Custom futuristic theme with neon colors
- Unified `style.css` with proper light/dark switching
- Author: Pravin Goomannee
- Version: 1.0.1

## Important Files

- `src/ia_writer_templates/main.py` - Build engine
- `templates/neon_flux/style.css` - Unified styles (reference for CSS structure)
- `templates/neon_flux/bundle.json` - Configuration example
- `tests/test_github_template.py` - Integration tests
