import os
import sys
import mock
sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------

project = 'Velkoz Web Scraping Library'
copyright = '2020, Matthew Teelucksingh'
author = 'Matthew Teelucksingh'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Mocking The installation of various C-dependent python packages:
MOCK_MODULES = ['sqlalchemy', 'sqlalchemy.orm', 'BeautifulSoup', 'pandas', 'sqlalchemy.ext.declarative']
for mod_name in MOCK_MODULES:
sys.modules[mod_name] = mock.Mock()

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon"
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# Indicating the name of the index.rst file for readthedocs:
master_doc = 'index'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
