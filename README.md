# iA Writer Templates

[![CI](https://github.com/cityhunteur/ia-writer-templates/actions/workflows/ci.yml/badge.svg)](https://github.com/cityhunteur/ia-writer-templates/actions/workflows/ci.yml)
[![Release](https://github.com/cityhunteur/ia-writer-templates/actions/workflows/release.yml/badge.svg)](https://github.com/cityhunteur/ia-writer-templates/actions/workflows/release.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python-powered build system for creating installable `.iatemplate` bundles for [iA Writer](https://ia.net/writer). Build custom templates from reusable HTML fragments and CSS themes, with support for both light and dark modes.

## Features

- **Modular Design**: Shared HTML fragments with per-template overrides
- **Multiple Templates**: Includes GitHub (reference) and Neon Flux (custom) templates
- **Dark/Light Mode Support**: Automatic mode switching with CSS variants
- **Build Validation**: Integration tests ensure pixel-perfect template generation
- **Zero Configuration**: Add new templates by dropping a directory under `templates/`

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended package manager)
- [iA Writer](https://ia.net/writer) for testing generated templates
- Git (for fetching reference templates)

> **Note**: This project uses `uv` for dependency management. If you don't have uv installed, you can install it with:
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```
> Or use pip as an alternative for all commands.

### Installation

```bash
# Clone the repository
git clone https://github.com/cityhunteur/ia-writer-templates.git
cd ia-writer-templates

# Install with uv (recommended)
uv sync --extra dev

# Or with pip
pip install -e ".[dev]"
```

### Build Templates

```bash
# Build all templates with uv (recommended)
uv run python -m ia_writer_templates.main

# Or without uv
python -m ia_writer_templates.main
```

This generates `.iatemplate` bundles in `dist/templates/`.

## Template Installation

1. Open `dist/templates/` in Finder
2. Double-click any `.iatemplate` bundle (e.g., `Neon-Flux.iatemplate`)
3. Confirm installation when iA Writer prompts
4. Find your template under Settings → Templates in iA Writer

## Project Structure

```
ia-writer-templates/
├── src/
│   ├── ia_writer_templates/
│   │   ├── __init__.py
│   │   └── main.py           # Template build engine
│   └── fragments/            # Shared HTML/plist fragments
│       ├── Info.plist
│       ├── title.html
│       ├── header.html
│       ├── footer.html
│       └── document.html
├── templates/
│   ├── github/              # GitHub reference template
│   │   ├── bundle.json      # Template configuration
│   │   ├── document.html    # Override fragment
│   │   ├── Info.plist       # Override plist
│   │   ├── github.css       # Main stylesheet
│   │   ├── github-markdown-*.css
│   │   └── LICENSE.txt
│   └── neon_flux/           # Neon Flux custom template
│       ├── bundle.json
│       ├── document.html
│       ├── title.html
│       ├── header.html
│       ├── footer.html
│       ├── Info.plist
│       ├── style.css         # Unified light/dark styles
│       └── LICENSE.txt
├── tests/
│   ├── fixtures/            # Test reference data
│   │   └── GitHub.iatemplate/
│   ├── test_github_template.py
│   └── test_github_download.py
└── dist/templates/          # Generated bundles (after build)
```

## Creating New Templates

1. **Create template directory**:
   ```bash
   mkdir templates/my_template
   ```

2. **Add configuration** (`templates/my_template/bundle.json`):
   ```json
   {
     "name": "My Template",
     "identifier": "com.example.my-template",
     "description": "My custom template",
     "author": "Your Name",
     "author_url": "https://example.com",
     "version": "1.0.0",
     "bundle_version": "1",
     "development_region": "en",
     "bundle_dir": "My-Template.iatemplate",
     "slug": "my_template",
     "header_height": 90,
     "footer_height": 90,
     "assets": [
       "document.html",
       "title.html",
       "header.html",
       "footer.html",
       "style.css"
     ],
     "skip_fragments": []
   }
   ```

3. **Add CSS files**:
   - `style.css` - Single unified stylesheet with light/dark mode support
   - Use `html.night-mode` selector for dark mode overrides

4. **Override fragments** (optional):
   - Place custom HTML files in template directory
   - Common overrides: `document.html`, `Info.plist`

5. **Build and test**:
   ```bash
   uv run python -m ia_writer_templates.main
   ```

## Development

### Code Quality

```bash
# Format code
uv run ruff format src

# Check for issues
uv run ruff check src

# Fix auto-fixable issues
uv run ruff check src --fix
```

### Testing

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest --cov=ia_writer_templates tests/

# Run only integration tests
uv run pytest -m integration tests/

# Run specific test
uv run pytest tests/test_github_template.py -v
```

The test suite includes:
- Template source validation
- Build process verification
- Exact output comparison with reference templates
- Automatic fixture management (downloads from GitHub if missing)

### Test Fixtures

The `tests/fixtures/` directory contains the official GitHub template for comparison testing. Tests will automatically download it from [iA Writer Templates](https://github.com/iainc/iA-Writer-Templates) if missing.

## Template Configuration

### bundle.json Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name in iA Writer |
| `identifier` | string | Unique bundle identifier (reverse DNS) |
| `description` | string | Template description |
| `author` | string | Template author name |
| `author_url` | string | Author website URL |
| `version` | string | Semantic version (e.g., "1.0.0") |
| `bundle_version` | string | Bundle build number |
| `bundle_dir` | string | Output directory name |
| `slug` | string | Internal identifier |
| `header_height` | integer | Header area height in pixels |
| `footer_height` | integer | Footer area height in pixels |
| `assets` | array | Files to copy to bundle |
| `skip_fragments` | array | Fragments to exclude (e.g., ["title.html"]) |
| `supports_smart_tables` | boolean | Enable smart table support (optional) |
| `supports_math` | boolean | Enable math/LaTeX support (optional) |
| `title_uses_header_footer_height` | boolean | Title page uses header/footer heights (optional) |

### Fragment System

Templates use a layered fragment system:

1. **Base fragments** (`src/fragments/`) - Default HTML structure
2. **Template overrides** (`templates/<name>/`) - Custom versions
3. **Build-time processing** - Variable substitution from bundle.json

Common variables available in fragments:
- `{name}` - Template name
- `{identifier}` - Bundle identifier
- `{description}` - Template description
- `{author}` - Author name
- `{author_url}` - Author URL
- `{version}` - Version string

## Included Templates

### GitHub
Reference implementation matching the official [GitHub template](https://github.com/iainc/iA-Writer-Templates). Used for testing build accuracy.

### Neon Flux
A futuristic dual-mode template featuring:
- Vibrant neon color scheme
- Automatic dark/light mode switching
- Custom title page with gradient effects
- Optimized for technical documentation

## Troubleshooting

### Using Hatch

If you prefer Hatch but encounter errors with `hatch run`, use uv or Python directly:
```bash
# Instead of: hatch run build
uv run python -m ia_writer_templates.main
```

### Missing Dependencies

```bash
# Reinstall with uv
uv sync --extra dev

# Or with pip
pip install -e ".[dev]"
```

### Template Not Showing

1. Verify bundle was generated in `dist/templates/`
2. Check iA Writer → Preferences → Templates
3. Try removing and reinstalling the template

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-template`)
3. Make your changes and test thoroughly
4. Run tests: `uv run pytest tests/`
5. Format code: `uv run ruff format src`
6. Create a pull request

Include:
- Description of changes
- Screenshots of template in iA Writer (if visual changes)
- Test results
- Any new dependencies

## Acknowledgments

- [iA Writer](https://ia.net/writer) for the excellent writing app
- [iA Writer Templates](https://github.com/iainc/iA-Writer-Templates) for reference implementations
- The Python packaging community for excellent tools