========================================
Community MySQL Collection Release Notes
========================================

.. contents:: Topics

This changelog describes changes after version 2.0.0.

v3.0.0
======

Release Summary
---------------

This is the major release of the ``community.mysql`` collection.
This changelog contains all breaking changes to the modules in this collection
that have been added after the release of ``community.mysql`` 2.3.2.

Breaking Changes / Porting Guide
--------------------------------

- mysql_replication - remove ``Is_Slave`` and ``Is_Master`` return values (were replaced with ``Is_Primary`` and ``Is_Replica`` (https://github.com/ansible-collections    /community.mysql/issues/145).
- mysql_replication - remove the mode options values containing ``master``/``slave`` and the master_use_gtid option ``slave_pos`` (were replaced with corresponding ``primary``/``replica`` values) (https://github.com/ansible-collections/community.mysql/issues/145).
- mysql_user - remove support for the `REQUIRESSL` special privilege as it has ben superseded by the `tls_requires` option (https://github.com/ansible-collections/community.mysql/discussions/121).
- mysql_user - validate privileges using database engine directly (https://github.com/ansible-collections/community.mysql/issues/234 https://github.com/ansible-collections/community.mysql/pull/243). Do not validate privileges in this module anymore.
