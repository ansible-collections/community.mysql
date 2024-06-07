# Maintaining this collection

Refer to the [Maintainer guidelines](https://github.com/ansible/community-docs/blob/main/maintaining.rst).

## Update pymysql connector

1. Clone https://github.com/PyMySQL/PyMySQL
1. Copy `PyMySQL/pymysql` recursivly into `plugins/module_utils/`
1. Update the pymysql version in the readme. The version can be found in `plugins/module_utils/pymysql/__initi__.py`
