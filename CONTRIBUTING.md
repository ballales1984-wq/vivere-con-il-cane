# Contributing to Vivere con il Cane

Thank you for considering contributing to our project! Please follow these guidelines to help us maintain a high-quality codebase.

## How to Contribute

### Reporting Issues
- Use the [GitHub Issues](https://github.com/ballales1984-wq/vivere-con-il-cane/issues) tracker.
- Check if the issue has already been reported.
- Include as much detail as possible: steps to reproduce, expected vs actual behavior, screenshots if applicable.
- Label the issue appropriately (bug, enhancement, question, etc.).

### Pull Requests
1. Fork the repository.
2. Create a new branch from `main`: `git checkout -b feature/your-feature-name`.
3. Make your changes.
4. Ensure your code follows the project's style guidelines.
5. Add or update tests as needed.
6. Run the test suite to ensure everything passes.
7. Commit your changes with a clear and descriptive message.
8. Push to your fork: `git push origin feature/your-feature-name`.
9. Open a Pull Request against the `main` branch.

### Code Style
- Follow [PEP 8](https://pep8.org/) for Python code.
- Use meaningful variable and function names.
- Keep functions small and focused.
- Write docstrings for public methods and classes.
- For HTML/CSS, follow standard web conventions and keep indentation consistent.

### Testing
- Write unit tests for new functionality.
- Ensure all existing tests pass before submitting a PR.
- Use the `--debug-mode` flag when running tests to avoid SSL redirect issues in the test environment:
  ```bash
  python manage.py test --debug-mode
  ```

### Documentation
- Update the README.md if your changes affect installation, usage, or configuration.
- Add inline comments for complex logic.
- If you add new settings, document them in the README.

## Development Setup

See the [README.md](README.md) for detailed installation instructions.

### Environment Variables
Copy `.env.example` to `.env` and fill in the required values:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to `True` for development
- `ALLOWED_HOSTS`: List of allowed hosts (e.g., `localhost,127.0.0.1`)

### Running the Server
```bash
python manage.py runserver
```

### Running Tests
```bash
# Run all tests
python manage.py test --debug-mode

# Run specific app tests
python manage.py test blog knowledge marketing --debug-mode

# Run with verbose output
python manage.py test blog -v 2
```

## License
By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for your contribution!