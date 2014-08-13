# flake8: noqa
from __future__ import absolute_import, division, print_function

import sys

dynamic = not '--nodyn' in sys.argv

from . import cyth_helpers
from . import cyth_importer
from .cyth_importer import import_cyth_execstr, import_cyth_dict
from .cyth_script import translate, translate_all
from .cyth_decorators import register

'''
Cyth:
* Create Cyth, to cythonize the code, make it faster
    annotate variable names with types in a scoped comment
    then type the variable names
 * Cythonize spatial verification and other parts of vtool
 * Cythonize matching_functions

Cyth Technical Description:

Overview - cyth works by parsing a .py file for comments specified in comments:
"""
<--CYTH>
cyth code
<--/CYTH>
"""

it deterines scope using the indentation. In multiples of 4.
If any module (__name__ + '.py') has at least one CYTH tag in, then a pyx file named (__name__ + '_cython.pyx') file will be generated.
Global CYTH tags will be simply copied into the pyx file.
CYTH tags in functions will also be copied and pasted, but a cython version of the function will be generated (at first as a strict copy, but we may be able to add improvements later).

CYTH will have a module

import cythe

@cythe.cythonize(return_type=None, dtype_list=[])
def python_func(*args, **kwargs):
    ...

@cythe.cythonize():
class SomeClass(object):
    def __init__(self):
    ...

This will simply grab the code object and parse out the same info.


# this will do magic
# Apply at the end of the module
exec(cythe.exec_module_definitions())

The _cython.pyx file will be autogenerated. This file will be converted into .c file and
compiled unless the user defers this step to the setup.py file.
'''
