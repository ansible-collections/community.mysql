# MySQL collection for Ansible
[![Plugins CI](https://github.com/ansible-collections/community.mysql/workflows/Plugins%20CI/badge.svg?event=push)](https://github.com/ansible-collections/community.mysql/actions?query=workflow%3A"Plugins+CI") [![Roles CI](https://github.com/ansible-collections/community.mysql/workflows/Roles%20CI/badge.svg?event=push)](https://github.com/ansible-collections/community.mysql/actions?query=workflow%3A"Roles+CI") [![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/community.mysql)](https://codecov.io/gh/ansible-collections/community.mysql) [![Discuss on Matrix at #mysql:ansible.com](https://img.shields.io/matrix/mysql:ansible.com.svg?server_fqdn=ansible-accounts.ems.host&label=Discuss%20on%20Matrix%20at%20%23mysql:ansible.com&logo=matrix)](https://matrix.to/#/#mysql:ansible.com)

This collection is a part of the Ansible package.

## Code of Conduct

We follow the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html) in all our interactions within this project.

If you encounter abusive behavior violating the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html), please refer to the [policy violations](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html#policy-violations) section of the Code of Conduct for information on how to raise a complaint.

## Contributing

The content of this collection is made by [people](https://github.com/ansible-collections/community.mysql/blob/main/CONTRIBUTORS) just like you, a community of individuals collaborating on making the world better through developing automation software.

We are actively accepting new contributors.

Any kind of contribution is very welcome.

You don't know how to start? Refer to our [contribution guide](https://github.com/ansible-collections/community.mysql/blob/main/CONTRIBUTING.md)!

## Collection maintenance

The current maintainers (contributors with `write` or higher access) are listed in the [MAINTAINERS](https://github.com/ansible-collections/community.mysql/blob/main/MAINTAINERS) file. If you have questions or need help, feel free to mention them in the proposals.

To learn how to maintain / become a maintainer of this collection, refer to the [Maintainer guidelines](https://github.com/ansible-collections/community.mysql/blob/main/MAINTAINING.md).

It is necessary for maintainers of this collection to be subscribed to:

* The collection itself (the `Watch` button -> `All Activity` in the upper right corner of the repository's homepage).
* The "Changes Impacting Collection Contributors and Maintainers" [issue](https://github.com/ansible-collections/overview/issues/45).

They also should be subscribed to Ansible's [The Bullhorn newsletter](https://docs.ansible.com/ansible/devel/community/communication.html#the-bullhorn).

## Communication

We announce releases and important changes through Ansible's [The Bullhorn newsletter](https://eepurl.com/gZmiEP). Be sure you are subscribed.

Join us on Matrix in the `#mysql:ansible.com` [room](https://matrix.to/#/#mysql:ansible.com), the `#users:ansible.com` [room](https://matrix.to/#/#users:ansible.com) (general use questions and support), `#ansible-community:ansible.com` [room](https://matrix.to/#/#community:ansible.com) (community and collection development questions), and other Matrix rooms or corresponding bridged Libera.Chat channels. See the [Ansible Communication Guide](https://docs.ansible.com/ansible/devel/community/communication.html) for details.

We take part in the global quarterly [Ansible Contributor Summit](https://github.com/ansible/community/wiki/Contributor-Summit) virtually or in-person. Track [The Bullhorn newsletter](https://eepurl.com/gZmiEP) and join us.

For more information about communication, refer to the [Ansible Communication guide](https://docs.ansible.com/ansible/devel/community/communication.html).

## Governance

The process of decision making in this collection is based on discussing and finding consensus among participants.

Every voice is important and every idea is valuable. If you have something on your mind, create an issue or dedicated discussion and let's discuss it!

## Included content

- **Modules**:
  - [mysql_db](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_db_module.html)
  - [mysql_info](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_info_module.html)
  - [mysql_query](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_query_module.html)
  - [mysql_replication](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_replication_module.html)
  - [mysql_role](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_role_module.html)
  - [mysql_user](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_user_module.html)
  - [mysql_variables](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_variables_module.html)


## Releases Support Timeline

It has been [decided](https://github.com/ansible-collections/community.mysql/discussions/537) to maintain each major release (1.x.y, 2.x.y, ...) for two years after the next major version is released.

Here is the table for the support timeline:

- 1.x.y: released 2020-08-17, EOL
- 2.x.y: released 2021-04-15, supported until 2023-12-01
- 3.x.y: released 2021-12-01, current
- 4.x.y: To be released


## Tested with

### ansible-core

- 2.12
- 2.13
- 2.14
- current development version

### Databases

For MariaDB, only Long Term releases are tested.

- mysql 5.7.40
- mysql 8.0.31
- mariadb:10.3.34 (only collection version <= 3.5.1)
- mariadb:10.4.24 (only collection version >= 3.5.2)
- mariadb:10.5.18 (only collection version >= 3.5.2)
- mariadb:10.6.11 (only collection version >= 3.5.2)
- mariadb:10.11.?? (waiting for release)


### Database connectors

- pymysql 0.7.11 (Only tested with MySQL 5.7)
- pymysql 0.9.3
- pymysql 1.0.2 (only collection version >= 3.6.1)
- mysqlclient 2.0.1
- mysqlclient 2.0.3 (only collection version >= 3.5.2)
- mysqlclient 2.1.1 (only collection version >= 3.5.2)

## External requirements

The MySQL modules rely on a MySQL connector. The list of supported drivers is below:

- [PyMySQL](https://github.com/PyMySQL/PyMySQL)
- [mysqlclient](https://github.com/PyMySQL/mysqlclient)
- Support for other Python MySQL connectors may be added in a future release.

## Using this collection

### Installing the Collection from Ansible Galaxy

Before using the MySQL collection, you need to install it with the Ansible Galaxy CLI:

```bash
ansible-galaxy collection install community.mysql
```

You can also include it in a `requirements.yml` file and install it via `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: community.mysql
```

Note that if you install the collection from Ansible Galaxy, it will not be upgraded automatically if you upgrade the Ansible package. To upgrade the collection to the latest available version, run the following command:

```bash
ansible-galaxy collection install community.mysql --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax:

```bash
ansible-galaxy collection install community.mysql:==2.0.0
```

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Licensing

<!-- Include the appropriate license information here and a pointer to the full licensing details. If the collection contains modules migrated from the ansible/ansible repo, you must use the same license that existed in the ansible/ansible repo. See the GNU license example below. -->

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
