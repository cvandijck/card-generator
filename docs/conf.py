# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import datetime
import os
import sys
from pathlib import Path

import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('..'))
import card_generator

full_version = card_generator.__version__
doc_path = Path(__file__).parent.resolve()
logo_path = str(doc_path / 'images' / 'logo.png')
icon_path = str(doc_path / 'images' / 'icon.ico')

# -- Project information -----------------------------------------------------

project = 'card-generator'
author = 'Christophe Van Dijck'
copyright_str = '2025 - {}, {}'.format(datetime.date.today().year, author)

# The short X.Y version.
version = full_version.split('+')[0]
# The full version, including alpha/beta/rc tags.
release = full_version

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinxcontrib.apidoc',
    # 'sphinx.ext.autodoc',
    # 'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'myst_parser',
    'jupyter_sphinx',
    'nbsphinx',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'depr', 'artwork', 'demos', 'tutorials']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}

myst_enable_extensions = [
    'amsmath',
    'colon_fence',
    'deflist',
    'dollarmath',
    'fieldlist',
    'html_admonition',
    'html_image',
    'replacements',
    'smartquotes',
    'strikethrough',
    'substitution',
    'tasklist',
]

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#
add_module_names = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# autosummary options
# autosummary_generate = False  # Make _autosummary files and include them

# Napoleon options
napoleon_numpy_docstring = False  # Force consistency, leave only Google
napoleon_use_rtype = False  # More legible
napoleon_include_init_with_doc = False
napoleon_preprocess_types = True

# apidoc options
apidoc_module_dir = '../card-generator'
apidoc_output_dir = 'api/_generated'
apidoc_excluded_paths = ['data']
apidoc_separate_modules = True

# automodule options
autoclass_content = 'both'

# autodoc options
# autodoc_typehints = 'both'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'prev_next_buttons_location': 'bottom',
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': True,
}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#
html_logo = logo_path
html_favicon = icon_path

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []
