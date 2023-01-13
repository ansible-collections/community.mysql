# Contributing

Refer to the [Ansible Contributing guidelines](https://docs.ansible.com/ansible/devel/community/index.html) to learn how to contribute to this collection.

Refer to the [review checklist](https://docs.ansible.com/ansible/devel/community/collection_contributors/collection_reviewing.html) when triaging issues or reviewing PRs.


## Testing locally

You can use GitHub to run ansible-test either on the community repo or your fork. But sometimes you want to quickly test a single version or a single target. To do that, you can use the Makefile present at the root of this repository.

Actually, the makefile only support Podman. I don't have tested with docker yet.

The Makefile accept the following options:

- ansible: Mandatory version of ansible to install in a venv to run ansible-test.
- docker_container:
    The container image to use to run our tests. Those images Dockerfile are in https://github.com/community.mysql-test-containers and then pushed to quay.io: E.G.:
    `quay.io/mws/community-mysql-test-containers-my57-py38-mysqlclient201-pymysql0711:0.0.1`. Look in the link above for a complete list of available containers. You can also look into `.github/workflows/ansible-test-plugins.yml`
    Unfortunatly you must provide the right container_image yourself. And you still need to provides db_engine_version, python, etc... because ansible-test won't do black magic to try to detect what we expect. Explicit is better than implicit anyway.
    To minimise the amount of images, pymysql 0.7.11 and mysqlclient are shipped together.
- db_engine_version: The name of the container to use for the service containers that will host a primary database and two replicas. Either MYSQL or MariaDB. Use ':' as a separator. Do not use short version, like mysql:8 for instance. Our tests expect a full version to filter tests precisely. For instance: `when: db_version is version ('8.0.22', '>')`.
- connector: The name of the python package of the connector along with its version number. Use '==' as a separator.
- python: The python version to use in the controller.
- target : If omitted, all test targets will run. But you can limit the tests to a single target to speed up your tests.

Examples:

```sh
# Run all targets
make ansible="stable-2.14" db_engine_version="mysql:5.7.40" connector="pymysql==0.7.10" python="3.8" docker_container="my57-py38-mysqlclient201-pymysql0711"

# A single target
make ansible="stable-2.14" db_engine_version="mysql:5.7.40" connector="pymysql==0.7.10" python="3.8" docker_container="my57-py38-mysqlclient201-pymysql0711" target="test_mysql_db"
```


### Run all tests

GitHub Action offer a test matrix that run every combination of Python, MySQL, MariaDB and Connector against each other. To reproduce this, this repo provides a script called *run_all_tests.py*.

Examples:

```sh
python run_all_tests.py
```