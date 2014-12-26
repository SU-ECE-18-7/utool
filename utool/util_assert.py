from __future__ import absolute_import, division, print_function
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    # TODO remove numpy
    pass
from utool import util_iter
from utool import util_alg
from utool import util_inject
print, print_, printDBG, rrr, profile = util_inject.inject(__name__, '[assert]')
from utool import util_arg


def assert_all_not_None(list_, list_name='some_list', key_list=[]):
    if util_arg.NO_ASSERTS:
        return
    try:
        for count, item in enumerate(list_):
            #if any([item is None for count, item in enumerate(list_)]):
            assert item is not None, 'a list element is None'
    except AssertionError as ex:
        from utool.util_dbg import printex
        msg = (list_name + '[%d] = %r') % (count, item)
        printex(ex, msg, key_list=key_list, N=1)
        raise ex


def assert_unflat_level(unflat_list, level=1, basetype=None):
    if util_arg.NO_ASSERTS:
        return
    num_checked = 0
    for item in unflat_list:
        if level == 1:
            for x in item:
                num_checked += 1
                assert not isinstance(x, (tuple, list)), \
                    'list is at an unexpected unflat level, x=%r' % (x,)
                if basetype is not None:
                    assert isinstance(x, basetype), \
                        'x=%r, type(x)=%r is not basetype=%r' % (x, type(x), basetype)
        else:
            assert_unflat_level(item, level - 1)
    #print('checked %r' % num_checked)
    #assert num_checked > 0, 'num_checked=%r' % num_checked


def assert_scalar_list(list_):
    if util_arg.NO_ASSERTS:
        return
    for count, item in enumerate(list_):
        assert not util_iter.isiterable(item), 'count=%r, item=%r is iterable!' % (count, item)


def assert_same_len(list1, list2, additional_msg=''):
    if util_arg.NO_ASSERTS:
        return
    assert len(list1) == len(list2), (
        'unequal lens. len(list1)=%r, len(list2)=%r%s' % (
            len(list1), len(list2), additional_msg))


def assert_lists_eq(list1, list2, failmsg='', verbose=False):
    if util_arg.NO_ASSERTS:
        return
    msg = ''
    if len(list1) != len(list2):
        msg += ('LENGTHS ARE UNEQUAL: len(list1)=%r, len(list2)=%r\n' % (len(list1), len(list2)))

    difflist = []
    for count, (item1, item2) in enumerate(zip(list1, list2)):
        if item1 != item2:
            difflist.append('count=%r, item1=%r, item2=%r' % (count, item1, item2))

    nTotal = max(len(list1), len(list2))

    if verbose or len(difflist) < 10:
        msg += '\n'.join(difflist)
    else:
        if len(difflist) > 0:
            msg += 'There are %d/%d different ordered items\n' % (len(difflist), nTotal)

    if len(msg) > 0:

        num_intersect = len(set(list1).intersection(set(list2)))
        msg = failmsg + '\n' + msg + 'There are %r/%d intersecting unordered items' % (num_intersect, nTotal)
        raise AssertionError(msg)


def assert_inbounds(num, low, high, msg=''):
    r"""
    Args:
        num (scalar):
        low (scalar):
        high (scalar):
        msg (str):
    """
    if util_arg.NO_ASSERTS:
        return
    if not util_alg.inbounds(num, low, high):
        msg_ = 'num=%r is out of bounds=(%r, %r)' % (num, low, high)
        raise AssertionError(msg_ + '\n' + msg)


def assert_almost_eq(arr_test, arr_target, thresh=1E-11):
    r"""
    Args:
        arr_test (ndarray or list):
        arr_target (ndarray or list):
        thresh (scalar or ndarray or list):
    """
    if util_arg.NO_ASSERTS:
        return
    import utool as ut
    arr1 = np.array(arr_test)
    arr2 = np.array(arr_target)
    passed, error = ut.almost_eq(arr1, arr2, thresh, ret_error=True)
    if not np.all(passed):
        failed_xs = np.where(np.logical_not(passed))
        failed_error = error.take(failed_xs)
        failed_arr_test = arr1.take(failed_xs)
        failed_arr_target = arr2.take(failed_xs)

        msg_list = [
            'FAILED ASSERT ALMOST EQUAL',
            '  * failed_xs = %r' % (failed_xs,),
            '  * failed_error = %r' % (failed_error,),
            '  * failed_arr_test   = %r' % (failed_arr_test,),
            '  * failed_arr_target = %r' % (failed_arr_target,),
        ]
        msg = '\n'.join(msg_list)
        raise AssertionError(msg)