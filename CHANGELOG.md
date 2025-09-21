# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2025-09-21)


### Features

* Initializes project structure ([87fb4a9](https://github.com/cityhunteur/ia-writer-templates/commit/87fb4a9688d37fd0459b2a3f233c2856a58e8bd7))
* removes the pypi publishing step from the release workflow. ([1c4206b](https://github.com/cityhunteur/ia-writer-templates/commit/1c4206b50ebb225082b588310666f8fb0801dcdf))

## [0.1.0] - 2025-09-21

### Features

- **Templates**: Added GitHub reference template for testing build accuracy
- **Templates**: Created Neon Flux template with unified light/dark mode support
  - Vibrant neon color scheme with cyan, mint, and violet accents
  - Automatic mode switching based on iA Writer's View settings
  - Custom title page with gradient effects
  - Optimized for technical documentation
- **Build System**: Python-powered template generator with fragment support
  - Modular design with shared HTML fragments
  - Per-template override capability
  - CSS variable-based theming system
- **Testing**: Integration tests with automatic fixture management
  - Exact output comparison with reference templates
  - GitHub template downloading if missing
- **Documentation**: Comprehensive README with usage instructions

### Build System

- Set up Python project with uv package manager support
- Created template build engine with variable substitution
- Added support for Info.plist generation
- Implemented asset copying with CSS variant support

### Continuous Integration

- Added GitHub Actions workflow for CI/CD
- Configured linting with ruff
- Set up pytest for automated testing
- Added coverage reporting with Codecov
- Implemented Release Please for automated releases
- Configured artifact attachment to GitHub releases

[0.1.0]: https://github.com/cityhunteur/ia-writer-templates/releases/tag/v0.1.0
