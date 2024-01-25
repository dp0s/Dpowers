#
#
# Copyright (c) 2020-2023 DPS, dps@my.mail.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os.path as path
import sys
sys.path.insert(0, path.join(path.realpath('..'),"Dlib"))

import Dpowers, Dhelpers
from Dpowers import keyb
from Dpowers.events.sending import event_sender

# -- Project information -----------------------------------------------------

project = 'Dpowers'
copyright = '2024, dp0s'
author = 'dp0s'
version = Dpowers.__version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', "sphinx.ext.autosummary",
    'sphinx_rtd_theme', 'sphinx.ext.autosectionlabel', 'hoverxref.extension']

# Make sure the target is unique for autosectionlabel extension
autosectionlabel_prefix_document = True
hoverxref_auto_ref = True
hoverxref_domains = ['py']

#napoleon_use_param = True

autodoc_default_options = {'member-order':"bysource", "members":True}
#autoclass_content = "both"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
import sphinx_rtd_theme
html_theme = "sphinx_rtd_theme"
#html_theme = "python_docs_theme"

html_logo = "../Dlib/Dpowers/iconpower/icons/Dicon.png"

html_favicon = "../Dlib/Dpowers/iconpower/icons/Dicon.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


def my_skip_member(app, what, name, obj, skip, options):
    if what == "class":
        if name == "adaptor" and isinstance(obj, Dpowers.Adaptor):
            return True
        if name == "ContainerClass": return True
        if name == "SingleClass" and issubclass(obj,Dpowers.editing.Resource):
            return True


from Dhelpers.sphinx_docs import ExecDirective, CustomTextDirective, ActiveCode,\
    Example_with_Refs, Ref_to_Examples, CreateMemberOrderedDocs
from Dhelpers.adaptor.sphinx_directives import AdaptiveClassDirective, AdaptorDirective

ExecDirective.get_globals(globals())
CustomTextDirective.get_globals(globals())



def setup(app):
    app.connect('autodoc-skip-member', my_skip_member)
    app.add_directive('autodoc_members', CreateMemberOrderedDocs)
    app.add_directive('exec', ExecDirective)
    app.add_directive('activecode', ActiveCode)
    app.add_directive("example", Example_with_Refs)
    app.add_directive("refexamples", Ref_to_Examples)
    app.add_directive("adaptiveclass", AdaptiveClassDirective)
    app.add_directive("adaptor", AdaptorDirective)