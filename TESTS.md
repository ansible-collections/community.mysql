# Tests

This page describe how to run and extend integrations tests.


## Testing locally

You can use GitHub to run ansible-test either on the community repo or your fork. But sometimes you want to quickly test a single version or a single target. To do that, you can use the Makefile present at the root of this repository.

Actually, the makefile only support Podman.

The Makefile accept the following options:

- **ansible**: Mandatory version of ansible to install in a venv to run ansible-test.
- **docker_image**:
    The container image to use to run our tests. Those images Dockerfile are in https://github.com/community.mysql-test-containers and then pushed to quay.io: E.G.:
    `quay.io/mws/community-mysql-test-containers-my57-py38-mysqlclient201-pymysql0711:latest`. Look in the link above for a complete list of available containers. You can also look into `.github/workflows/ansible-test-plugins.yml`
    Unfortunatly you must provide the right container_image yourself. And you still need to provides db_engine_version, python, etc... because ansible-test won't do black magic to try to detect what we expect. Explicit is better than implicit anyway.
    To minimise the amount of images, pymysql 0.7.11 and mysqlclient are shipped together.
- **db_engine_version**: The name of the container to use for the service containers that will host a primary database and two replicas. Either MYSQL or MariaDB. Use ':' as a separator. Do not use short version, like mysql:8 for instance. Our tests expect a full version to filter tests precisely. For instance: `when: db_version is version ('8.0.22', '>')`.
- **connector**: The name of the python package of the connector along with its version number. Use '==' as a separator.
- **python**: The python version to use in the controller.
- **target** : If omitted, all test targets will run. But you can limit the tests to a single target to speed up your tests.
- **keep_containers_alive**: This option keeps all tree databases containers and the ansible-test container alive at the end of tests or in case of failure. This is useful to enter one of the containers with `podman exec -it <container-name> bash` for debugging.

Examples:

```sh
# Run all targets
make ansible="stable-2.14" db_engine_version="mysql:5.7.40" python="3.8" connector="pymysql==0.7.10" docker_image="ghcr.io/community.mysql/test-container-my80-py39-mysqlclient203:latest"

# A single target
make ansible="stable-2.14" db_engine_version="mysql:5.7.40" python="3.8" connector="pymysql==0.7.10" docker_image="ghcr.io/community.mysql/test-container-my80-py39-mysqlclient203:latest" target="test_mysql_db"

# Keep databases and ansible tests containers alives
# A single target
make ansible="stable-2.14" db_engine_version="mysql:5.7.40" python="3.8" connector="pymysql==0.7.10" docker_image="ghcr.io/community.mysql/test-container-my80-py39-mysqlclient203:latest" target="test_mysql_db" keep_containers_alive=1

# Rerun tests after using `keep_containers_alive=1`
podman stop -a; podman rm -a; make ansible="stable-2.14" db_engine_version="mysql:5.7.40" python="3.8" connector="pymysql==0.7.10" docker_image="ghcr.io/community.mysql/test-container-my80-py39-mysqlclient203:latest" target="test_mysql_db" keep_containers_alive=1
```


### Run all tests

GitHub Action offer a test matrix that run every combination of Python, MySQL, MariaDB and Connector against each other. To reproduce this, this repo provides a script called *run_all_tests.py*.

Examples:

```sh
python run_all_tests.py
```


### Add a new Python, Connector or Database version

1. Add a workflow in *.github/workflows/*
1. Add a new folder in *test-containers* containing a new Dockerfile. Your container must contains 3 things:
  - The python interpreter
  - The python package to connect to the database (pymysql, mysqlclient, ...)
  - A mysql client to query the database before to prepare tests before our tests starts. This client must provide both `mysql` and `mysqldump` commands.
1. Add your version in *.github/workflows/ansible-test-plugins.yml*

After pushing the commit to the remote, the container will be build and published on ghcr.io. Have a look in the "Action" tab to see if it worked. In case of error `failed to copy: io: read/write on closed pipe` re-run the workflow, this append unfortunately a lot.

To see the docker image produced, go to the main GitHub page of your fork or community.mysql (depending were you pushed) and look for the link "Packages" on the right hand side of the page. This page indicate a "Published x days ago" that is updated infrequently. To see the last time the container has been updated you must click on its title and look in the right hands side bellow the title "Last published".

