.PHONY: all test bandit safety black flake

# Run all checks
all: black flake test bandit safety

# Run tests with coverage
test:
	poetry run pytest --cov-report term-missing --cov=statsuite_lib --cov-fail-under=95 tests/*

# Run security check with bandit
bandit:
	poetry run bandit -r statsuite_lib

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
	@echo "  bandit           - Run security check with bandit"
	@echo "  safety           - Check dependencies for known security issues"
	@echo "  black            - Format code with black"
	@echo "  flake            - Run linting checks"
