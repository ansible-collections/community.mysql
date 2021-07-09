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

version_added: '2.2.0'

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
      - "You can specify multiple privileges by separating each one using
        a forward slash: C(db.table:priv/db.table:priv)."
      - The format is based on MySQL C(GRANT) statement.
      - Database and table names can be quoted, MySQL-style.
      - If column privileges are used, the C(priv1,priv2) part must be
        exactly as returned by a C(SHOW GRANT) statement. If not followed,
        the module will always report changes. It includes grouping columns
        by permission (C(SELECT(col1,col2)) instead of C(SELECT(col1),SELECT(col2))).
      - Can be passed as a dictionary (see the examples).
      - Supports GRANTs for procedures and functions
        (see the examples for the M(community.mysql.mysql_user) module).
    type: raw

  append_privs:
    description:
      - Append the privileges defined by the I(priv) option to the existing ones
        for this role instead of overwriting them.
    type: bool
    default: no

  members:
    description:
      - List of members of the role.
      - For users, use the format C(username@hostname).
        In other words, always specify the hostname part explicitly.
      - For roles, use the format C(rolename).
      - Mutually exclusive with I(admin).
    type: list
    elements: str

  append_members:
    description:
      - Add members defined by the I(members) option to the existing ones
        for this role instead of overwriting them.
      - Mutually exclusive with the I(detach_members) and I(admin) option.
    type: bool
    default: no

  detach_members:
    description:
      - Detaches members defined by the I(members) option from the role instead of overwriting them.
      - Mutually exclusive with the I(append_members) and I(admin) option.
    type: bool
    default: no

  set_default_role_all:
    description:
      - Is not supported by MariaDB.
      - If C(yes), runs B(SET DEFAULT ROLE ALL TO) each of the I(members) when changed.
      - If you want to avoid this behavior, set this option to C(no) explicitly.
    type: bool
    default: yes

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
  - Pay attention that the module runs C(SET DEFAULT ROLE ALL TO)
    all the I(members) passed by default when the state has changed.
    If you want to avoid this behavior, set I(set_default_role_all) to C(no).
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
# You can also use the string format like in the community.mysql.mysql_user module, for example
# mydb.*:INSERT,UPDATE/anotherdb.*:SELECT/yetanotherdb.*:ALL
#
# For more examples on how to specify privileges, refer to the community.mysql.mysql_user module

# Create a role developers with all database privileges
# and add alice and bob as members.
# The statement 'SET DEFAULT ROLE ALL' to them will be run.
- name: Create role developers, add members
  community.mysql.mysql_role:
    name: developers
    state: present
    priv: '*.*:ALL'
    members:
    - 'alice@%'
    - 'bob@%'

- name: Same as above but do not run SET DEFAULT ROLE ALL TO each member
  community.mysql.mysql_role:
    name: developers
    state: present
    priv: '*.*:ALL'
    members:
    - 'alice@%'
    - 'bob@%'
    set_default_role_all: no

# Assuming that the role developers exists,
# add john to the current members
- name: Add members to an existing role
  community.mysql.mysql_role:
    name: developers
    state: present
    append_members: yes
    members:
    - 'joe@localhost'

# Create role readers with the SELECT privilege
# on all tables in the fiction database
- name: Create role developers, add members
  community.mysql.mysql_role:
    name: readers
    state: present
    priv: 'fiction.*:SELECT'

# Assuming that the role readers exists,
# add the UPDATE privilege to the role on all tables in the fiction database
- name: Create role developers, add members
  community.mysql.mysql_role:
    name: readers
    state: present
    priv: 'fiction.*:UPDATE'
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
    members:
    - 'joe@localhost'
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
# and will be ignored if a role currently exists.
# To change members, you need to run a separate task using the admin
# of the role as the login_user.
- name: On MariaDB, create the role readers with alice as its admin
  community.mysql.mysql_role:
    state: present
    name: readers
    admin: 'alice@%'

- name: Create the role business, add the role marketing to members
  community.mysql.mysql_role:
    state: present
    name: business
    members: marketing
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
    """Get a current server implementation depending on its type.

    Args:
        cursor (cursor): Cursor object of a database Python connector.

    Returns:
        library: Depending on a server type (MySQL or MariaDB).
    """
    cursor.execute("SELECT VERSION()")

    if 'mariadb' in cursor.fetchone()[0].lower():
        import ansible_collections.community.mysql.plugins.module_utils.implementations.mariadb.role as role_impl
    else:
        import ansible_collections.community.mysql.plugins.module_utils.implementations.mysql.role as role_impl

    return role_impl


