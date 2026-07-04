# Contributing

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- pip

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/hr-analytics.git
cd hr-analytics

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Verify setup
pytest tests/ -v
```

## How to Contribute

### Reporting Issues

Before creating an issue, check existing issues to avoid duplicates. When creating a bug report:

- Use a clear, descriptive title
- Include steps to reproduce
- Provide expected vs actual behavior
- Include environment details (Python version, OS)
- Add relevant logs or screenshots

### Suggesting Enhancements

Enhancement suggestions are welcome. Please:

- Check existing issues for similar suggestions
- Explain the use case and expected behavior
- Consider alignment with project scope (see `Business/BRD.md`)

## Development Workflow

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests

### Commit Messages

Follow conventional commits format:

```
type(scope): description
```

Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Formatting changes
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat(etl): add retry logic for Excel file loading
fix(sql): add missing index on DepartmentKey
docs(readme): update installation instructions
test(pipeline): add integration test for full ETL flow
```

## Code Standards

### Python

Automated tools enforce consistency:

- **Black** for code formatting (line length: 100)
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run before committing:

```bash
black ETL/ tests/
isort ETL/ tests/
flake8 ETL/ tests/
mypy ETL/
```

### Python Best Practices

1. **Type hints**: All functions must have type hints
2. **Docstrings**: All functions, classes, and modules need docstrings
3. **Error handling**: Use specific exception types
4. **Logging**: Use structured logging with appropriate levels
5. **Constants**: Use uppercase for constants

### SQL

- Keywords in UPPERCASE
- Comments for complex logic
- 4-space indentation
- Line length: 100 characters max

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=ETL --cov-report=html

# Run specific test file
pytest tests/unit/test_data_cleaning.py -v
```

### Test Requirements

- Minimum coverage: 80%
- New features must include tests
- Bug fixes must include regression tests

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes following code standards
3. Write or update tests as needed
4. Update documentation if applicable
5. Ensure all tests pass and coverage doesn't decrease
6. Submit a pull request

### PR Review Criteria

- Code follows project standards
- Tests are included and passing
- Documentation is updated
- No security vulnerabilities introduced
- Backward compatibility maintained

## Documentation

Update documentation when making changes:

- **README.md**: User-facing changes
- **Business/BRD.md**: Requirement changes
- **Architecture/*.md**: Design changes
- **Code docstrings**: Function signature or behavior changes

## Questions?

- Open an issue for technical questions
- Check existing documentation first
- Review closed issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License (see [LICENSE](LICENSE) file).