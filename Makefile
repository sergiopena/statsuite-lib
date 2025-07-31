.PHONY: all test security-check dependency-check format lint

# Run all checks
all: test security-check dependency-check format lint

# Run tests with coverage
test:
	poetry run pytest --cov-report term-missing --cov=statsuite_lib --cov-fail-under=95 tests/*

# Run security check with bandit
security-check:
	poetry run bandit -r statsuite_lib

# Run dependency security scan
dependency-check:
	poetry run safety scan

# Format code with black
black:
	poetry run black --check .

# Run linting with flake8
flake:
	poetry run flake8 .

# Show help
help:
	@echo "Available targets:"
	@echo "  all              - Run all checks (test, security, dependencies, format, lint)"
	@echo "  test             - Run tests with coverage"
	@echo "  security         - Run security check with bandit"
	@echo "  dependency       - Check dependencies for known security issues"
	@echo "  black            - Format code with black"
	@echo "  flake            - Run linting checks"