def normalize_users(module, users, is_mariadb=False):
    """Normalize passed user names.

    Example of transformation:
    ['user0'] => [('user0', '')] / ['user0'] => [('user0', '%')]
    ['user0@host0'] => [('user0', 'host0')]

    Args:
        module (AnsibleModule): Object of the AnsibleModule class.
        cursor (cursor): Cursor object of a database Python connector.
        users (list): List of user names.
        is_mariadb (bool): Flag indicating we are working with MariaDB

    Returns:
        list: List of tuples like [('user0', ''), ('user0', 'host0')].
    """
    normalized_users = []

    for user in users:
        tmp = user.split('@')

        if tmp[0] == '':
            module.fail_json(msg="Member's name cannot be empty")

        if len(tmp) == 1:
            if not is_mariadb:
                normalized_users.append((tmp[0], '%'))
            else:
                normalized_users.append((tmp[0], ''))

        elif len(tmp) == 2:
            normalized_users.append((tmp[0], tmp[1]))

        else:
            msg = ('Formatting error in member name: "%s". It must be in the '
                   'format "username" or "username@hostname" ' % tmp[0])
            module.fail_json(msg=msg)

    return normalized_users


def check_users_in_db(module, users, users_in_db):
    for user in users:
        if user not in users_in_db:
            msg = 'User / role `%s` with host `%s` does not exist' % (user[0], user[1])
            module.fail_json(msg=msg)


def server_supports_roles(cursor, role_impl):
    """Check if a server supports roles.

    Roles supported since MySQL 8.0.0 and MariaDB 10.0.5

    Args:
        cursor (cursor): Cursor object of a database Python connector.
        role_impl (library): A corresponding library depending on a server type (MySQL or MariaDB)
            and version. Refer to the get_implementation function.

    Returns:
        bool: True if the server type supports roles, otherwise returns False
    """
    return role_impl.supports_roles(cursor)


def get_users(cursor):
    """Get users.

    Args:
        cursor (cursor): Cursor object of a database Python connector.

    Returns:
        list: List of tuples (username, hostname).
    """
    cursor.execute('SELECT User, Host FROM mysql.user')
    return cursor.fetchall()


def get_grants(cursor, user, host):
    """Get grants.

    Args:
        cursor (cursor): Cursor object of a database Python connector.
        user (str): User name
        host (str): Host name

    Returns:
        list: List of tuples like [(grant1,), (grant2,), ... ].
    """
    if host:
        cursor.execute('SHOW GRANTS FOR %s@%s', (user, host))
    else:
        cursor.execute('SHOW GRANTS FOR %s', (user,))

    return cursor.fetchall()


class MySQLQueryBuilder():

    def __init__(self, name, host):
        self.name = name
        self.host = host

    def role_exists(self):
        return 'SELECT count(*) FROM mysql.user WHERE user = %s AND host = %s', (self.name, self.host)

    def role_grant(self, user):
        if user[1]:
            return 'GRANT %s@%s TO %s@%s', (self.name, self.host, user[0], user[1])
        else:
            return 'GRANT %s@%s TO %s', (self.name, self.host, user[0])

    def role_revoke(self, user):
        if user[1]:
            return 'REVOKE %s@%s FROM %s@%s', (self.name, self.host, user[0], user[1])
        else:
            return 'REVOKE %s@%s FROM %s', (self.name, self.host, user[0])

    def role_create(self, admin):
        # It is NOT supported by MySQL, so we ignore it
        return 'CREATE ROLE %s', (self.name,)


class MariaDBQueryBuilder():

    def __init__(self, name):
        self.name = name

    def role_exists(self):
        return "SELECT count(*) FROM mysql.user WHERE user = %s AND is_role  = 'Y'", (self.name)

    def role_grant(self, user):
        if user[1]:
            return 'GRANT %s TO %s@%s', (self.name, user[0], user[1])
        else:
            return 'GRANT %s TO %s', (self.name, user[0])

    def role_revoke(self, user):
        if user[1]:
            return 'REVOKE %s FROM %s@%s', (self.name, user[0], user[1])
        else:
            return 'REVOKE %s FROM %s', (self.name, user[0])

    def role_create(self, admin):
        if not admin:
            return 'CREATE ROLE %s', (self.name,)

        if admin[1]:
            return 'CREATE ROLE %s WITH ADMIN %s@%s', (self.name, admin[0], admin[1])
        else:
            return 'CREATE ROLE %s WITH ADMIN %s', (self.name, admin[0])


class MySQLRoleImpl():

    def __init__(self, module, cursor, name, host):
        self.module = module
        self.cursor = cursor
        self.name = name
        self.host = host

    def set_default_role_all(self, user):
        if user[1]:
            self.cursor.execute('SET DEFAULT ROLE ALL TO %s@%s', (user[0], user[1]))
        else:
            self.cursor.execute('SET DEFAULT ROLE ALL TO %s', (user[0],))

    def get_admin(self, admin):
        pass

    def set_admin(self, admin):
        pass

    def get_missed_user_err_msg(self):
        return "Unknown authorization ID"


