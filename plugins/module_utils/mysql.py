# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Jonathan Mainguy <jon@soh.re>, 2015
# Most of this was originally added by Sven Schliesing @muffl0n in the mysql_user.py module
#
# Simplified BSD License (see licenses/simplified_bsd.txt or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import (absolute_import, division, print_function)
from functools import reduce
__metaclass__ = type

import os

from ansible.module_utils.six.moves import configparser
from ansible.module_utils._text import to_native

try:
    import pymysql as mysql_driver
    _mysql_cursor_param = 'cursor'
except ImportError:
    try:
        import MySQLdb as mysql_driver
        import MySQLdb.cursors
        _mysql_cursor_param = 'cursorclass'
    except ImportError:
        mysql_driver = None

mysql_driver_fail_msg = 'The PyMySQL (Python 2.7 and Python 3.X) or MySQL-python (Python 2.X) module is required.'


def parse_from_mysql_config_file(cnf):
    # Default values of comment_prefix is '#' and ';'.
    # '!' added to prevent a parsing error
    # when a config file contains !includedir parameter.
    cp = configparser.ConfigParser(comment_prefixes=('#', ';', '!'))
    cp.read(cnf)
    return cp


def mysql_connect(module, login_user=None, login_password=None, config_file='', ssl_cert=None,
                  ssl_key=None, ssl_ca=None, db=None, cursor_class=None, connect_timeout=30,
                  autocommit=False, config_overrides_defaults=False, check_hostname=None, protocol=None):
    config = {}

    if config_file and os.path.exists(config_file):
        config['read_default_file'] = config_file

        if config_overrides_defaults:
            try:
                cp = parse_from_mysql_config_file(config_file)
            except Exception as e:
                module.fail_json(msg="Failed to parse %s: %s" % (config_file, to_native(e)))

            # Override some common defaults with values from config file if needed
            if cp and cp.has_section('client'):
                try:
                    module.params['login_host'] = cp.get('client', 'host', fallback=module.params['login_host'])
                    module.params['login_port'] = cp.getint('client', 'port', fallback=module.params['login_port'])
                except Exception as e:
                    if "got an unexpected keyword argument 'fallback'" in e.message:
                        module.fail_json(msg='To use config_overrides_defaults, '
                                             'it needs Python 3.5+ as the default interpreter on a target host')

    if ssl_ca is not None or ssl_key is not None or ssl_cert is not None or check_hostname is not None:
        config['ssl'] = {}

    if module.params['login_unix_socket']:
        config['unix_socket'] = module.params['login_unix_socket']
    else:
        config['host'] = module.params['login_host']
        config['port'] = module.params['login_port']

    # If login_user or login_password are given, they should override the
    # config file
    if login_user is not None:
        config['user'] = login_user
    if login_password is not None:
        config['passwd'] = login_password
    if ssl_cert is not None:
        config['ssl']['cert'] = ssl_cert
    if ssl_key is not None:
        config['ssl']['key'] = ssl_key
    if ssl_ca is not None:
        config['ssl']['ca'] = ssl_ca
    if db is not None:
        config['db'] = db
    if protocol is not None and protocol.upper() in ('TCP', 'SOCKET', 'PIPE', 'MEMORY'):
        config['protocol'] = protocol.upper()
    if connect_timeout is not None:
        config['connect_timeout'] = connect_timeout
    if check_hostname is not None:
        if mysql_driver.__name__ == "pymysql":
            version_tuple = (n for n in mysql_driver.__version__.split('.') if n != 'None')
            if reduce(lambda x, y: int(x) * 100 + int(y), version_tuple) >= 711:
                config['ssl']['check_hostname'] = check_hostname
            else:
                module.fail_json(msg='To use check_hostname, pymysql >= 0.7.11 is required on the target host')

    if _mysql_cursor_param == 'cursor':
        # In case of PyMySQL driver:
        db_connection = mysql_driver.connect(autocommit=autocommit, **config)
    else:
        # In case of MySQLdb driver
        db_connection = mysql_driver.connect(**config)
        if autocommit:
            db_connection.autocommit(True)

    # Monkey patch the Connection class to close the connection when garbage collected
    def _conn_patch(conn_self):
        conn_self.close()
    db_connection.__class__.__del__ = _conn_patch
    # Patched

    if cursor_class == 'DictCursor':
        return db_connection.cursor(**{_mysql_cursor_param: mysql_driver.cursors.DictCursor}), db_connection
    else:
        return db_connection.cursor(), db_connection


def mysql_common_argument_spec():
    return dict(
        login_user=dict(type='str', default=None),
        login_password=dict(type='str', no_log=True),
        login_host=dict(type='str', default='localhost'),
        login_port=dict(type='int', default=3306),
        login_unix_socket=dict(type='str'),
        config_file=dict(type='path', default='~/.my.cnf'),
        connect_timeout=dict(type='int', default=30),
        client_cert=dict(type='path', aliases=['ssl_cert']),
        client_key=dict(type='path', aliases=['ssl_key']),
        ca_cert=dict(type='path', aliases=['ssl_ca']),
        check_hostname=dict(type='bool', default=None),
        protocol=dict(type='str', default=None),
    )


def get_server_version(cursor):
    """Returns a string representation of the server version."""
    cursor.execute("SELECT VERSION() AS version")
    result = cursor.fetchone()

    if isinstance(result, dict):
        version_str = result['version']
    else:
        version_str = result[0]

    return version_str
