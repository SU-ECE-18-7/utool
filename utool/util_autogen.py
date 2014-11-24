from __future__ import absolute_import, division, print_function
import inspect
from utool import util_inject
print, print_, printDBG, rrr, profile = util_inject.inject(__name__, '[alg]')


class PythonStatement(object):
    """ Thin wrapper around a string representing executable python code """
    def __init__(self, stmt):
        self.stmt = stmt
    def __repr__(self):
        return self.stmt
    def __str__(self):
        return self.stmt


def autofix_codeblock(codeblock, max_line_len=80,
                      aggressive=False,
                      very_aggressive=False,
                      experimental=False):
    r"""
    Uses autopep8 to format a block of code

    Example:
        >>> import utool
        >>> codeblock = utool.codeblock(
            '''
            def func( with , some = 'Problems' ):


             syntax ='Ok'
             but = 'Its very messy'
             if None:
                    # syntax might not be perfect due to being cut off
                    ommiting_this_line_still_works=   True
            ''')
        >>> fixed_codeblock = utool.autofix_codeblock(codeblock)
        >>> print(fixed_codeblock)
    """
    # FIXME idk how to remove the blank line following the function with
    # autopep8. It seems to not be supported by them, but it looks bad.
    import autopep8
    arglist = ['--max-line-length', '80']
    if aggressive:
        arglist.extend(['-a'])
    if very_aggressive:
        arglist.extend(['-a', '-a'])
    if experimental:
        arglist.extend(['--experimental'])
    arglist.extend([''])
    autopep8_options = autopep8.parse_args(arglist)
    fixed_codeblock = autopep8.fix_code(codeblock, options=autopep8_options)
    return fixed_codeblock


def auto_docstr(modname, funcname, verbose=True):
    """
    Args:
        modname (str):
        funcname (str):

    Returns:
        docstr

    Example:
        >>> import utool
        >>> utool.util_autogen.rrr()
        >>> #docstr = utool.auto_docstr('ibeis.model.hots.smk.smk_index', 'compute_negentropy_names')
        >>> modname = 'utool.util_autogen'
        >>> funcname = 'auto_docstr'
        >>> docstr = utool.util_autogen.auto_docstr(modname, funcname)
        >>> print(docstr)
    """
    import utool
    docstr = 'error'
    if isinstance(modname, str):
        module = __import__(modname)
        import imp
        imp.reload(module)
        #try:
        #    func = getattr(module, funcname)
        #    docstr = make_default_docstr(func)
        #    return docstr
        #except Exception as ex1:
        #docstr = 'error ' + str(ex1)
        #if utool.VERBOSE:
        #    print('make_default_docstr is falling back')
        #print(ex)
        #print('modname = '  + modname)
        #print('funcname = ' + funcname)
        try:
            # FIXME: PYTHON 3
            execstr = utool.codeblock(
                '''
                import {modname}
                import imp
                imp.reload({modname})
                import utool
                imp.reload(utool.util_autogen)
                imp.reload(utool.util_inspect)
                docstr = utool.util_autogen.make_default_docstr({modname}.{funcname})
                '''
            ).format(**locals())
            exec(execstr)
            #return 'BARFOOO' +  docstr
            return docstr
            #print(execstr)
        except Exception as ex2:
            docstr = 'error ' + str(ex2)
            if verbose:
                import utool
                #utool.printex(ex1, 'ex1')
                utool.printex(ex2, 'ex2', tb=True)
            error_str = utool.formatex(ex2, 'ex2', tb=True)
            return error_str
            #return docstr + '\n' + execstr
    else:
        docstr = 'error'
    return docstr


def print_auto_docstr(modname, funcname):
    """
    python -c "import utool; utool.print_auto_docstr('ibeis.model.hots.smk.smk_index', 'compute_negentropy_names')"
    python -c "import utool;
    utool.print_auto_docstr('ibeis.model.hots.smk.smk_index', 'compute_negentropy_names')"
    """
    print(auto_docstr(modname, funcname))


# <INVIDIAL DOCSTR COMPONENTS>

def make_args_docstr(argname_list, argtype_list, argdesc_list):
    r"""
    make_args_docstr

    Args:
        argname_list (list): names
        argtype_list (list): types
        argdesc_list (list): descriptions

    Returns:
        str: arg_docstr

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_autogen import *  # NOQA
        >>> argname_list = ['argname_list', 'argtype_list', 'argdesc_list']
        >>> argtype_list = ['list', 'list', 'list']
        >>> argdesc_list = ['names', 'types', 'descriptions']
        >>> arg_docstr = make_args_docstr(argname_list, argtype_list, argdesc_list)
        >>> result = str(arg_docstr)
        >>> print(result)
        argname_list (list): names
        argtype_list (list): types
        argdesc_list (list): descriptions

    """
    import utool as ut
    argdoc_list = [arg + ' (%s): %s' % (_type, desc)
                   for arg, _type, desc in zip(argname_list, argtype_list, argdesc_list)]
    # align?
    argdoc_aligned_list = ut.align_lines(argdoc_list, character='(')
    arg_docstr = '\n'.join(argdoc_aligned_list)
    return arg_docstr


def make_returns_or_yeilds_docstr(return_type, return_name):
    return_doctr = return_type + ': '
    if return_name is not None:
        return_doctr += return_name
    return return_doctr


