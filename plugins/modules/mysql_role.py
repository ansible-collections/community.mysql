#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Andrew Klychkov <aaklychkov@mail.ru>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: mysql_role

short_description: Adds, removes, or updates a MySQL role

description:
   - Adds, removes, or updates a MySQL role.
   - Roles are supported since MySQL 8.0.0 and MariaDB 10.0.5.

options:
  name:
    description:
      - Name of the role to add or remove.
    type: str
    required: true

  priv:
    description:
      - "MySQL privileges dict of elements in the format C('db.table': 'priv1,priv2')."
      - Refer to the examples section.
    type: dict

  append_privs:
    description:
      - Append the privileges defined by I(priv) to the existing ones
        for this role instead of overwriting them.
    type: bool
    default: no

  detach_privs:
    description:
      - Detach the privileges defined by I(priv) from the existing ones
        for this role instead of overwriting existing ones.
    type: bool
    default: no

  members:
    description:
      - List of members of the role.
    type: list
    elements: str

  add_members:
    description:
      - Add members defined by I(members) to the existing ones
        for this role instead of overwriting them.
    type: bool
    default: no

  remove_members:
    description:
      - Remove members defined by I(members) from the existing ones
        for this role instead of overwriting them.
    type: bool
    default: no

  state:
    description:
      - If C(present) and the role does not exist, creates the role.
      - If C(present) and the role exists, does nothing or updates its attributes.
      - If C(absent), removes the role.
    type: str
    choices: [ absent, present ]
    default: present

  check_implicit_admin:
    description:
      - Check if mysql allows login as root/nopassword before trying supplied credentials.
      - If success, passed I(login_user)/I(login_password) will be ignored.
    type: bool
    default: no

notes:
  - Supports (check_mode).

seealso:
  - module: community.mysql.mysql_user
  - name: MySQL role reference
    description: Complete reference of the MySQL role documentation.
    link: https://dev.mysql.com/doc/refman/8.0/en/create-role.html

author:
  - Andrew Klychkov (@Andersson007)

extends_documentation_fragment:
  - community.mysql.mysql
'''

EXAMPLES = r'''
# Example of a .my.cnf file content for setting a root password
# [client]
# user=root
# password=n<_665{vS43y
#
# Example of a privileges dictionary passed through the priv option
# priv:
#   'mydb.*': 'INSERT,UPDATE'
#   'anotherdb.*': 'SELECT'
#   'yetanotherdb.*': 'ALL'

# Create a role developers with all database privileges
# and add alice and bob as members
- name: Create role developers, add members
  community.mysql.mysql_role:
    name: developers
    state: present
    priv:
      '*.*': 'ALL'
    members:
    - alice
    - bob

# Assuming that the role developers exists,
# add john to the current members
- name: Add members to an existing role
  community.mysql.mysql_role:
    name: developers
    state: present
    append_members: yes
    members:
    - joe

# Create role readers with the SELECT privilege
# on all tables in the fiction database
- name: Create role developers, add members
  community.mysql.mysql_role:
    name: readers
    state: present
    priv:
      'fiction.*': 'SELECT'

# Assuming that the role readers exists,
# add the UPDATE privilege to the role on all tables in the fiction database
- name: Create role developers, add members
  community.mysql.mysql_role:
    name: readers
    state: present
    priv:
      'fiction.*': 'UPDATE'
    append_privs: yes

- name: Create role with the 'SELECT' and 'UPDATE' privileges in db1 and db2
  community.mysql.mysql_role:
    state: present
    name: foo
    priv:
      'db1.*': 'SELECT,UPDATE'
      'db2.*': 'SELECT,UPDATE'

- name: Revoke the 'UPDATE' privilege from the role foo in db1 and db2
  community.mysql.mysql_role:
    state: present
    name: foo
    detach_privs: yes
    priv:
      'db1.*': 'UPDATE'
      'db2.*': 'UPDATE'

- name: Remove joe from readers
  community.mysql.mysql_role:
    state: present
    name: readers
    members: joe
    detach_members: yes

- name: Remove the role readers if exists
  community.mysql.mysql_role:
    state: absent
    name: readers

- name: Example of using login_unix_socket to connect to the server
  community.mysql.mysql_role:
    name: readers
    state: present
    login_unix_socket: /var/run/mysqld/mysqld.sock
'''

RETURN = '''#'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.mysql.plugins.module_utils.mysql import (
    mysql_connect,
    mysql_driver,
    mysql_driver_fail_msg,
    mysql_common_argument_spec
)
from ansible.module_utils._text import to_native


def get_implementation(cursor):
    cursor.execute("SELECT VERSION()")

    if 'mariadb' in cursor.fetchone()[0].lower():
        import ansible_collections.community.mysql.plugins.module_utils.implementations.mariadb.role as impl
    else:
        import ansible_collections.community.mysql.plugins.module_utils.implementations.mysql.role as impl

    return impl


