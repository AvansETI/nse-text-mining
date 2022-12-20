def is_number(to_test):
    is_int = isinstance(to_test, int)
    is_float = isinstance(to_test, float)

    return is_int or is_float
