# Contributing to Retail Web Analytics Dashboard

Thank you for your interest in contributing to our retail analytics dashboard! We welcome contributions from the community.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+ (for production setup)
- Git
- pip or conda for package management

### Local Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/retail-web-analytics-dashboard.git
   cd retail-web-analytics-dashboard
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

4. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

5. **Run Database Migrations**
   ```bash
   flask db upgrade
   ```

6. **Run the Application**
   ```bash
   python app_enhanced.py
   # Or for Streamlit: streamlit run app.py
   ```

## Development Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Urgent production fixes

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Making Changes

1. Write your code
2. Add tests for new functionality
3. Ensure all tests pass: `pytest`
4. Run code quality checks:
   ```bash
   black .  # Format code
   flake8 . # Lint code
   mypy .   # Type check
   ```

### Commit Guidelines

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat(api): add JWT authentication endpoint

Implements user login with JWT token generation
and refresh token mechanism.

Closes #5
```

### Pull Request Process

1. **Update Documentation**
   - Update README.md if needed
   - Add docstrings to new functions
   - Update API documentation

2. **Test Coverage**
   - Maintain 80%+ code coverage
   - Add unit and integration tests
   - Run: `pytest --cov=app tests/`

3. **Create Pull Request**
   - Push your branch: `git push origin feature/your-feature-name`
   - Open PR on GitHub
   - Fill out the PR template completely
   - Link related issues

4. **Code Review**
   - Address reviewer comments
   - Keep PR focused and small
   - Squash commits if requested

5. **CI/CD Checks**
   - Ensure all GitHub Actions workflows pass
   - Fix any failing tests or linting issues

## Code Standards

### Python Style Guide

- Follow PEP 8
- Use Black for formatting (line length: 88)
- Use type hints for function signatures
- Write docstrings for all public functions

### Testing Standards

- Write unit tests for business logic
- Write integration tests for API endpoints
- Use pytest fixtures for test setup
- Mock external dependencies

### Documentation

- Update README for user-facing changes
- Add inline comments for complex logic
- Document all API endpoints
- Update changelog

## Project Structure

```
retail-web-analytics-dashboard/
├── app/
│   ├── __init__.py     # Application factory
│   ├── models/         # Database models
│   ├── routes/         # API routes
│   ├── services/       # Business logic
│   └── utils/          # Utility functions
├── tests/
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── docs/               # Documentation
├── migrations/         # Database migrations
└── requirements.txt    # Dependencies
```

## Reporting Issues

### Bug Reports

Include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Screenshots if applicable
- Error messages or logs

### Feature Requests

Include:
- Clear use case
- Proposed implementation (if any)
- Alternative solutions considered
- Potential impact on existing features

## Getting Help

- Check existing [Issues](https://github.com/mr-adonis-jimenez/retail-web-analytics-dashboard/issues)
- Read the [README](README.md)
- Review [Documentation](docs/)
- Ask questions in [Discussions](https://github.com/mr-adonis-jimenez/retail-web-analytics-dashboard/discussions)

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect differing viewpoints

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Publishing private information
- Any unethical or unprofessional conduct

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing! 🎉
