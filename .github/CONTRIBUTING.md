# Contributing to the Underwriting Dashboard

Thank you for your interest in contributing to the Underwriting Dashboard project! This document provides guidelines and instructions for contributors.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd underwriting-dashboard
   ```

2. **Set up the environment**
   ```bash
   # Using conda
   conda env create -f environment.yml
   conda activate underwriting-dashboard
   
   # Using pip
   pip install -e ".[dev]"
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Project Structure

```
├── config/              # Configuration files
├── database/            # SQLite database files
├── logs/                # Application logs
├── notebooks/           # Jupyter notebooks for testing
├── prompt/              # Excel reference files
├── src/                 # Source code
│   ├── dashboard/       # Streamlit dashboard components
│   ├── data_processing/ # Excel data extraction utilities
│   ├── database/        # Database management
│   └── file_monitoring/ # File system monitoring
└── tests/               # Test files
```

## Development Workflow

1. **Create a branch for your feature or bugfix**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the code style guidelines (see below)
   - Add tests for new functionality
   - Update documentation as necessary

3. **Run the tests**
   ```bash
   pytest
   ```

4. **Format and lint your code**
   ```bash
   # Format code with black
   black .
   
   # Check imports
   isort .
   
   # Run linter
   flake8
   
   # Check types
   mypy src tests
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Clear description of your changes"
   ```

6. **Submit a pull request**

## Code Style Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guidelines
- Use [Black](https://black.readthedocs.io/en/stable/) for code formatting
- Sort imports with [isort](https://pycqa.github.io/isort/)
- Include type hints for all function parameters and return values
- Write docstrings for all functions, classes, and modules using [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

Example of proper docstring format:

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """Short description of the function.
    
    More detailed description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of the return value
        
    Raises:
        ExceptionType: When and why this exception is raised
    """
    # function implementation
```

## Testing Guidelines

- All new features should include appropriate tests
- Tests should be placed in the `tests/` directory, mirroring the structure of the `src/` directory
- Use pytest for writing and running tests
- Keep tests isolated and independent

## Documentation

- Update the README.md if you add new features or change functionality
- Document any configuration changes in the appropriate files
- Keep API documentation up to date

## Reporting Issues

When reporting issues, please include:

- A clear description of the issue
- Steps to reproduce the problem
- Expected vs. actual behavior
- Version information (Python, libraries, OS)
- Screenshots if applicable

## Pull Request Process

1. Update documentation with details of changes
2. Update the tests to cover your changes
3. Make sure all tests pass
4. Get your code reviewed by at least one other developer
5. Once approved, your PR will be merged

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

Thank you for contributing!