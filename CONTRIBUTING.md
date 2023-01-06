# Contributing

Refer to the [Ansible Contributing guidelines](https://docs.ansible.com/ansible/devel/community/index.html) to learn how to contribute to this collection.

Refer to the [review checklist](https://docs.ansible.com/ansible/devel/community/collection_contributors/collection_reviewing.html) when triaging issues or reviewing PRs.


## Testing locally

You can use GitHub to run ansible-test either on the community repo or your fork. But sometimes you want to quickly test a single version or a single target. To do that, you can use the Makefile present at the root of this repository.

Actually, the makefile only support Podman. I don't have tested with docker yet.

The Makefile accept the following options:

- db_engin_version: The name of the container to use. Either MYSQL or MariaDB. Use ':' as a separator. Do not use short version, like mysql:8 for instance. Our tests expect a full version to filter tests based on released version. For instance: when: db_version is version ('8.0.22', '>').
- connector: The name of the python package of the connector along with its version number. Use '==' as a separator.
- python: The python version to use in the controller.
- target : TODO, I need to implement a Makefile optional variable for that.

Exemples:

```sh
make db_engine_version="mysql:5.7.40" connector="pymysql==0.7.10" python="3.8"
```