class MariaDBRoleImpl():

    def __init__(self, module, cursor, name):
        self.module = module
        self.cursor = cursor
        self.name = name

    def set_default_role_all(self, user):
        # "SET DEFAULT ROLE ALL" statement is not supported by MariaDB, ignored.
        pass

    def get_admin(self):
        """Get a current admin of a role.

        Returns:
            tuple: Of the form (username, hostname).
        """
        query = ("SELECT User, Host FROM mysql.roles_mapping "
                 "WHERE Role = %s and Admin_option = 'Y'")

        self.cursor.execute(query, (self.name,))
        return self.cursor.fetchone()

    def set_admin(self, admin):
        admin_user = admin[0]
        admin_host = admin[1]
        current_admin = self.get_admin()

        # current_admin is a tuple (user, host)
        if (admin_user, admin_host) != current_admin:
            # TODO Implement changing when ALTER ROLE statement to
            # change role's admin gets supported
            msg = ('The "admin" option value and the current '
                   'roles admin (%s@%s) don not match. Ignored. '
                   'To change the admin, you need to drop and create the '
                   'role again.' % (current_admin[0], current_admin[1]))
            self.module.warn(msg)

    def get_missed_user_err_msg(self):
        return "Can't find any matching row in the user table"


class Role():
    """Class to work with MySQL role objects.

    Args:
        module (AnsibleModule): Object of the AnsibleModule class.
        cursor (cursor): Cursor object of a database Python connector.
        is_mariadb (bool): Is a server MariaDB?

    Attributes:
        module (AnsibleModule): Object of the AnsibleModule class.
        cursor (cursor): Cursor object of a database Python connector.
        name (str): Role's name.
        is_mariadb (bool): Is a server MariaDB?
        host (str): Role's host.
        full_name (str): Role's full name.
        exists (bool): Indicates if a role exists or not.
        members (set): Set of current role's members.
    """
    def __init__(self, module, cursor, name, is_mariadb):
        self.module = module
        self.cursor = cursor
        self.name = name
        self.is_mariadb = is_mariadb

        if self.is_mariadb:
            self.q_builder = MariaDBQueryBuilder(self.name)
            self.role_impl = MariaDBRoleImpl(self.module, self.cursor, self.name)
            self.full_name = '`%s`' % self.name
            self.host = ''
        else:
            self.host = '%'
            self.q_builder = MySQLQueryBuilder(self.name, self.host)
            self.role_impl = MySQLRoleImpl(self.module, self.cursor, self.name, self.host)
            self.full_name = '`%s`@`%s`' % (self.name, self.host)

        self.exists = self.__role_exists()
        self.members = set()

        if self.exists:
            self.members = self.__get_members()

    def __role_exists(self):
        """Check if a role exists.

        Returns:
            bool: True if the role exists, False if it does not.
        """
        self.cursor.execute(*self.q_builder.role_exists())
        return self.cursor.fetchone()[0] > 0

    def add(self, users, privs, check_mode=False, admin=False,
            set_default_role_all=True):
        """Add a role.

        Args:
            users (list): Role members.
            privs (str): String containing privileges.
            check_mode (bool): If True, just checks and does nothing.
            admin (tuple): Role's admin. Contains (username, hostname).
            set_default_role_all (bool): If True, runs SET DEFAULT ROLE ALL TO each member.

        Returns:
            bool: True if the state has changed, False if has not.
        """
        if check_mode:
            if not self.exists:
                return True
            return False

        self.cursor.execute(*self.q_builder.role_create(admin))

        if users:
            self.add_members(users, set_default_role_all=set_default_role_all)

        if privs:
            for db_table, priv in iteritems(privs):
                privileges_grant(self.cursor, self.name, self.host,
                                 db_table, priv, tls_requires=None,
                                 maria_role=self.is_mariadb)

        return True

    def drop(self, check_mode=False):
        """Drop a role.

        Args:
            check_mode (bool): If True, just checks and does nothing.

        Returns:
            bool: True if the state has changed, False if has not.
        """
        if not self.exists:
            return False

        if check_mode and self.exists:
            return True

        self.cursor.execute('DROP ROLE %s', (self.name,))
        return True

    def add_members(self, users, check_mode=False, append_members=False,
                    set_default_role_all=True):
        """Add users to a role.

        Args:
            users (list): Role members.
            check_mode (bool): If True, just checks and does nothing.
            append_members (bool): If True, adds new members passed through users
                not touching current members.
            set_default_role_all (bool): If True, runs SET DEFAULT ROLE ALL TO each member.

        Returns:
            bool: True if the state has changed, False if has not.
        """
        if not users:
            return False

        changed = False
        for user in users:
            if user not in self.members:
                if check_mode:
                    return True

                self.cursor.execute(*self.q_builder.role_grant(user))

                self.role_impl.set_default_role_all(user)

                changed = True

        if append_members:
            return changed

        for user in self.members:
            if user not in users and user != ('root', 'localhost'):
                if check_mode:
                    return True

                self.cursor.execute(*self.q_builder.role_revoke(user))

                changed = True

        return changed

    def remove_members(self, users, check_mode=False):
        """Remove members from a role.

        Args:
            users (list): Role members.
            check_mode (bool): If True, just checks and does nothing.

        Returns:
            bool: True if the state has changed, False if has not.
        """
        if not users:
            return False

        changed = False
        for user in users:
            if user in self.members:
                if check_mode:
                    return True

                self.cursor.execute(*self.q_builder.role_revoke(user))

                changed = True

        return changed

    def update(self, users, privs, check_mode=False,
               append_privs=False, append_members=False,
               detach_members=False, admin=False,
               set_default_role_all=True):
        """Update a role.

        Update a role if needed.

        Todo: Implement changing of role's admin when ALTER ROLE statement
            to do that gets supported.

        Args:
            users (list): Role members.
            privs (str): String containing privileges.
            check_mode (bool): If True, just checks and does nothing.
            append_privs (bool): If True, adds new privileges passed through privs
                not touching current privileges.
            append_members (bool): If True, adds new members passed through users
                not touching current members.
            detach_members (bool): If True, removes members passed through users from a role.
            admin (tuple): Role's admin. Contains (username, hostname).
            set_default_role_all (bool): If True, runs SET DEFAULT ROLE ALL TO each member.

        Returns:
            bool: True if the state has changed, False if has not.
        """
        changed = False
        members_changed = False

        if users:
            if detach_members:
                members_changed = self.remove_members(users, check_mode=check_mode)

            else:
                members_changed = self.add_members(users, check_mode=check_mode,
                                                   append_members=append_members,
                                                   set_default_role_all=set_default_role_all)

        if privs:
            changed, msg = user_mod(self.cursor, self.name, self.host,
                                    None, None, None, None, None, None,
                                    privs, append_privs, None,
                                    self.module, role=True, maria_role=self.is_mariadb)

        if admin:
            self.role_impl.set_admin(admin)

        changed = changed or members_changed

        return changed

    def __get_members(self):
        """Get current role's members.

        Returns:
            set: Members.
        """
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
        """Check if a user / role is a member of a role.

        To check if a user is a member of a role,
        we parse their grants looking for the role name in them.
        In the following grants, we can see that test@% is a member of readers.
        +---------------------------------------------------+
        | Grants for test@%                                 |
        +---------------------------------------------------+
        | GRANT SELECT, INSERT, UPDATE ON *.* TO `test`@`%` |
        | GRANT ALL PRIVILEGES ON `mysql`.* TO `test`@`%`   |
        | GRANT INSERT ON `mysql`.`user` TO `test`@`%`      |
        | GRANT `readers`@`%` TO `test`@`%`                 |
        +---------------------------------------------------+

        Args:
            grants (list): Grants of a user to parse.

        Returns:
            bool: True if the self.full_name has been found in grants,
                otherwise returns False.
        """
        if not grants:
            return False

        for grant in grants:
            if self.full_name in grant[0]:
                return True

        return False


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
        set_default_role_all=dict(type='bool', default=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=(
            ('append_members', 'detach_members'),
            ('admin', 'members'),
            ('admin', 'append_members'),
            ('admin', 'detach_members'),
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
    set_default_role_all = module.params['set_default_role_all']

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
    is_mariadb = role_impl.is_mariadb()

    # Check if the server supports roles
    if not server_supports_roles(cursor, role_impl):
        msg = ('Roles are not supported by the server. '
               'Minimal versions are MySQL 8.0.0 or MariaDB 10.0.5.')
        module.fail_json(msg=msg)

    users_in_db = set(get_users(cursor))

    if admin:
        if not is_mariadb:
            module.fail_json(msg='The "admin" option can be used only with MariaDB.')

        admin = normalize_users(module, [admin])[0]
        check_users_in_db(module, [admin], users_in_db)

    if members:
        members = normalize_users(module, members, is_mariadb)
        check_users_in_db(module, members, users_in_db)

    # Main job starts here
    role = Role(module, cursor, name, is_mariadb)

    try:
        if state == 'present':
            if not role.exists:
                changed = role.add(members, priv, module.check_mode, admin,
                                   set_default_role_all)

            else:
                changed = role.update(members, priv, module.check_mode, append_privs,
                                      append_members, detach_members, admin,
                                      set_default_role_all)

        elif state == 'absent':
            changed = role.drop(module.check_mode)

    except Exception as e:
        module.fail_json(msg=to_native(e))

    # Exit
    db_conn.close()
    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
