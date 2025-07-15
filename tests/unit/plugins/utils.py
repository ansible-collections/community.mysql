from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class dummy_cursor_class():
    """Dummy class for returning an answer for SELECT VERSION()."""
    def __init__(self, output, ret_val_type='dict'):
        self.output = output
        self.ret_val_type = ret_val_type

    def execute(self, query):
        pass

    def fetchone(self):
        if self.ret_val_type == 'dict':
            return {'version': self.output}

        elif self.ret_val_type == 'list':
            return [self.output]


class MockCursor:
    Warning = None

    def __init__(self, status="ONLINE", warning = None):
        self.status = status
        self.executed_queries = []
        self.Warning = warning

    def execute(self, query):
        self.executed_queries.append(query)
        if self.status == "ERROR":
            # Create a custom exception that mimics mysql_driver.Warning
            class MockWarning(Exception):
                pass
            # Make it available as a class attribute for tests to use
            MockCursor.Warning = MockWarning
            raise MockWarning("Mocked execution error")

    def fetchone(self):
        if len(self.executed_queries) > 0 and "group_replication_status" in self.executed_queries[-1]:
            return ["group_replication_status", self.status]
        return None
