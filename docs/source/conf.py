# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

project = "statsuite_lib"
copyright = "2025, Sergio Pena"  # noqa VNE003
author = "Sergio Pena"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    # 'sphinx.ext.intersphinx',
    # 'sphinx.ext.coverage',
    # 'sphinx.ext.viewcode',
    # 'sphinx.ext.githubpages',
    #    'm2r2',
    "sphinx.ext.napoleon",
    "myst_parser",
    "sphinx_toolbox.sidebar_links",
    "sphinx_toolbox.github",
]

templates_path = ["_templates"]
exclude_patterns = []

github_username = "sergiopena"
github_repository = "statsuite-lib"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
