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

  admin:
    description:
      - Supported by B(MariaDB).
      - Name of the admin user of the role (the I(login_user), by default).
    type: str

  priv:
    description:
      - "MySQL privileges string in the format: C(db.table:priv1,priv2)."
      - "Multiple privileges can be specified by separating each one using
        a forward slash: C(db.table:priv/db.table:priv)."
      - The format is based on MySQL C(GRANT) statement.
      - Database and table names can be quoted, MySQL-style.
      - If column privileges are used, the C(priv1,priv2) part must be
        exactly as returned by a C(SHOW GRANT) statement. If not followed,
        the module will always report changes. It includes grouping columns
        by permission (C(SELECT(col1,col2)) instead of C(SELECT(col1),SELECT(col2))).
      - Can be passed as a dictionary (see the examples).
      - Supports GRANTs for procedures and functions (see the examples).
    type: raw

  append_privs:
    description:
      - Append the privileges defined by I(priv) to the existing ones
        for this role instead of overwriting them.
    type: bool
    default: no

  members:
    description:
      - List of members of the role.
    type: list
    elements: str

  append_members:
    description:
      - Add members defined by I(members) to the existing ones
        for this role instead of overwriting them.
      - Mutually exclusive with I(detach_members).
    type: bool
    default: no

  detach_members:
    description:
      - Detaches members defined by I(members) from the role instead of overwriting them.
      - Mutually exclusive with I(append_members).
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
#
# You can also use the string format like in mysql_user module, for example
# mydb.*:INSERT,UPDATE/anotherdb.*:SELECT/yetanotherdb.*:ALL

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

# Pay attention that the admin cannot be changed later
# and will be ignored if a role currently exists
- name: Create the role readers with alice as its admin
  community.mysql.mysql_role:
    state: present
    name: readers
    admin: alice
'''

RETURN = '''#'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.mysql.plugins.module_utils.mysql import (
    mysql_connect,
    mysql_driver,
    mysql_driver_fail_msg,
    mysql_common_argument_spec
)
from ansible_collections.community.mysql.plugins.module_utils.user import (
    convert_priv_dict_to_str,
    get_impl,
    get_mode,
    user_mod,
    privileges_grant,
    privileges_unpack,
)
from ansible.module_utils._text import to_native
from ansible.module_utils.six import iteritems


def get_implementation(cursor):
    cursor.execute("SELECT VERSION()")

    if 'mariadb' in cursor.fetchone()[0].lower():
        import ansible_collections.community.mysql.plugins.module_utils.implementations.mariadb.role as role_impl
    else:
        import ansible_collections.community.mysql.plugins.module_utils.implementations.mysql.role as role_impl

    return role_impl


def normalize_users(module, users):
    # Example of transformation:
    # ['user0'] => [('user0', 'localhost')]
    # ['user0@host0'] => [('user0', 'host0')]
    normalized_users = []

    for user in users:
        tmp = user.split('@')

        if tmp[0] == '':
            module.fail_json(msg="Member's name cannot be empty")

        if len(tmp) == 1:
            normalized_users.append((tmp[0], 'localhost'))

        elif len(tmp) == 2:
            normalized_users.append((tmp[0], tmp[1]))

        else:
            msg = ('Formatting error in member name: "%s". It must be in the '
                   'format "username" or "username@hostname" ' % tmp[0])
            module.fail_json(msg=msg)

    return normalized_users


# Roles supported since MySQL 8.0.0 and MariaDB 10.0.5
def server_supports_roles(cursor, role_impl):
    return role_impl.supports_roles(cursor)


def get_users(cursor):
    cursor.execute('SELECT User, Host FROM mysql.user')
    return cursor.fetchall()


def get_grants(cursor, user, host):
    cursor.execute('SHOW GRANTS FOR %s@%s', (user, host))
    return cursor.fetchall()


