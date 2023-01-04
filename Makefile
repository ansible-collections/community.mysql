.PHONY: test-integration
test-integration:
	podman run \
		--detach \
		--name primary \
		--env MARIADB_ROOT_PASSWORD=msandbox \
		--env MYSQL_ROOT_PASSWORD=msandbox \
		--network podman \
		--publish 3307:3306 \
		--health-cmd 'mysqladmin ping -P 3306 -pmsandbox | grep alive || exit 1' \
		mysql:8.0.22
	podman run \
		--detach \
		--name replica1 \
		--env MARIADB_ROOT_PASSWORD=msandbox \
		--env MYSQL_ROOT_PASSWORD=msandbox \
		--network podman \
		--publish 3308:3306 \
		--health-cmd 'mysqladmin ping -P 3306 -pmsandbox | grep alive || exit 1' \
		mysql:8.0.22 \
		--server_id 2
	podman run \
		--detach \
		--name replica2 \
		--env MARIADB_ROOT_PASSWORD=msandbox \
		--env MYSQL_ROOT_PASSWORD=msandbox \
		--network podman \
		--publish 3309:3306 \
		--health-cmd 'mysqladmin ping -P 3306 -pmsandbox | grep alive || exit 1' \
		mysql:8.0.22 \
		--server_id 3
	while ! podman healthcheck run primary && [[ "$$SECONDS" -lt 120 ]]; do sleep 1; done
		-set -x; ansible-test integration -v --color --coverage --retry-on-error --continue-on-error --diff --docker --docker-network podman --python 3.8; set +x
	podman stop --time 0 --ignore primary
	podman stop --time 0 --ignore replica1
	podman stop --time 0 --ignore replica2
	podman rm --ignore primary
	podman rm --ignore replica1
	podman rm --ignore replica2
