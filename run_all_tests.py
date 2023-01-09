#!/usr/bin/env python

import yaml

github_workflow_file = '.github/workflows/ansible-test-plugins.yml'


def read_github_workflow_file():
    with open(github_workflow_file, 'r') as gh_file:
        try:
            return yaml.safe_load(gh_file)
        except yaml.YAMLError as exc:
            print(exc)


def extract_value(target, dict_yaml):
    for key, value in dict_yaml.items():
        if key == target:
            return value


def extract_matrix(workflow_yaml):
    jobs = extract_value('jobs', workflow_yaml)
    integration = extract_value('integration', jobs)
    strategy = extract_value('strategy', integration)
    matrix = extract_value('matrix', strategy)
    return matrix


def is_exclude(exclude_list, test_suite):
    test_is_excluded = False
    for excl in exclude_list:
        match = 0

        if 'db_engine_version' in excl:
            if excl.get('db_engine_version') == test_suite[0]:
                match += 1

        if 'ansible' in excl:
            if excl.get('ansible') == test_suite[1]:
                match += 1

        if 'python' in excl:
            if excl.get('python') == test_suite[2]:
                match += 1

        if 'connector' in excl:
            if excl.get('connector') == test_suite[3]:
                match += 1

        if match > 1:
            test_is_excluded = True

    return test_is_excluded


def main():
    workflow_yaml = read_github_workflow_file()
    tests_matrix_yaml = extract_matrix(workflow_yaml)

    matrix = []
    exclude_list = tests_matrix_yaml.get('exclude')
    for db_engine in tests_matrix_yaml.get('db_engine_version'):
        for ansible in tests_matrix_yaml.get('ansible'):
            for python in tests_matrix_yaml.get('python'):
                for connector in tests_matrix_yaml.get('connector'):
                    if not is_exclude(exclude_list, (db_engine, ansible, python, connector)):
                        matrix.append((db_engine, ansible, python, connector))

    print(len(matrix))


if __name__ == '__main__':
    main()
