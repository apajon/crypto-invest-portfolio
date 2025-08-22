# crypto-invest-portfolio

[![Release](https://img.shields.io/github/v/release/apajon/crypto-invest-portfolio)](https://img.shields.io/github/v/release/apajon/crypto-invest-portfolio)
[![Build status](https://img.shields.io/github/actions/workflow/status/apajon/crypto-invest-portfolio/main.yml?branch=main)](https://github.com/apajon/crypto-invest-portfolio/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/apajon/crypto-invest-portfolio/branch/main/graph/badge.svg)](https://codecov.io/gh/apajon/crypto-invest-portfolio)
[![Commit activity](https://img.shields.io/github/commit-activity/m/apajon/crypto-invest-portfolio)](https://img.shields.io/github/commit-activity/m/apajon/crypto-invest-portfolio)
[![License](https://img.shields.io/github/license/apajon/crypto-invest-portfolio)](https://img.shields.io/github/license/apajon/crypto-invest-portfolio)

This is a repository python project of a crypto investment portfolio.

- **Github repository**: <https://github.com/apajon/crypto-invest-portfolio/>
- **Documentation** <https://apajon.github.io/crypto-invest-portfolio/>

## Getting started with your project

### 1. Create a New Repository

First, create a repository on GitHub with the same name as this project, and then run the following commands:

```bash
git init -b main
git add .
git commit -m "init commit"
git remote add origin git@github.com:apajon/crypto-invest-portfolio.git
git push -u origin main
```

### 2. Set Up Your Development Environment

Then, install the environment and the pre-commit hooks with

```bash
make install
```

This will also generate your `poetry.lock` file

### 3. Run the pre-commit hooks

Initially, the CI/CD pipeline might be failing due to formatting issues. To resolve those run:

```bash
poetry run pre-commit run -a
```

### 4. Commit the changes

Lastly, commit the changes made by the two steps above to your repository.

```bash
git add .
git commit -m 'Fix formatting issues'
git push origin main
```

You are now ready to start development on your project!
The CI/CD pipeline will be triggered when you open a pull request, merge to main, or when you create a new release.

To finalize the set-up for publishing to PyPI, see [here](https://apajon.github.io/cookiecutter-python-poetry-template/features/publishing/#set-up-for-pypi).
For activating the automatic documentation with MkDocs, see [here](https://apajon.github.io/cookiecutter-python-poetry-template/features/mkdocs/#enabling-the-documentation-on-github).
To enable the code coverage reports, see [here](https://apajon.github.io/cookiecutter-python-poetry-template/features/codecov/).

## Development Commands

This project uses Poetry for dependency management and includes several useful development commands:

### Installing Dependencies

```bash
# Install project dependencies
poetry install

# Add a new dependency
poetry add <package-name>

# Add a development dependency
poetry add --group dev <package-name>
```

### Code Quality and Testing

```bash
# Run all quality checks
make check

# Run tests
make test

# Run pre-commit hooks
poetry run pre-commit run --all-files
```

### Code Formatting

This project uses Black for code formatting:

```bash
# Format code with Black
poetry run black .

# Check formatting without making changes
poetry run black --check .
```

### Version Management

This project uses tbump for automated version management:

```bash
# Bump version to 1.2.3 (automatically commits and tags)
poetry run tbump 1.2.3
./scripts/bump.sh patch           # bump patch
./scripts/bump.sh minor --push     # bump minor + push

# Dry run to see what would happen
poetry run tbump --dry-run 1.2.3
./scripts/bump.sh major --dry-run  # dry-run d’un bump major

# Simple version bump with Poetry (no commit/tag)
poetry version patch|minor|major
```

### Custom Scripts

Example custom scripts are available in the `scripts/` directory. To enable them in pre-commit:

1. Edit `.pre-commit-config.yaml`
2. Uncomment the local hooks section
3. Run `poetry run pre-commit install`

### VSCode Integration

This project includes VSCode settings for:
- Black formatting on save
- Ruff linting
- pytest test discovery
- Python interpreter configuration

## Development Tools and Environment

This template includes several powerful development tools to enhance your workflow:

### Dependency Management with deptry
[deptry](https://github.com/fpgmaas/deptry) is included to check for unused and missing dependencies:

```bash
# Check for unused dependencies
poetry run deptry .

# Check with custom configuration
poetry run deptry . --config pyproject.toml
```

Configure deptry in your `pyproject.toml`:
```toml
[tool.deptry]
skip_obsolete = false
skip_missing = false
skip_transitive = false
skip_misplaced_dev = false
ignore_missing = []
ignore_obsolete = []
ignore_transitive = []
ignore_misplaced_dev = []
```

### Documentation with MkDocs
This project uses [MkDocs](https://www.mkdocs.org/) with Material theme for documentation:

```bash
# Serve documentation locally
poetry run mkdocs serve

# Build documentation
poetry run mkdocs build

# Deploy to GitHub Pages
poetry run mkdocs gh-deploy
```

Documentation structure:
- `docs/` - Documentation source files
- `mkdocs.yml` - MkDocs configuration
- Automatically generates API docs from docstrings
- Material theme with search, navigation, and dark mode

### Testing with tox

[tox](https://tox.readthedocs.io/) provides testing across multiple Python versions:

```bash
# Run tests on all Python versions
poetry run tox

# Run tests on specific Python version
poetry run tox -e py312

# Run with coverage
poetry run tox -e py312 -- --cov
```

The `tox.ini` configuration:
- Tests on Python 3.12 and 3.13
- Uses Poetry for dependency management
- Runs pytest with coverage
- Includes type checking with mypy/ty
- Integrates with GitHub Actions for CI

### Development Container (devcontainer)
The project includes a development container configuration for consistent development environments:

**Features:**
- Pre-configured Python 3.12 environment
- Poetry pre-installed and configured
- All development dependencies included
- VSCode extensions for Python development
- Git configuration and pre-commit hooks

**Usage:**
1. Open in GitHub Codespaces, or
2. Use VSCode "Reopen in Container" command, or
3. Use the Dev Containers extension

**Configuration files:**
- `.devcontainer/devcontainer.json` - Container configuration
- `.devcontainer/Dockerfile` - Custom container setup (if needed)

The devcontainer automatically:
- Installs Poetry and dependencies
- Sets up pre-commit hooks
- Configures Python interpreter
- Installs recommended VSCode extensions

### Docker Support
The included `Dockerfile` provides a production-ready container:

```bash
# Build the Docker image
docker build -t crypto-invest-portfolio .

# Run the container
docker run crypto-invest-portfolio

# Run with volume mount for development
docker run -v $(pwd):/app crypto-invest-portfolio
```

**Dockerfile features:**
- Based on Python 3.12 slim image
- Poetry for dependency management
- Multi-stage build for optimization
- Non-root user for security
- Optimized for production deployment

**Build optimization:**
- Dependencies installed before code copy
- Poetry cache excluded from final image
- Only production dependencies in final stage

## Releasing a new version



---

Repository initiated with [apajon/cookiecutter-python-poetry-template](https://github.com/apajon/cookiecutter-python-poetry-template).
