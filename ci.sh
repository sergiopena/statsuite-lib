#!/usr/bin/env bash

poetry run pytest --cov-report term-missing --cov=statsuite_lib --cov-fail-under=95 tests/*
bandit -r statsuite_lib 
safety scan --key eda22bc0-4998-4f81-a0ac-b2ad943d172e
black .
flake8 .
