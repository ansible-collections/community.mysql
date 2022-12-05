.PHONY: test-integration-ansible-2-11-python-3-8-mariadb-10-5
test-integration-ansible-2-11-python-3-8-mariadb-10-5:
	podman run --detach --name mariadb105 --env MARIADB_ROOT_PASSWORD=msandbox --publish 3307:3306 mariadb:10.5
	ansible-test integration --docker --python 3.8 test_mysql_user
