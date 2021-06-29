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
from ansible.module_utils.six import iteritems


def get_implementation(cursor):
    cursor.execute("SELECT VERSION()")

    if 'mariadb' in cursor.fetchone()[0].lower():
        import ansible_collections.community.mysql.plugins.module_utils.implementations.mariadb.role as impl
    else:
        import ansible_collections.community.mysql.plugins.module_utils.implementations.mysql.role as impl

    return impl


def normalize_users(module, users):
    # Example of transformation:
    # ['user0'] => ['`user0`@`localhost`']
    # ['user0@host0'] => ['`user0`@`host0`']
    normalized_users = []

    for user in users:
        tmp = user.split('@')

        if tmp[0] == '':
            module.fail_json(msg="Member's name cannot be empty")

        if len(tmp) == 1:
            normalized_users.append('`%s`@`localhost`' % tmp[0])

        elif len(tmp) == 2:
            normalized_users.append('`%s`@`%s`' % (tmp[0], tmp[1]))

        else:
            msg = ('Formatting error in member name: "%s". It must be in the '
                   'format "username" or "username@hostname" ' % tmp[0])
            module.fail_json(msg=msg)

    return normalized_users


def normalize_privs(module, privs):
    # TODO move shared code from this function and Role.__set_db_privs() method
    # to a separate function

    # The privs argument is a dict that will be transformed.
    # Example:
    # { '*.*': 'SELECT', 'db0.*': 'UPDATE', 'db1.t0': 'INSERT'} =>
    # { 'global': {'SELECT'}, 'db': {'all': 'UPDATE', 'tables': {'t0': {'INSERT'}}} }
    norm_privs = {
        'global': set(),
        'db': {}
    }

    for scope, priv_str in iteritems(privs):
        privs = priv_str.split(',')
        if scope == '*.*':
            for p in privs:
                norm_privs['global'].add(p)
            continue

        tmp = scope.split('.')
        db = '`%s`' % tmp[0]
        table = tmp[1]

        if db not in norm_privs['db']:
            norm_privs['db'][db] = {}
            norm_privs['db'][db]['all'] = set()
            norm_privs['db'][db]['tables'] = {}

        # When the scope is all the tables,
        # put the privs in the corresponding set
        if table == '*':
            for p in privs:
                p = p.rstrip(',')
                norm_privs['db'][db]['all'].add(p)

            continue

        table = '`%s`' % table
        if table not in norm_privs['db'][db]['tables']:
            norm_privs['db'][db]['tables'][table] = set()

        # When the scope is a table,
        # put the privs in the corresponding table set
        for p in privs:
            p = p.rstrip(',')
            norm_privs['db'][db]['tables'][table].add(p)

    return norm_privs


def get_grant_query(to_whom, privs, glob=False, db=None, table=None):
    query = 'GRANT %s ' % ','.join(privs)

    objs = None
    if glob:
        objs = 'ON *.* '

    elif db:
        if table:
            objs = 'ON %s.%s ' % (db, table)
        else:
            objs = 'ON %s.* ' % db

    query += objs
    query += 'TO %s' % to_whom

    return query


