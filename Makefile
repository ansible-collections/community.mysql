SHELL := /bin/bash

.PHONY: test-integration
test-integration:
	echo -n $(db_engine_version) > tests/integration/db_engine_version
	echo -n $(connector) > tests/integration/connector
	podman run \
		--detach \
		--name primary \
		--env MARIADB_ROOT_PASSWORD=msandbox \
		--env MYSQL_ROOT_PASSWORD=msandbox \
		--network podman \
		--publish 3307:3306 \
		--health-cmd 'mysqladmin ping -P 3306 -pmsandbox | grep alive || exit 1' \
		$(db_engine_version) \
		mysqld
	podman run \
		--detach \
		--name replica1 \
		--env MARIADB_ROOT_PASSWORD=msandbox \
		--env MYSQL_ROOT_PASSWORD=msandbox \
		--network podman \
		--publish 3308:3306 \
		--health-cmd 'mysqladmin ping -P 3306 -pmsandbox | grep alive || exit 1' \
		$(db_engine_version) \
		mysqld
	podman run \
		--detach \
		--name replica2 \
		--env MARIADB_ROOT_PASSWORD=msandbox \
		--env MYSQL_ROOT_PASSWORD=msandbox \
		--network podman \
		--publish 3309:3306 \
		--health-cmd 'mysqladmin ping -P 3306 -pmsandbox | grep alive || exit 1' \
		$(db_engine_version) \
		mysqld
	# Setup replication and restart containers
	podman exec primary bash -c 'echo -e [mysqld]\\nserver-id=1\\nlog-bin=/var/lib/mysql/primary-bin > /etc/mysql/conf.d/replication.cnf'
	podman exec replica1 bash -c 'echo -e [mysqld]\\nserver-id=2\\nlog-bin=/var/lib/mysql/replica1-bin > /etc/mysql/conf.d/replication.cnf'
	podman exec replica2 bash -c 'echo -e [mysqld]\\nserver-id=3\\nlog-bin=/var/lib/mysql/replica2-bin > /etc/mysql/conf.d/replication.cnf'
	# Don't restart a container unless it is healthy
	while ! podman healthcheck run primary && [[ "$$SECONDS" -lt 120 ]]; do sleep 1; done
	podman restart -t 30 primary
	while ! podman healthcheck run replica1 && [[ "$$SECONDS" -lt 120 ]]; do sleep 1; done
	podman restart -t 30 replica1
	while ! podman healthcheck run replica2 && [[ "$$SECONDS" -lt 120 ]]; do sleep 1; done
	podman restart -t 30 replica2
	while ! podman healthcheck run primary && [[ "$$SECONDS" -lt 120 ]]; do sleep 1; done
	mkdir -p .venv/$(ansible)
	python -m venv .venv/$(ansible)
	source .venv/$(ansible)/bin/activate
	python -m pip install --disable-pip-version-check --user https://github.com/ansible/ansible/archive/$(ansible).tar.gz ansible-test
	-set -x; ansible-test integration $(target) -v --color --coverage --retry-on-error --continue-on-error --diff --docker $(docker_image) --docker-network podman --python $(python); set +x
	# -set -x; ansible-test integration $(target) -v --color --coverage --retry-on-error --continue-on-error --diff --docker $(docker_image) --docker-network podman --python $(python); set +x
	# -set -x; ansible-test integration $(target) -v --color --coverage --diff --docker $(docker_image) --docker-network podman --docker-terminate never --python $(python); set +x
	rm tests/integration/db_engine_version
	rm tests/integration/connector
	podman stop --time 0 --ignore primary
	podman stop --time 0 --ignore replica1
	podman stop --time 0 --ignore replica2
	podman rm --ignore primary
	podman rm --ignore replica1
	podman rm --ignore replica2
