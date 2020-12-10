# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Andrew Klychkov (@Andersson007) <aaklychkov@mail.ru>

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.mysql.plugins.modules.mysql_replication import uses_replica_terminology


class dummy_cursor_class():
    def __init__(self, output, ret_val_type='dict'):
        self.output = output
        self.ret_val_type = ret_val_type

    def execute(self, query):
        pass

    def fetchone(self):
        if self.ret_val_type == 'dict':
            return {'version': self.output}

        elif self.ret_val_type == 'list':
            return [self.output]


@pytest.mark.parametrize(
    'f_output,c_output,c_ret_type',
    [
        (False, '5.5.1-mysql', 'list'),
        (False, '5.7.0-mysql', 'dict'),
        (False, '8.0.0-mysql', 'list'),
        (False, '8.0.11-mysql', 'dict'),
        (False, '8.0.21-mysql', 'list'),
        (False, '10.5.0-mariadb', 'dict'),
        (True, '8.0.22-mysql', 'list'),
        (True, '8.1.2-mysql', 'dict'),
        (True, '9.0.0-mysql', 'list'),
        (True, '10.5.1-mariadb', 'dict'),
        (True, '10.6.0-mariadb', 'dict'),
        (True, '11.5.1-mariadb', 'dict'),
    ]
)
def test_uses_replica_terminology(f_output, c_output, c_ret_type):
    cursor = dummy_cursor_class(c_output, c_ret_type)
    assert uses_replica_terminology(cursor) == f_output