def make_example_docstr(func, argname_list, defaults, return_type, return_name):
    import utool as ut
    examplecode_lines = []
    top_import = 'from {modname} import *  # NOQA'.format(modname=func.__module__)
    import_lines = [top_import]

    # TODO: Externally register these
    default_argval_map = {
        'ibs':      'ibeis.opendb(\'testdb1\')',
        'aid_list': 'ibs.get_valid_aids()',
    }
    import_depends_map = {
        'ibs':      'import ibeis',
    }

    def find_arg_defaultval(argname, val):
        if val == '?':
            if argname in default_argval_map:
                val = ut.PythonStatement(default_argval_map[argname])
                if argname in import_depends_map:
                    import_lines.append(import_depends_map[argname])
        return (argname, val)

    # Default example values
    defaults_ = [] if defaults is None else defaults
    default_vals = ['?'] * (len(argname_list) - len(defaults_)) + list(defaults_)
    arg_val_iter = zip(argname_list, default_vals)
    argdef_lines = ['%s = %r' % find_arg_defaultval(argname, val) for argname, val in arg_val_iter]
    import_lines = ut.unique_ordered(import_lines)

    examplecode_lines.append('# DISABLE_DOCTEST')
    examplecode_lines.extend(import_lines)
    examplecode_lines.extend(argdef_lines)
    # Default example result assignment
    result_assign = ''
    result_print = None
    if 'return_name' in vars():
        if return_type is not None:
            if return_name is None:
                return_name = 'result'
            result_assign = return_name + ' = '
            result_print = 'print(result)'  # + return_name + ')'
    # Default example call
    example_call = func.func_name + '(' + ', '.join(argname_list) + ')'
    examplecode_lines.append(result_assign + example_call)
    if result_print is not None:
        if return_name != 'result':
            examplecode_lines.append('result = str(' + return_name + ')')
        examplecode_lines.append(result_print)
    examplecode = '\n'.join(examplecode_lines)
    return examplecode

# </INVIDIAL DOCSTR COMPONENTS>


def make_docstr_block(header, block):
    import utool as ut
    indented_block = '\n' + ut.indent(block)
    return ''.join([header, ':', indented_block])


def make_default_docstr(func):
    """
    Tries to make a sensible default docstr so the user
    can fill things in without typing too much

    # TODO: Interleave old documentation with new documentation

    Args:
        func (function): live python function

    Returns:
        tuple: (argname, val)

    Example:
        >>> # ENABLE_DOCTEST
        >>> from utool.util_autogen import *  # NOQA
        >>> import utool as ut
        >>> func = ut.make_default_docstr
        >>> func = ut.make_args_docstr
        >>> default_docstr = make_default_docstr(func)
        >>> result = str(default_docstr)
        >>> print(result)

    """
    import utool as ut
    current_doc = inspect.getdoc(func)
    needs_surround = current_doc is None or len(current_doc) == 0
    argspec = inspect.getargspec(func)
    (argname_list, varargs, varkw, defaults) = argspec

    # See util_inspect
    argtype_list, argdesc_list = ut.infer_arg_types_and_descriptions(argname_list, defaults)

    docstr_parts = []

    # Move source down to base indentation, but remember original indentation
    sourcecode = inspect.getsource(func)
    num_indent = ut.get_indentation(sourcecode)
    sourcecode = ut.unindent(sourcecode)

    # Header part
    header_block = func.func_name
    docstr_parts.append(header_block)

    # Args part
    if len(argname_list) > 0:
        argheader = 'Args'
        arg_docstr = make_args_docstr(argname_list, argtype_list, argdesc_list)
        argsblock = make_docstr_block(argheader, arg_docstr)
        docstr_parts.append(argsblock)

    # Return / Yeild part
    if sourcecode is not None:
        return_type, return_name, return_header = ut.parse_return_type(sourcecode)
        if return_header is not None:
            return_doctr = make_returns_or_yeilds_docstr(return_type, return_name)
            returnblock = make_docstr_block(return_header, return_doctr)
            docstr_parts.append(returnblock)

    # Example part
    if sourcecode is not None:
        # try to generate a simple and unit testable example
        exampleheader = 'Example'
        examplecode = make_example_docstr(func, argname_list, defaults, return_type, return_name)
        examplecode_ = ut.indent(examplecode, '>>> ')
        exampleblock = make_docstr_block(exampleheader, examplecode_)
        docstr_parts.append(exampleblock)

    # DEBUG part (in case something goes wrong)
    DEBUG_DOC = False
    if DEBUG_DOC:
        debugheader = 'Debug'
        debugblock = ut.codeblock(
            '''
            num_indent = {num_indent}
            '''
        ).format(num_indent=num_indent)
        debugblock = make_docstr_block(debugheader, debugblock)
        docstr_parts.append(debugblock)

    # Enclosure / Indentation Parts
    if needs_surround:
        docstr_parts = ['"""'] + ['\n\n'.join(docstr_parts)] + ['"""']
        default_docstr = '\n'.join(docstr_parts)
    else:
        default_docstr = '\n\n'.join(docstr_parts)

    docstr_indent = ' ' * (num_indent + 4)
    default_docstr = ut.indent(default_docstr, docstr_indent)
    return default_docstr


if __name__ == '__main__':
    """
    CommandLine:
        python ibeis/control/template_generator.py --tbls annotations --Tflags getters native

        python -c "import utool, utool.util_autogen; utool.doctest_funcs(utool.util_autogen, allexamples=True)"
        python -c "import utool, utool.util_autogen; utool.doctest_funcs(utool.util_autogen)"
        python utool/util_autogen.py
        python utool/util_autogen.py --allexamples
        python utool/util_autogen.py --allexamples --noface --nosrc
    """
    import multiprocessing
    multiprocessing.freeze_support()  # for win32
    import utool as ut  # NOQA
    ut.doctest_funcs()