class Role():
    def __init__(self, module, cursor, name):
        self.module = module
        self.cursor = cursor
        self.name = name
        self.host = '%'
        self.full_name = '`%s`@`%s`' % (self.name, self.host)

        self.exists = self.__role_exists()
        self.members = set()

        if self.exists:
            self.members = self.__get_members()

            # TODO: remove this debug
            self.module.warn('%s' % self.members)

    def __role_exists(self):
        query = ('SELECT count(*) FROM mysql.user '
                 'WHERE user = %s AND host = %s')
        self.cursor.execute(query, (self.name, '%'))
        return self.cursor.fetchone()[0] > 0

    def add(self, users, privs, check_mode=False, admin=False):
        if check_mode:
            if not self.exists:
                return True
            return False

        if not admin:
            self.cursor.execute('CREATE ROLE %s', (self.name,))
        else:
            query = 'CREATE ROLE %s WITH ADMIN %s@%s'
            admin_user = admin[0]
            admin_host = admin[1]
            self.cursor.execute(query, (self.name, admin_user, admin_host))

        if users:
            self.add_members(users)

        if privs:
            for db_table, priv in iteritems(privs):
                privileges_grant(self.cursor, self.name, self.host,
                                 db_table, priv, tls_requires=None)

        return True

    def drop(self, check_mode=False):
        if not self.exists:
            return False

        if check_mode and self.exists:
            return True

        self.cursor.execute('DROP ROLE %s', (self.name,))
        return True

    def add_members(self, users, check_mode=False, append_members=False):
        if not users:
            return False

        changed = False
        for user in users:
            if user not in self.members:
                if check_mode:
                    return True

                self.cursor.execute('GRANT %s@%s TO %s@%s', (self.name, self.host, user[0], user[1]))
                changed = True

        if append_members:
            return changed

        for user in self.members:
            if user not in users:
                if check_mode:
                    return True

                self.cursor.execute('REVOKE %s@%s FROM %s@%s', (self.name, self.host, user[0], user[1]))
                changed = True

        return changed

    def remove_members(self, users, check_mode=False):
        if not users:
            return False

        changed = False
        for user in users:
            if user in self.members:
                if check_mode:
                    return True

                self.cursor.execute('REVOKE %s@%s FROM %s@%s', (self.name, self.host, user[0], user[1]))
                changed = True

        return changed

    def update(self, users, privs, check_mode=False,
               append_privs=False, append_members=False,
               detach_members=False, admin=False):
        changed = False

        if users:
            if detach_members:
                changed = self.remove_members(users, check_mode=check_mode)

            else:
                changed = self.add_members(users, check_mode=check_mode,
                                           append_members=append_members)

        if privs:
            changed, msg = user_mod(self.cursor, self.name, self.host,
                                    None, None, None, None, None, None,
                                    privs, append_privs, None,
                                    self.module, role=True)

        # TODO Implement changing when ALTER ROLE statement to
        # change role's admin gets supported
        if admin:
            admin_user = admin[0]
            admin_host = admin[1]
            current_admin = self.get_admin()

            # current_admin is a tuple (user, host)
            if (admin_user, admin_host) != current_admin:
                msg = ('The "admin" option value and the current '
                       'roles admin (%s@%s) don not match. Ignored. '
                       'To change the admin, you need to drop and create the '
                       'role again.' % (current_admin[0], current_admin[1]))
                self.module.warn(msg)

        return changed

    def __get_members(self):
        all_users = get_users(self.cursor)

        members = set()

        for user, host in all_users:
            # Don't handle itself
            if user == self.name and host == self.host:
                continue

            grants = get_grants(self.cursor, user, host)

            if self.__is_member(grants):
                members.add((user, host))

        return members

    def __is_member(self, grants):
        if not grants:
            return False

        for grant in grants:
            if self.full_name in grant[0]:
                return True

        return False

    def get_admin(self):
        query = ("SELECT User, Host FROM mysql.roles_mapping "
                 "WHERE Role = %s and Admin_option = 'Y'")

        self.cursor.execute(query, (self.name,))
        return self.cursor.fetchone()


def main():
    argument_spec = mysql_common_argument_spec()
    argument_spec.update(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        admin=dict(type='str'),
        priv=dict(type='raw'),
        append_privs=dict(type='bool', default=False),
        members=dict(type='list', elements='str'),
        append_members=dict(type='bool', default=False),
        detach_members=dict(type='bool', default=False),
        check_implicit_admin=dict(type='bool', default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=(
            ('append_members', 'detach_members'),
        ),
    )

    login_user = module.params['login_user']
    login_password = module.params['login_password']
    name = module.params['name']
    state = module.params['state']
    admin = module.params['admin']
    priv = module.params['priv']
    check_implicit_admin = module.params['check_implicit_admin']
    connect_timeout = module.params['connect_timeout']
    config_file = module.params['config_file']
    append_privs = module.params['append_privs']
    members = module.params['members']
    append_members = module.params['append_members']
    detach_members = module.params['detach_members']
    ssl_cert = module.params['client_cert']
    ssl_key = module.params['client_key']
    ssl_ca = module.params['ca_cert']
    check_hostname = module.params['check_hostname']
    db = ''

    if priv and not isinstance(priv, (str, dict)):
        msg = ('The "priv" parameter must be str or dict '
               'but %s was passed' % type(priv))
        module.fail_json(msg=msg)

    if priv and isinstance(priv, dict):
        priv = convert_priv_dict_to_str(priv)

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
            cursor, db_conn = mysql_connect(module, login_user, login_password,
                                            config_file, ssl_cert, ssl_key,
                                            ssl_ca, db, connect_timeout=connect_timeout,
                                            check_hostname=check_hostname)

    except Exception as e:
        module.fail_json(msg='unable to connect to database, '
                             'check login_user and login_password '
                             'are correct or %s has the credentials. '
                             'Exception message: %s' % (config_file, to_native(e)))

    # Set defaults
    changed = False

    get_impl(cursor)

    if priv is not None:
        try:
            mode = get_mode(cursor)
        except Exception as e:
            module.fail_json(msg=to_native(e))

        try:
            priv = privileges_unpack(priv, mode)
        except Exception as e:
            module.fail_json(msg='Invalid privileges string: %s' % to_native(e))

    role_impl = get_implementation(cursor)

    # Check if the server supports roles
    if not server_supports_roles(cursor, role_impl):
        msg = ('Roles are not supported by the server. '
               'Minimal versions are MySQL 8.0.0 or MariaDB 10.0.5.')
        module.fail_json(msg=msg)

    if admin:
        if not role_impl.is_mariadb():
            module.fail_json(msg='The "admin" option can be used only with MariaDB.')

        admin = normalize_users(module, [admin])[0]

    if members:
        members = normalize_users(module, members)

    # Main job starts here
    role = Role(module, cursor, name)

    if state == 'present':
        if not role.exists:
            changed = role.add(members, priv, module.check_mode, admin)

        else:
            changed = role.update(members, priv, module.check_mode, append_privs,
                                  append_members, detach_members, admin)

    elif state == 'absent':
        changed = role.drop(module.check_mode)

    # Exit
    db_conn.close()
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