# Roles supported since MySQL 8.0.0 and MariaDB 10.0.5
def server_supports_roles(cursor, impl):
    """Check if the server supports ALTER USER statement or doesn't.

    Args:
        cursor (cursor): DB driver cursor object.

    Returns: True if supports, False otherwise.
    """
    return impl.supports_roles(cursor)


def get_users(cursor):
    cursor.execute('SELECT User, Host FROM mysql.user')
    return cursor.fetchall()


def get_grants(cursor, user, host):
    cursor.execute("SHOW GRANTS FOR %s@%s", (user, host))
    return cursor.fetchall()


class Role():
    def __init__(self, module, cursor, name):
        self.module = module
        self.cursor = cursor
        self.name = name
        self.host = '%s'
        self.full_name = '`%s`@`%s`' % (self.name, self.host)
        self.exists = self.__role_exists()
        self.members = set()
        self.privs = {}

        if self.exists:
            self.members = self.__get_members()
            self.module.warn('%s' % self.members)
        #    self.privs = self.get_privs()

    def __role_exists(self):
        query = ("SELECT count(*) FROM mysql.user "
                 "WHERE user = %s AND host = %s")
        self.cursor.execute(query, (self.name, '%'))
        return self.cursor.fetchone()[0] > 0

    def add(self):
        self.cursor.execute('CREATE ROLE %s', (self.name))

    def update(self):
        return False

    def get_privs(self):
        return {}

    def grant_priv(self):
        pass

    def revoke_priv(self):
        pass

    def __get_members(self):
        all_users = get_users(self.cursor)

        members = set()

        for user, host in all_users:
            # Don't handle itself
            if user == self.name and host == self.host:
                continue

            grants = get_grants(self.cursor, user, host)

            if self.__is_member(grants):
                members.add("%s@`%s`" % (user, host))

        return members

    def __is_member(self, grants):
        if not grants:
            return False

        for grant in grants:
            if self.full_name in grant:
                return True

        return False

    def add_member(self):
        pass

    def revoke_member(self):
        pass


def get_hostnames():
    pass


def main():
    argument_spec = mysql_common_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        priv=dict(type='dict'),
        append_privs=dict(type='bool', default=False),
        detach_privs=dict(type='bool', default=False),
        members=dict(type='list', elements='str'),
        add_members=dict(type='bool', default=False),
        remove_members=dict(type='bool', default=False),
        check_implicit_admin=dict(type='bool', default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    login_user = module.params['login_user']
    login_password = module.params['login_password']
    name = module.params['name']
    state = module.params['state']
    priv = module.params['priv']
    check_implicit_admin = module.params['check_implicit_admin']
    connect_timeout = module.params['connect_timeout']
    config_file = module.params['config_file']
    append_privs = module.params['append_privs']
    detach_privs = module.params['detach_privs']
    members = module.params['members']
    add_members = module.params['add_members']
    remove_members = module.params['remove_members']
    ssl_cert = module.params['client_cert']
    ssl_key = module.params['client_key']
    ssl_ca = module.params['ca_cert']
    check_hostname = module.params['check_hostname']
    db = ''

    if priv and not isinstance(priv, (str, dict)):
        module.fail_json(msg='priv parameter must be str or dict but %s was passed' % type(priv))

    if mysql_driver is None:
        module.fail_json(msg=mysql_driver_fail_msg)

    cursor = None
    try:
        if check_implicit_admin:
            try:
                cursor, db_conn = mysql_connect(module, 'root', '', config_file,
                                                ssl_cert, ssl_key, ssl_ca, db,
                                                connect_timeout=connect_timeout,
                                                check_hostname=check_hostname)
            except Exception:
                pass

        if not cursor:
            cursor, db_conn = mysql_connect(module, login_user, login_password, config_file,
                                            ssl_cert, ssl_key, ssl_ca, db,
                                            connect_timeout=connect_timeout,
                                            check_hostname=check_hostname)

    except Exception as e:
        module.fail_json(msg='unable to connect to database, check login_user and login_password '
                             'are correct or %s has the credentials. '
                             'Exception message: %s' % (config_file, to_native(e)))

    # Set defaults
    changed = False

    impl = get_implementation(cursor)

    # Check if the server supports roles
    if not server_supports_roles(cursor, impl):
        msg = ('Roles are not supported by the server. '
               'Minimal versions are MySQL 8.0.0 or MariaDB 10.0.5.')
        module.fail_json(msg=msg)

    # Main job starts here
    role = Role(module, cursor, name)

    if state == 'present':
        if not role.exists:
            role.add()
            changed = True

        else:
            changed = role.update()

    # It's time to exit
    db_conn.close()
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
