# MySQL collection for Ansible
[![Plugins CI](https://github.com/ansible-collections/community.mysql/workflows/Plugins%20CI/badge.svg?event=push)](https://github.com/ansible-collections/community.mysql/actions?query=workflow%3A"Plugins+CI") [![Roles CI](https://github.com/ansible-collections/community.mysql/workflows/Roles%20CI/badge.svg?event=push)](https://github.com/ansible-collections/community.mysql/actions?query=workflow%3A"Roles+CI") [![Codecov](https://img.shields.io/codecov/c/github/ansible-collections/community.mysql)](https://codecov.io/gh/ansible-collections/community.mysql)

## Code of Conduct

We follow the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html) in all our interactions within this project.

If you encounter abusive behavior violating the [Ansible Code of Conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html), please refer to the [policy violations](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html#policy-violations) section of the Code of Conduct for information on how to raise a complaint.

## Contributing

The content of this collection is made by [people](CONTRIBUTORS) like you.

Any kind of contribution is very welcome.

You don't know how to start? Refer to our [contribution guide](CONTRIBUTING.md)!

The current maintainers are listed in the [MAINTAINERS](MAINTAINERS) file. Don't hesitate to reach them out mentioning in the proposals.

## Governance

The process of decision making in this collection is based on discussing and finding consensus among participants.

Every voice is important and every idea is valuable. If you have something on your mind, create an issue or dedicated discussion and let's discuss it!

## Included content

- **Modules**:
  - [mysql_db](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_db_module.html)
  - [mysql_info](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_info_module.html)
  - [mysql_query](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_query_module.html)
  - [mysql_replication](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_replication_module.html)
  - [mysql_user](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_user_module.html)
  - [mysql_variables](https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_variables_module.html)

## Tested with Ansible

- 2.9
- 2.10
- 2.11
- devel

## External requirements

The MySQL modules rely on a MySQL connector. The list of supported drivers is below:

- [PyMySQL](https://github.com/PyMySQL/PyMySQL)
- [MySQLdb](https://github.com/PyMySQL/mysqlclient-python)
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

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Licensing

<!-- Include the appropriate license information here and a pointer to the full licensing details. If the collection contains modules migrated from the ansible/ansible repo, you must use the same license that existed in the ansible/ansible repo. See the GNU license example below. -->

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