# Roles supported since MySQL 8.0.0 and MariaDB 10.0.5
def server_supports_roles(cursor, impl):
    return impl.supports_roles(cursor)


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

        self.privs = {
            'global': set(),
            'db': {},
        }

        if self.exists:
            self.members = self.__get_members()

            # Fetch and fill up self.global_privs and self.db_privs
            self.get_privs()

            # TODO: remove this debug
            self.module.warn('%s' % self.members)
            self.module.warn('GLOBAL PRIVS: %s' % self.privs['global'])
            self.module.warn('DB PRIVS: %s' % self.privs['db'])

    def __role_exists(self):
        query = ('SELECT count(*) FROM mysql.user '
                 'WHERE user = %s AND host = %s')
        self.cursor.execute(query, (self.name, '%'))
        return self.cursor.fetchone()[0] > 0

    def add(self, users, privs, check_mode=False):
        if check_mode:
            if not self.exists:
                return True
            return False

        self.cursor.execute('CREATE ROLE %s', (self.name,))

        if users:
            self.add_members(users)

        if privs:
            self.grant_privs(privs)

        return True

    def grant_privs(self, privs):
        if privs['global']:
            q1 = get_grant_query(self.full_name, list(privs['global']), glob=True)
            self.module.warn(q1)
            self.cursor.execute(q1)

        if privs['db']:
            for db in privs['db']:
                if privs['db'][db]['all']:
                    q2 = get_grant_query(self.full_name, list(privs['db'][db]['all']), db=db)
                    self.module.warn(q2)
                    self.cursor.execute(q2)

                if privs['db'][db]['tables']:
                    for table in privs['db'][db]['tables']:
                        q3 = get_grant_query(self.full_name, list(privs['db'][db]['tables'][table]),
                                             db=db, table=table)
                        self.module.warn(q3)
                        self.cursor.execute(q3)

        return True

    def drop(self, check_mode=False):
        if not self.exists:
            return False

        if check_mode and self.exists:
            return True

        self.cursor.execute('DROP ROLE %s', (self.name,))
        return True

    def add_members(self, users, check_mode=False):
        if not users:
            return False

        changed = False
        for user in users:
            if user not in self.members:
                if check_mode:
                    return True

                self.cursor.execute('GRANT %s TO %s' % (self.full_name, user))
                changed = True

        return changed

    def update(self, users, privs, check_mode=False,
               append_members=False, append_privs=False):
        # TODO implement append_members and append_privs.
        # 1) if append_members=False, if don't match,
        # remove membership from all except required and add missed
        # 2) if append_privs=False, if don't match,
        # remove all grants except required and add missed
        changed = False

        if users:
            changed = self.add_members(users, check_mode=check_mode)

        if privs:
            self.module.warn('CURRENT PRIVS: %s' % self.privs)
            self.module.warn('REQUIRED PRIVS: %s' % privs)

            if self.privs != privs:
                if check_mode:
                    return True

                self.grant_privs(privs)
                return True

        return changed

    def get_privs(self):
        """Get role's privileges."""
        res = get_grants(self.cursor, self.name, self.host)

        for line in res:
            self.__extract_grants(line[0])

    def __extract_grants(self, line):
        # Can be:
        # GRANT SELECT, INSERT, UPDATE ON *.* TO `test`@`%`
        # GRANT INSERT ON `mysql`.* TO `test`@`%
        # GRANT INSERT ON `mysql`.`user` TO `test`@`%`
        # GRANT `readers`@`%` TO `test`@`%`
        # ...
        # TODO check cases when several roles granted
        # TODO implement via sets

        # Grant lines have format
        # 'GRANT something [ON something] TO someone'
        tmp = line.split()[1:-2]
        # After we have
        # ['something', 'ON', 'something']
        # where 'ON' and 'something' are optional

        # Say, we have the line argument passed as
        # GRANT `readers`@`%` TO `test`@`%`
        if 'ON' not in tmp:
            # Means that a role is granted.
            # Return the role
            return tmp[0]

        # Say, we have the line argument passed as
        # GRANT SELECT, INSERT, UPDATE ON *.* TO `test`@`%`
        scope = tmp[-1]

        # Before ['SELECT', 'INSERT,', 'UPDATE', 'ON', '*.*']
        tmp = tmp[:-2]
        # After ['SELECT,', 'INSERT,', 'UPDATE']

        # When privs are relevant for all DBs,
        # set self.global_privs
        if scope == '*.*':
            self.__set_global_privs(tmp)
            return

        # When privs are relevant for a particular DB,
        # fill up the self.db_privs dict
        self.__set_db_privs(scope, tmp)

    def __set_global_privs(self, privs):
        for p in privs:
            self.privs['global'].add(p.rstrip(','))

    def __set_db_privs(self, scope, privs):
        # For cases such as 'dbname.*' or 'dbname.tblname'.
        # We have the self.db_privs dict which has two keys
        # 1) 'all' (is a set containing privs for all the tables) and
        # 2) 'tables' (is a dict containing table names which are, in tern, sets.
        tmp = scope.split('.')
        db = tmp[0]
        table = tmp[1]

        if db not in self.privs['db']:
            self.privs['db'][db] = {}
            self.privs['db'][db]['all'] = set()
            self.privs['db'][db]['tables'] = {}

        # When the scope is all the tables,
        # put the privs in the corresponding set
        if table == '*':
            for p in privs:
                p = p.rstrip(',')
                self.privs['db'][db]['all'].add(p)

            return

        if table not in self.privs['db'][db]['tables']:
            self.privs['db'][db]['tables'][table] = set()

        # When the scope is a table,
        # put the privs in the corresponding table set
        for p in privs:
            p = p.rstrip(',')
            self.privs['db'][db]['tables'][table].add(p)

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
                members.add("`%s`@`%s`" % (user, host))

        return members

    def __is_member(self, grants):
        if not grants:
            return False

        for grant in grants:
            if self.full_name in grant[0]:
                return True

        return False

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
    privs = module.params['priv']
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

    if privs and not isinstance(privs, (str, dict)):
        msg = 'priv parameter must be str or dict but %s was passed' % type(privs)
        module.fail_json(msg=msg)

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

    impl = get_implementation(cursor)

    # Check if the server supports roles
    if not server_supports_roles(cursor, impl):
        msg = ('Roles are not supported by the server. '
               'Minimal versions are MySQL 8.0.0 or MariaDB 10.0.5.')
        module.fail_json(msg=msg)

    if members:
        members = normalize_users(module, members)

    if privs:
        privs = normalize_privs(module, privs)

    # Main job starts here
    role = Role(module, cursor, name)

    if state == 'present':
        if not role.exists:
            changed = role.add(members, privs, module.check_mode)

        else:
            changed = role.update(members, privs, module.check_mode)

    elif state == 'absent':
        changed = role.drop(module.check_mode)

    # It's time to exit
    db_conn.close()
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
