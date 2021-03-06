# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andrew Klychkov (@Andersson007) <aaklychkov@mail.ru>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
name: mysql

short_description: Fetch data from MySQL table

description:
  - Fetch data from MySQL table.
  - For complex queries use M(community.mysql.mysql_query) module.

version_added: '1.3.0'

options:
  _terms:
    description:
      - Tables to fetch data from.
      - "You can use colons to pass optional column list, for example, 'mytable:col1,col2'."
    type: str
    required: yes

  limit:
    description:
      - Limits number of selected rows.
    type: int

  db:
    description:
      - Name of database to connect to and fetch data from.
    type: str

seealso:
  - module: community.mysql.mysql_query

author:
  - Andrew Klychkov (@Andersson007)

extends_documentation_fragment:
  - community.mysql.mysql
'''

EXAMPLES = r'''
- name:  Fetch data from test_table of acme database
  ansible.builtin.debug:
    msg: "{{ lookup('community.mysql.mysql', 'test_table', db='acme') }}"

# The output of the command above can look like:
# [{'col1': 1, 'col2': 'first_value'}, {'col1': 2, 'col2': 'second_value'}]

- name:  Fetch data from test_table of acme database, fetch only 1 row
  ansible.builtin.debug:
    msg: "{{ lookup('community.mysql.mysql', 'test_table', limit=1, db='acme') }}"

# The output of the command above can look like:
# [{'col1': 1, 'col2': 'first_value'}]

- name:  Fetch data from col1 column only of test_table in acme database
  ansible.builtin.debug:
    msg: "{{ lookup('community.mysql.mysql', 'test_table:col1', db='acme') }}"

# The output of the command above can look like:
# [{'col1': 1}, {'col1': 2}]
'''

RETURN = r'''
_raw:
  description: "List of dictionaries 'column name': 'value' representing returned rows."
  returned: always
  type: list
  sample: [{"column1": "value1", "column2", "value1"},{"column1": "value2", "column2": "value2"}]
'''

from ansible_collections.community.mysql.plugins.module_utils.mysql import (
    mysql_connect,
    mysql_driver,
    mysql_driver_fail_msg,
)
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.plugins.lookup import LookupBase


def split_table_and_columns(table):
    tmp = table.split(':')
    table_name = tmp[0]
    columns = tmp[1].strip()
    return table_name, columns


class DummyModule():
    def __init__(self):
        self.params = {}

    def fail_json(self, msg):
        raise AnsibleError(msg)


class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):

        if mysql_driver is None:
            raise AnsibleError(mysql_driver_fail_msg)

        # Get and set arguments
        self.set_options(direct=kwargs)

        # Initialize a dummy module object
        module = DummyModule()

        # General connection options
        db = self.get_option('db')
        login_user = self.get_option('login_user')
        login_password = self.get_option('login_password')
        config_file = self.get_option('config_file')
        connect_timeout = self.get_option('connect_timeout')
        check_hostname = self.get_option('check_hostname')
        ca_cert = self.get_option('ca_cert')
        client_cert = self.get_option('client_cert')
        client_key = self.get_option('client_key')

        # Specific options
        limit = self.get_option('limit')

        # We pass the following parameters to the
        # mysql_connect function through our dummy module object
        # because of mysql_connect function implementation
        module.params['login_host'] = self.get_option('login_host')
        module.params['login_port'] = self.get_option('login_port')
        module.params['login_unix_socket'] = self.get_option('login_unix_socket')

        # Connect to DB
        try:
            cursor, db_connection = mysql_connect(module,
                                                  db=db,
                                                  login_user=login_user,
                                                  login_password=login_password,
                                                  config_file=config_file,
                                                  cursor_class='DictCursor',
                                                  connect_timeout=connect_timeout,
                                                  autocommit=False,
                                                  ssl_ca=ca_cert,
                                                  ssl_cert=client_cert,
                                                  ssl_key=client_key,
                                                  check_hostname=check_hostname)

        except Exception as e:
            raise AnsibleError("Unable to connect to database, "
                               "check login_user and "
                               "login_password are correct. "
                               "Exception message: %s" % to_native(e))

        # Execute query(s)
        result = []
        for table in terms:

            columns = None
            if ':' in table:
                table, columns = split_table_and_columns(table)

            if columns:
                query = "SELECT %s FROM %s" % (columns, table)
            else:
                query = "SELECT * FROM %s" % table

            if limit:
                query += " LIMIT %s" % limit

            try:
                cursor.execute(query)

                # Fetch data from cursor
                try:
                    # TODO: maybe cursor.fetchmany(size)?
                    res = [dict(row) for row in cursor.fetchall()]
                    result += res

                except Exception as e:
                    raise AnsibleError("Cannot fetch rows "
                                       "from cursor: %s" % to_native(e))

            except Exception as e:
                raise AnsibleError(
                    "Cannot execute SQL '%s': "
                    "%s" % (query, to_native(e))
                )

        return result
