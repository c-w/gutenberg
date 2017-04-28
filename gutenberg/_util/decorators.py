"""Module to deal with decorators"""


def execute_only_once(func):
    """Decorator that will only allow a function to be executed the first time
    it's called

    """
    def call_once(*args, **kwargs):
        if not call_once._called:
            try:
                return func(*args, **kwargs)
            finally:
                call_once._called = True
    call_once._called = False
    return call_once
