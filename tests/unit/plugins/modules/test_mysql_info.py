# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from ansible_collections.community.mysql.plugins.modules.mysql_info import MySQL_Info


@pytest.mark.parametrize(
    'suffix,cursor_output,server_implementation,server_version,user_implementation',
    [
        ('mysql', '5.5.1-mysql', 'mysql', '5.5.1', 'mysql'),
        ('log', '5.7.31-log', 'mysql', '5.7.31', 'mysql'),
        ('mariadb', '10.5.0-mariadb', 'mariadb', '10.5.0', 'mariadb'),
        ('', '8.0.22', 'mysql', '8.0.22', 'mysql'),
    ]
)
def test_get_info_suffix(suffix, cursor_output, server_implementation, server_version, user_implementation):
    def __cursor_return_value(input_parameter):
        if input_parameter == "SHOW GLOBAL VARIABLES":
            cursor.fetchall.return_value = [{"Variable_name": "version", "Value": cursor_output}]
        else:
            cursor.fetchall.return_value = MagicMock()

    cursor = MagicMock()
    cursor.execute.side_effect = __cursor_return_value

    info = MySQL_Info(MagicMock(), cursor, server_implementation, server_version, user_implementation)

    assert info.get_info([], [], False)['version']['suffix'] == suffix
