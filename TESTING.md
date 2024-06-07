# Tests

This collection uses GitHub Actions to run ansible-test to validate its content. Three type of tests are used: Sanity, Integration and Units.

The tests covers plugins and roles (no role available yet, but tests are ready) and can be found here:

- Plugins: *.github/workflows/ansible-test-plugins.yml*
- Roles: *.github/workflows/ansible-test-roles.yml* (unused yet)

Everytime you push on your fork or you create a pull request, both workflows runs. You can see the output on the "Actions" tab.


## Integration tests

You can use GitHub to run ansible-test either on the community repo or your fork. But sometimes you want to quickly test a single version or a single target. To do that, you can use the Makefile present at the root of this repository.

For now, the makefile only supports Podman.


### Requirements

- python >= 3.8 and <= 3.10
- make
- podman
- Minimum 15GB of free space on the device storing containers images and volumes. You can use this command to check: `podman system info --format='{{.Store.GraphRoot}}'|xargs findmnt --noheadings --nofsroot --output SOURCE --target|xargs df -h --output=size,used,avail,pcent,target`
- Minimum 2GB of RAM


### Makefile options

The Makefile accept the following options

- `local_python_version`
  - Mandatory: false
  - Choices:
    - "3.8"
    - "3.9"
    - "3.10"
  - Description: If `Python -V` shows an unsupported version, use this option and choose one of the version available on your system. Use `ls /usr/bin/python3*|grep -v config` to list them.

- `ansible`
  - Mandatory: true
  - Choices:
    - "stable-2.15"
    - "stable-2.16"
    - "stable-2.17"
    - "devel"
  - Description: Version of ansible to install in a venv to run ansible-test

- `db_engine_name`
  - Mandatory: true
  - Choices:
    - "mysql"
    - "mariadb"
  - Description: The name of the database engine to use for the service containers that will host a primary database and two replicas.

- `db_engine_version`
  - Mandatory: true
  - Choices:
    - "5.7.40" <- mysql
    - "8.0.31" <- mysql
    - "10.4.24" <- mariadb
    - "10.5.18" <- mariadb
    - "10.6.11" <- mariadb
  - Description: The tag of the container to use for the service containers that will host a primary database and two replicas. Do not use short version, like `mysql:8` (don't do that) because our tests expect a full version to filter tests precisely. For instance: `when: db_version is version ('8.0.22', '>')`. You can use any tag available on [hub.docker.com/_/mysql](https://hub.docker.com/_/mysql) and [hub.docker.com/_/mariadb](https://hub.docker.com/_/mariadb) but GitHub Action will only use the versions listed above.

- `python`
  - Mandatory: true
  - Choices:
    - "3.8"
    - "3.9"
    - "3.10"
  - Description: The python version to use in the controller (ansible-test container).

- `target`
  - Mandatory: false
  - Choices:
    - "test_mysql_db"
    - "test_mysql_info"
    - "test_mysql_query"
    - "test_mysql_replication"
    - "test_mysql_role"
    - "test_mysql_user"
    - "test_mysql_variables"
  - Description: If omitted, all test targets will run. But you can limit the tests to a single target to speed up your tests.

- `keep_containers_alive`
  - Mandatory: false
  - Description: This option keeps all tree databases containers and the ansible-test container alive at the end of tests or in case of failure. This is useful to enter one of the containers with `podman exec -it <container-name> bash` for debugging. Rerunning the
tests will overwrite the 3 databases containers so no need to kill them in advance. But nothing will kill the ansible-test container. You must do that using `podman stop` and `podman rm`. Add any value to activate this option: `keep_containers_alive=1`

- `continue_on_errors`
  - Mandatory: false
  - Description: Tells ansible-test to retry on errors and also continue on errors. This is the way the GitHub Action's workflow runs the tests. This can be used to catch all errors in a single run, but you'll need to scroll up to find them. Add any value to activate this option: `continue_on_errors=1`


#### Makefile usage examples:

```sh
# Run all targets
make ansible="stable-2.12" db_engine_name="mysql" db_engine_version="5.7.40" python="3.8"

# A single target
make ansible="stable-2.14" db_engine_name="mysql" db_engine_version="5.7.40" python="3.8" target="test_mysql_info"

# Keep databases and ansible tests containers alives
# A single target and continue on errors
make ansible="stable-2.14" db_engine_name="mysql" db_engine_version="8.0.31" python="3.9" target="test_mysql_query" keep_containers_alive=1 continue_on_errors=1

# If your system has an usupported version of Python:
make local_python_version="3.8" ansible="stable-2.14" db_engine_name="mariadb" db_engine_version="10.6.11" python="3.9"
```


### Run all tests

GitHub Action offer a test matrix that run every combination of Python, MySQL, MariaDB and Connector against each other. To reproduce this, this repo provides a script called *run_all_tests.py*.

Examples:

```sh
python run_all_tests.py
```


### Add a new Python or Database version

You can look into [.github/workflows/ansible-test-plugins.yml](https://github.com/ansible-collections/community.mysql/tree/main/.github/workflows)


1. Add your version in the matrix of *.github/workflows/ansible-test-plugins.yml*. You can use [run_all_tests.py](run_all_tests.py) to help you see what the matrix will be. Simply comment out the line `os.system(make_cmd)` before runing the script. You can also add `print(len(matrix))` to display how many tests there will be on GitHub Action.

