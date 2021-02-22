# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.mysql.plugins.modules.mysql_user import (
    has_select_on_col,
    sort_column_order,
    supports_identified_by_password,
)
from ..utils import dummy_cursor_class


@pytest.mark.parametrize(
    'function_return,cursor_output,cursor_ret_type',
    [
        (True, '5.5.1-mysql', 'list'),
        (True, '5.7.0-mysql', 'dict'),
        (True, '10.5.0-mariadb', 'dict'),
        (True, '10.5.1-mariadb', 'dict'),
        (True, '10.6.0-mariadb', 'dict'),
        (True, '11.5.1-mariadb', 'dict'),
        (False, '8.0.22-mysql', 'list'),
        (False, '8.1.2-mysql', 'dict'),
        (False, '9.0.0-mysql', 'list'),
        (False, '8.0.0-mysql', 'list'),
        (False, '8.0.11-mysql', 'dict'),
        (False, '8.0.21-mysql', 'list'),
    ]
)
def test_supports_identified_by_password(function_return, cursor_output, cursor_ret_type):
    """
    Tests whether 'CREATE USER %s@%s IDENTIFIED BY PASSWORD %s' is supported,
    which is currently supported by everything besides MySQL >= 8.0.
    """
    cursor = dummy_cursor_class(cursor_output, cursor_ret_type)
    assert supports_identified_by_password(cursor) == function_return


@pytest.mark.parametrize(
    'input_list,output_tuple',
    [
        (['INSERT', 'DELETE'], (None, None)),
        (['SELECT', 'UPDATE'], (None, None)),
        (['INSERT', 'UPDATE', 'INSERT', 'DELETE'], (None, None)),
        (['just', 'a', 'random', 'text'], (None, None)),
        (['SELECT (A, B, C)'], (0, 0)),
        (['UPDATE', 'SELECT (A, B, C)'], (1, 1)),
        (['INSERT', 'SELECT (', 'A)'], (1, 2)),
        (['SELECT (', 'A', 'B)', 'UPDATE'], (0, 2)),
        (['INSERT', 'SELECT (', 'A', 'B)', 'UPDATE'], (1, 3)),
    ]
)
def test_has_select_on_col(input_list, output_tuple):
    """Tests has_select_on_col function."""
    assert has_select_on_col(input_list) == output_tuple


@pytest.mark.parametrize(
    'input_,output',
    [
        ('SELECT (A)', 'SELECT (A)'),
        ('SELECT (`A`)', 'SELECT (A)'),
        ('SELECT (A, B)', 'SELECT (A, B)'),
        ('SELECT (`A`, `B`)', 'SELECT (A, B)'),
        ('SELECT (B, A)', 'SELECT (A, B)'),
        ('SELECT (`B`, `A`)', 'SELECT (A, B)'),
        ('SELECT (`B`, `A`, C)', 'SELECT (A, B, C)'),
    ]
)
def test_sort_column_order(input_, output):
    """Tests sort_column_order function."""
    assert sort_column_order(input_) == output
