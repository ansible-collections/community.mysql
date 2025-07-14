# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Andrew Klychkov (@Andersson007) <andrew.a.klychkov@gmail.com>

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.mysql.plugins.module_utils.implementations.mariadb.replication import uses_replica_terminology
from ..utils import dummy_cursor_class


class MockCursor:
    def __init__(self, status="ONLINE"):
        self.status = status
        self.executed_queries = []

    def execute(self, query):
        self.executed_queries.append(query)

    def fetchone(self):
        if "group_replication_status" in self.executed_queries[-1]:
            return ["group_replication_status", self.status]
        return None


@pytest.mark.parametrize(
    'f_output,c_output,c_ret_type',
    [
        (False, '10.5.0-mariadb', 'dict'),
        (True, '10.5.1-mariadb', 'dict'),
        (True, '10.6.0-mariadb', 'dict'),
        (True, '11.5.1-mariadb', 'dict'),
    ]
)
def test_uses_replica_terminology(f_output, c_output, c_ret_type):
    cursor = dummy_cursor_class(c_output, c_ret_type)
    assert uses_replica_terminology(cursor) == f_output


@pytest.mark.parametrize(
    'user,password,expected_query',
    [
        (None, None, "START GROUP_REPLICATION"),
        ("repl_user", None, "START GROUP_REPLICATION USER='repl_user'"),
        (None, "repl_pass", "START GROUP_REPLICATION"),
        ("repl_user", "repl_pass", "START GROUP_REPLICATION USER='repl_user' PASSWORD='repl_pass'"),
    ]
)
def test_start_group_replication(user, password, expected_query):
    """Test startgroupreplication function with different parameters."""
    from ansible_collections.community.mysql.plugins.modules.mysql_replication import startgroupreplication

    cursor = MockCursor()
    module = type('obj', (object,), {
        'fail_json': lambda msg: None,
    })

    chm = []
    if user:
        chm.append(" USER='%s'" % user)
    if password:
        chm.append(" PASSWORD='%s'" % password)

    result = startgroupreplication(module, cursor, chm, False)

    assert result is True
    assert cursor.executed_queries[0] == expected_query
    assert cursor.executed_queries[1] == "SHOW STATUS LIKE 'group_replication_status';"


def test_stop_group_replication():
    """Test stopgroupreplication function."""
    from ansible_collections.community.mysql.plugins.modules.mysql_replication import stopgroupreplication

    cursor = MockCursor()
    module = type('obj', (object,), {
        'fail_json': lambda msg: None,
    })

    result = stopgroupreplication(module, cursor, False)

    assert result is True
    assert cursor.executed_queries[0] == "STOP GROUP_REPLICATION"
    assert cursor.executed_queries[1] == "SHOW STATUS LIKE 'group_replication_status';"


def test_start_group_replication_fail():
    """Test startgroupreplication function with failure."""
    from ansible_collections.community.mysql.plugins.modules.mysql_replication import startgroupreplication
    import pymysql

    cursor = MockCursor(status="ERROR")
    module = type('obj', (object,), {
        'fail_json': lambda msg: None,
    })

    # Mock the Warning exception
    pymysql.Warning = Exception

    result = startgroupreplication(module, cursor, [], True)

    assert result is False


def test_stop_group_replication_fail():
    """Test stopgroupreplication function with failure."""
    from ansible_collections.community.mysql.plugins.modules.mysql_replication import stopgroupreplication
    import pymysql

    cursor = MockCursor(status="ERROR")
    module = type('obj', (object,), {
        'fail_json': lambda msg: None,
    })

    # Mock the Warning exception
    pymysql.Warning = Exception

    result = stopgroupreplication(module, cursor, True)

    assert result is False
