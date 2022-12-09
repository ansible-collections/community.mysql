.PHONY: test-integration-mariadb-10-5
test-integration-mariadb-10-5:
	podman run \
		--detach \
		--name mariadb105 \
		--env MARIADB_ROOT_PASSWORD=msandbox \
		--network podman \
		--publish 3307:3306 \
		--health-cmd 'mysqladmin ping -P 3306 -pmsandbox | grep alive || exit 1' \
		mariadb:10.5
	while ! podman healthcheck run mariadb105 && [[ "$$SECONDS" -lt 120 ]]; do sleep 1; done
	-ansible-test integration test_mysql_db --venv
	podman stop --time 0 --ignore mariadb105
	podman rm --ignore mariadb105
